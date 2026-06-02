import numpy as np
import pandas as pd
from ceci.config import StageParameter
from rail.core.data import PqHandle
from rail.core.stage import RailStage


class SmokeTestSource(RailStage):
    """Generate a tiny synthetic galaxy catalog for pipeline smoke testing.

    No external data files are required.
    Produces LSST-band magnitudes (u, g, r, i, z, y) and redshifts suitable
    for passing through downstream RAIL degradation stages.

    Parameters
    ----------
    n_galaxies : int
        Number of synthetic galaxies to generate.
        Default: ``200``.
    seed : int
        Random seed for reproducibility.
        Default: ``42``.
    """

    name = "SmokeTestSource"
    inputs = []
    outputs = [("smoke_catalog", PqHandle)]
    config_options = RailStage.config_options.copy()
    config_options.update(
        n_galaxies=StageParameter(int, 200, msg="Number of synthetic galaxies"),
        seed=StageParameter(int, 42, msg="Random seed"),
    )

    def run(self):
        rng = np.random.default_rng(self.config.seed)
        n = self.config.n_galaxies

        mag_i = rng.normal(24.0, 1.5, n)

        data = pd.DataFrame(
            {
                "redshift": rng.uniform(0.0, 3.0, n),
                "u": mag_i + rng.normal(2.5, 0.3, n),
                "g": mag_i + rng.normal(1.0, 0.2, n),
                "r": mag_i + rng.normal(0.3, 0.1, n),
                "i": mag_i,
                "z": mag_i + rng.normal(-0.2, 0.1, n),
                "y": mag_i + rng.normal(-0.4, 0.1, n),
            }
        )

        self.add_data("smoke_catalog", data)
