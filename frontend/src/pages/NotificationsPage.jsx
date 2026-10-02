/** Notifications page: bilingual alert list. */
export default function NotificationsPage({ notifications }) {
  return (
    <div className="ks-card">
      <h3>🔔 User Notifications & System Status Alerts</h3>
      <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {notifications.length === 0 ? (
          <p>No notifications available.</p>
        ) : (
          notifications.map((n) => (
            <div
              key={n.id}
              style={{
                border: '1px solid var(--border-color)',
                padding: '14px',
                borderRadius: '8px',
                background: n.is_read ? 'var(--bg-card)' : 'var(--rice-paper)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong style={{ color: 'var(--leaf-900)' }}>{n.title}</strong>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {new Date(n.created_at).toLocaleString()}
                </span>
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', margin: '6px 0' }}>{n.message}</p>
              {n.malayalam_message && (
                <div className="malayalam-text" style={{ fontSize: '0.88rem', color: 'var(--leaf-800)' }}>
                  {n.malayalam_message}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
