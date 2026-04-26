import React, { useCallback, useState, useEffect } from 'react';
import axios from 'axios';
import { UploadCloud, Loader2, CheckCircle, Search, ShieldCheck } from 'lucide-react';
import { useAppContext } from '../AppContext';

const UploadComponent = ({ onSuccess, onError, isLoading, setIsLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const { t } = useAppContext();

  useEffect(() => {
    if (isLoading) {
      const interval = setInterval(() => {
        setLoadingStep(prev => (prev < 3 ? prev + 1 : prev));
      }, 700);
      return () => clearInterval(interval);
    } else {
      setLoadingStep(0);
    }
  }, [isLoading]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file) => {
    if (!file.name.endsWith('.csv')) {
      onError(t('csvError'));
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setTimeout(() => {
        setIsLoading(false);
        onSuccess(response.data);
      }, 500);
    } catch (err) {
      console.error(err);
      onError(err.response?.data?.detail || t('serverError'));
      setIsLoading(false);
    } 
  };

  const steps = [
    { text: t('step1'), icon: <Search size={18} className="animate-spin text-blue-400" color="#60a5fa" /> },
    { text: t('step2'), icon: <ShieldCheck size={18} className="animate-pulse" color="#c084fc" /> },
    { text: t('step3'), icon: <CheckCircle size={18} color="#10b981" /> },
    { text: t('step4'), icon: <Search size={18} className="animate-pulse" color="#fbbf24" /> }
  ];

  return (
    <div 
      className={`glass-panel upload-container ${dragActive ? 'drag-active' : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {isLoading ? (
        <div style={{ animation: 'slideUpFade 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards', width: '100%', maxWidth: '400px' }}>
          
          <div style={{ position: 'relative', width: '80px', height: '80px', margin: '0 auto 2rem auto' }}>
            <div className="ring ring-outer"></div>
            <div className="ring ring-inner"></div>
            <ShieldCheck size={36} color="#60a5fa" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />
          </div>
          
          <h2 style={{ marginBottom: '2rem', background: 'linear-gradient(to right, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', color: 'transparent' }}>
             {t('analyzingTitle')}
          </h2>
          
          <div style={{ textAlign: 'left', background: 'var(--loading-box-bg)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--loading-box-border)', boxShadow: 'var(--loading-box-shadow)' }}>
            {steps.map((step, idx) => (
              <div key={idx} style={{ 
                display: 'flex', alignItems: 'center', gap: '12px', 
                margin: '12px 0', opacity: loadingStep >= idx ? 1 : 0.2,
                transform: loadingStep >= idx ? 'translateX(0)' : 'translateX(-15px)',
                transition: 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
              }}>
                <span style={{ display: 'inline-flex', width: '20px' }}>{step.icon}</span>
                <span style={{ fontSize: '0.9rem', fontWeight: 500, color: loadingStep >= idx ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                  {step.text}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          <UploadCloud size={72} className="icon" style={{ filter: 'drop-shadow(0px 8px 16px rgba(59, 130, 246, 0.4))' }} />
          <h2 style={{ marginBottom: '1rem', fontSize: '1.75rem' }}>{t('dropTitle')}</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2.5rem', fontSize: '1.05rem', maxWidth: '500px' }}>
            {t('dropDescription')}
          </p>
          <label className="upload-btn" style={{ cursor: 'pointer', overflow: 'hidden', position: 'relative' }}>
            {t('browseFile')}
            <input 
              type="file" 
              accept=".csv" 
              style={{ display: 'none' }} 
              onChange={handleFileChange}
            />
          </label>
        </>
      )}
    </div>
  );
};

export default UploadComponent;
