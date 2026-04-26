const translations = {
  id: {
    // Navbar
    brandName: 'BankShield AI',
    systemActive: 'Sistem Deteksi Anomali Aktif',

    // Upload
    dropTitle: 'Drop File Transaksi (CSV)',
    dropDescription: 'Seret dan lepas file CSV Anda ke zona ini, atau klik tombol di bawah untuk menelusuri penjelajah file.',
    browseFile: 'Browse File',
    csvError: 'Harap unggah file dengan format .csv',
    serverError: 'Terjadi kesalahan saat terhubung ke server backend FastAPI.',
    analyzingTitle: 'Menganalisis Pola Entitas...',
    step1: 'Membaca kompresi CSV transaksi...',
    step2: 'Sistem Ekstrapolasi Kolom Cerdas berjalan...',
    step3: 'Proyeksi Isolation Forest Pipeline...',
    step4: 'Mengekstrak Vektor Anomali...',

    // Dashboard
    analysisReport: 'Laporan Analisis',
    back: 'Kembali',
    transactionsEvaluated: 'Transaksi Dievaluasi',
    normalProfile: 'Profil Normal',
    anomalyIndication: 'Indikasi Anomali',

    // Chart
    transactionProportion: 'Proporsi Transaksi',
    scatterMap: 'Peta Persebaran (Amount vs Skor)',
    transactions: 'Transaksi',
    anomalyDetected: '🚨 Anomali Terdeteksi',
    normalTransaction: '✅ Transaksi Wajar',
    transactionId: 'ID Transaksi',
    amountNominal: 'Amount (Nominal)',
    anomalyScore: 'Anomaly Score',
    normal: 'Normal',
    anomaly: 'Anomali',

    // Table
    tableTitle: 'Catatan Transaksi Menyeluruh (Log)',
    showingAll: 'Menampilkan seluruh atribut (16 Kolom)',
    thTransactionId: 'ID Transaksi',
    thAccountId: 'Account Id',
    thAmount: 'Amount',
    thDate: 'Transaction Date',
    thType: 'Type',
    thLocation: 'Location',
    thDeviceId: 'Device Id',
    thIpAddress: 'IP Address',
    thMerchantId: 'Merchant Id',
    thChannel: 'Channel',
    thAge: 'Usia',
    thOccupation: 'Pekerjaan',
    thDuration: 'Duration (Detik)',
    thLogins: 'Logins',
    thBalance: 'Balance',
    thPrevTransaction: 'Prev. Transaction',
    thAnomalyScore: 'Anomaly Skor',
    thLabel: 'Label',
    labelAnomaly: 'Anomali',
    labelNormal: 'Wajar',
    error: 'Error',

    // Theme
    darkMode: 'Gelap',
    lightMode: 'Terang',
  },
  en: {
    // Navbar
    brandName: 'BankShield AI',
    systemActive: 'Anomaly Detection System Active',

    // Upload
    dropTitle: 'Drop Transaction File (CSV)',
    dropDescription: 'Drag and drop your CSV file into this zone, or click the button below to browse your file explorer.',
    browseFile: 'Browse File',
    csvError: 'Please upload a file in .csv format',
    serverError: 'An error occurred while connecting to the FastAPI backend server.',
    analyzingTitle: 'Analyzing Entity Patterns...',
    step1: 'Reading CSV transaction compression...',
    step2: 'Smart Column Extrapolation System running...',
    step3: 'Isolation Forest Pipeline Projection...',
    step4: 'Extracting Anomaly Vectors...',

    // Dashboard
    analysisReport: 'Analysis Report',
    back: 'Back',
    transactionsEvaluated: 'Transactions Evaluated',
    normalProfile: 'Normal Profile',
    anomalyIndication: 'Anomaly Indication',

    // Chart
    transactionProportion: 'Transaction Proportion',
    scatterMap: 'Distribution Map (Amount vs Score)',
    transactions: 'Transactions',
    anomalyDetected: '🚨 Anomaly Detected',
    normalTransaction: '✅ Normal Transaction',
    transactionId: 'Transaction ID',
    amountNominal: 'Amount (Nominal)',
    anomalyScore: 'Anomaly Score',
    normal: 'Normal',
    anomaly: 'Anomaly',

    // Table
    tableTitle: 'Comprehensive Transaction Records (Log)',
    showingAll: 'Showing all attributes (16 Columns)',
    thTransactionId: 'Transaction ID',
    thAccountId: 'Account Id',
    thAmount: 'Amount',
    thDate: 'Transaction Date',
    thType: 'Type',
    thLocation: 'Location',
    thDeviceId: 'Device Id',
    thIpAddress: 'IP Address',
    thMerchantId: 'Merchant Id',
    thChannel: 'Channel',
    thAge: 'Age',
    thOccupation: 'Occupation',
    thDuration: 'Duration (Seconds)',
    thLogins: 'Logins',
    thBalance: 'Balance',
    thPrevTransaction: 'Prev. Transaction',
    thAnomalyScore: 'Anomaly Score',
    thLabel: 'Label',
    labelAnomaly: 'Anomaly',
    labelNormal: 'Normal',
    error: 'Error',

    // Theme
    darkMode: 'Dark',
    lightMode: 'Light',
  }
};

export default translations;
