import { useState } from 'react';

function SearchForm({ onSearch, isLoading }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleChange = (e) => {
    setQuery(e.target.value);
  };

  return (
    <section className="search-section">
      <form className="search-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="search-input"
          placeholder="Enter alumni name (e.g., Aman Sharma)"
          value={query}
          onChange={handleChange}
          disabled={isLoading}
          aria-label="Alumni name search"
        />
        <button
          type="submit"
          className="search-button"
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </form>
    </section>
  );
}

export default SearchForm;