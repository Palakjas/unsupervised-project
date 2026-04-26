import pandas as pd
import numpy as np
import time
import os

def simulate_updates():
    file_path = 'data.csv'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print("--- DATA SIMULATOR STARTED ---")
    print("Modifying prices and adding noise to trigger real-time updates...")
    
    while True:
        try:
            # Read the current data
            df = pd.read_csv(file_path)
            
            # Randomly fluctuate the current_price and constant_price for some rows
            # This simulates real-time economic data updates
            mask = np.random.choice([True, False], size=len(df), p=[0.1, 0.9])
            df.loc[mask, 'current_price'] = df.loc[mask, 'current_price'] * np.random.uniform(0.95, 1.05)
            df.loc[mask, 'constant_price'] = df.loc[mask, 'constant_price'] * np.random.uniform(0.95, 1.05)
            
            # Save it back to trigger the main.py observer
            df.to_csv(file_path, index=False)
            
            print(f"[{time.ctime()}] Data updated. Engine should trigger now.")
            time.sleep(3) # Wait for 3 seconds before next update
            
        except Exception as e:
            print(f"Simulation Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    simulate_updates()
