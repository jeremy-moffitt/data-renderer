from __future__ import annotations

from data_renderer.dataset import DatasetProvider


from data_renderer.renderers.us_presidential_elections import (
    presidential_elections_dataset,
)

DATASETS: dict[str, DatasetProvider] = {
    presidential_elections_dataset.id: presidential_elections_dataset,
}
