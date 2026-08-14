import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def train_predictive_ai_on_tep(excel_filename):
    print(f"Loading TEP dataset from '{excel_filename}'...")
    
    try:
        # 1. Read the Excel file using pandas
        df = pd.read_excel(excel_filename)
        print(f"Dataset successfully loaded! Shape: {df.shape[0]} rows, {df.shape[1]} columns.")
        
        # 2. Inspect column names to find available plant measurements
        print("Columns preview:", list(df.columns[:10]))
        
        # TEP datasets usually use generic column headers (e.g., 'xmeas_1', 'xmv_1')
        # Let's map target prediction using available process columns dynamically
        # If columns match standard TEP format, xmeas_9 is often Reactor Temp, xmv_1 is Valve 1, etc.
        target_col = df.columns[8] if len(df.columns) > 8 else df.columns[-1]
        feature_cols = [df.columns[1], df.columns[2], df.columns[3]] # using first few sensor streams as features
        
        print(f"Training machine learning forecaster using target '{target_col}'...")
        
        # Clean data (drop missing values)
        clean_df = df[feature_cols + [target_col]].dropna()
        
        X = clean_df[feature_cols]
        y = clean_df[target_col]
        
        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 3. Train a Random Forest Regressor (Machine Learning Predictive Model)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 4. Evaluate model performance
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        print(f"Model Training Complete! Test Mean Squared Error (MSE): {mse:.4f}")
        
        return model

    except Exception as e:
        print(f"Error processing the Excel file: {e}")
        return None

if __name__ == "__main__":
    file_path = "mode1_normal_500.xlsx"
    ml_model = train_predictive_ai_on_tep(file_path)