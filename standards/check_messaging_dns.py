#!/usr/bin/env python3
"""检查一个发信域的邮件身份与传输配置，对照 MESSAGING.md 的 AUTH 规则。

不依赖第三方库，也不依赖本机有 dig：走 DNS-over-HTTPS（RFC 8484，Cloudflare/Google），
因此在 CI、容器、本机都能跑。只做只读查询，不改任何东西。

    python3 standards/check_messaging_dns.py vertciti.com
    python3 standards/check_messaging_dns.py vertciti.com --selector resend --md

退出码：全部 MUST 达标且无 WARN → 0；有 WARN → 0；有 FAIL(MUST 不达标) → 1。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request

DOH = ["https://cloudflare-dns.com/dns-query", "https://dns.google/resolve"]


def resolve_txt(name: str) -> list[str]:
    """返回 name 的 TXT 记录（已拼接分段、去引号）。任一 DoH 解析器成功即可。"""
    return _resolve(name, "TXT")


def _resolve(name: str, rtype: str) -> list[str]:
    last = None
    for base in DOH:
        q = base + "?" + urllib.parse.urlencode({"name": name, "type": rtype})
        req = urllib.request.Request(q, headers={"accept": "application/dns-json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.load(r)
        except Exception as e:  # noqa: BLE001 - 换下一个解析器
            last = e
            continue
        out = []
        for ans in data.get("Answer", []):
            val = ans.get("data", "")
            if rtype == "TXT":
                # DoH 把每个字符串分段加引号，拼起来去引号
                parts = re.findall(r'"((?:[^"\\]|\\.)*)"', val)
                val = "".join(parts) if parts else val.strip('"')
            out.append(val)
        return out
    raise RuntimeError(f"所有 DoH 解析器都失败：{last}")


def https_get(url: str) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str, str]] = []  # (rule, level, status, detail)
        self.fail = False

    def add(self, rule: str, level: str, ok: bool | None, detail: str) -> None:
        if ok is True:
            status = "PASS"
        elif ok is None:
            status = "WARN"
        else:
            status = "FAIL"
            if level == "MUST":
                self.fail = True
        self.rows.append((rule, level, status, detail))


def check(domain: str, selector: str | None) -> Report:
    rep = Report()

    # AUTH-2a SPF：域上有 v=spf1
    spf = [t for t in resolve_txt(domain) if t.lower().startswith("v=spf1")]
    rep.add("AUTH-2 SPF", "MUST", bool(spf), spf[0] if spf else "未找到 v=spf1 TXT")

    # AUTH-2b DKIM：给了 selector 才查；检查公钥位数
    if selector:
        dk = resolve_txt(f"{selector}._domainkey.{domain}")
        dk_txt = next((t for t in dk if "p=" in t), "")
        bits = _dkim_bits(dk_txt)
        if not dk_txt:
            rep.add("AUTH-2 DKIM", "MUST", False, f"{selector}._domainkey 无记录")
        elif bits and bits >= 2048:
            rep.add("AUTH-2 DKIM", "MUST", True, f"{selector}: {bits} 位")
        elif bits:
            rep.add("AUTH-2 DKIM", "MUST", False, f"{selector}: {bits} 位（需 ≥2048）")
        else:
            rep.add("AUTH-2 DKIM", "MUST", None, f"{selector}: 有记录但位数无法判定")
    else:
        rep.add("AUTH-2 DKIM", "MUST", None, "未提供 --selector，跳过（请指定发信 selector）")

    # AUTH-3 DMARC：策略进档到 reject
    dmarc = [t for t in resolve_txt(f"_dmarc.{domain}") if t.lower().startswith("v=dmarc1")]
    if not dmarc:
        rep.add("AUTH-3 DMARC", "MUST", False, "无 _dmarc 记录")
    else:
        pol = _tag(dmarc[0], "p") or "none"
        has_rua = "rua=" in dmarc[0].lower()
        if pol == "reject":
            rep.add("AUTH-3 DMARC", "MUST", True, f"p=reject{' +rua' if has_rua else '（缺 rua）'}")
        elif pol == "quarantine":
            rep.add("AUTH-3 DMARC", "MUST", None, f"p=quarantine（目标 reject）{' +rua' if has_rua else '，且缺 rua'}")
        else:
            rep.add("AUTH-3 DMARC", "MUST", False, f"p={pol}（仅监控，未强制）")

    # AUTH-4 MTA-STS：_mta-sts TXT + policy 文件 mode: enforce
    sts_txt = [t for t in resolve_txt(f"_mta-sts.{domain}") if t.lower().startswith("v=stsv1")]
    if not sts_txt:
        rep.add("AUTH-4 MTA-STS", "MUST", False, "无 _mta-sts TXT")
    else:
        pol = https_get(f"https://mta-sts.{domain}/.well-known/mta-sts.txt") or ""
        mode = _wellknown(pol, "mode")
        rep.add("AUTH-4 MTA-STS", "MUST", mode == "enforce",
                f"mode={mode or '取不到策略文件'}")
    # AUTH-4b TLS-RPT
    rpt = [t for t in resolve_txt(f"_smtp._tls.{domain}") if t.lower().startswith("v=tlsrptv1")]
    rep.add("AUTH-4 TLS-RPT", "MUST", bool(rpt), rpt[0] if rpt else "无 _smtp._tls TXT")

    # AUTH-5 CAA
    caa = _resolve(domain, "CAA")
    rep.add("AUTH-5 CAA", "MUST", bool(caa), (", ".join(caa) if caa else "无 CAA 记录"))

    # AUTH-6 BIMI（SHOULD）
    bimi = [t for t in resolve_txt(f"default._bimi.{domain}") if t.lower().startswith("v=bimi1")]
    rep.add("AUTH-6 BIMI", "SHOULD", True if bimi else None,
            bimi[0] if bimi else "无 BIMI（DMARC 到 reject 后再做）")
    return rep


def _dkim_bits(txt: str) -> int | None:
    m = re.search(r"p=([A-Za-z0-9+/=]+)", txt)
    if not m:
        return None
    import base64
    try:
        der = base64.b64decode(m.group(1) + "===")
    except Exception:  # noqa: BLE001
        return None
    if len(der) <= 50:
        return None
    # RSA 公钥位数估计：SubjectPublicKeyInfo DER 去掉 ~38 字节结构开销后即模数，×8 得位数；
    # 只需区分 1024 / 2048 这档，snap 到最近的常见密钥长度。
    raw = (len(der) - 38) * 8
    return min((1024, 2048, 3072, 4096), key=lambda b: abs(b - raw))


def _tag(txt: str, tag: str) -> str | None:
    m = re.search(rf"\b{tag}=([^;]+)", txt)
    return m.group(1).strip() if m else None


def _wellknown(body: str, key: str) -> str | None:
    for line in body.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            if k.strip().lower() == key:
                return v.strip()
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="检查发信域对照 MESSAGING.md 的 AUTH 规则")
    ap.add_argument("domain")
    ap.add_argument("--selector", help="DKIM selector（如 resend、google、s1）")
    ap.add_argument("--md", action="store_true", help="输出 markdown 表")
    a = ap.parse_args()
    rep = check(a.domain, a.selector)

    if a.md:
        print(f"## 发信域检查：`{a.domain}`\n")
        print("| 规则 | 级别 | 结果 | 详情 |")
        print("|---|---|---|---|")
        for rule, lvl, st, detail in rep.rows:
            mark = {"PASS": "✅", "WARN": "🟡", "FAIL": "❌"}[st]
            print(f"| {rule} | {lvl} | {mark} {st} | {detail} |")
    else:
        for rule, lvl, st, detail in rep.rows:
            print(f"[{st:4}] {rule} ({lvl}) — {detail}")
    return 1 if rep.fail else 0


if __name__ == "__main__":
    sys.exit(main())
