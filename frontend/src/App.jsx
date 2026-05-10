import React, { useState } from 'react';
import Navbar from './components/Navbar';
import UploadComponent from './components/UploadComponent';
import Dashboard from './components/Dashboard';
import { useAppContext } from './AppContext';

function App() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { t } = useAppContext();

  const handleUploadSuccess = (responseData) => {
    setData(responseData);
    setError(null);
  };

  const handleError = (errMessage) => {
    setError(errMessage);
  };

  return (
    <div className="app-container">
      <Navbar />
      
      <main className="main-content">
        {error && (
          <div className="glass-panel" style={{ padding: '1rem', color: '#ef4444', marginBottom: '2rem', border: '1px solid #ef4444', background: 'rgba(239, 68, 68, 0.1)' }}>
            <strong>{t('error')}:</strong> {error}
          </div>
        )}

        {!data ? (
          <UploadComponent 
            onSuccess={handleUploadSuccess} 
            onError={handleError}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        ) : (
          <Dashboard 
            data={data} 
            onReset={() => setData(null)} 
          />
        )}
      </main>
    </div>
  );
}

export default App;
