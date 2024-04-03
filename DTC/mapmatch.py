from mappymatch import package_root
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
from mappymatch.utils.plot import plot_matches
from DTC.dtc_executor import DTCExecutor
import pandas as pd

def run_mapmatch():
    dtc_executor = DTCExecutor()
    pc = dtc_executor.create_point_cloud_with_n_points(25000)
    df = pd.DataFrame(columns=['longitude', 'latitude'])
    i = 0
    for trajectory in pc.trajectories:
        for point in trajectory.points:
            df.loc[i, 'longitude'] = point.longitude
            df.loc[i, 'latitude'] = point.latitude
            i += 1
    trace = Trace.from_dataframe(df, lon_column='longitude', lat_column='latitude')

    # generate a geofence polygon that surrounds the trace; units are in meters;
    # this is used to query OSM for a small map that we can match to
    geofence = Geofence.from_trace(trace, padding=1e3)

    # uses osmnx to pull a networkx map from the OSM database
    nx_map = NxMap.from_geofence(geofence)

    matcher = LCSSMatcher(nx_map)

    matches = matcher.match_trace(trace)

    plot_matches(matches.matches).show_in_browser()
