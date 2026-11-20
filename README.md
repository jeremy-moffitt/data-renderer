# Data Renderer

A Python web dashboard for exploring datasets with a reusable line-chart view.
It includes U.S. presidential vote share and NBA team scoring data.

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

## Download the NBA games data

Download `Games.csv` from the
[Historical NBA Data and Player Box Scores Kaggle dataset](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores?resource=download)
(a free Kaggle account is required), then place it at:

```text
datasets/nba_games/Games.csv
```

The source is also recorded in `datasets/nba_games/sources.txt`. Select a
team and year in the dashboard to see the franchise's points in each game,
with opponent and score details available by hovering over a point. Years use
the season-ending year, so the 1946–47 season is labeled 1947.

## Data and calculations

The election CSV is the source. The dashboard uses the `party_simplified`
field, grouping its blank value into `OTHER`. Each share is a party's candidate
votes divided by total votes cast. The national view sums votes and totals
across all included states and the District of Columbia for each election year.

NBA scores come from `homeScore` and `awayScore`; games are grouped using their
team IDs so franchise relocations and name changes stay together.

The source page is recorded in `datasets/us_presidential_elections/sources.txt`.

## Add a dataset

The browser chart is data-driven: it accepts category labels, named colored
series, axis descriptions, and optional select filters. To add a
dataset, implement a loader following the `Dataset` contract in
`data_renderer/registry.py`, return the same payload shape as the existing
renderers, and register it in `data_renderer/registry.py`. The dataset selector
and line-chart renderer support datasets with multiple filters.

## Tests

```powershell
python -m unittest discover -s tests -v
```
