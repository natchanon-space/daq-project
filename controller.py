import sys
from flask import abort
import pymysql
from dbutils.pooled_db import PooledDB
from config import OPENAPI_STUB_DIR, DB_HOST, DB_USER, DB_PASSWD, DB_NAME

import numpy as np
import pandas as pd
import scipy

sys.path.append(OPENAPI_STUB_DIR)
from swagger_server import models

pool = PooledDB(creator=pymysql,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWD,
                database=DB_NAME,
                maxconnections=1,
                blocking=True)

def generate_table(date=None, offset=None):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT aave.time time, borrow, lend, withdraw, deposit, price, count 
            FROM aave 
            LEFT OUTER JOIN unibtc ON aave.time = unibtc.time 
            LEFT OUTER JOIN price ON aave.time = price.time 
            LEFT OUTER JOIN twitter ON aave.time = DATE_ADD(twitter.time, INTERVAL 1 DAY_HOUR) 
            WHERE (aave.time >= %s AND aave.time < %s) 
            ORDER BY aave.time
            """, [f"{date} 00:00:00", f"{date[:7]}-{int(int(date[8:])+offset+1):02d} 00:00:00"])
        result = cs.fetchall()
    df = pd.DataFrame(result, columns=["time", "borrow", "lend", "withdraw", "deposit", "price", "count"])
    df = df.sort_values(by="time")
    return df

def get_info(date=None, offset=None):
    df = generate_table(date=date, offset=offset)
    df = df.replace([np.nan], [None])
    features = df.drop(columns=["time"]).columns
    data = []
    for f in features:
        data.append(
            models.InfoItem(
                name=f,
                vals=df[f].to_list()
            )
        )
    return models.Info(
        _datetime=df["time"].to_list(),
        data=list([models.InfoItem(
            name=f,
            vals=df[f].to_list()
        ) for f in features])
    )

def get_info_feat(feature, date=None, offset=None):
    df = generate_table(date=date, offset=offset)
    df = df.dropna()
    return models.Info(
        _datetime=df["time"].to_list(), 
        data=[models.InfoItem(name=feature, vals=df[feature].to_list())]
        )

def get_stat(date=None, offset=None):
    df = generate_table(date=date, offset=offset)
    features = df.drop(columns=["time"]).columns
    data = []
    for f in features:
        temp = df[f].dropna()
        data.append(models.BasicStats(
            name=f,
            avg=temp.mean(),
            std=temp.std(),
            count=len(temp)
        ))
    return data

def get_stat_feat(feature, date=None, offset=None):
    df = generate_table(date=date, offset=offset)
    df = df.dropna()
    feat = df[feature]
    return models.BasicStats(
        name=feature,
        avg=feat.mean(),
        std=feat.std(),
        count=len(feat)
    )

def get_corr(date=None, offset=None):
    df = generate_table(date=date, offset=offset)
    df = df.drop(columns="time").dropna()
    features = df.columns
    data = []
    for f1 in features:
        for f2 in features:
            data.append(models.CorrStat(
                x=f1,
                y=f2,
                corr=scipy.stats.pearsonr(df[f1], df[f2])[0])
            )
    return data

def get_corr_feat(feature, date=None, offset=None):
    df = generate_table(date=date, offset=offset)
    df = df.drop(columns="time").dropna()
    features = df.columns
    return [models.CorrStat(
        x=feature,
        y=f,
        corr=scipy.stats.pearsonr(df[feature], df[f])[0]
    ) for f in features]

def get_corr_feat_feat2(feature, feature2, date=None, offset=None):
    df = generate_table(date=date, offset=offset)
    if feature != feature2:
        df = df[[feature, feature2]]
    else:
        pass
    df = df.dropna()
    val, _ = scipy.stats.pearsonr(df[feature], df[feature2])
    return models.CorrStat(
        x=feature,
        y=feature2,
        corr=val
    )