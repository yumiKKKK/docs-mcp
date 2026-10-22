type Props = { page: number; totalPages: number; hasPrevious: boolean; hasNext: boolean; onPage: (page: number) => void };
export default function Pagination({ page, totalPages, hasPrevious, hasNext, onPage }: Props) {
  if (!totalPages) return null;
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1).filter(n => Math.abs(n - page) <= 2 || n === 1 || n === totalPages);
  return <nav className="pagination" aria-label="검색 결과 페이지">
    <button disabled={!hasPrevious} onClick={() => onPage(page - 1)}>← 이전</button>
    {pages.map((n, i) => <span className="page-wrap" key={n}>{i > 0 && pages[i - 1] !== n - 1 ? <span className="ellipsis">…</span> : null}<button className={n === page ? 'page active' : 'page'} aria-current={n === page ? 'page' : undefined} onClick={() => onPage(n)}>{n}</button></span>)}
    <button disabled={!hasNext} onClick={() => onPage(page + 1)}>다음 →</button>
  </nav>;
}
