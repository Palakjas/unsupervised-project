import pandas as pd

def get_stats():
    df = pd.read_csv('data.csv')
    industries = df['industry'].dropna().unique()
    subindustries = df['subindustry'].dropna().unique()
    
    print(f"Total Records: {len(df)}")
    print(f"Total Unique Industries: {len(industries)}")
    print(f"Total Unique Sub-Industries: {len(subindustries)}")
    print("\nTop 10 Industries:")
    print(df['industry'].value_counts().head(10))

if __name__ == "__main__":
    get_stats()
