"""
批改模块：读取题目文件和答案文件，统计对错。

结对作者：谭添睿（3224004344）、李采云（3224004382）
"""
import re
from fractions import Fraction

from fraction_util import parse_fraction


def _placeholder(index: int) -> str:
    """
    生成占位符。占位符中**不能出现数字**，否则会被后面的整数正则误匹配，
    因此把序号 0-9 映射成字母 A-J（0->A, 12->BC）。
    """
    return "__" + "".join(chr(65 + int(ch)) for ch in str(index)) + "__"


def evaluate_expression_string(expr: str) -> Fraction:
    """
    对题目字符串求值。
    支持 3/5、2'3/8、整数、+ − × ÷ 和括号。

    要点：所有操作数都必须包成 Fraction 后参与运算。
    若放任整数直接相除（如 2 / 3），Python 会得到浮点数 0.6666...，
    与分数答案比较时必然不相等 —— 这是本函数最容易踩的坑。
    """
    s = expr.replace("×", "*").replace("÷", "/")

    mapping = {}
    counter = [0]

    def next_key() -> str:
        key = _placeholder(counter[0])
        counter[0] += 1
        return key

    # ① 带分数 2'3/8 —— 必须最先处理，否则会被真分数规则拆坏
    def replace_mixed(m):
        key = next_key()
        whole, num, den = int(m.group(1)), int(m.group(2)), int(m.group(3))
        mapping[key] = f"Fraction({whole} * {den} + {num}, {den})"
        return key

    # ② 真分数 a/b（题目里的写法，数字紧贴斜杠，如 1/2）
    def replace_fraction(m):
        key = next_key()
        mapping[key] = f"Fraction({int(m.group(1))}, {int(m.group(2))})"
        return key

    # ③ 其余整数（包括 ÷ 两侧带空格的整数，例如 "2 / 3" 中的 2 和 3）
    def replace_integer(m):
        key = next_key()
        mapping[key] = f"Fraction({int(m.group(1))}, 1)"
        return key

    s = re.sub(r"(\d+)'(\d+)/(\d+)", replace_mixed, s)
    s = re.sub(r"(\d+)/(\d+)", replace_fraction, s)
    s = re.sub(r"(\d+)", replace_integer, s)

    # ④ 回填：此时已完成所有扫描，可以安全地写入带数字的表达式
    for key, value in mapping.items():
        s = s.replace(key, value)

    return eval(s, {"__builtins__": {}}, {"Fraction": Fraction})


def read_lines(path: str):
    """读取文件所有非空行"""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def strip_number_prefix(line: str) -> str:
    """去掉行首的 '1. ' 之类的编号"""
    m = re.match(r"^\d+\.\s*(.*)", line)
    return m.group(1) if m else line


def check_answers(exercise_file: str, answer_file: str):
    """批改答案并输出 Grade.txt"""
    exercises = read_lines(exercise_file)
    user_answers = read_lines(answer_file)

    correct = []
    wrong = []

    for i, (ex, ua) in enumerate(zip(exercises, user_answers), 1):
        ex_clean = strip_number_prefix(ex)
        ua_clean = strip_number_prefix(ua)

        if "=" in ex_clean:
            ex_clean = ex_clean.split("=")[0].strip()

        try:
            correct_ans = evaluate_expression_string(ex_clean)
            user_ans = parse_fraction(ua_clean)
            if correct_ans == user_ans:
                correct.append(i)
            else:
                wrong.append(i)
        except Exception:
            wrong.append(i)

    with open("Grade.txt", "w", encoding="utf-8") as f:
        f.write(f"Correct: {len(correct)} ({', '.join(map(str, correct))})\n")
        f.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})\n")

    return correct, wrong
