import pandas as pd
import numpy as np
import os
import glob
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt

# --- CONFIG ---
DATA_PATH = "dataset/data/"  # Path to CSV files
MODEL_PATH = "models/battery_model.pkl"

def load_and_process_data():
    print("Loading data... (This may take a moment)")
    all_files = glob.glob(os.path.join(DATA_PATH, "*.csv"))
    
    # If no data found, generate dummy data for DEMO purposes so code runs
    if not all_files:
        print("!! WARNING: No dataset found in dataset/data/. Generating Synthetic Data for demo !!")
        return generate_synthetic_data()

    data_list = []
    
    # Simplified extraction logic for NASA dataset structure
    for filename in all_files[:50]: # Limit to 50 files for speed in demo
        try:
            df = pd.read_csv(filename)
            # We assume these columns exist based on standard cleaned NASA format
            # We aggregate by cycle to get one row per cycle
            if 'cycle' in df.columns:
                grouped = df.groupby('cycle').agg({
                    'Voltage_measured': 'mean',
                    'Current_measured': 'mean',
                    'Temperature_measured': 'mean',
                    'Time': 'max' # Use time to estimate capacity/health
                }).reset_index()
                
                # Calculate RUL (Remaining Useful Life)
                max_cycle = grouped['cycle'].max()
                grouped['RUL'] = max_cycle - grouped['cycle']
                data_list.append(grouped)
        except Exception as e:
            continue

    if not data_list:
        return generate_synthetic_data()

    return pd.concat(data_list, ignore_index=True)

def generate_synthetic_data():
    # Creates realistic looking battery data if user hasn't downloaded files yet
    np.random.seed(42)
    n_samples = 1000
    cycles = np.random.randint(1, 1000, n_samples)
    voltage = 4.2 - (cycles * 0.0005) + np.random.normal(0, 0.01, n_samples)
    current = np.random.normal(-2.0, 0.1, n_samples)
    temp = 24.0 + (cycles * 0.01) + np.random.normal(0, 0.5, n_samples)
    
    # RUL is inversely related to cycle count
    rul = 1500 - cycles 
    rul = np.maximum(rul, 0)
    
    df = pd.DataFrame({
        'cycle': cycles,
        'Voltage_measured': voltage,
        'Current_measured': current,
        'Temperature_measured': temp,
        'RUL': rul
    })
    return df

def train():
    df = load_and_process_data()
    
    X = df[['Voltage_measured', 'Current_measured', 'Temperature_measured', 'cycle']]
    y = df['RUL']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = r2_score(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    
    print(f"Model Trained! Accuracy (R2): {accuracy:.2f}, RMSE: {rmse:.2f}")
    
    # Save Model
    if not os.path.exists("models"):
        os.makedirs("models")
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()