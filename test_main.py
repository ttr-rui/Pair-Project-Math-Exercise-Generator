"""
单元测试：覆盖分数工具、表达式求值、题目生成、批改功能。

结对作者：谭添睿（3224004344）、李采云（3224004382）
"""
import unittest
from fractions import Fraction

from fraction_util import format_fraction, parse_fraction
from calculator import evaluate_tree
from generator import generate_tree, canonical, generate_exercises
from checker import evaluate_expression_string


class TestFractionUtil(unittest.TestCase):
    def test_format_integer(self):
        self.assertEqual(format_fraction(Fraction(5, 1)), "5")

    def test_format_proper_fraction(self):
        self.assertEqual(format_fraction(Fraction(3, 5)), "3/5")

    def test_format_mixed_fraction(self):
        self.assertEqual(format_fraction(Fraction(19, 8)), "2'3/8")

    def test_parse_proper_fraction(self):
        self.assertEqual(parse_fraction("3/5"), Fraction(3, 5))

    def test_parse_mixed_fraction(self):
        self.assertEqual(parse_fraction("2'3/8"), Fraction(19, 8))

    def test_parse_integer(self):
        self.assertEqual(parse_fraction("5"), Fraction(5, 1))


class TestCalculator(unittest.TestCase):
    def test_add(self):
        tree = ("+", ("num", Fraction(1, 2)), ("num", Fraction(1, 3)))
        self.assertEqual(evaluate_tree(tree), Fraction(5, 6))

    def test_sub(self):
        tree = ("-", ("num", Fraction(5, 6)), ("num", Fraction(1, 3)))
        self.assertEqual(evaluate_tree(tree), Fraction(1, 2))

    def test_mul(self):
        tree = ("×", ("num", Fraction(1, 2)), ("num", Fraction(2, 3)))
        self.assertEqual(evaluate_tree(tree), Fraction(1, 3))

    def test_div(self):
        tree = ("÷", ("num", Fraction(1, 3)), ("num", Fraction(2, 3)))
        self.assertEqual(evaluate_tree(tree), Fraction(1, 2))


class TestGenerator(unittest.TestCase):
    def _count_ops(self, tree):
        if tree[0] == "num":
            return 0
        return 1 + self._count_ops(tree[1]) + self._count_ops(tree[2])

    def _check_no_negative(self, tree):
        """所有子表达式的值均非负"""
        if tree[0] == "num":
            return
        op, l, r = tree[0], tree[1], tree[2]
        lv = evaluate_tree(l)
        rv = evaluate_tree(r)
        if op == "-":
            self.assertGreaterEqual(lv, rv)
        self._check_no_negative(l)
        self._check_no_negative(r)

    def _check_div_proper(self, tree):
        """所有除法结果均为真分数（左 < 右）"""
        if tree[0] == "num":
            return
        op, l, r = tree[0], tree[1], tree[2]
        if op == "÷":
            lv = evaluate_tree(l)
            rv = evaluate_tree(r)
            self.assertLess(lv, rv)
            self.assertNotEqual(rv, 0)
        self._check_div_proper(l)
        self._check_div_proper(r)

    def test_operator_count_max_3(self):
        for _ in range(30):
            for op_count in (1, 2, 3):
                tree, _ = generate_tree(10, op_count)
                self.assertEqual(self._count_ops(tree), op_count)

    def test_no_negative_results(self):
        for _ in range(100):
            tree, val = generate_tree(10, 3)
            self.assertGreaterEqual(val, 0)
            self._check_no_negative(tree)

    def test_division_always_proper(self):
        for _ in range(100):
            tree, _ = generate_tree(10, 3)
            self._check_div_proper(tree)

    def test_no_duplicate_exercises(self):
        exercises, _ = generate_exercises(20, 10)
        canons = [canonical(t) for t in exercises]
        self.assertEqual(len(canons), len(set(canons)))

    def test_commutative_dedup(self):
        """3+2 和 2+3 应视为同一题"""
        t1 = ("+", ("num", Fraction(3, 1)), ("num", Fraction(2, 1)))
        t2 = ("+", ("num", Fraction(2, 1)), ("num", Fraction(3, 1)))
        self.assertEqual(canonical(t1), canonical(t2))


class TestChecker(unittest.TestCase):
    def test_eval_simple_fraction(self):
        self.assertEqual(evaluate_expression_string("1/2 + 1/3"), Fraction(5, 6))

    def test_eval_mixed_fraction(self):
        self.assertEqual(
            evaluate_expression_string("2'3/8 + 1/8"), Fraction(5, 2)
        )

    def test_eval_with_multiplication(self):
        self.assertEqual(
            evaluate_expression_string("1/2 × 2/3"), Fraction(1, 3)
        )

    def test_eval_integer_division_is_exact(self):
        """回归测试：整数 ÷ 整数必须精确，不能退化成浮点"""
        self.assertEqual(evaluate_expression_string("2 ÷ 3"), Fraction(2, 3))
        self.assertEqual(
            evaluate_expression_string("5 ÷ (9 - 2)"), Fraction(5, 7)
        )
        self.assertEqual(
            evaluate_expression_string("1 ÷ 5 ÷ 8"), Fraction(1, 40)
        )


if __name__ == "__main__":
    unittest.main()
