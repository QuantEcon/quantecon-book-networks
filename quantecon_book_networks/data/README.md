# About the datasets

---

### `data/commercial-aircraft-sitcr2-7924-yr2019`

Description:

This dataset is obtained and cleaned from [Harvard, CID Dataverse](https://dataverse.harvard.edu/dataverse/atlas).

Not updated.

---

### `data/crude_oil_sitcr2_3330_yr2021`

Description:

This dataset is obtained and cleaned from `HS92` file in [CEPII - BACI](http://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37).

The original `HS92` file has data for multiple goods where you can find a `Product category (HS 6-digit code)` attribute.

There is another file in `HS92` where you can look up the corresponding product code and its detail, in this case it is `270900, Oils: petroleum oils and oils obtained from bituminous minerals, crude`.

Files:

* data.csv
  * `location_code` is the ISO3C country code for the exporter country.
  * `partner_code` is the ISO3C country code for the importer country.
* regions-iso3c.csv
  * to look up the ISO3C country codes

---

### `data/csv_files`

#### `adjacency_matrix_31-12-2022.csv`

Description:

These data are obtained from the [BIS consolidated banking statistics](https://www.bis.org/statistics/consstats.htm), for Q4 of 2022. Our calculations used the immediate counterparty basis for financial claims of domestic and foreign banks, which calculates the sum of cross-border claims and local claims of foreign affiliates in both foreign and local currency. The foreign claim of a node to itself is set to zero.

These data are originally obtained in countries and then formed into one single file.

We need to filter some attributes which represent the international private credit flows:

``` python
df = df[df["CBS bank type"] == "4R:Domestic banks(4B), excl. domestic positions"]
df = df[df["CBS reporting basis"] == "F:Immediate counterparty basis"]
df = df[df["Balance sheet position"] == "C:Total claims"]
```
---

#### `forbes-global2000.csv`

Descroption:

This dataset is scrapped in [this](https://github.com/QuantEcon/high_dim_data/blob/main/cross_section/webscrape_forbes.ipynb) file

Not updated.

---

#### `(make|use)_(15|71)_2021.csv`

Description:

Obtained and cleaned from the Supply Tables and Use Tables from [Input-Output Accounts Data](https://www.bea.gov/industry/input-output-accounts-data).

Representing domestic supply and use of commodities by 15 and 71 industries in the US.

The attributes we want for `Total Industry Output` in the original dataset should be `T013`, `Total product supply (basic prices)`.

We need to use the code of industries instead of names in `use_71_2021.csv` as the code is written in this way.

---

#### `(make|use)_114_aus_20-21.csv`

Description:

Obtained from [ABS](https://www.abs.gov.au/statistics/economy/national-accounts/australian-national-accounts-input-output-tables/latest-release).

Representing domestic supply and use of commodities by 114 industries in Australia.

The original data is in `.xlsx` which can be problematic when exporting to `.csv`. Need to be careful with the white spaces in numbers possibly.

---
