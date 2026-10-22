import type { SearchResult } from '../types/search';
import SearchResultCard from './SearchResultCard';
export default function SearchResultList({ results, page, pageSize }: { results: SearchResult[]; page: number; pageSize: number }) {
  return <div className="results-list">{results.map((result, i) => <SearchResultCard key={result.filename} result={result} index={(page - 1) * pageSize + i + 1} />)}</div>;
}
