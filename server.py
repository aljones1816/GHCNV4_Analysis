import pandas as pd
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.get('/data')
def dataset():
    gistemp = pd.read_csv('data/clean/giss_anomalies_clean.csv')
    crutem = pd.read_csv('data/clean/crutem_anomalies_clean.csv')
    ghcn = pd.read_csv('data/clean/ghcnm_anomalies_clean.csv')

    combined = gistemp.merge(crutem, on='year', suffixes=('_gistemp', '_crutem'))
    combined = combined.merge(ghcn, on='year')
    combined.rename(columns={'anomaly (deg C)': 'anomaly_ghcn'}, inplace=True)
    
    #dictionary with an array of years, array of giss anomalies, array of crutem anomalies, and array of ghcn anomalies
    data = {
        'years': combined['year'].tolist(),
        'giss': combined['anomaly (deg C)_gistemp'].tolist(),
        'crutem': combined['anomaly (deg C)_crutem'].tolist(),
        'ghcn': combined['anomaly_ghcn'].tolist()
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
