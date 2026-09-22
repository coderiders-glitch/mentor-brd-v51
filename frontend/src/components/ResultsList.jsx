function ResultsList({ results, onSelect, isLoading }) {
  if (isLoading) {
    return (
      <section className="results-section">
        <div className="loading-state">
          <div className="spinner" aria-hidden="true"></div>
          <span>Searching alumni...</span>
        </div>
      </section>
    );
  }

  if (!results || results.length === 0) {
    return null;
  }

  return (
    <section className="results-section">
      <h2 className="results-title">Search Results ({results.length})</h2>
      <ul className="results-list" role="list">
        {results.map((result, index) => (
          <li
            key={index}
            className="result-item"
            onClick={() => onSelect(result)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onSelect(result);
              }
            }}
          >
            <div className="result-name">{result.name}</div>
            {result.title && <div className="result-title">{result.title}</div>}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default ResultsList;