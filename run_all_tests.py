"""Запускает все автоматические тесты проекта и печатает общий итог."""
import subprocess
import sys

TESTS = [
    "test_product.py", "test_discount.py", "test_discount_extra.py",
    "test_discount_boundaries.py", "test_indicator.py", "test_highlight.py",
    "test_color.py", "test_catalog.py", "test_orders.py", "check_style.py",
]


def main():
    failed = []
    for name in TESTS:
        result = subprocess.run([sys.executable, name], capture_output=True, text=True,
                                encoding="utf-8")
        output = result.stdout + result.stderr
        ok = result.returncode == 0 and "❌" not in output and "Traceback" not in output
        print(f"{'✅' if ok else '❌'} {name}")
        if not ok:
            failed.append(name)
            print(output[-800:])
    print("=" * 50)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if not failed else f"ЕСТЬ ОШИБКИ: {', '.join(failed)}")
    return not failed


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
