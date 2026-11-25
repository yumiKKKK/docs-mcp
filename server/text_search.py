
from collections import deque
from typing import Iterable, Iterator

def _build_automaton(terms: Iterable[str]) -> list[dict]:
    """검색어 Trie 및 Failure Link 구성."""
    nodes = [{
        "next": {},
        "fail": 0,
        "outputs": [],
    }]

    for term in dict.fromkeys(terms):
        if not term:
            continue

        folded = term.casefold()
        if not folded:
            continue

        state = 0

        for char in folded:
            next_state = nodes[state]["next"].get(char)

            if next_state is None:
                next_state = len(nodes)
                nodes[state]["next"][char] = next_state
                nodes.append({
                    "next": {},
                    "fail": 0,
                    "outputs": [],
                })

            state = next_state

        nodes[state]["outputs"].append((len(folded), term))

    # Failure Link 구성
    queue = deque()

    for child in nodes[0]["next"].values():
        queue.append(child)

    while queue:
        state = queue.popleft()

        for char, child in nodes[state]["next"].items():
            queue.append(child)

            fail = nodes[state]["fail"]

            while fail and char not in nodes[fail]["next"]:
                fail = nodes[fail]["fail"]

            nodes[child]["fail"] = nodes[fail]["next"].get(char, 0)

            nodes[child]["outputs"].extend(
                nodes[nodes[child]["fail"]]["outputs"]
            )

    return nodes


def _iter_matches(
        content: str,
        terms: Iterable[str],
) -> Iterator[tuple[int, int, str]]:
    """원본 문자열 기준 검색 위치와 검색어 반환."""

    nodes = _build_automaton(terms)

    if len(nodes) == 1 or not content:
        return

    # 전체 문자열을 한 번에 정규화
    normalized = content.casefold()

    # Unicode casefold 확장 문자가 있는지 확인
    index_map = None

    if len(normalized) != len(content):
        index_map = []

        for original_index, char in enumerate(content):
            folded_length = len(char.casefold())
            index_map.extend([original_index] * folded_length)

    state = 0

    for index, char in enumerate(normalized):
        while state and char not in nodes[state]["next"]:
            state = nodes[state]["fail"]

        state = nodes[state]["next"].get(char, 0)

        for term_length, term in nodes[state]["outputs"]:
            start = index - term_length + 1

            if index_map is None:
                original_start = start
                original_end = index + 1
            else:
                original_start = index_map[start]
                original_end = index_map[index] + 1

            yield original_start, original_end, term