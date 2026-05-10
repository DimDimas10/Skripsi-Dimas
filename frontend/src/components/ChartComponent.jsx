import React, { useMemo } from 'react';
import { 
  PieChart, Pie, Cell, Tooltip as PieTooltip, Legend, 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as ScatterTooltip,
  ResponsiveContainer 
} from 'recharts';
import { PieChart as PieIcon, Activity } from 'lucide-react';
import { useAppContext } from '../AppContext';

const ChartComponent = React.memo(({ data }) => {
  const { t } = useAppContext();

  if (!data || !data.results) return null;

  const normalCount = data.total_processed - data.anomalies_detected;

  // useMemo: hitung data chart hanya saat 'data' berubah,
  // BUKAN saat bahasa atau tema berubah — label diterjemahkan di render saja
  const pieData = useMemo(() => [
    { name: 'normal', value: normalCount },
    { name: 'anomaly', value: data.anomalies_detected }
  ], [normalCount, data.anomalies_detected]);

  const scatterNormal = useMemo(() =>
    data.results
      .filter(item => !(item['Is Anomaly'] === 1 || item.is_anomaly === 1))
      .map((item, index) => ({
        x: index + 1,
        y: item['Transaction Amount'] !== undefined ? item['Transaction Amount'] : item.amount,
        z: item['Anomaly Score'] !== undefined ? item['Anomaly Score'] : item.anomaly_score,
      })),
  [data.results]);

  const scatterAnomaly = useMemo(() =>
    data.results
      .filter(item => item['Is Anomaly'] === 1 || item.is_anomaly === 1)
      .map((item, index) => ({
        x: index + 1,
        y: item['Transaction Amount'] !== undefined ? item['Transaction Amount'] : item.amount,
        z: item['Anomaly Score'] !== undefined ? item['Anomaly Score'] : item.anomaly_score,
      })),
  [data.results]);

  const COLORS = ['#10b981', '#ef4444'];

  const CustomPieTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-panel" style={{ padding: '0.75rem 1rem', border: '1px solid var(--surface-border)', boxShadow: '0 10px 25px rgba(0,0,0,0.3)' }}>
          <p style={{ color: payload[0].color, fontWeight: '700', margin: 0 }}>{`${t(payload[0].name).toUpperCase()}`}</p>
          <p style={{ margin: 0, fontSize: '1.25rem', color: 'var(--text-primary)' }}>{payload[0].value} <span style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>{t('transactions')}</span></p>
        </div>
      );
    }
    return null;
  };

  const CustomScatterTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload;
      return (
        <div className="glass-panel" style={{ padding: '1rem', border: '1px solid var(--surface-border)', boxShadow: '0 10px 30px rgba(0,0,0,0.3)' }}>
          <h4 style={{ margin: '0 0 10px 0', color: 'var(--text-primary)', borderBottom: '1px solid var(--surface-border)', paddingBottom: '5px' }}>
            {t('transactionId')}: {d.x}
          </h4>
          <p style={{ margin: '4px 0' }}><strong>{t('amountNominal')}:</strong> <span style={{fontFamily: 'monospace', color: '#60a5fa'}}>{d.y}</span></p>
          <p style={{ margin: '4px 0' }}><strong>{t('anomalyScore')}:</strong> <span style={{fontFamily: 'monospace', color: '#c084fc'}}>{d.z?.toFixed(4)}</span></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="dashboard-grid">
      <div className="dashboard-card glass-panel glass-hover">
        <h3 className="card-title"><PieIcon size={20} color="#c084fc"/> {t('transactionProportion')}</h3>
        <div style={{ width: '100%', height: 320, position: 'relative' }}>
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={pieData}
                innerRadius={70}
                outerRadius={110}
                paddingAngle={8}
                dataKey="value"
                stroke="none"
                isAnimationActive={false}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <PieTooltip content={<CustomPieTooltip />} cursor={{fill: 'transparent'}} />
              <Legend
                verticalAlign="bottom"
                height={36}
                iconType="circle"
                formatter={(value) => t(value)}
                wrapperStyle={{ fontSize: '14px', fontWeight: '600' }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ position: 'absolute', top: '45%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
             <span style={{ fontSize: '1.8rem', fontWeight: '800', color: 'var(--text-primary)' }}>{((data.anomalies_detected / data.total_processed)*100).toFixed(1)}%</span>
             <br/><span style={{ fontSize: '0.75rem', color: 'var(--danger-color)', fontWeight: 'bold' }}>{t('anomaly')}</span>
          </div>
        </div>
      </div>

      <div className="dashboard-card glass-panel glass-hover">
        <h3 className="card-title"><Activity size={20} color="#60a5fa"/> {t('scatterMap')}</h3>
        <div style={{ width: '100%', height: 320 }}>
          <ResponsiveContainer>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--surface-border)" vertical={false} />
              <XAxis type="number" dataKey="x" name="Index" stroke="#64748b" tick={{fill: '#64748b'}} axisLine={{stroke: '#334155'}} />
              <YAxis type="number" dataKey="y" name="Amount" stroke="#64748b" tick={{fill: '#64748b'}} axisLine={{stroke: '#334155'}} />
              <ScatterTooltip cursor={{ strokeDasharray: '3 3', stroke: 'rgba(255,255,255,0.2)' }} content={<CustomScatterTooltip />} />
              <Scatter name={t('normal')} data={scatterNormal} fill="#10b981" isAnimationActive={false} />
              <Scatter name={t('anomaly')} data={scatterAnomaly} fill="#fca5a5" isAnimationActive={false} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
});

ChartComponent.displayName = 'ChartComponent';

export default ChartComponent;
