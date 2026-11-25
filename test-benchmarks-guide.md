~~① 최적화 전 성능 측정
```bash
pytest tests/benchmarks \
    --benchmark-only \
    --benchmark-json=tests/benchmark-results/before-pytest.json
```

② 최적화 후 성능 측정
```bash
pytest tests/benchmarks \
    --benchmark-only \
    --benchmark-json=tests/benchmark-results/after-pytest.json
```

③ 벤치마크 결과 비교
```bash
pytest tests/benchmarks \
    --benchmark-only \
    --benchmark-compare=tests/benchmark-results/before-pytest.json
```

④ 전체 테스트 실행
```bash
pytest tests/
```

⑤ 기타) 메모리 측정 
```bash
pytest tests/benchmarks/test_memory_bench.py -s
```

