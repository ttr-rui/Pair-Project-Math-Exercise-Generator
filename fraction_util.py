"""
分数工具模块：负责分数的格式化输出与解析。

结对作者：谭添睿（3224004344）、李采云（3224004382）
"""
from fractions import Fraction


def format_fraction(f: Fraction) -> str:
    """
    把 Fraction 转换成题目要求的格式：
    - 整数：5
    - 真分数：3/5
    - 带分数：2'3/8
    """
    if f.denominator == 1:
        return str(f.numerator)
    if abs(f.numerator) > f.denominator:
        whole = f.numerator // f.denominator
        remainder = f.numerator % f.denominator
        return f"{whole}'{remainder}/{f.denominator}"
    return f"{f.numerator}/{f.denominator}"


def parse_fraction(s: str) -> Fraction:
    """
    把字符串解析为 Fraction，支持：
    - "5"       -> 5
    - "3/5"     -> 3/5
    - "2'3/8"   -> 19/8
    """
    s = s.strip()
    if not s:
        raise ValueError("空字符串无法解析为分数")
    if "'" in s:
        whole, frac = s.split("'")
        num, den = frac.split("/")
        return Fraction(int(whole) * int(den) + int(num), int(den))
    if "/" in s:
        num, den = s.split("/")
        return Fraction(int(num), int(den))
    return Fraction(int(s))
