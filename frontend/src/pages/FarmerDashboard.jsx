/** Farmer home dashboard: stats summary + active crop cases list. */
export default function FarmerDashboard({ user, cases, subsidies, auditLogs, lang, onNewCase, onViewCase }) {
  return (
    <div>
      <div className="ks-card" style={{ background: 'linear-gradient(135deg, #1e3a1e 0%, #2d5a27 100%)', color: '#fff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ color: '#fff', fontSize: '1.8rem', marginBottom: '8px' }}>
              {lang === 'ml' ? `സ്വാഗതം, ${user.full_name}` : `Welcome, ${user.full_name}`}
            </h2>
            <p style={{ color: '#eaf4e9', fontSize: '1rem' }}>
              {lang === 'ml'
                ? 'നിങ്ങളുടെ വിള സംരക്ഷണവും സബ്‌സിഡി വിവരങ്ങളും ഇവിടെ കാണാം.'
                : 'AI-assisted crop disease assessment & officer-verified guidance system.'}
            </p>
          </div>
          <button className="ks-btn ks-btn-gold" style={{ padding: '14px 24px', fontSize: '1.05rem' }} onClick={onNewCase}>
            🌱 + New Crop Case
          </button>
        </div>
      </div>

      {/* Farmer Stats Summary */}
      <div className="grid-4">
        <div className="ks-card">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>ACTIVE CROP CASES</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--leaf-700)' }}>{cases.length}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Cases under active tracking</div>
        </div>
        <div className="ks-card">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>OFFICER VERIFIED</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--leaf-600)' }}>
            {cases.filter((c) => c.status === 'Officer Verified').length}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--badge-verified-text)' }}>✓ Verified by Agri Officer</div>
        </div>
        <div className="ks-card">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>MATCHED SUBSIDIES</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--harvest-gold)' }}>{subsidies.length}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--harvest-gold)' }}>Available for application</div>
        </div>
        <div className="ks-card">
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>AUDIT RECORDS</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--water-teal)' }}>{auditLogs.length}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--water-teal)' }}>🔒 SHA-256 Ledger signed</div>
        </div>
      </div>

      {/* Active Crop Cases List */}
      <div className="ks-card">
        <div className="ks-card-header">
          <h3>🌾 Active Crop Cases</h3>
          <button className="ks-btn ks-btn-outline" onClick={onNewCase}>+ New Case</button>
        </div>
        {cases.length === 0 ? (
          <p>No active crop cases found.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {cases.map((c) => (
              <div
                key={c.id}
                style={{
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'var(--rice-paper)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 800, color: 'var(--leaf-900)' }}>{c.case_number}</span>
                    <span className="ks-badge ks-badge-ai">🤖 Crop: {c.crop_type} ({c.variety})</span>
                    {c.status === 'Officer Verified' ? (
                      <span className="ks-badge ks-badge-verified">✓ Verified by Agricultural Officer</span>
                    ) : (
                      <span className="ks-badge ks-badge-review">⏳ Awaiting Officer Review</span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    📍 Location: {c.field_location} | 📋 Symptoms: {c.symptoms_description}
                  </div>
                  {c.ai_assessment && (
                    <div
                      style={{
                        marginTop: '8px',
                        fontSize: '0.85rem',
                        color: 'var(--badge-ai-text)',
                        background: 'rgba(44,94,107,0.08)',
                        padding: '6px 12px',
                        borderRadius: '6px',
                      }}
                    >
                      🤖 <strong>CropDoctor AI Preliminary Assessment:</strong> {c.ai_assessment.probable_disease} (Confidence: {c.ai_assessment.confidence}%)
                    </div>
                  )}
                </div>
                <button className="ks-btn ks-btn-primary" onClick={() => onViewCase(c)}>
                  View Full Workflow
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
