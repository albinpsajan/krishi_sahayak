import React, { useState } from 'react';

/** AutoClerk report editor modal: review and sign the generated markdown report. */
export default function AutoClerkModal({ report, onClose }) {
  const [content, setContent] = useState(report.content_markdown);

  return (
    <div className="modal-overlay">
      <div className="modal-card" style={{ maxWidth: '800px' }}>
        <div className="modal-header">
          <h3>📑 AutoClerk Official Administrative Report Editor</h3>
          <button className="ks-btn ks-btn-outline" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <textarea
            className="ks-textarea"
            rows={16}
            style={{ fontFamily: 'monospace', fontSize: '0.88rem', background: 'var(--rice-paper)' }}
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        <div className="modal-footer">
          <button className="ks-btn ks-btn-primary" onClick={() => { alert('Report approved & signed!'); onClose(); }}>
            ✓ Approve & Sign Report
          </button>
          <button className="ks-btn ks-btn-outline" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
