# airbnb-madrid

Data analysis of Madrid Airbnb listings for nightly price prediction using property metrics (neighborhood, room type, number of bedrooms, reviews...).

## Data

All data for this project is from [Get the Data](https://insideairbnb.com/es/get-the-data/), a free public resource providing downloadable datasets, metrics, and quarterly archives about Airbnb listings in major cities across the world. Specifically, this project utilizes the Madrid Airbnb listings dataset [listings.csv.gz](https://data.insideairbnb.com/spain/comunidad-de-madrid/madrid/2026-06-20/data/listings.csv.gz) from June 20, 2026. To replicate this study, first create a `data/` folder at the root of the repository and move the decompressed file `listings.csv` there.

## Repository structure

- `data/`: contains the Madrid Airbnb listings dataset [listings.csv.gz](https://data.insideairbnb.com/spain/comunidad-de-madrid/madrid/2026-06-20/data/listings.csv.gz) from June 20, 2026, as well as its cleaned version `listings_clean.csv`. This folder is not included in the repository (it is excluded via .gitignore) and must be created as described in Data.

- `notebooks/01_exploration.ipynb`: contains multiple separate analyses of the dataset (from Q1 to Q5) and other scripts related to later stages of the project

- `scripts/clean.py`: processes the original dataset to create `listings_clean.csv`.

## T2

### How to run:

The `clean.py` script filters the original dataset and creates `data/listings_clean.csv` and must be run from the root of the repository.

```bash
python scripts/clean.py
```

| Step | Rows | Reason |
|:--|--:|:--|
| load | 22,708 | — |
| rm previous scrape | 18,548 | 78.1% missing price and 100% missing beds (vs 1.5% and 2.1% in city scrape) |
| clean price | 18,548 | text with currency symbol and commas converted to float |
| rm missing price | 18,263 | price is the target variable (285 missing) |
| check duplicate ids | 18,263 | 0 duplicates (assert) |
| rm price over 2000 | 18,211 | implausible values (e.g. 15,000 repeated, 22,832.50 for 1 guest); 52 listings, 0.28% |
| host_is_superhost to bool | 18,211 | t/f text to boolean (assert: only t/f values) |

No listings were removed due to low prices, as these prices seemed plausible and there was no indication that they served as placeholders or had any other meaning.

### Candidate columns:

| Candidate column | Missing | % | Note |
|:--|--:|--:|:--|
| bedrooms | 3,930 | 21.58 | |
| review_scores_rating | 2,441 | 13.40 | listings with no reviews yet |
| bathrooms | 1,232 | 6.77 | |
| beds | 374 | 2.05 | |
| bathrooms_text | 15 | 0.08 | kept as text until T3 |
| amenities | 0 | 0.00 | kept as text until T3 |
| hosts_time_as_host_months | 0 | 0.00 | |
| accommodates | 0 | 0.00 | |
| latitude | 0 | 0.00 | |
| longitude | 0 | 0.00 | |
| property_type | 0 | 0.00 | |
| room_type | 0 | 0.00 | |
| neighbourhood_cleansed | 0 | 0.00 | |
| minimum_nights | 0 | 0.00 | |
| maximum_nights | 0 | 0.00 | |
| host_is_superhost | 0 | 0.00 | converted to bool |

Missing values are left as they are; they will be handled in T3, after the split.

## T3

### How to run:

Run in order from the root of the repository `clean.py` → `split.py` → `features.py`.

- The `clean.py` script filters the original dataset and creates `data/listings_clean.csv`.
- The `split.py` script splits the data into train (70%), val (15%) and test (15%) and creates `data/train.csv`, `data/val.csv` and `data/test.csv`.
- The `features.py` script builds the model variables (imputation, one-hot encoding, derived columns) using statistics computed on train only, and creates `data/train_features.csv`, `data/val_features.csv` and `data/test_features.csv` (134 columns: `id`, the target `price` and 132 features).

```bash
python scripts/clean.py
python scripts/split.py
python scripts/features.py
```

### Why there is no data leakage

Leakage means the model sees information during training that it would not have when predicting the price of a new listing. Four sources were checked:

- **Columns derived from the price.** `estimated_revenue_l365d` divided by `estimated_occupancy_l365d` gives the exact price (e.g. 39,234 / 78 = 503), so it was excluded, together with `price_quote_price_per_night` and `price_quote_total_price`.
- **Imputation after the split.** Missing values are filled only after splitting, and every statistic is computed on train alone: the median `review_scores_rating`, and the medians of `bedrooms`, `beds` and `bath_num` by `accommodates`. Val and test are filled with these same train values. Computing them on the full dataset would let val and test rows influence the training data, so the evaluation would no longer be on truly unseen data and would look better than it really is.
- **Categories decided on train.** For `neighbourhood_cleansed` and `property_type`, the list of frequent categories (at least 20 listings in train), the `Other` group and the reference category (the most common one in train) are all decided on train and applied unchanged to val and test. The threshold also avoids learning a separate effect from just a few listings. A category that never appears in train goes to `Other`: 3 rows in val and 1 in test have a property type not seen in train, and all of them end up in `Other`.
- **Row-wise transformations.** `bath_num` and `bath_shared` (parsed from `bathrooms_text`), `has_reviews` (whether `review_scores_rating` was missing, created before filling it), `amenities_count` (number of items in the `amenities` list) and `host_months` (`hosts_time_as_host_years` × 12 + `hosts_time_as_host_months`) only use values from the same row. They do not depend on other rows or on the price, so they cannot leak information between splits.