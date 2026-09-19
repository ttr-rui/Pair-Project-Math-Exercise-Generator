def _placeholder(index: int) -> str:
    """占位符里不能出现数字，否则会被后面的整数正则误匹配，
       因此把序号 0-9 映射成字母 A-J。"""
    return "__" + "".join(chr(65 + int(ch)) for ch in str(index)) + "__"


def evaluate_expression_string(expr: str) -> Fraction:
    s = expr.replace("×", "*").replace("÷", "/")
    mapping, counter = {}, [0]

    def next_key():
        key = _placeholder(counter[0]); counter[0] += 1; return key

    def replace_mixed(m):          # ① 带分数 2'3/8 —— 必须最先处理，否则被真分数规则拆坏
        key = next_key()
        whole, num, den = int(m.group(1)), int(m.group(2)), int(m.group(3))
        mapping[key] = f"Fraction({whole} * {den} + {num}, {den})"
        return key

    def replace_fraction(m):       # ② 真分数 1/2
        key = next_key()
        mapping[key] = f"Fraction({int(m.group(1))}, {int(m.group(2))})"
        return key

    def replace_integer(m):        # ③ 剩下的整数，包括 "2 / 3" 里的 2 和 3
        key = next_key()
        mapping[key] = f"Fraction({int(m.group(1))}, 1)"
        return key

    s = re.sub(r"(\d+)'(\d+)/(\d+)", replace_mixed,    s)
    s = re.sub(r"(\d+)/(\d+)",       replace_fraction, s)
    s = re.sub(r"(\d+)",             replace_integer,  s)

    for key, value in mapping.items():                 # ④ 回填（三步全部扫完后再写）
        s = s.replace(key, value)

    return eval(s, {"__builtins__": {}}, {"Fraction": Fraction})
