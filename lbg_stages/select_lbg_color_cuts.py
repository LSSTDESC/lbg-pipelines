import numpy as np
from ceci.config import StageParameter
from txpipe.data_types import PhotometryCatalog
from txpipe.lens_selector import TXBaseLensSelector
from txpipe.utils import LensNumberDensityStats


class SelectLBGColorCuts(TXBaseLensSelector):
    """
    Applies colour-magnitude to photometry catalog to select dropouts.

    Inherits from `TXBaseLensSelector` to produce outputs in TXPipe-
    compatible format. The input is a catalog (in HDF5 format) containing
    photometric information for a sample of galaxies. The output file is an
    HDF5 file containing "tomographic" information about each dropout sample,
    which primarily includes a label for each source to assign it to a given
    sample.
    """

    name = "SelectLBGColorCuts"
    inputs = [("photometry_catalog", PhotometryCatalog)]

    config_options = TXBaseLensSelector.config_options.copy()
    config_options.update(
        {
            "colour_mag_cuts": StageParameter(
                dict,
                {"g-dropouts": [
                    "g - r > 1",
                    "r - i < 1",
                    "g - r > 1.5 * (r - i) + 0.8"
                    ]
                },
                msg="Colour-magnitude cuts to apply for each dropout sample."
            ),
        }
    )

    def run(self):
        """
        Run the LBG selection process.

        This is an almost exact copy of the `run` method from `TXBaseLensSelector`, with
        two main differences:
        - the number of lens bins is now determined from the length of the
          "colour_mag_cuts" stage parameter
        - `apply_redshift_cut` has been replaced by a new method, `apply_colmag_cuts`
        """
        # Suppress some warnings from numpy that are not relevant
        original_warning_settings = np.seterr(all="ignore")

        # Determine number of lens bins (i.e. dropout samples)
        nbin_lens = len(self.config["colour_mag_cuts"])
        # Since we're not using redshift bins, set the bin edges to NaN
        # (parameter is required for TXPipe-format output)
        self.config["lens_zbin_edges"] = [np.nan] * (nbin_lens + 1)

        # The output file we will put the tomographic
        # information into
        output_file = self.setup_output()
        # Iterator for cycling through "chunks" of the input catalog
        iterator = self.data_iterator()

        # If removing lens galaxies outside the mask, load the mask
        if self.config["apply_mask"]:
            with self.open_input("mask", wrapper=True) as f:
                self.mask, self.mask_nside = f.read_healsparse("mask", return_all=True)

        number_density_stats = LensNumberDensityStats(nbin_lens, self.comm)

        # Loop through the input data, processing it chunk by chunk
        for start, end, phot_data in iterator:
            print(f"Process {self.rank} running selection for rows {start:,}-{end:,}")

            pz_data = self.apply_colmag_cuts(phot_data)

            # Select lens bin objects
            lens_gals = self.select_lens(phot_data)

            # Combine this selection with size and snr cuts to produce a source
            # selection and calculate the shear bias it would generate
            tomo_bin, _ = self.calculate_tomography(pz_data, phot_data, lens_gals)

            # Save the tomography for this chunk
            self.write_tomography(output_file, start, end, tomo_bin)

            # Accumulate information on the number counts and the selection biases.
            # These will be brought together at the end.
            number_density_stats.add_data(tomo_bin)

        # Do the selection bias averaging and output that too.
        self.write_global_values(output_file, number_density_stats)

        # Save and complete
        output_file.close()

        # Restore original warning settings in case we are being called from a library
        np.seterr(**original_warning_settings)


    def data_iterator(self):
        chunk_rows = self.config["chunk_rows"]
        phot_cols = [f"mag_{b}" for b in "ugrizy"] + ["ra", "dec"]
        #extra_cols = [c for c in self.config["extra_cols"] if c]
        #phot_cols += extra_cols

        it = self.combined_iterators(
            chunk_rows,
            "photometry_catalog",
            "photometry",
            phot_cols
        )

        return it

    def select_lens(self, phot_data):
        """
        Method for selecting LBGs ("lens" samples).

        For now, this just selects galaxies within the survey footprint (only if the
        "apply_mask" config option is set to `True`).
        TODO: Include SNR cuts?
        """
        # select only galaxies that are in the footprint
        s = self.select_in_footprint(phot_data)

        ntot = s.size
        nsel = s.sum()
        print(f"Rank {self.rank} selected {nsel} objects out of {ntot} "
              f"as potential LBGs.")
        return s

    def apply_colmag_cuts(self, phot_data):
        """
        Applies the colour-magnitude cuts to identify candidate LBGs.
        """

        from functools import reduce

        import numexpr

        u, g, r, i, z, y = [phot_data[f"mag_{b}"] for b in "ugrizy"]
        ntot = len(u)
        zbin = np.repeat(-1, ntot)

        pz_data = {}
        cuts = self.config["colour_mag_cuts"]
        nsel = 0

        for ik, k in enumerate(cuts):
            mask_zbin = reduce(
                self.combine_and,
                [numexpr.evaluate(c) for c in cuts[k]]
            )
            nsel += mask_zbin.sum()
            zbin[mask_zbin] = ik
        print(f"Rank {self.rank} found {nsel} / {ntot} LBGs (any bin).")

        pz_data["zbin"] = zbin


    def combine_and(self, a, b):
        """
        Simple multiplication function.

        Designed to be fed into `functools.reduce()` to combine an arbitrary
        number of masks.
        """
        return a * b
