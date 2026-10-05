import pandas as pd

train = pd.read_csv("data/train.csv")
val = pd.read_csv("data/val.csv")
test = pd.read_csv("data/test.csv")

medians = train.groupby("accommodates")["bedrooms"].median()

def fill_bedrooms(df, medians):
    df["bedrooms"] = df["bedrooms"].fillna(df["accommodates"].map(medians))
    return df

train = fill_bedrooms(train, medians)
val = fill_bedrooms(val, medians)
test = fill_bedrooms(test, medians)

assert train["bedrooms"].isna().sum() == 0