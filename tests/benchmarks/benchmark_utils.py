
import time
import tracemalloc
import statistics


def measure_execution(func, *args, repeat=5, **kwargs):
    """
    함수 실행 시간 측정.
    반환값은 초 단위.
    """

    # 워밍업
    func(*args, **kwargs)

    results = []

    for _ in range(repeat):
        start = time.perf_counter()

        func(*args, **kwargs)

        elapsed = time.perf_counter() - start
        results.append(elapsed)

    return {
        "min": min(results),
        "max": max(results),
        "mean": statistics.mean(results),
        "median": statistics.median(results),
        "samples": results,
    }


def measure_memory(func, *args, **kwargs):
    """
    함수 실행 중 Python 메모리 증가량 측정.
    반환 메모리 단위는 bytes.
    """

    tracemalloc.start()

    try:
        before_current, _ = tracemalloc.get_traced_memory()

        result = func(*args, **kwargs)

        after_current, peak = tracemalloc.get_traced_memory()

        return {
            "result": result,
            "current_bytes": after_current - before_current,
            "peak_bytes": peak,
        }

    finally:
        tracemalloc.stop()
