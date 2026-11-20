# Data Renderer

A Python web dashboard for exploring datasets with a reusable line-chart view.
The first included dataset shows U.S. presidential vote share by election year,
for an individual state or the combined United States.

## Run locally

Requirements: Python 3.10 or newer.

```powershell
cd data-renderer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

### Git Bash

```bash
cd data-renderer
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

## Download the election data

The election CSV is not included in this repository. Download
[`1976-2024-president.csv`](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX)
from the Harvard Dataverse source page, then place it at:

```text
datasets/us_presidential_elections/1976-2024-president.csv
```

Create the destination folder first if it does not exist. The app expects this
exact filename and location. The `datasets/` directory is ignored by Git, so
the downloaded data will remain local and must be downloaded separately in
each clone.

## Data and calculations

The election CSV is the source. The dashboard uses the `party_simplified`
field, grouping its blank value into `OTHER`. Each share is a party's candidate
votes divided by total votes cast. The national view sums votes and totals
across all included states and the District of Columbia for each election year.

The source page is recorded in `datasets/us_presidential_elections/sources.txt.txt`.

## Add a dataset

The browser chart is data-driven: it accepts election-year labels, named
colored series, axis descriptions, and optional select filters. To add a
dataset, implement a loader following the `Dataset` contract in
`data_renderer/registry.py`, return the same payload shape as the existing
renderer, and register it in `data_renderer/registry.py`. The dataset selector
and line-chart renderer will then serve it without dataset-specific frontend
changes.

## Tests

```powershell
python -m unittest discover -s tests -v
```
