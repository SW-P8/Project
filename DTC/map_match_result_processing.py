import json
import pandas as pd
import sys

def process_results(path):
    with open(path) as matched_data:
        json_in = json.load(matched_data)

    df = pd.DataFrame.from_records(json_in, columns=["longitude", "latitude", "distance"])
    print(df['distance'].describe())


if __name__ == '__main__':
    
    if not len(sys.argv) == 0:
        path = sys.argv[1]
    else:
        path = "data/perpendicular_distance_100.json"
    
    process_results(path)