import numpy as np

def calc(df):
    df["Profit"] = df["Current"] - df["Investment"]
    df["Risk"] = np.random.rand(len(df)) * 100
    return df