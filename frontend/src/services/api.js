const API_BASE = '/api';

export async function searchAlumni(query) {
  const params = new URLSearchParams({ query });
  const response = await fetch(`${API_BASE}/search?${params.toString()}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Search failed: ${response.status}`);
  }
  return response.json();
}

export async function getProfile(url) {
  const params = new URLSearchParams({ url });
  const response = await fetch(`${API_BASE}/profile?${params.toString()}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Profile fetch failed: ${response.status}`);
  }
  return response.json();
}