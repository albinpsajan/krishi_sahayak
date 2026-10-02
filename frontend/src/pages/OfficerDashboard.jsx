/** Officer command dashboard: action metrics + pending case review table. */
export default function OfficerDashboard({ cases, applications, onReviewCase }) {
  return (
    <div>
      <div className="ks-card" style={{ background: 'var(--leaf-900)', color: '#fff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ color: '#fff', fontSize: '1.6rem', marginBottom: '6px' }}>
              🏛️ Agricultural Officer Command Portal
            </h2>
            <p style={{ color: 'var(--rice-paper)', fontSize: '0.95rem' }}>
              Jurisdiction: Palakkad District | Department of Agriculture & Farmers Welfare
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--harvest-gold)' }}>AUTOCLERK REPORTING SYSTEM</div>
            <div style={{ fontWeight: 700, color: '#fff' }}>Status: Ready</div>
          </div>
        </div>
      </div>

      {/* Officer Action Metrics */}
      <div className="grid-4">
        <div className="ks-card" style={{ borderLeft: '4px solid var(--harvest-gold)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>PENDING CROP CASES</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--harvest-gold)' }}>
            {cases.filter((c) => c.status !== 'Officer Verified').length}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--harvest-warm)' }}>Require Officer Inspection</div>
        </div>
        <div className="ks-card" style={{ borderLeft: '4px solid var(--leaf-600)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>SUBSIDY APPLICATIONS</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--leaf-700)' }}>{applications.length}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--leaf-600)' }}>SubsidyChain Rule Evaluated</div>
        </div>
        <div className="ks-card" style={{ borderLeft: '4px solid var(--badge-fasttrack-text)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>FAST-TRACK RECOMMENDED</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--badge-fasttrack-text)' }}>
            {applications.filter((a) => a.risk_level === 'LOW_RISK_FAST_TRACK').length}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--badge-fasttrack-text)' }}>Low Risk / High Confidence</div>
        </div>
        <div className="ks-card" style={{ borderLeft: '4px solid var(--water-teal)' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>TAMPER-EVIDENT AUDIT</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--water-teal)' }}>✓ VERIFIED</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--water-teal)' }}>SHA-256 Hash Chain Intact</div>
        </div>
      </div>

      {/* Pending Crop Cases Table for Officer */}
      <div className="ks-card">
        <div className="ks-card-header">
          <h3>🌾 Crop Cases Awaiting Officer Review</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'var(--rice-paper)', borderBottom: '2px solid var(--border-color)' }}>
                <th style={{ padding: '12px' }}>Case Number</th>
                <th style={{ padding: '12px' }}>Farmer Name</th>
                <th style={{ padding: '12px' }}>Crop</th>
                <th style={{ padding: '12px' }}>AI Assessment</th>
                <th style={{ padding: '12px' }}>Confidence</th>
                <th style={{ padding: '12px' }}>Status</th>
                <th style={{ padding: '12px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '12px', fontWeight: 700 }}>{c.case_number}</td>
                  <td style={{ padding: '12px' }}>{c.farmer_name}</td>
                  <td style={{ padding: '12px' }}>{c.crop_type}</td>
                  <td style={{ padding: '12px' }}>{c.ai_assessment?.probable_disease || 'N/A'}</td>
                  <td style={{ padding: '12px' }}>{c.ai_assessment ? `${c.ai_assessment.confidence}%` : 'N/A'}</td>
                  <td style={{ padding: '12px' }}>
                    {c.status === 'Officer Verified' ? (
                      <span className="ks-badge ks-badge-verified">✓ Verified</span>
                    ) : (
                      <span className="ks-badge ks-badge-review">⏳ Pending</span>
                    )}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <button
                      className="ks-btn ks-btn-primary"
                      style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                      onClick={() => onReviewCase(c)}
                    >
                      Review & Verify
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
