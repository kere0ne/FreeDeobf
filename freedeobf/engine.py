from __future__ import annotations
import base64
import re
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class TransformResult:
    name: str
    changed: bool
    detail: str

Transform = Callable[[str], tuple[str, str]]

def _lua_decimal_escapes(source: str) -> tuple[str, str]:
    pattern = re.compile(r'''(["'])(?:(?:\\.)|[^\\])*?\1''', re.DOTALL)
    count = 0
    def decode(match: re.Match[str]) -> str:
        nonlocal count
        literal = match.group(0)
        quote, body = literal[0], literal[1:-1]
        decoded = re.sub(r"\\(\d{1,3})", lambda m: chr(int(m.group(1)) % 256), body)
        if decoded != body: count += 1
        return quote + decoded + quote
    return pattern.sub(decode, source), f"decoded {count} string literal(s)"

def _lua_concat_strings(source: str) -> tuple[str, str]:
    pattern = re.compile(r'''(["'])([^\\'" \n\r]*)\1\s*\.\.\s*(["'])([^\\'" \n\r]*)\3''')
    count = 0
    def replace(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return match.group(1) + match.group(2) + match.group(4) + match.group(1)
    return pattern.sub(replace, source), f"folded {count} literal concatenation(s)"

def _decode_base64_literals(source: str) -> tuple[str, str]:
    pattern = re.compile(r'''(?:base64\.decode|b64decode)\(\s*(['"])([A-Za-z0-9+/=_-]{8,})\1\s*\)''')
    count = 0
    def replace(match: re.Match[str]) -> str:
        nonlocal count
        try:
            raw = base64.urlsafe_b64decode(match.group(2) + "=" * (-len(match.group(2)) % 4))
            decoded = raw.decode("utf-8")
        except (ValueError, UnicodeDecodeError): return match.group(0)
        if not decoded.isprintable() and "\n" not in decoded and "\t" not in decoded: return match.group(0)
        count += 1
        return repr(decoded)
    return pattern.sub(replace, source), f"decoded {count} explicit base64 call(s)"

def _format_whitespace(source: str) -> tuple[str, str]:
    result = source.replace("\r\n", "\n").replace("\r", "\n")
    result = "\n".join(line.rstrip() for line in result.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", result).strip() + "\n", "normalized line endings and trailing whitespace"

TRANSFORMS: tuple[tuple[str, Transform], ...] = (("lua-decimal-escapes", _lua_decimal_escapes), ("lua-string-concat", _lua_concat_strings), ("explicit-base64", _decode_base64_literals), ("whitespace", _format_whitespace))

def deobfuscate(source: str, language: str = "auto", passes: int = 3) -> tuple[str, list[TransformResult]]:
    """Apply conservative deterministic transforms; never execute input code."""
    if not 1 <= passes <= 20: raise ValueError("passes must be between 1 and 20")
    current, history = source, []
    for _ in range(passes):
        changed_this_pass = False
        for name, transform in TRANSFORMS:
            updated, detail = transform(current)
            changed = updated != current
            history.append(TransformResult(name, changed, detail))
            current = updated
            changed_this_pass |= changed
        if not changed_this_pass: break
    return current, history