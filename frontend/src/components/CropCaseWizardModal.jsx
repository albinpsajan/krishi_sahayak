import React, { useState } from 'react';
import { casesAPI, uploadAPI } from '../services/api';

/** Farmer-facing wizard that creates a crop case and triggers CropDoctor AI. */
export default function CropCaseWizardModal({ onClose, onSuccess }) {
  const [cropType, setCropType] = useState('Paddy');
  const [variety, setVariety] = useState('Uma (MO-16)');
  const [location, setLocation] = useState('Chittur East, Block A');
  const [symptoms, setSymptoms] = useState('Spindle-shaped brown spots on upper leaves, slight yellow halos.');
  const [previewUrl, setPreviewUrl] = useState('/assets/sample_leaf.jpg');
  const [loading, setLoading] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const res = await uploadAPI.uploadFile(file);
      setPreviewUrl(res.file_url);
    } catch (err) {
      console.error('Upload failed', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await casesAPI.createCase({
        crop_type: cropType,
        variety: variety,
        field_location: location,
        symptoms_description: symptoms,
        image_base64_or_url: previewUrl,
      });
      alert('Crop case created! CropDoctor AI preliminary assessment generated.');
      onSuccess();
    } catch (err) {
      alert('Failed to submit case: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div className="modal-header">
          <h3>🌱 Create New Crop Case & Trigger CropDoctor AI</h3>
          <button className="ks-btn ks-btn-outline" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="ks-form-group">
              <label className="ks-label">Select Target Crop</label>
              <select className="ks-select" value={cropType} onChange={(e) => setCropType(e.target.value)}>
                <option value="Paddy">Paddy / Rice (നെല്ല്)</option>
                <option value="Tomato">Tomato (തക്കാളി)</option>
                <option value="Pepper">Pepper (കുരുമുളക്)</option>
                <option value="Cotton">Cotton (പരുത്തി)</option>
                <option value="Wheat">Wheat (ഗോതമ്പ്)</option>
              </select>
            </div>
            <div className="ks-form-group">
              <label className="ks-label">Crop Variety / Strain</label>
              <input className="ks-input" value={variety} onChange={(e) => setVariety(e.target.value)} required />
            </div>
            <div className="ks-form-group">
              <label className="ks-label">Field Parcel Location</label>
              <input className="ks-input" value={location} onChange={(e) => setLocation(e.target.value)} required />
            </div>
            <div className="ks-form-group">
              <label className="ks-label">Observed Field Symptoms</label>
              <textarea className="ks-textarea" rows={3} value={symptoms} onChange={(e) => setSymptoms(e.target.value)} required />
            </div>

            <div style={{ border: '2px dashed var(--border-color)', padding: '16px', textAlign: 'center', borderRadius: '8px', background: 'var(--rice-paper)' }}>
              📸 <strong>Upload Crop Leaf Photo:</strong>
              <input type="file" accept="image/*" onChange={handleFileChange} style={{ marginTop: '8px', display: 'block', margin: '8px auto' }} />
              <img
                src={previewUrl}
                alt="Crop Preview"
                style={{ maxHeight: '140px', borderRadius: '8px', marginTop: '8px', border: '1px solid var(--border-color)' }}
              />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="ks-btn ks-btn-outline" onClick={onClose}>Cancel</button>
            <button type="submit" className="ks-btn ks-btn-gold" disabled={loading}>
              {loading ? 'Analyzing with AI...' : '🤖 Submit & Run CropDoctor AI'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
