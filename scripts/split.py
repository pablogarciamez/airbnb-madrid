import pandas as pd

df = pd.read_csv("data/listings_clean.csv")

start_val_idx = int(len(df) * 0.7)
start_test_idx = int(len(df) * 0.85)

shuffled = df.sample(frac=1, random_state=42)

train = shuffled.iloc[0:start_val_idx]
val = shuffled.iloc[start_val_idx:start_test_idx]
test = shuffled.iloc[start_test_idx:]

assert pd.concat([train, val, test])["id"].nunique() == 18211

train.to_csv("data/train.csv", index=False)
val.to_csv("data/val.csv", index=False)
test.to_csv("data/test.csv", index=False)

