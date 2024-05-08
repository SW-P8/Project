from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.plot import plot_matches
from DTC.distance_calculator import DistanceCalculator
from database.db import new_tdrive_db_pool
from database.taxi_data_handler import TaxiDataHandler

import multiprocessing as mp
import pandas as pd
import json
import gpxpy
import gpxpy.gpx

bb = Trace.from_dataframe(pd.DataFrame([
    (116.342222, 39.866389),
    (116.342222, 39.983056),
    (116.436389, 39.866389),
    (116.436389, 39.983056)
], columns=['longitude', 'latitude']))

def create_gpx_file(coords):
    gpx = gpxpy.gpx.GPX()

    for coord in coords:
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(coord[0], coord[1]))
        gpx_track.segments.append(gpx_segment)
        gpx.tracks.append(gpx_track)

    return gpx.to_xml()

def transform(point):
    return DistanceCalculator.convert_cell_to_point(
        (116.20287663548845, 39.75112986803514), point)

def run_mapmatch(n_points:int):
    print("Preparing data...")
    print('    Loading rsk data')
    with open("data/City area/All/AllcityRSK.json", "r") as rskinfile:
            json_data = json.load(rskinfile)
    data = [transform(eval(x)) for x in json_data]
    df = pd.DataFrame(data, columns=['longitude', 'latitude'])

    print('    Loading trajectories')
    connection = new_tdrive_db_pool()
    db_handler = TaxiDataHandler(connection)
    records = db_handler.read_records_inside_bbb(20000)
    
    print('    Creating dataframes')
    df1 = pd.DataFrame(
        [(longitude, latitude) for _, _, longitude, latitude, _ in records],
        columns=['longitude', 'latitude']
    )
    trace = Trace.from_dataframe(df1)

    # generate a geofence polygon that surrounds the trace; units are in meters;
    # this is used to query OSM for a small map that we can match to
    print("Creating Geofence...")
    geofence = Geofence.from_trace(bb, padding=1e3)

    # uses osmnx to pull a networkx map from the OSM database
    nx_map = NxMap.from_geofence(geofence)
    
    matcher = LCSSMatcher(nx_map)
    
    print("Matching...")
    matches = matcher.match_trace(trace)

    print("Creating result dataframe...")
    result_df = matches.matches_to_dataframe()
    print(result_df.head())
    mean = result_df['distance_to_road'].mean()
    print(mean)
    plot_matches(matches.matches).show_in_browser()

if __name__ == '__main__':
    run_mapmatch(1000)
