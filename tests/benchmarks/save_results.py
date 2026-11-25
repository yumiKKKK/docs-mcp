
import json
from pathlib import Path


RESULT_DIR = Path("tests/benchmark-results")
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def save_results(name, results):
    path = RESULT_DIR / f"{name}.json"

    path.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"Saved: {path}")


def compare_results(before_file, after_file):
    before = json.loads(
        Path(before_file).read_text(encoding="utf-8")
    )

    after = json.loads(
        Path(after_file).read_text(encoding="utf-8")
    )

    print("\n===== Performance Comparison =====")

    for name, before_time in before.items():
        if name not in after:
            continue

        after_time = after[name]

        improvement = (
            (before_time - after_time)
            / before_time * 100
            if before_time else 0
        )

        print(f"\n{name}")
        print(f"  Before: {before_time:.6f} sec")
        print(f"  After : {after_time:.6f} sec")
        print(f"  Change: {improvement:+.2f}%")


if __name__ == "__main__":
    compare_results(
        RESULT_DIR / "before.json",
        RESULT_DIR / "after.json"
    )
