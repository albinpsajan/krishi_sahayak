/** Subsidies page: schemes directory (farmer apply) + application tracker (officer decide). */
export default function SubsidiesPage({ subsidies, applications, isFarmer, isOfficer, onApply, onDecide }) {
  return (
    <div>
      <div className="ks-card" style={{ background: 'var(--rice-paper)', borderLeft: '4px solid var(--harvest-gold)' }}>
        <h3>📜 SubsidyChain Automated Eligibility & Rule Engine</h3>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          "AI evaluates applicable rules & flags missing documents. The authorized Agricultural Officer makes the final decision."
        </p>
      </div>

      <div className="grid-2">
        {/* Left Column: Schemes Directory */}
        <div className="ks-card">
          <h4>Government Schemes Directory</h4>
          <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {subsidies.map((s) => (
              <div key={s.id} style={{ border: '1px solid var(--border-color)', borderRadius: '8px', padding: '16px', background: '#fff' }}>
                <h5 style={{ color: 'var(--leaf-800)', fontSize: '1.05rem', marginBottom: '4px' }}>{s.name}</h5>
                <div className="malayalam-text" style={{ fontSize: '0.85rem', color: 'var(--harvest-gold)', fontWeight: 600, marginBottom: '8px' }}>
                  {s.hindi_malayalam_name}
                </div>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>{s.description}</p>
                <div style={{ fontSize: '0.8rem', background: 'var(--rice-paper)', padding: '8px', borderRadius: '6px', marginBottom: '12px' }}>
                  <strong>Benefit:</strong> {s.benefit_information} | <strong>Docs:</strong> {s.required_documents}
                </div>
                {isFarmer && (
                  <button className="ks-btn ks-btn-gold" style={{ width: '100%' }} onClick={() => onApply(s)}>
                    Submit Subsidy Application
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Applications Workflow Tracker */}
        <div className="ks-card">
          <h4>Submitted Applications & Screening Status</h4>
          <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {applications.map((a) => (
              <div key={a.id} style={{ border: '1px solid var(--border-color)', borderRadius: '8px', padding: '16px', background: '#fff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 800 }}>{a.application_number}</span>
                  <span className={`ks-badge ${a.risk_level === 'LOW_RISK_FAST_TRACK' ? 'ks-badge-fasttrack' : 'ks-badge-review'}`}>
                    {a.risk_level === 'LOW_RISK_FAST_TRACK' ? '⚡ Fast-Track Recommended' : '👤 Human Review Required'}
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', marginBottom: '4px' }}>Scheme: {a.scheme_name}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Applicant: {a.farmer_name}</div>

                <div style={{ marginTop: '8px', padding: '8px', background: 'var(--bg-subtle)', borderRadius: '6px', fontSize: '0.82rem' }}>
                  <strong>Decision Status:</strong>{' '}
                  <span style={{ fontWeight: 700, color: a.status === 'Approved' ? 'var(--leaf-700)' : 'var(--harvest-gold)' }}>
                    {a.status}
                  </span>
                  {a.officer_decision_notes && <div>Officer Notes: {a.officer_decision_notes}</div>}
                </div>

                {isOfficer && (
                  <div style={{ marginTop: '12px', display: 'flex', gap: '8px' }}>
                    <button
                      className="ks-btn ks-btn-primary"
                      style={{ flex: 1, padding: '6px', fontSize: '0.8rem' }}
                      onClick={() => onDecide(a, { status: 'Approved', approved_amount: a.requested_subsidy_amount, decision_notes: 'Approved after verification.' })}
                    >
                      ✓ Approve Subsidy
                    </button>
                    <button
                      className="ks-btn ks-btn-outline"
                      style={{ flex: 1, padding: '6px', fontSize: '0.8rem', color: '#b91c1c' }}
                      onClick={() => onDecide(a, { status: 'Rejected', decision_notes: 'Land record threshold unfulfilled.' })}
                    >
                      ❌ Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
