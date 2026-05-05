import pandas as pd

def load_dvf(path):
    return pd.read_csv(path, sep="|")