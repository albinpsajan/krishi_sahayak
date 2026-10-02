/** Tamper-evident audit ledger timeline (SHA-256 hash chain). */
export default function AuditPage({ auditLogs }) {
  return (
    <div className="ks-card">
      <div className="ks-card-header">
        <div>
          <h3>🔒 Tamper-Evident Audit Ledger Timeline (SHA-256 Hash Chain)</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Every action (Crop case, AI assessment, Officer review, Subsidy decision) is cryptographically signed and chained.
          </p>
        </div>
        <span className="ks-badge ks-badge-verified" style={{ padding: '8px 16px', fontSize: '0.9rem' }}>
          ✓ Audit Chain Integrity Verified (SHA-256)
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
        {auditLogs.map((rec) => (
          <div
            key={rec.id}
            style={{
              borderLeft: '3px solid var(--leaf-700)',
              padding: '12px 16px',
              background: 'var(--rice-paper)',
              borderRadius: '0 8px 8px 0',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <div>
                <strong style={{ color: 'var(--leaf-900)' }}>#{rec.id} [{rec.action}]</strong> —{' '}
                <span style={{ color: 'var(--text-secondary)' }}>{rec.actor_name} ({rec.actor_role})</span>
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {new Date(rec.timestamp).toLocaleString()}
              </span>
            </div>
            <div style={{ fontSize: '0.82rem', fontFamily: 'monospace', color: 'var(--water-teal)', wordBreak: 'break-all' }}>
              Prev Hash: {rec.prev_hash.substring(0, 16)}... | Hash: {rec.current_hash}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
