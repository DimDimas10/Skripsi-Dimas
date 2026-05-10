import numpy as np
from sklearn.ensemble import IsolationForest

n_samples = 2512
contamination = 0.20

# Generate dummy data
X = np.random.rand(n_samples, 2)

# Fit Isolation Forest
clf = IsolationForest(contamination=contamination, random_state=42)
clf.fit(X)

# Predict
y_pred = clf.predict(X)

# Count anomalies (-1 is anomaly)
n_anomalies = np.sum(y_pred == -1)

print(f"Total samples: {n_samples}")
print(f"Contamination: {contamination}")
print(f"Anomalies found: {n_anomalies}")
print(f"Expected (theoretical): {n_samples * contamination}")
