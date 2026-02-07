"""Subsampling the original data of pyramid example."""

import pathlib
import dataclasses
import numpy as np


@dataclasses.dataclass
class SubsamplingConfig:
    """Configuration for subsampling."""

    num_samples: int = 1000
    """Number of samples to draw from the original data."""

    # =============================================================================
    # original constants
    # =============================================================================

    original_file_size_nbyte: int = 10_797_276_672
    """Size of the original data file in bytes."""

    original_values_per_sample: int = 384
    """Number of values per sample in the original data."""

    original_sample_nbyte: int = original_values_per_sample * np.float16().nbytes
    """Number of bytes per sample in the original data."""

    original_sample_count = original_file_size_nbyte // original_sample_nbyte
    """Number of samples in the original data file. 14_058_954"""

    original_value_dtype = np.float16
    """Data type of the values in the original data file."""

    # =============================================================================
    # target constants
    # =============================================================================

    target_values_per_sample: int = 30
    """Number of values per sample in the subsampled data."""

    target_sample_count = original_sample_count // 100
    """Number of samples to draw from the original data. 140_589"""


# =============================================================================
#
# =============================================================================


def original_file_path() -> str:
    """Returns the path to the original data file."""
    file_path = pathlib.Path(__file__).parent / ".." / "tmp" / "pyramid" / "res_00.bin"
    return str(file_path)


def target_folder_path() -> str:
    """Returns the path to the original data file."""
    file_path = pathlib.Path(__file__).parent / ".." / "tmp" / "pyramid" / "pyramid_small"
    return str(file_path)


# =============================================================================
#
# =============================================================================


def load_original_data() -> np.ndarray:
    """Loads the original data from the specified file path."""
    file_path = original_file_path()

    np_array = np.memmap(file_path, dtype=SubsamplingConfig.original_value_dtype)
    np_array = np_array.reshape(-1, SubsamplingConfig.original_values_per_sample)
    return np_array


def main():
    """Main function to perform subsampling."""
    # =============================================================================
    # Load the original file
    # =============================================================================
    file_original_numpy = load_original_data()

    print(f"Original data shape: {file_original_numpy.shape} {file_original_numpy.dtype}")

    # =============================================================================
    # Subsample to target file
    # =============================================================================

    subsampling_mode = "LINEAR"
    subsampling_mode = "NEAREST"
    subsampling_level_min = 0
    subsampling_level_max = 10

    for subsample_level in range(subsampling_level_min, subsampling_level_max):
        file_target_path = pathlib.Path(target_folder_path()) / f"res_{subsample_level:02}.bin"
        # Subsample the data - in NEAREST and LINEAR modes
        if subsampling_mode == "LINEAR":
            # Linear interpolation for both dimensions
            target_sample_count_level = int(SubsamplingConfig.target_sample_count / (2**subsample_level))

            # Linear interpolation for samples (first dimension)
            sample_indices = np.linspace(0, len(file_original_numpy) - 1, target_sample_count_level)
            sample_indices_floor = np.floor(sample_indices).astype(int)
            sample_indices_ceil = np.ceil(sample_indices).astype(int)
            sample_weights = sample_indices - sample_indices_floor

            # Interpolate samples
            samples_floor = file_original_numpy[sample_indices_floor]
            samples_ceil = file_original_numpy[sample_indices_ceil]
            interpolated_samples = samples_floor * (1 - sample_weights[:, np.newaxis]) + samples_ceil * sample_weights[:, np.newaxis]

            # Linear interpolation for values per sample (second dimension)
            value_indices = np.linspace(0, SubsamplingConfig.original_values_per_sample - 1, SubsamplingConfig.target_values_per_sample)
            value_indices_floor = np.floor(value_indices).astype(int)
            value_indices_ceil = np.ceil(value_indices).astype(int)
            value_weights = value_indices - value_indices_floor

            # Interpolate values
            values_floor = interpolated_samples[:, value_indices_floor]
            values_ceil = interpolated_samples[:, value_indices_ceil]
            file_target_numpy = values_floor * (1 - value_weights) + values_ceil * value_weights

            # Cast back to the original dtype
            file_target_numpy = file_target_numpy.astype(SubsamplingConfig.original_value_dtype)
        elif subsampling_mode == "NEAREST":
            file_target_numpy = file_original_numpy[
                : int(SubsamplingConfig.target_sample_count / (2**subsample_level)),
                : SubsamplingConfig.target_values_per_sample,
            ]
        else:
            raise ValueError(f"Unknown subsampling mode: {subsampling_mode}")

        print(f"Target data shape: {subsample_level} {file_target_numpy.shape} {file_target_numpy.dtype}")

        # Save the subsampled data to a new file - save them raw as binary data
        file_target_numpy.tofile(file_target_path)


if __name__ == "__main__":
    main()
