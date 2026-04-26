import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import os

def generate_visuals():
    # Load data
    df = pd.read_csv('data.csv', usecols=['industry', 'subindustry', 'current_price', 'constant_price'])
    df = df.dropna(subset=['industry'])
    df = df[~df['industry'].str.contains('Total', case=False)]
    df['subindustry'] = df['subindustry'].fillna('Other')
    df['current_price'] = pd.to_numeric(df['current_price'], errors='coerce').fillna(0)
    df['constant_price'] = pd.to_numeric(df['constant_price'], errors='coerce').fillna(0)

    # Features
    df['text_content'] = df['industry'].astype(str) + " " + df['subindustry'].astype(str)
    tfidf = TfidfVectorizer(stop_words='english', max_features=20)
    text_features = tfidf.fit_transform(df['text_content']).toarray()
    numerical_features = df[['current_price', 'constant_price']].values
    
    scaler = StandardScaler()
    numerical_scaled = scaler.fit_transform(numerical_features)
    X = np.hstack((numerical_scaled, text_features))

    # Clustering
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    # 1. PCA Plot
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    
    plt.figure(figsize=(10, 6), facecolor='#030712')
    ax = plt.gca()
    ax.set_facecolor('#030712')
    
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='viridis', alpha=0.6, s=30)
    plt.colorbar(scatter, label='Cluster ID')
    plt.title('Real-Time PCA Cluster Mapping', color='white', fontsize=14, fontweight='bold')
    plt.xlabel('Principal Component 1', color='#9ca3af')
    plt.ylabel('Principal Component 2', color='#9ca3af')
    plt.tick_params(colors='#9ca3af')
    for spine in ax.spines.values():
        spine.set_color('#1f2937')
    
    plt.savefig('pca_now.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Heatmap (Correlation)
    plt.figure(figsize=(10, 8), facecolor='#030712')
    # Combine some features for correlation
    corr_df = pd.DataFrame(X[:, :12], columns=['Current Price', 'Constant Price'] + [f'TFIDF_{i}' for i in range(10)])
    corr_matrix = corr_df.corr()
    
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', 
                cbar_kws={'label': 'Correlation'}, 
                annot_kws={"size": 8})
    plt.title('Industry Feature Correlation Heatmap', color='white', fontsize=14, fontweight='bold')
    plt.xticks(color='#9ca3af', rotation=45)
    plt.yticks(color='#9ca3af')
    
    plt.savefig('heatmap_now.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Graphs generated successfully.")

if __name__ == "__main__":
    generate_visuals()
