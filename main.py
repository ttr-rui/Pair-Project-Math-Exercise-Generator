"""
程序入口：解析命令行参数，调用生成或批改功能。

运行示例：
    python main.py -n 10 -r 10
    python main.py -e Exercises.txt -a Answers.txt

结对作者：谭添睿（3224004344）、李采云（3224004382）
"""
import argparse
import sys

from fraction_util import format_fraction
from generator import generate_exercises, tree_to_string
from checker import check_answers


def main():
    parser = argparse.ArgumentParser(description="小学四则运算题目生成器")
    parser.add_argument("-n", type=int, help="生成题目数量")
    parser.add_argument("-r", type=int, help="数值范围（必须与 -n 一起使用）")
    parser.add_argument("-e", type=str, help="题目文件（用于批改）")
    parser.add_argument("-a", type=str, help="答案文件（用于批改）")

    args = parser.parse_args()

    if args.e and args.a:
        check_answers(args.e, args.a)
        print("批改完成，结果已保存到 Grade.txt")
        return

    if args.n is not None:
        if args.r is None:
            print("错误：必须指定 -r 参数（数值范围）", file=sys.stderr)
            parser.print_help()
            sys.exit(1)

        exercises, answers = generate_exercises(args.n, args.r)

        with open("Exercises.txt", "w", encoding="utf-8") as f:
            for i, tree in enumerate(exercises, 1):
                f.write(f"{i}. {tree_to_string(tree)} =\n")

        with open("Answers.txt", "w", encoding="utf-8") as f:
            for i, ans in enumerate(answers, 1):
                f.write(f"{i}. {format_fraction(ans)}\n")

        print(f"已生成 {len(exercises)} 道题目")
        print("题目已保存到 Exercises.txt")
        print("答案已保存到 Answers.txt")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
