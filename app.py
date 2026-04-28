from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        distance REAL,
        price REAL,
        duration REAL,
        traffic INTEGER
    )''')
    conn.commit()
    conn.close()

init_db()

def encode_traffic(t):
    return {"faible":1, "moyen":2, "élevé":3}.get(t,1)

@app.route('/')
def index():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT * FROM transports", conn)
    conn.close()
    return render_template("index.html", data=df.to_dict(orient="records"))

@app.route('/add', methods=['POST'])
def add():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO transports (distance, price, duration, traffic) VALUES (?, ?, ?, ?)",
              (
                  float(request.form['distance']),
                  float(request.form['price']),
                  float(request.form['duration']),
                  encode_traffic(request.form['traffic'])
              ))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/predict')
def predict():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT * FROM transports", conn)
    conn.close()

    X = df[['distance']]
    y = df['price']

    model = LinearRegression().fit(X,y)
    pred = model.predict([[10]])[0]

    return jsonify({"prediction": round(pred,2)})

@app.route('/cluster')
def cluster():
    conn = sqlite3.connect("database.db")
    df = pd.read_sql_query("SELECT * FROM transports", conn)
    conn.close()

    X = df[['distance','price']]
    kmeans = KMeans(n_clusters=3).fit(X)
    df['cluster'] = kmeans.labels_

    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run()
