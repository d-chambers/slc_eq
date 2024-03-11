"""
Download data used in the excercise.
"""
import obspy
from obspy.clients.fdsn import Client

import local

if __name__ == "__main__":
    client = Client()
    st = obspy.Stream()
    requests = []
    for network_station in local.stations:
        network, station = network_station.split(".")
        requests.append(
            (network, station, "*", "*", local.time_1, local.time_2)
        )
    st = client.get_waveforms_bulk(requests)
    st.write(local.waveform_path, "mseed")
    inv = client.get_stations_bulk(requests, level="response")
    inv.write(local.station_path, "stationxml")
