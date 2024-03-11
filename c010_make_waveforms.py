"""
Make waveform plots.
"""
import numpy as np
import obspy
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

import local

# --------------------------- Global stuff --------------------------- #
PAZ_WA = {
    "sensitivity": 2080,
    "zeros": [0 + 0j],
    "gain": 1.0,
    "poles": [-6.283 + 4.7124j, -6.283 - 4.7124j],
}


def simulate_wood_anderson(st, inv):
    """
    Remove instrument response and simulate a Wood-Anderson seismometer

    Parameters
    ----------
    st : obspy Stream or obspy Trace (required)
        Stream or Trace on which to apply the simulation
    inv : obspy Inventory
        The station inventory to use for removal.

    Returns
    -------
    st : obspy Stream or obspy Trace
        The stream/trace with the simulated data.
    """
    st = st.copy()
    st.remove_response(inventory=inv)
    st.simulate(paz_remove=None, paz_simulate=PAZ_WA)
    return st


def get_bb_stream(st):
    """Get only broadband stations. """
    is_bb = {
        tr.stats.channel for tr in st
        if tr.stats.channel.startswith('BH') or tr.stats.channel.startswith('HH')
    }
    out = obspy.Stream([tr for tr in st if tr.stats.channel in is_bb])
    return out


def center(ax, tr):
    """Center the axis on trace data."""
    dist = tr.data.max() - tr.data.min()
    buf = dist * 0.04
    maxval = np.abs(tr.data).max()
    ax.set_ylim(-maxval - buf, maxval + buf)


def annotate_channel(ax, tr, wa=False):
    """Annotate the channel in axes."""
    text = tr.stats.station + "." + tr.stats.channel
    plt.text(.01, .95, text, ha='left', va='top', transform=ax.transAxes)


def make_plot(st, wa_st):
    """Make plots of waveforms for manual processing."""
    fig, axes = plt.subplots(6, 1, figsize=(8, 10.5), sharex=True)
    wa_axes = axes[:3]
    norm_axes = axes[3:]
    space = " " * 16
    name = st[0].stats.station
    title = f"S-P time:{space} ML:{space}\n\nP pick:{space} S pick:{space} Amp 1: {space} Amp2: {space}"

    wa_axes[0].set_title(title)

    for tr, ax in zip(st, norm_axes):
        duration = tr.stats.endtime - tr.stats.starttime
        x_vals = np.linspace(0, duration, len(tr.data))
        ax.plot(x_vals, tr.data, color="tab:blue")
        ax.set_yticks([])
        annotate_channel(ax, tr)
        center(ax, tr)

    for tr, ax in zip(wa_st, wa_axes):
        duration = tr.stats.endtime - tr.stats.starttime
        x_vals = np.linspace(0, duration, len(tr.data))
        ax.plot(x_vals, tr.data, color="tab:orange")
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        annotate_channel(ax, tr)
        center(ax, tr)
    ax = axes[-1]
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.set_xlim(0, duration)
    ax.set_xlabel("Time (s)")
    wa_axes[1].set_ylabel("Amplitude (mm)")

    return fig


if __name__ == "__main__":
    st = get_bb_stream(obspy.read(local.waveform_path))
    inv = obspy.read_inventory(local.station_path)

    stations = sorted({tr.stats.station for tr in st})
    for station in stations:
        sub = st.select(station=station)
        # set origin time relative to arbitrary point
        for tr in sub:
            tr.stats.starttime = obspy.UTCDateTime("2020-01-01T00:00:00")

        wa = simulate_wood_anderson(sub, inv)
        fig = make_plot(sub, wa)
        path = local.waveform_dir_path / f"{sub[0].stats.station}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=350)
