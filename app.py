from flask import Flask, redirect, url_for, render_template, request
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf
import warnings
import itertools
import json

app=Flask(__name__)

@app.route("/")
def man():
    konsumsi = pd.read_excel('DATA PENELITIAN.xlsx',index_col='Tahun', parse_dates=True)
    df_Bahan_Pangan = konsumsi.Bahan_Pangan.unique()
    return render_template('home.html',data=str(df_Bahan_Pangan).replace('\n',''))

@app.route("/predict",methods=['POST'])
def home():
    data1=request.form['bahanpangan']
    data2=request.form['step']
    konsumsi = pd.read_excel('DATA PENELITIAN.xlsx',index_col='Tahun', parse_dates=True)
    df_prod=konsumsi.loc[konsumsi['Bahan_Pangan'] == data1]
    y=df_prod['Jumlah_Konsumsi']
    # json = y.to_json(orient='records')[1:-1].replace('},{', '} {')
    mod = sm.tsa.statespace.SARIMAX(y, order=(1, 1, 1),seasonal_order=(0, 1, 1, 12),enforce_stationarity=True, enforce_invertibility=False)
    results = mod.fit()
    # results.summary().tables[1]

    pred_uc = results.get_forecast(steps=int(data2))
    result1 = str(pred_uc.predicted_mean.index.year.values)
    result2 = str(pred_uc.predicted_mean.values)
    data_prod=str(y.values)
    
    
    labels=str(np.concatenate((np.array(df_prod.index.year.values),np.array(pred_uc.predicted_mean.index.year.values)),axis=0))
    result3={"tahun":labels,"data1":data_prod,"data2":result2,"bahanpangan":data1,"step":data2}

    return render_template('after.html',data=str(result3))


@app.route("/<name>")
def user(name):
    return f"Hello {name}!"

@app.route("/admin")
def admin():
    return redirect(url_for("home"))


if __name__=='__main__':
    app.run(debug=True)