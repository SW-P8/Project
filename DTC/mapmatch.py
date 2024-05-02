from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.plot import plot_matches
from DTC.distance_calculator import DistanceCalculator
import multiprocessing as mp
import pandas as pd
import json

def transform(point):
    return DistanceCalculator.convert_cell_to_point(
        (116.20287663548845, 39.75112986803514), point)

def run_mapmatch(n_points:int):
    with open("data/City area/All/AllcityRSK.json", "r") as rskinfile:
            json_data = json.load(rskinfile)
    data = [transform(eval(x)) for x in json_data]
    df = pd.DataFrame(data, columns=['longitude', 'latitude'])
    
    num_processes = mp.cpu_count()
    chunk_size = len(df) // num_processes
    df_chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    
    traces = [Trace.from_dataframe(chunk) for chunk in df_chunks]

    # generate a geofence polygon that surrounds the trace; units are in meters;
    # this is used to query OSM for a small map that we can match to
    print("Creating Geofence...")
    geofence = Geofence.from_trace(traces[0], padding=1e3)

    # uses osmnx to pull a networkx map from the OSM database
    nx_map = NxMap.from_geofence(geofence)

    matcher = LCSSMatcher(nx_map)
    
    print("Matching...")
    matches = matcher.match_trace_batch(traces, num_processes)

    print("Creating result dataframe...")
    dfs = [trace.to_dataframe() for trace in traces]
    result_df = pd.concat(dfs, ignore_index=True)
    print(result_df.head())

    #plot_matches(matches.matches).show_in_browser()

if __name__ == '__main__':
    run_mapmatch(1000)
