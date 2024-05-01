from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.plot import plot_matches
from DTC.distance_calculator import DistanceCalculator
import faulthandler
import pandas as pd
import json

def transform(point):
    return DistanceCalculator.convert_cell_to_point(
        (115.41989767769675, 39.43983985835822), point)


def run_mapmatch(n_points:int):
    with open("data/Full area/Alle punkter/AllRSK.json", "r") as rskinfile:
            json_data = json.load(rskinfile)
    data = [transform(eval(x)) for x in json_data]
    df = pd.DataFrame(data, columns=['longitude', 'latitude'])
    trace = Trace.from_dataframe(df.iloc[:1000])
    # generate a geofence polygon that surrounds the trace; units are in meters;
    # this is used to query OSM for a small map that we can match to
    geofence = Geofence.from_trace(trace, padding=1e3)

    # uses osmnx to pull a networkx map from the OSM database
    nx_map = NxMap.from_geofence(geofence)

    matcher = LCSSMatcher(nx_map)

    matches = matcher.match_trace(trace)

    result_df = matches.matches_to_dataframe()
    print(result_df.columns)

    plot_matches(matches.matches).show_in_browser()

if __name__ == '__main__':
    run_mapmatch(1000)
