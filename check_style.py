"""Проверка стиля кода (пара 30): snake_case для функций и переменных,
CamelCase для классов, UPPER_CASE для констант."""
import ast
import os
import re
import sys

SNAKE = re.compile(r"^(_|_{0,2}[a-z][a-z0-9_]*_{0,2})$")
CAMEL = re.compile(r"^_?[A-Z][A-Za-z0-9]*$")
UPPER = re.compile(r"^_?[A-Z][A-Z0-9_]*$")
SKIP_NAMES = {"self", "cls"}


def check_file(path):
    """Возвращает список нарушений в файле."""
    with open(path, encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=path)
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not SNAKE.match(node.name):
                problems.append((node.lineno, f"функция «{node.name}» — нужен snake_case"))
            for arg in node.args.args + node.args.kwonlyargs:
                if arg.arg not in SKIP_NAMES and not SNAKE.match(arg.arg):
                    problems.append((node.lineno, f"аргумент «{arg.arg}» — нужен snake_case"))
        elif isinstance(node, ast.ClassDef):
            if not CAMEL.match(node.name):
                problems.append((node.lineno, f"класс «{node.name}» — нужен CamelCase"))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if not (SNAKE.match(node.id) or UPPER.match(node.id)):
                problems.append((node.lineno, f"переменная «{node.id}» — нужен snake_case"))
    return sorted(set(problems))


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    files = sorted(f for f in os.listdir(folder) if f.endswith(".py"))
    total = 0
    print("=" * 60)
    print("ПРОВЕРКА СТИЛЯ КОДА")
    print("=" * 60)
    for name in files:
        problems = check_file(os.path.join(folder, name))
        total += len(problems)
        if problems:
            print(f"❌ {name}")
            for line, text in problems:
                print(f"     строка {line}: {text}")
        else:
            print(f"✅ {name}")
    print("=" * 60)
    print("Нарушений нет" if total == 0 else f"Нарушений: {total}")
    return total == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
