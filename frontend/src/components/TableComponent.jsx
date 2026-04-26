import React, { useState, useEffect } from 'react';
import { FileSearch } from 'lucide-react';
import { useAppContext } from '../AppContext';

const TableComponent = React.memo(({ data }) => {
  const [renderCount, setRenderCount] = useState(0);
  const { t } = useAppContext();

  useEffect(() => {
    setRenderCount(Math.min(data.results.length, 50));
  }, [data]);

  if (!data || !data.results) return null;

  return (
    <div className="dashboard-card glass-panel" style={{ marginTop: '2rem', width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 className="card-title" style={{ margin: 0 }}><FileSearch size={20} color="#c084fc" /> {t('tableTitle')}</h3>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('showingAll')}</span>
      </div>

      <div className="table-container custom-scrollbar" style={{ maxHeight: '500px', overflowY: 'auto', overflowX: 'auto', borderRadius: '8px' }}>
        <table style={{ whiteSpace: 'nowrap' }}>
          <thead>
            <tr>
              <th>{t('thTransactionId')}</th>
              <th>{t('thAccountId')}</th>
              <th style={{ textAlign: 'right' }}>{t('thAmount')}</th>
              <th>{t('thDate')}</th>
              <th>{t('thType')}</th>
              <th>{t('thLocation')}</th>
              <th>{t('thDeviceId')}</th>
              <th>{t('thIpAddress')}</th>
              <th>{t('thMerchantId')}</th>
              <th>{t('thChannel')}</th>
              <th>{t('thAge')}</th>
              <th>{t('thOccupation')}</th>
              <th>{t('thDuration')}</th>
              <th>{t('thLogins')}</th>
              <th style={{ textAlign: 'right' }}>{t('thBalance')}</th>
              <th>{t('thPrevTransaction')}</th>
              <th style={{ textAlign: 'right' }}>{t('thAnomalyScore')}</th>
              <th style={{ textAlign: 'center' }}>{t('thLabel')}</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((row, idx) => {
              const isAnomaly = row['Is Anomaly'] === 1 || row.is_anomaly === 1;
              const statusClass = isAnomaly ? 'badge badge-anomaly' : 'badge badge-normal';
              const rowClass = isAnomaly ? 'row-anomaly' : '';

              const animationDelay = idx < 20 ? `${idx * 0.02}s` : '0s';
              const animationClass = idx < 20 ? 'row-fade-in' : '';

              const sanitizeDate = (dateStr) => {
                if (!dateStr) return "-";
                try {
                  return new Date(dateStr).toLocaleString('id-ID', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
                } catch { return dateStr }
              }

              return (
                <tr key={idx} className={`${rowClass} ${animationClass}`} style={{ animationDelay }}>
                  <td style={{ fontWeight: '600', color: 'var(--text-secondary)' }}>{row['Transaction ID'] || `TRX-${1000 + idx}`}</td>
                  <td>{row['Account Id'] || '-'}</td>
                  <td style={{ fontFamily: 'monospace', textAlign: 'right', fontWeight: '600' }}>
                    {(row['Transaction Amount'] || row.amount)?.toLocaleString('en-US')}
                  </td>
                  <td>{sanitizeDate(row['Transaction Date'])}</td>
                  <td><span style={{ opacity: 0.9 }}>{row['Transaction Type'] || row.transaction_type}</span></td>
                  <td>{row['Location'] || row.location}</td>
                  <td>{row['Device Id'] || row.device}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>{row['IP Address'] || '-'}</td>
                  <td>{row['Merchant Id'] || '-'}</td>
                  <td>{row['Channel'] || '-'}</td>
                  <td>{row['Customer Age'] || '-'}</td>
                  <td>{row['Customer Occupation'] || '-'}</td>
                  <td>{row['Transaction Duration'] || '-'}</td>
                  <td>{row['Login Attempts'] || '-'}</td>
                  <td style={{ fontFamily: 'monospace', textAlign: 'right' }}>{(row['Account Balance'] || 0).toLocaleString('en-US')}</td>
                  <td>{sanitizeDate(row['Previous Transaction Date'])}</td>
                  <td style={{ fontFamily: 'monospace', textAlign: 'right', color: isAnomaly ? '#fca5a5' : 'var(--text-secondary)' }}>
                    {(row['Anomaly Score'] || row.anomaly_score)?.toFixed(4)}
                  </td>
                  <td style={{ textAlign: 'center', position: 'sticky', right: 0, backgroundColor: isAnomaly ? 'rgba(127, 29, 29, 0.9)' : 'var(--table-sticky-bg)' }}>
                    <span className={statusClass}>
                      {isAnomaly ? t('labelAnomaly') : t('labelNormal')}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
});

TableComponent.displayName = 'TableComponent';

export default TableComponent;
