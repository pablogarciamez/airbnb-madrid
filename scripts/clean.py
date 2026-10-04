import pandas as pd

steps = []
df = pd.read_csv("data/listings.csv")
steps.append(("load", len(df)))

# Since listings from previous scrapes contain significantly more missing data (78.1% missing 'price' and 100% missing 'beds') compared to those marked as city scrape (only 1.5% and 2.1% missing, respectively), I have excluded them from the analysis and prediction.

df = df[df["source"] == "city scrape"]
steps.append(("rm previous scrape", len(df)))

df["price"] = df["price"].str.replace("$", "").str.replace(",", "").astype(float)
steps.append(("clean price", len(df)))

# Since the aim of this project is to predict the price of listings, those missing 'price' must be removed.

df = df[df["price"].notna()]
steps.append(("rm missing price", len(df)))

assert df["id"].duplicated().sum() == 0

# I have excluded all listings priced over €2,000 per night, as they lack credibility and account for just 52 listings, an insignificant fraction of the total dataset. Furthermore, these entries are highly unrealistic, featuring exact duplicates at €15,000 and even a single-occupancy apartment in Sol priced at over €22,000 per night.

df = df[df["price"] <= 2000]
steps.append(("rm price over 2000", len(df)))

print(steps)

df.to_csv("data/listings_clean.csv", index = False)
