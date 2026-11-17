#!/usr/bin/env python3
"""WAR-35 research-only raw I-JSON gate; deliberately NOT installed in runtime.

Call BEFORE any generic parser/JSON Schema/JCS operation. RFC7493 and RFC8785
input constraints plus WAR-35's conservative exact-integer application rule.
"""
import json
import math
import re
from decimal import Decimal, InvalidOperation

MAX_SAFE_INTEGER = (1 << 53) - 1

class RawIJsonError(ValueError):
    pass

def _pairs_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RawIJsonError(f"duplicate decoded object property: {key!r}")
        result[key] = value
    return result

def _exact_integer(token):
    value = int(token, 10)
    if abs(value) > MAX_SAFE_INTEGER:
        raise RawIJsonError("unsafe JSON integer token: encode exact integers as strings")
    return value

def _binary64_number(token):
    # JSON exponent/decimal tokens can overflow or underflow on a binary64 parse.
    # Prevent silent conversion of an exact *integer-valued* decimal/exponent
    # to an unsafe integer, including e.g. 9007199254740993.0 and 9.007...e15.
    # This is a conservative WAR-35 restriction stronger than RFC 7493 SHOULD.
    try:
        value = float(token)
        exact = Decimal(token)
    except (InvalidOperation, ValueError, OverflowError) as exc:
        # Decimal may reject an extreme exponent even when the mantissa is
        # mathematically zero. Such JSON numbers have an unambiguous binary64
        # representation, and canonicalize back to safe integer zero.
        if re.fullmatch(r"-?0(?:\.0+)?[eE][+-]?\d+", token):
            return float(token)
        raise RawIJsonError("unrepresentable JSON number") from exc
    if not math.isfinite(value):
        raise RawIJsonError("non-finite JSON numeric overflow")
    if value == 0 and exact != 0:
        raise RawIJsonError("nonzero JSON number underflows to zero")
    # Test the exact token and ALSO the parsed binary64. A fractional source
    # such as 9007199254740991.9 can round to unsafe integer 2^53, which JCS
    # emits as integer token 9007199254740992: accepted inputs must remain
    # acceptable after canonicalization and fresh raw parsing.
    if exact != 0 and exact == exact.to_integral_value() and abs(exact) > MAX_SAFE_INTEGER:
        raise RawIJsonError("unsafe integer-valued JSON number: use string for exact identity")
    if value.is_integer() and abs(value) > MAX_SAFE_INTEGER:
        raise RawIJsonError("unsafe rounded binary64 integer: use string for exact identity")
    return value

def _no_non_json_constants(token):
    raise RawIJsonError(f"non-JSON numeric literal: {token}")

def _valid_unicode_scalar(s):
    for char in s:
        code = ord(char)
        if (0xD800 <= code <= 0xDFFF or 0xFDD0 <= code <= 0xFDEF or
                (code <= 0x10FFFF and (code & 0xFFFE) == 0xFFFE)):
            raise RawIJsonError(f"disallowed surrogate/noncharacter: U+{code:04X}")

def _walk_strings(obj):
    if isinstance(obj, str):
        _valid_unicode_scalar(obj)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            _valid_unicode_scalar(key)
            _walk_strings(value)
    elif isinstance(obj, list):
        for value in obj:
            _walk_strings(value)

def parse_raw_ijson(raw: bytes):
    """Lossless-sensitive input gate. Accepts UTF-8 JSON bytes; returns parsed Python value.

    This is a *design test reference* with a strict safe integer policy, not a
    general replacement for RFC8785 canonicalization or a production validator.
    """
    if not isinstance(raw, bytes):
        raise TypeError("pass original raw UTF-8 bytes, not a pre-parsed object")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RawIJsonError("UTF-8 BOM not permitted for WAR-35 raw package")
    try:
        text = raw.decode("utf-8", errors="strict")
        result = json.loads(text, object_pairs_hook=_pairs_without_duplicates,
                            parse_int=_exact_integer, parse_float=_binary64_number,
                            parse_constant=_no_non_json_constants)
        _walk_strings(result)
        return result
    except (UnicodeError, json.JSONDecodeError, OverflowError) as exc:
        raise RawIJsonError(str(exc)) from exc
