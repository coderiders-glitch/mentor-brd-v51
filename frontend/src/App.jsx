import { useState } from 'react';
import SearchForm from './components/SearchForm';
import ResultsList from './components/ResultsList';
import ProfileDetail from './components/ProfileDetail';
import * as apiModule from './services/api';
import * as api from './services/api';
function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [profileError, setProfileError] = useState(null);
  const [view, setView] = useState('search');

  const handleSearch = async (query) => {
    setIsSearching(true);
    setSearchError(null);
    setSearchResults(null);
    setSelectedProfile(null);
    setProfileError(null);
    setSearchQuery(query);

    try {
      const data = await api.searchAlumni(query);
      setSearchResults(data.results || []);
    } catch (err) {
      setSearchError(err.message || 'Search failed. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectResult = async (result) => {
    if (!result.url) {
      setProfileError('No profile URL available for this result.');
      return;
    }

    setIsLoadingProfile(true);
    setProfileError(null);
    setView('profile');

    try {
      const profile = await api.getProfile(result.url);
      setSelectedProfile(profile);
    } catch (err) {
      setProfileError(err.message || 'Failed to load profile.');
    } finally {
      setIsLoadingProfile(false);
    }
  };

  const handleBackToResults = () => {
    setView('search');
    setSelectedProfile(null);
    setProfileError(null);
  };

  return (
    <div className="app-container">
      <h1 className="page-title">Alumni Search</h1>

      {view === 'search' && (
        <>
          <SearchForm onSearch={handleSearch} isLoading={isSearching} />

          {searchError && (
            <div className="error-state" role="alert">
              {searchError}
            </div>
          )}

          {isSearching === false && searchResults !== null && searchResults.length === 0 && (
            <div className="empty-state">
              No alumni found for "{searchQuery}". Try a different name.
            </div>
          )}

          <ResultsList
            results={searchResults}
            onSelect={handleSelectResult}
            isLoading={isSearching}
          />
        </>
      )}

      {view === 'profile' && (
        <ProfileDetail
          profile={selectedProfile}
          isLoading={isLoadingProfile}
          error={profileError}
          onBack={handleBackToResults}
        />
      )}
    </div>
  );
}

export default App;