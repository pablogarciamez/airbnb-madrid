import pandas as pd
import json

def add_amenities_count(df):
    df["amenities_count"] = df["amenities"].map(lambda s: len(json.loads(s)))
    return df

train = pd.read_csv("data/train.csv")
val = pd.read_csv("data/val.csv")
test = pd.read_csv("data/test.csv")

def fill_by_accommodates(df, medians, col):
    df[col] = df[col].fillna(df["accommodates"].map(medians))
    return df

def add_bath_num_and_bath_shared(df):
    df["bath_num"] = df["bathrooms_text"].str.lower().str.replace("half-bath", "0.5 baths").str.replace("shared ", "").str.replace("private ", "").str.split(" ").str[0].astype(float)
    df["bath_shared"] = df["bathrooms_text"].str.lower().str.contains("shared", na=False)
    return df

def add_has_reviews(df):
    df["has_reviews"] = df["review_scores_rating"].notna()
    return df

def add_room_type_one_hot(df):
    df["is_private"] = (df["room_type"] == "Private room").astype(int)
    df["is_shared"] = (df["room_type"] == "Shared room").astype(int)
    df["is_hotel"] = (df["room_type"] == "Hotel room").astype(int)
    return df

def add_neighbourhood_grouped(df, frequent_neighbourhoods):
    df["neighbourhood_grouped"] = df["neighbourhood_cleansed"].where(df["neighbourhood_cleansed"].isin(frequent_neighbourhoods), "Other")
    return df

def add_property_grouped(df, frequent_types):
    df["property_grouped"] = df["property_type"].where(df["property_type"].isin(frequent_types), "Other")
    return df

def add_one_hot(df, column, prefix, reference, categories):
    start_columns = len(df.columns)
    newColumns = []
    for category in categories:
        df[f"{prefix}_{category}"] = (df[column] == category).astype(int)
        newColumns.append(f"{prefix}_{category}")
    assert len(df.columns) == start_columns + len(categories)
    assert df[newColumns].sum(axis=1).isin([0, 1]).all()
    assert (df[newColumns].sum(axis=1) == 0).sum() == (df[column] == reference).sum()
    return df

counts = train["neighbourhood_cleansed"].value_counts()
frequent_neighbourhoods = counts[counts >= 20].index
counts = train["property_type"].value_counts()
frequent_types = counts[counts >= 20].index

train = add_neighbourhood_grouped(train, frequent_neighbourhoods)
val = add_neighbourhood_grouped(val, frequent_neighbourhoods)
test = add_neighbourhood_grouped(test, frequent_neighbourhoods)
train = add_property_grouped(train, frequent_types)
val = add_property_grouped(val, frequent_types)
test = add_property_grouped(test, frequent_types)

train = add_amenities_count(train)
val = add_amenities_count(val)
test = add_amenities_count(test)

train["host_months"]  = train["hosts_time_as_host_years"] * 12 + train["hosts_time_as_host_months"]
val["host_months"]  = val["hosts_time_as_host_years"] * 12 + val["hosts_time_as_host_months"]
test["host_months"]  = test["hosts_time_as_host_years"] * 12 + test["hosts_time_as_host_months"]


reference = train["neighbourhood_grouped"].value_counts().index[0]
neighbourhoods = []
for neighbourhood in train["neighbourhood_grouped"].value_counts().index:
    if (neighbourhood != reference):
        neighbourhoods.append(neighbourhood)

train = add_one_hot(train, "neighbourhood_grouped", "nb", reference, neighbourhoods)
val = add_one_hot(val, "neighbourhood_grouped", "nb", reference, neighbourhoods)
test = add_one_hot(test, "neighbourhood_grouped", "nb", reference, neighbourhoods)

reference = train["property_grouped"].value_counts().index[0]
types = []
for ptype in train["property_grouped"].value_counts().index:
    if (ptype != reference):
        types.append(ptype)

train = add_one_hot(train, "property_grouped", "pt", reference, types)
val = add_one_hot(val, "property_grouped", "pt", reference, types)
test = add_one_hot(test, "property_grouped", "pt", reference, types)

train = add_room_type_one_hot(train)
val = add_room_type_one_hot(val)
test = add_room_type_one_hot(test)

assert (train[["is_private", "is_shared", "is_hotel"]].sum(axis=1).isin((0, 1))).all()
assert (val[["is_private", "is_shared", "is_hotel"]].sum(axis=1).isin((0, 1))).all()
assert (test[["is_private", "is_shared", "is_hotel"]].sum(axis=1).isin((0, 1))).all()

train = add_bath_num_and_bath_shared(train)
val = add_bath_num_and_bath_shared(val)
test = add_bath_num_and_bath_shared(test)

no_reviews = train["review_scores_rating"].isna().sum()

train = add_has_reviews(train)
val = add_has_reviews(val)
test = add_has_reviews(test)

median_review_scores_rating = train["review_scores_rating"].median()

train["review_scores_rating"] = train["review_scores_rating"].fillna(median_review_scores_rating)
val["review_scores_rating"] = val["review_scores_rating"].fillna(median_review_scores_rating)
test["review_scores_rating"] = test["review_scores_rating"].fillna(median_review_scores_rating)

medians_bedrooms = train.groupby("accommodates")["bedrooms"].median()
medians_beds = train.groupby("accommodates")["beds"].median()
medians_bath = train.groupby("accommodates")["bath_num"].median()

train = fill_by_accommodates(train, medians_bath, "bath_num")
val = fill_by_accommodates(val, medians_bath, "bath_num")
test = fill_by_accommodates(test, medians_bath, "bath_num")

train = fill_by_accommodates(train, medians_bedrooms, "bedrooms")
val = fill_by_accommodates(val, medians_bedrooms, "bedrooms")
test = fill_by_accommodates(test, medians_bedrooms, "bedrooms")
train = fill_by_accommodates(train, medians_beds, "beds")
val = fill_by_accommodates(val, medians_beds, "beds")
test = fill_by_accommodates(test, medians_beds, "beds")

assert train["bedrooms"].isna().sum() == 0
assert train["beds"].isna().sum() == 0
assert val["bedrooms"].isna().sum() == 0
assert val["beds"].isna().sum() == 0
assert test["bedrooms"].isna().sum() == 0
assert test["beds"].isna().sum() == 0

assert train["bath_num"].isna().sum() == 0
assert train["bath_shared"].isin([True, False]).all()
assert val["bath_num"].isna().sum() == 0
assert val["bath_shared"].isin([True, False]).all()
assert test["bath_num"].isna().sum() == 0
assert test["bath_shared"].isin([True, False]).all()

assert train["review_scores_rating"].isna().sum() == 0
assert val["review_scores_rating"].isna().sum() == 0
assert test["review_scores_rating"].isna().sum() == 0

assert (train["has_reviews"] == False).sum() == no_reviews

columns = ["id", "price", "accommodates", "bedrooms", "beds", "bath_num", "review_scores_rating", "amenities_count", "host_months", "latitude", "longitude", "minimum_nights", "maximum_nights", "bath_shared", "has_reviews", "host_is_superhost", "is_private", "is_shared", "is_hotel"]
for ptype in types:
    columns.append(f"pt_{ptype}")
for neighbourhood in neighbourhoods:
    columns.append(f"nb_{neighbourhood}")

train_features = train[columns]
val_features = val[columns]
test_features = test[columns]

assert train_features.shape[1] == 134
assert val_features.shape[1] == 134
assert test_features.shape[1] == 134

train_features.to_csv("data/train_features.csv", index=False)
val_features.to_csv("data/val_features.csv", index=False)
test_features.to_csv("data/test_features.csv", index=False)