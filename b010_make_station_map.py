"""
A script for making the station map.
"""
import matplotlib.pyplot as plt
import obspy
import pygmt
from obspy.geodetics import gps2dist_azimuth

import local


def add_distance(df):
    """Add distance from event to each station."""
    lat, lon = local.latitude, local.longitude
    out = []
    for _, ser in df.iterrows():
        dist = gps2dist_azimuth(
            lat1=ser.latitude, lon1=ser.longitude,
            lat2=lat, lon2=lon,
        )[0]
        out.append(dist / 1_000)
    df['distance'] = out
    return df


if __name__ == "__main__":
    inv = obspy.read_inventory(local.station_path)
    df = local.inventory_to_df(inv).pipe(add_distance)

    font = "15p,Helvetica-Bold"

    region = (
        df['longitude'].min() - 1,
        df['longitude'].max() + 1,
        df['latitude'].min() - 1,
        df['latitude'].max() + 1,
    )

    fig = pygmt.Figure()
    fig.basemap(region=region, projection="M15c", frame=True)
    fig.coast(borders=["2/0.5p,black"], land="white", water="skyblue")
    with pygmt.config(MAP_SCALE_HEIGHT="10p"):
        fig.basemap(map_scale="n0.2/0.06+c+w200k+f+l")

    fig.plot(x=df['longitude'], y=df['latitude'], style="t0.5c", fill="white", pen="black")
    fig.text(x=df['longitude'], y=df['latitude'] - 0.14, text=df['station'], font=font)
    # fig.plot(x=local.longitude, y=local.latitude, style="c0.6c", fill="blue", pen="blue")
    plt.tight_layout()
    fig.savefig(local.map_path, dpi=350)
