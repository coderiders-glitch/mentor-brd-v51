function ProfileDetail({ profile, isLoading, error, onBack }) {
  if (isLoading) {
    return (
      <section className="profile-section">
        <div className="loading-state">
          <div className="spinner" aria-hidden="true"></div>
          <span>Loading profile...</span>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="profile-section">
        <button className="back-button" onClick={onBack}>
          ← Back to results
        </button>
        <div className="error-state" role="alert">
          {error}
        </div>
      </section>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <section className="profile-section">
      <button className="back-button" onClick={onBack}>
        ← Back to results
      </button>
      <div className="profile-header">
        <h2 className="profile-name">{profile.name}</h2>
        {profile.headline && (
          <p className="profile-headline">{profile.headline}</p>
        )}
      </div>
      {profile.experience && profile.experience.length > 0 && (
        <div className="experience-section">
          <h3 className="experience-title">Experience</h3>
          <ul className="experience-list">
            {profile.experience.map((exp, index) => (
              <li key={index} className="experience-item">
                <div className="experience-role">{exp.title}</div>
                {exp.company && (
                  <div className="experience-company">{exp.company}</div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export default ProfileDetail;