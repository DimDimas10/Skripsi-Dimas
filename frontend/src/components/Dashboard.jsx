import React, { useState, useEffect, memo } from 'react';
import ChartComponent from './ChartComponent';
import TableComponent from './TableComponent';
import { FileBarChart2, ShieldAlert, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useAppContext } from '../AppContext';

// memo: Dashboard tidak re-render saat tema/bahasa berubah jika data tidak berubah
const Dashboard = memo(({ data, onReset }) => {
  const [show, setShow] = useState(false);
  const { t } = useAppContext();
  
  useEffect(() => {
    const timer = setTimeout(() => setShow(true), 50);
    return () => clearTimeout(timer);
  }, []);

  if (!data || !show) return null;

  const isDanger = data.anomalies_detected > 0;

  return (
    <div className="animate-slide-up" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.75rem', fontWeight: 800 }}>
          <FileBarChart2 size={28} color="#60a5fa" /> 
          {t('analysisReport')}
        </h2>
        <button 
          onClick={onReset}
          className="glass-panel"
          style={{ 
            display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer',
            padding: '0.65rem 1.25rem', color: 'var(--text-primary)', fontWeight: '600', transition: 'transform 0.2s ease, background 0.2s ease'
          }}
          onMouseOver={(e) => { e.currentTarget.style.background = 'var(--accent-color)'; e.currentTarget.style.color = '#ffffff'; e.currentTarget.style.transform = 'translateX(-3px)'; }}
          onMouseOut={(e) => { e.currentTarget.style.background = ''; e.currentTarget.style.color = 'var(--text-primary)'; e.currentTarget.style.transform = 'translateX(0)'; }}
        >
          <ArrowLeft size={18} /> {t('back')}
        </button>
      </div>

      {/* Stats — tanpa animate-slide-up agar tidak replay saat toggle tema/lang */}
      <div className="stats-container">
        <div className="stat-box glass-panel glass-hover">
          <div style={{ position: 'absolute', top: '-10px', right: '10px', fontSize: '4rem', opacity: 0.05 }}>Σ</div>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600 }}>
            {t('transactionsEvaluated')}
          </span>
          <span className="stat-value">{data.total_processed}</span>
        </div>
        
        <div className="stat-box glass-panel glass-hover" style={{ borderBottom: '4px solid #10b981' }}>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={16} color="#10b981" /> {t('normalProfile')}
          </span>
          <span className="stat-value success">{data.total_processed - data.anomalies_detected}</span>
        </div>

        <div className={`stat-box glass-panel glass-hover ${isDanger ? 'danger-pulse' : ''}`} style={{ borderBottom: '4px solid #ef4444' }}>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={16} color="#ef4444" /> {t('anomalyIndication')}
          </span>
          <span className="stat-value danger">{data.anomalies_detected}</span>
        </div>
      </div>

      <div>
        <ChartComponent data={data} />
        <TableComponent data={data} />
      </div>
    </div>
  );
});

Dashboard.displayName = 'Dashboard';

export default Dashboard;
