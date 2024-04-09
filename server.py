import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.get('/gistemp')
def gistemp():
    gistemps = pd.read_csv('data/clean/giss_anomalies_clean.csv')
    response = gistemps.to_json()
    print(response)
    return response

if __name__ == '__main__':
    app.run(debug=True)