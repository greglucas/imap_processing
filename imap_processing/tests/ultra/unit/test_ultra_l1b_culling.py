"""Tests Culling for ULTRA L1b."""

import numpy as np
import pytest

from imap_processing.quality_flags import ImapHkUltraFlags
from imap_processing.ultra.constants import UltraConstants
from imap_processing.ultra.l1b.ultra_l1b_culling import (
    flag_spin,
    get_energy_histogram,
    get_spin,
)


@pytest.fixture()
def test_data(use_fake_spin_data_for_time):
    """Fixture to compute and return test data."""
    time = np.arange(0, 32, 2)
    spin_number = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2])
    energy = np.array([5, 5, 5, 5, 5, 5, 5, 5, 5, 15, 15, 25, -2, -2, -2, 2])

    use_fake_spin_data_for_time(time[0], time[-1])

    energy_edges = UltraConstants.CULLING_ENERGY_BIN_EDGES
    unique_spins = np.unique(spin_number)
    expected_counts = np.zeros((len(energy_edges) - 1, len(unique_spins)))

    for spin_idx, spin in enumerate(unique_spins):
        for energy_idx in range(len(energy_edges) - 1):
            count = np.sum(
                (spin_number == spin)
                & (energy >= energy_edges[energy_idx])
                & (energy < energy_edges[energy_idx + 1])
            )
            expected_counts[energy_idx, spin_idx] = count

    return time, spin_number, energy, expected_counts


def test_get_spin(use_fake_spin_data_for_time, l1b_de_dataset):
    """Tests get_spin function."""
    use_fake_spin_data_for_time(
        l1b_de_dataset["event_times"][0], l1b_de_dataset["event_times"][-1]
    )
    spin_number = get_spin(l1b_de_dataset["event_times"])

    assert len(spin_number) == len(l1b_de_dataset["event_times"])
    expected_num_spins = np.ceil(
        (
            l1b_de_dataset["event_times"].values[-1]
            - l1b_de_dataset["event_times"].values[0]
        )
        / 15
    )
    assert np.array_equal(len(np.unique(spin_number)), expected_num_spins)


def test_get_energy_histogram(test_data):
    """Tests get_energy_histogram function."""

    _, spin_number, energy, expected_counts = test_data

    hist, _ = get_energy_histogram(spin_number, energy)

    assert np.all(hist == expected_counts / 15)


def test_flag_spin(test_data):
    """Tests flag_spin function."""

    time, _, energy, expected_counts = test_data
    quality_flags, spin, energy = flag_spin(time, energy)

    flag = ImapHkUltraFlags(quality_flags[1])
    assert flag.name == "HIGHCOUNTS"

    flagged_indices = np.unique(spin)[expected_counts[0, :] / 15 > 0]
    unflagged_indices = np.setdiff1d(np.unique(spin), flagged_indices)
    assert np.all(quality_flags[flagged_indices] == ImapHkUltraFlags.HIGHCOUNTS.value)
    assert np.all(quality_flags[unflagged_indices] == ImapHkUltraFlags.NONE.value)

    # Only HIGHCOUNT bits were set
    assert np.all(quality_flags == quality_flags & ImapHkUltraFlags.HIGHCOUNTS)
