import json
from DTC.construct_safe_area import SafeArea

def write_grid_to_json(file_name: str, grid: dict) -> None:
    with open(file_name, "w") as outfile: 
        json.dump({str(k): v for k, v in grid.items()}, outfile, indent=4)

def read_grid_from_json(file_name: str) -> dict:
    with open(file_name, 'r') as gridfile:
        grid_data = json.load(gridfile)

    grid = dict()
    for key, value in grid_data.items():
        key_tuple = eval(key)
        value_tuples = [tuple(sublist) for sublist in value]
        grid[key_tuple] = value_tuples

    return grid

def write_set_of_tuples_to_json(file_name: str, set_of_tuples: set[tuple[float, float]]) -> None:
    with open(file_name, "w") as outfile: 
        json.dump([str(v) for v in set_of_tuples], outfile, indent=4)

def read_set_of_tuples_from_json(file_name: str) -> set[tuple[float, float]]:
    with open(file_name, "r") as rskinfile:
        rsk_data = json.load(rskinfile)
    return {eval(v) for v in rsk_data}

def write_safe_areas_to_json(file_name: str, safe_areas: dict) -> None:
    with open(file_name, "w") as outfile: 
        json.dump({str(k): [v.radius, v.cardinality] for k, v in safe_areas.items()}, outfile, indent=4) 

def read_safe_areas_from_json(file_name: str) -> dict:
    with open(file_name, "r") as safe_areas_file:
        safe_areas_data = json.load(safe_areas_file)
    
    safe_areas = dict()
    for key, value in safe_areas_data.items():
        key_tuple = eval(key)
        safe_area_object = SafeArea.from_meta_data(key_tuple, value[0], value[1])
        safe_areas[key_tuple] = safe_area_object
        
    return safe_areas