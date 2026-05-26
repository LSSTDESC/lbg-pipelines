import os

import pyarrow.parquet as pq
from ceci.config import StageParameter
from ceci.stage import PipelineStage
from rail.core.data import PqHandle
from rail.core.stage import RailStage
from rail.projects.reducer import COLUMNS_FLAGSHIP as _RAIL_FLAGSHIP_COLUMNS
from rail.projects.reducer import FlagshipReducer as RailFlagshipReducer

_FLAGSHIP_ORIGINAL_COLS = frozenset(_RAIL_FLAGSHIP_COLUMNS)

_DROP_COLUMNS = frozenset(
    [
        "lsst_u_el_model3_ext",
        "lsst_g_el_model3_ext",
        "lsst_r_el_model3_ext",
        "lsst_i_el_model3_ext",
        "lsst_z_el_model3_ext",
        "lsst_y_el_model3_ext",
        "euclid_nisp_h_el_model3_ext",
        "euclid_nisp_j_el_model3_ext",
        "euclid_nisp_y_el_model3_ext",
        "euclid_vis_el_model3_ext",
        "ra_mag_gal",
        "dec_mag_gal",
        "observed_redshift_gal",
        "_orientationAngle",
    ]
)


class FlagshipReducer(RailStage):
    """Load Flagship simulation pixel files and reduce to a standard catalog.

    Wraps ``FlagshipReducer`` from ``rail_projects`` to convert raw per-pixel
    parquet files (flux columns, Flagship coordinate convention) into a reduced
    catalog with AB magnitudes and standard ra/dec.
    The output is a single parquet file suitable for downstream RAIL
    degradation stages.

    Parameters
    ----------
    input_dir : str
        Directory containing Flagship pixel parquet files (wNIR).
        Default: ``/global/cfs/cdirs/lsst/groups/PZ/Flagship/Roman``.
    pixels : list of int
        HEALPix pixel IDs to load.
        Default: ``[27, 28, 35, 36, 43, 44]``.
    file_pattern : str
        Filename template; ``{pixel}`` is substituted with each pixel ID.
        Default: ``euclid_fs2_mock_dr_v1_1_phz_wNIR.pix{pixel}.pq``.
    cuts : dict
        Column cuts forwarded to the underlying ``FlagshipReducer``.
        Each key is a column name and each value is a ``[min, max]`` pair
        (``None`` means no bound).
        Default: ``{"maglim_i": [None, 99.0]}``.
    """

    name = "FlagshipReducer"
    inputs = []
    outputs = [("flagship_catalog", PqHandle)]
    config_options = RailStage.config_options.copy()
    config_options.update(
        dict(
            input_dir=StageParameter(
                str,
                "/global/cfs/cdirs/lsst/groups/PZ/Flagship/Roman",
                msg="Directory containing Flagship pixel parquet files (wNIR)",
            ),
            pixels=StageParameter(
                list,
                [27, 28, 35, 36, 43, 44],
                msg="HEALPix pixel IDs to load",
            ),
            file_pattern=StageParameter(
                str,
                "euclid_fs2_mock_dr_v1_1_phz_wNIR.pix{pixel}.pq",
                msg="Filename pattern; {pixel} is replaced with each pixel ID",
            ),
            cuts=StageParameter(
                dict,
                {"maglim_i": [None, 99.0]},
                msg="Magnitude/column cuts passed to FlagshipReducer",
            ),
        )
    )

    def run(self):
        """Read pixel files and write the reduced catalog to the output path."""
        pixel_files = [
            os.path.join(
                self.config.input_dir,
                self.config.file_pattern.format(pixel=p),
            )
            for p in self.config.pixels
        ]
        # Write to the inprogress path; _finalize_tag will rename it.
        out_path = self.get_output("flagship_catalog", final_name=False)
        reducer = RailFlagshipReducer(name="flagship_reducer", cuts=self.config.cuts)
        reducer.run(pixel_files, out_path)

        # We will drop unwanted columns that were "projected" by the RAIL reducer
        schema = pq.read_schema(out_path)
        keep = [c for c in schema.names if c not in _DROP_COLUMNS]

        # And we will reorder the table so the "projected" columns come first
        projected = [c for c in keep if c not in _FLAGSHIP_ORIGINAL_COLS]
        original = [c for c in keep if c in _FLAGSHIP_ORIGINAL_COLS]

        # Finally read only those columns and overwrite the original table
        pq.write_table(pq.read_table(out_path, columns=projected + original), out_path)

    def _finalize_tag(self, tag):
        # RailFlagshipReducer.run() writes directly to disk and returns None, so
        # RAIL's handle never receives data.  Skip handle.write() and delegate to
        # ceci's rename logic (inprogress_ → final name) instead.
        final_name = PipelineStage._finalize_tag(self, tag)
        handle = self.get_handle(tag, allow_missing=True)
        if handle is not None:
            handle.path = final_name
        return final_name
