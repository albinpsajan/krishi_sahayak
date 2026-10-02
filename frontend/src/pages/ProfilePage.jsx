/** Profile page: account facts plus role-specific profile card. */
export default function ProfilePage({ userProfile }) {
  return (
    <div className="ks-card" style={{ maxWidth: '640px' }}>
      <h3>👤 User Account Profile</h3>
      {userProfile && (
        <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div><strong>Full Name:</strong> {userProfile.full_name}</div>
          <div><strong>Email:</strong> {userProfile.email}</div>
          <div><strong>Role:</strong> {userProfile.role}</div>
          <div><strong>Contact Phone:</strong> {userProfile.phone || 'N/A'}</div>

          {userProfile.farmer_profile && (
            <div style={{ background: 'var(--rice-paper)', padding: '14px', borderRadius: '8px', marginTop: '8px' }}>
              <h4 style={{ marginBottom: '8px' }}>🌾 Farm Profile</h4>
              <div>District: {userProfile.farmer_profile.district}</div>
              <div>State: {userProfile.farmer_profile.state}</div>
              <div>Land Area: {userProfile.farmer_profile.land_size_acres} Acres</div>
              <div>Primary Crops: {userProfile.farmer_profile.primary_crops}</div>
              <div>Water Source: {userProfile.farmer_profile.water_source}</div>
            </div>
          )}

          {userProfile.officer_profile && (
            <div style={{ background: 'var(--rice-paper)', padding: '14px', borderRadius: '8px', marginTop: '8px' }}>
              <h4 style={{ marginBottom: '8px' }}>🏛️ Officer Profile</h4>
              <div>Officer Code: {userProfile.officer_profile.officer_code}</div>
              <div>Designation: {userProfile.officer_profile.designation}</div>
              <div>Jurisdiction: {userProfile.officer_profile.jurisdiction_district}</div>
              <div>Department: {userProfile.officer_profile.department}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
