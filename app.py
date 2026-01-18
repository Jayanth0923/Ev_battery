from flask import Flask, render_template, request, send_file
import joblib
import numpy as np
import os
from pdf_gen import create_pdf

app = Flask(__name__)

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'battery_model.pkl')
REPORT_PATH = os.path.join(BASE_DIR, 'report.pdf')

# Load Model
try:
    model = joblib.load(MODEL_PATH)
except:
    print(f"Model not found at {MODEL_PATH}. Please run train_model.py first.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Get Inputs
        v = float(request.form['voltage'])
        i = float(request.form['current'])
        t = float(request.form['temperature'])
        c = float(request.form['cycle'])
        
        # 2. Predict RUL
        features = np.array([[v, i, t, c]])
        rul_pred = model.predict(features)[0]
        
        # 3. Calculate Base Health Score
        max_life = 1500 
        health = max(0, min(100, (rul_pred / max_life) * 100))
        
        # --- LOGIC START ---
        condition = "Excellent"
        rec = "Battery is in good shape. Maintain standard charging habits."
        cost = 0
        css_class = "text-success-custom"
        
        if health < 75:
            condition = "Good"
            rec = "Minor degradation detected. Avoid deep discharges."
            cost = 20
            css_class = "text-warning-custom"
        if health < 50:
            condition = "Fair/Risk"
            rec = "Significant aging. Plan for replacement soon. Check cooling systems."
            cost = 150
            css_class = "text-warning-custom"
        if health < 25:
            condition = "Critical"
            rec = "IMMEDIATE REPLACEMENT REQUIRED. High risk of failure."
            cost = 300
            css_class = "text-danger-custom"

        # OVERHEAT LOGIC
        if t > 40:
            condition = "OVERHEATING WARNING"
            rec = "DANGER: Temperature is too high! Cool down immediately to prevent permanent damage."
            css_class = "text-danger-custom"
            health = max(0, health - 10)
            cost = cost + 100

        results = {
            'rul': int(rul_pred),
            'health_score': int(health),
            'condition': condition,
            'recommendation': rec,
            'cost': cost,
            'css_class': css_class
        }
        
        data = {'voltage': v, 'current': i, 'temperature': t, 'cycle': c}
        
        # Generate PDF
        create_pdf(data, results)
        
        return render_template('dashboard.html', data=data, res=results)

    except Exception as e:
        return f"Error: {e}"

@app.route('/download')
def download_pdf():
    # Robust check to see if file exists
    if os.path.exists(REPORT_PATH):
        return send_file(REPORT_PATH, as_attachment=True)
    else:
        return "Error: Report file not found. Please run the analysis again."

if __name__ == '__main__':
    app.run(debug=True)