"""
表达式求值模块：对表达式树求值。

结对作者：谭添睿（3224004344）、李采云（3224004382）
"""
from fractions import Fraction


def evaluate_tree(tree) -> Fraction:
    """
    对表达式树求值。
    表达式树结构：
    - 叶子节点：("num", Fraction)
    - 运算节点：(op, left, right)，op 取 "+", "-", "×", "÷"
    """
    if tree[0] == "num":
        return tree[1]
    op, left, right = tree[0], tree[1], tree[2]
    lv = evaluate_tree(left)
    rv = evaluate_tree(right)
    if op == "+":
        return lv + rv
    if op == "-":
        return lv - rv
    if op == "×":
        return lv * rv
    if op == "÷":
        return lv / rv
    raise ValueError(f"未知运算符: {op}")
