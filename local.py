"""
Local variables for this project.
"""
from pathlib import Path
from collections import Counter

import pandas as pd
import obspy

here = Path(__file__).parent
output_path = here / 'output'
output_path.mkdir(exist_ok=True)

waveform_path = output_path / 'waveforms.mseed'
station_path = output_path / 'stations.xml'

map_path = output_path / "b010_map.png"

waveform_dir_path = output_path / 'waveforms_plots'

origin_time = obspy.UTCDateTime(2020, 3, 18, 13, 9, 31)

time_1 = origin_time + 5
time_2 = time_1 + 60 * 3

stations = ('UU.LIUT', "US.DUG", "UU.RDMU", "US.AHID", "US.ELK", "US.HLID")

latitude = 40.851
longitude = -112.081


def load_seismic_data(path=output_path, require_3c=True):
    """
    Load the waveform and station data in a directory.

    The directory must have sub-folders name "waveforms" and "stations".

    Parameters
    ----------
    path
        The directory path which contains the data.
    """
    path = Path(path)
    # Ensure expected paths exist.
    wave_folder_path = path / "waveforms"
    sta_folder_path = path / "stations"
    assert wave_folder_path.is_dir(), f"{wave_folder_path} does not exist"
    assert sta_folder_path.is_dir(), f"{sta_folder_path} does not exist"
    # Load waveforms into stream.
    st = obspy.Stream()
    for wpath in wave_folder_path.glob("*.mseed"):
        st += obspy.read(wpath)
    # Filter out traces that don't have at least 3 coponents
    if require_3c:
        counter = Counter()
        counter.update([tr.stats.station for tr in st])
        has_3c = {x for x, i in counter.items() if i == 3}
        st = obspy.Stream([tr for tr in st if tr.stats.station in has_3c])
    # Load station info into inventory.
    inv = obspy.Inventory()
    for sta_path in sta_folder_path.glob("*.xml"):
        inv += obspy.read_inventory(sta_path)

    return st, inv


def inventory_to_df(inv):
    """
    Extract station names and locations to a dataframe.

    Parameters
    ----------
    inv
        The obspy Inventory object.
    """
    data = []
    for network in inv.networks:
        for station in network.stations:
            sta_info = {
                "network": network.code,
                "station": station.code,
                "latitude": station.latitude,
                "longitude": station.longitude,
                "elevation": station.elevation,
            }
            data.append(sta_info)
    return pd.DataFrame(data)


