import { FormEvent } from 'react';
type Props = { query: string; setQuery: (value: string) => void; onSearch: () => void; loading: boolean };
export default function SearchBar({ query, setQuery, onSearch, loading }: Props) {
  function submit(event: FormEvent) { event.preventDefault(); onSearch(); }
  return <form className="searchbar" onSubmit={submit}>
    <span className="search-icon" aria-hidden="true">⌕</span>
    <input aria-label="검색어" value={query} onChange={e => setQuery(e.target.value)} placeholder="문서에서 찾고 싶은 내용을 입력하세요" />
    <button type="submit" disabled={loading || !query.trim()}>{loading ? '검색 중…' : '검색'}</button>
  </form>;
}
