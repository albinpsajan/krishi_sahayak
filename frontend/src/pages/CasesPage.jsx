/** Shared crop-cases list page (farmer "My Cases" / officer "Case Reviews"). */
export default function CasesPage({ cases, onViewCase }) {
  return (
    <div className="ks-card">
      <h3>🌾 All Crop Cases & Diagnostic History</h3>
      <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {cases.map((c) => (
          <div key={c.id} className="ks-card" style={{ background: 'var(--bg-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h4>{c.case_number} - {c.crop_type} ({c.variety})</h4>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  Farmer: {c.farmer_name} | Location: {c.field_location}
                </p>
              </div>
              <button className="ks-btn ks-btn-primary" onClick={() => onViewCase(c)}>
                Open Full Case Record
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
