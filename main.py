import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import os
import json
import time

def load_and_clean(file_path):
    df = pd.read_csv(file_path, usecols=['industry', 'subindustry', 'current_price', 'constant_price'])
    df = df.dropna(subset=['industry'])
    df = df[~df['industry'].str.contains('Total', case=False)]
    df['subindustry'] = df['subindustry'].fillna('Other')
    df['current_price'] = pd.to_numeric(df['current_price'], errors='coerce').fillna(0).astype(np.float32)
    df['constant_price'] = pd.to_numeric(df['constant_price'], errors='coerce').fillna(0).astype(np.float32)
    return df

def extract_features(df):
    df['text_content'] = df['industry'].astype(str) + " " + df['subindustry'].astype(str)
    tfidf = TfidfVectorizer(stop_words='english', max_features=40)
    text_features = tfidf.fit_transform(df['text_content']).toarray().astype(np.float32)
    numerical_features = df[['current_price', 'constant_price']].values.astype(np.float32)
    scaler = StandardScaler()
    numerical_scaled = scaler.fit_transform(numerical_features)
    X = np.hstack((numerical_scaled, text_features))
    return X

def run_clustering(X):
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=5)
    labels = kmeans.fit_predict(X)
    return labels

def export_viz_data(X, labels, df):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    
    pca_export = []
    limit = min(500, len(X_pca))
    for i in range(limit):
        pca_export.append({
            "x": float(X_pca[i, 0]),
            "y": float(X_pca[i, 1]),
            "label": int(labels[i]),
            "industry": str(df.iloc[i]['industry']),
            "features": X[i, :10].tolist() # CRITICAL: Ensure this is here
        })
    
    with open('pca_data.json', 'w') as f:
        json.dump(pca_export, f)
    
    summary_data = []
    for i in range(int(labels.max()) + 1):
        cluster_data = df[labels == i]
        if len(cluster_data) == 0: continue
        summary_data.append({
            "id": i,
            "size": len(cluster_data),
            "top_industry": cluster_data['industry'].value_counts().index[0],
            "avg_price": float(cluster_data['current_price'].mean()),
            "industries": cluster_data['industry'].value_counts().head(5).to_dict()
        })
        
    with open('results.json', 'w') as f:
        json.dump(summary_data, f)
    
    print(f"-> Exported {limit} rows with features.", flush=True)

if __name__ == "__main__":
    data_path = 'data.csv'
    print("--- RESTARTING REAL-TIME ENGINE ---", flush=True)
    
    while True:
        try:
            df = load_and_clean(data_path)
            X = extract_features(df)
            labels = run_clustering(X)
            export_viz_data(X, labels, df)
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(10)
