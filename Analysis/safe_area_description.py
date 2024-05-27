import json
import pandas as pd
import os

def process_results(dir_path):
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    combined_dict = {}

    for file in files:
        with open(dir_path + "/" + file, "r") as matched_data:
            json_in = json.load(matched_data)        
        df = pd.DataFrame.from_records(list(json_in.values()), columns=["radius", "cardinality", "timestamp"])

        # Calculate descriptive statistics for the distance column
        distance_stats = df["radius"].describe().to_dict()

        # Add the statistics to combined_dict with the key based on the file name
        combined_dict[file] = distance_stats

    with open("Outputs/SafeAreas/Details/details.json", "w") as outfile:
        json.dump(combined_dict, outfile, indent=4)

    sorted_files = sorted(combined_dict.keys(), key=lambda x: combined_dict[x]["50%"])
    sorted_files_with_count = [(file, combined_dict[file]["50%"],combined_dict[file]["count"]) for file in sorted_files]
    with open("Outputs/SafeAreas/Details/sortedDetails.json", "w") as keysoutfile:
        json.dump(sorted_files_with_count, keysoutfile, indent=4)


if __name__ == '__main__':
    dir_path = "Outputs/SafeAreas"
    process_results(dir_path)