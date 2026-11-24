from __future__ import annotations

from data_renderer.dataset import DatasetProvider
from data_renderer.renderers.nba_games import nba_games_dataset
from data_renderer.renderers.us_cities_temps import us_cities_temps_dataset
from data_renderer.renderers.us_presidential_elections import (
    presidential_elections_dataset,
)

DATASETS: dict[str, DatasetProvider] = {
    presidential_elections_dataset.id: presidential_elections_dataset,
    nba_games_dataset.id: nba_games_dataset,
    us_cities_temps_dataset.id: us_cities_temps_dataset,
}
