import React, { useState } from 'react';
import { casesAPI } from '../services/api';

/** Case record viewer with the officer verification form (human-in-the-loop). */
export default function CaseDetailModal({ caseData, isOfficer, onClose, onUpdate, onGenerateAutoClerk }) {
  const [isConfirmed, setIsConfirmed] = useState(true);
  const [notes, setNotes] = useState('Field inspection confirms early stage leaf blast symptoms.');
  const [recommendation, setRecommendation] = useState('Spray Pseudomonas fluorescens @ 10g/L water early morning. Drain standing water.');
  const [product, setProduct] = useState('Pseudomonas fluorescens Bio-Agent');
  const [submitting, setSubmitting] = useState(false);

  const handleOfficerSubmit = async () => {
    setSubmitting(true);
    try {
      await casesAPI.submitOfficerReview(caseData.id, {
        is_confirmed: isConfirmed,
        officer_notes: notes,
        verified_recommendation: recommendation,
        recommended_product: product,
      });
      alert('Officer verification submitted successfully!');
      onUpdate();
    } catch (e) {
      alert('Error submitting review: ' + e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card" style={{ maxWidth: '840px' }}>
        <div className="modal-header">
          <div>
            <h3>{caseData.case_number} - {caseData.crop_type} ({caseData.variety})</h3>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Farmer: {caseData.farmer_name}</span>
          </div>
          <button className="ks-btn ks-btn-outline" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Section 1: AI Assessment */}
          <div style={{ background: 'var(--badge-ai-bg)', border: '1px solid var(--badge-ai-border)', padding: '16px', borderRadius: '8px', marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span className="ks-badge ks-badge-ai">🤖 AI-Assisted Preliminary Assessment (CropDoctor)</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--badge-ai-text)' }}>
                Confidence: {caseData.ai_assessment?.confidence || 88}%
              </span>
            </div>
            <h4 style={{ color: 'var(--badge-ai-text)', fontSize: '1.2rem', marginBottom: '6px' }}>
              Probable Issue: {caseData.ai_assessment?.probable_disease}
            </h4>
            <div className="malayalam-text" style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--leaf-800)', marginBottom: '8px' }}>
              {caseData.ai_assessment?.hindi_malayalam_name}
            </div>
            <p style={{ fontSize: '0.9rem', marginBottom: '8px' }}>
              <strong>AI Observations:</strong> {caseData.ai_assessment?.observations}
            </p>
            <div style={{ background: '#fff', padding: '10px', borderRadius: '6px', fontSize: '0.88rem' }}>
              <strong>Preliminary AI Guidance:</strong> {caseData.ai_assessment?.preliminary_guidance}
              <div className="malayalam-text" style={{ marginTop: '4px', color: 'var(--leaf-800)' }}>
                <strong>മലയാളം നിർദ്ദേശം:</strong> {caseData.ai_assessment?.malayalam_guidance}
              </div>
            </div>
          </div>

          {/* Section 2: Officer Verification */}
          {caseData.officer_review ? (
            <div style={{ background: 'var(--badge-verified-bg)', border: '1px solid var(--badge-verified-border)', padding: '16px', borderRadius: '8px' }}>
              <div className="ks-badge ks-badge-verified" style={{ marginBottom: '8px' }}>
                ✓ Verified by Agricultural Officer
              </div>
              <h4>Officer Recommendation</h4>
              <p style={{ fontSize: '0.95rem', fontWeight: 600, margin: '8px 0' }}>
                {caseData.officer_review.verified_recommendation}
              </p>
              <div className="malayalam-text" style={{ background: '#fff', padding: '10px', borderRadius: '6px', marginTop: '8px' }}>
                <strong>കൃഷി ഓഫീസറുടെ സന്ദേശം:</strong> {caseData.officer_review.malayalam_recommendation}
              </div>
            </div>
          ) : isOfficer ? (
            <div style={{ background: 'var(--rice-paper)', border: '1px solid var(--border-color)', padding: '16px', borderRadius: '8px' }}>
              <h4>🏛️ Officer Field Verification & Recommendation Form</h4>
              <div className="ks-form-group" style={{ marginTop: '12px' }}>
                <label className="ks-label">Confirm AI Diagnosis?</label>
                <select className="ks-select" value={isConfirmed} onChange={(e) => setIsConfirmed(e.target.value === 'true')}>
                  <option value="true">✓ Confirm AI Diagnosis ({caseData.ai_assessment?.probable_disease})</option>
                  <option value="false">⚠️ Correct / Change Diagnosis</option>
                </select>
              </div>

              <div className="ks-form-group">
                <label className="ks-label">Officer Inspection Notes</label>
                <textarea className="ks-textarea" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
              </div>

              <div className="ks-form-group">
                <label className="ks-label">Verified Recommendation & Treatment Dosage</label>
                <textarea className="ks-textarea" rows={2} value={recommendation} onChange={(e) => setRecommendation(e.target.value)} />
              </div>

              <div className="ks-form-group">
                <label className="ks-label">Recommended Bio-Treatment Product</label>
                <input className="ks-input" value={product} onChange={(e) => setProduct(e.target.value)} />
              </div>

              <button className="ks-btn ks-btn-primary" style={{ width: '100%' }} onClick={handleOfficerSubmit} disabled={submitting}>
                {submitting ? 'Submitting...' : '✓ Issue Verified Officer Recommendation'}
              </button>
            </div>
          ) : (
            <div style={{ background: 'var(--badge-review-bg)', padding: '14px', borderRadius: '8px', color: 'var(--badge-review-text)' }}>
              ⏳ Awaiting Agricultural Officer Verification.
            </div>
          )}
        </div>

        <div className="modal-footer">
          {isOfficer && (
            <button className="ks-btn ks-btn-gold" onClick={() => onGenerateAutoClerk(caseData.id)}>
              📑 Generate AutoClerk Official Report
            </button>
          )}
          <button className="ks-btn ks-btn-outline" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
