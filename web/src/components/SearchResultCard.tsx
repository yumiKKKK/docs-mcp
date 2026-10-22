import type { SearchResult } from '../types/search';
export default function SearchResultCard({ result, index }: { result: SearchResult; index: number }) {
  return <article className="result-card">
    <div className="result-top"><div className="file-label"><span className="file-icon">MD</span><span className="filename" title={result.filename}>{result.filename}</span></div><span className="score">점수 {result.score}</span></div>
    <div className="tags">{result.matched_terms.map(term => <span className="tag" key={term}>{term}</span>)}</div>
    <p className="snippet">{result.snippet}</p>
    <div className="result-foot">검색 결과 #{index}</div>
  </article>;
}
