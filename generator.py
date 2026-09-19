"""
题目生成模块：生成合法的四则运算表达式树，并进行去重。

约束：
1. 减法结果非负
2. 除法结果是真分数（左 < 右，结果 < 1）
3. 每道题运算符不超过 3 个
4. 题目不重复（考虑 + 和 × 的交换律）

结对作者：谭添睿（3224004344）、李采云（3224004382）
"""
import random
from fractions import Fraction

from fraction_util import format_fraction


def generate_number(max_value: int) -> Fraction:
    """生成一个 1 到 max_value-1 的自然数或真分数"""
    if max_value <= 2:
        return Fraction(1, 1)
    if random.random() < 0.4:
        return Fraction(random.randint(1, max_value - 1), 1)
    den = random.randint(2, max_value - 1)
    num = random.randint(1, den - 1)
    return Fraction(num, den)


def generate_tree(max_value: int, op_count: int, _depth: int = 0):
    """
    递归生成一个有 op_count 个运算符的表达式树。
    返回 (tree, value)，value 是表达式的值。
    树结构：(op, left, right) 或 ("num", Fraction)
    """
    if op_count == 0:
        v = generate_number(max_value)
        return ("num", v), v

    left_ops = random.randint(0, op_count - 1)
    right_ops = op_count - 1 - left_ops

    left_tree, left_val = generate_tree(max_value, left_ops, _depth + 1)
    right_tree, right_val = generate_tree(max_value, right_ops, _depth + 1)

    op = random.choice(["+", "-", "×", "÷"])

    if op == "-":
        if left_val < right_val:
            left_tree, right_tree = right_tree, left_tree
            left_val, right_val = right_val, left_val
        value = left_val - right_val

    elif op == "÷":
        # 右值不能为 0
        if right_val == 0:
            right_tree, right_val = ("num", Fraction(1, 1)), Fraction(1, 1)

        # 若左右相等，除法结果会是 1，不是真分数。
        # 优先尝试修改左叶子（如果它是叶子）
        if left_val == right_val and left_tree[0] == "num":
            for _ in range(20):
                new_v = generate_number(max_value)
                if new_v != right_val:
                    left_tree, left_val = ("num", new_v), new_v
                    break

        # 如果左子树不是叶子（无法简单改值），重试整棵树
        if left_val == right_val:
            if _depth < 50:
                return generate_tree(max_value, op_count, _depth + 1)
            # 兜底（实测约 0.1% 触发）：放弃本轮随机结果，退化为确定合法的最简除法
            # 1/(max-1) ÷ 1。不能用 left_val + 1 兜底 —— 那样会造出超出 -r 范围的数值。
            den = max(2, max_value - 1)
            return ("÷", ("num", Fraction(1, den)), ("num", Fraction(1, 1))), Fraction(1, den)

        if left_val > right_val:
            left_tree, right_tree = right_tree, left_tree
            left_val, right_val = right_val, left_val
        value = left_val / right_val

    elif op == "+":
        value = left_val + right_val

    else:  # ×
        value = left_val * right_val

    return (op, left_tree, right_tree), value


def canonical(tree):
    """
    把表达式树规范化为一个元组，用于去重。
    对 + 和 × 应用交换律：左右子树按字典序排序。
    """
    if tree[0] == "num":
        return (0, tree[1])

    op, left, right = tree[0], tree[1], tree[2]
    lc = canonical(left)
    rc = canonical(right)

    if op in ("+", "×"):
        if lc > rc:
            lc, rc = rc, lc

    return (1, op, lc, rc)


def _to_string_with_parens(tree, parent_op, is_left):
    """递归生成字符串，按运算优先级决定是否加括号"""
    if tree[0] == "num":
        return format_fraction(tree[1])

    op = tree[0]
    s = tree_to_string(tree)

    prec = {"+": 1, "-": 1, "×": 2, "÷": 2}
    if prec[op] < prec[parent_op]:
        return f"({s})"
    if prec[op] == prec[parent_op] and not is_left and parent_op in ("-", "÷"):
        return f"({s})"
    return s


def tree_to_string(tree) -> str:
    """把表达式树转成可读的字符串"""
    if tree[0] == "num":
        return format_fraction(tree[1])

    op, left, right = tree[0], tree[1], tree[2]
    left_s = _to_string_with_parens(left, op, True)
    right_s = _to_string_with_parens(right, op, False)
    return f"{left_s} {op} {right_s}"


def generate_exercises(n: int, r: int):
    """
    生成 n 道题，数值范围 < r。
    返回 (exercises, answers)：
    - exercises: 表达式树列表
    - answers: 答案（Fraction）列表
    """
    exercises = []
    answers = []
    seen = set()

    attempts = 0
    max_attempts = max(n * 1000, 200000)

    while len(exercises) < n and attempts < max_attempts:
        attempts += 1
        op_count = random.randint(1, 3)
        tree, value = generate_tree(r, op_count)
        canon = canonical(tree)
        if canon in seen:
            continue
        seen.add(canon)
        exercises.append(tree)
        answers.append(value)

    if len(exercises) < n:
        print(f"警告：在尝试 {attempts} 次后仅生成了 {len(exercises)} 道不重复题目。")

    return exercises, answers
