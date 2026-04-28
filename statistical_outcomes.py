import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import json
import warnings

warnings.filterwarnings('ignore')

def load_and_clean(file_path='data.csv'):
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

def analyze_statistical_outcomes():
    print("--- Calculating Statistical Outcomes ---")
    
    # 1. Load Data
    df = load_and_clean()
    total_records = len(df)
    
    # 2. Extract Features
    X = extract_features(df)

    # 3. K-Means Clustering
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=5)
    labels = kmeans.fit_predict(X)
    inertia = kmeans.inertia_

    # 4. Silhouette Score
    # Using a sample if data is huge, but here we can compute directly
    try:
        sil_score = silhouette_score(X, labels)
    except Exception as e:
        sil_score = 0.0
        print(f"Error computing Silhouette Score: {e}")

    # 5. PCA Variance Explained
    pca = PCA(n_components=2)
    pca.fit(X)
    pca_variance = sum(pca.explained_variance_ratio_) * 100

    # Print Outcomes for PoC/Reporting
    print(f"Total Records Processed: {total_records}")
    print(f"Silhouette Score: {sil_score:.4f}")
    print(f"PCA Variance Explained: {pca_variance:.2f}%")
    print(f"Inertia (SSE): {inertia:.2f}")
    
    print("\nCluster Distribution (Segmentation):")
    cluster_distribution = {}
    for i in range(5):
        cluster_data = df[labels == i]
        cluster_size = len(cluster_data)
        if cluster_size > 0:
            top_industry = cluster_data['industry'].value_counts().index[0]
        else:
            top_industry = "None"
        print(f"- Cluster {i} ({top_industry}): {cluster_size} records")
        cluster_distribution[f"Cluster {i}"] = {
            "size": cluster_size,
            "top_industry": top_industry
        }
        
    # Export stats to a JSON for the frontend if needed
    stats_export = {
        "total_records": total_records,
        "silhouette_score": float(sil_score),
        "pca_variance_explained_percent": float(pca_variance),
        "inertia": float(inertia),
        "clusters": cluster_distribution
    }
    
    with open('statistical_outcomes.json', 'w') as f:
        json.dump(stats_export, f, indent=4)
    print("\n-> Exported statistical outcomes to statistical_outcomes.json")

if __name__ == "__main__":
    analyze_statistical_outcomes()
