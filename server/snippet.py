
def create_snippet(
        content: str,
        position: int,
        end_position: int,
        snippet_before: int = 100,
        snippet_after: int = 500,
) -> str:
    """검색어 주변 문맥을 추출한다."""

    start = max(0, position - snippet_before)
    end = min(len(content), end_position + snippet_after)

    snippet = content[start:end].strip()

    if start > 0:
        snippet = "..." + snippet

    if end < len(content):
        snippet += "..."

    return snippet
