import os
import json
import pandas as pd
import geopandas as gpd
import geodatasets
import multiprocessing as mp
from osmnx.graph import graph_from_bbox
from osmnx.io import save_graphml, load_graphml
from osmnx.distance import nearest_edges
from DTC.distance_calculator import DistanceCalculator
from DTC.collection_utils import CollectionUtils
from progress.bar import Bar

class mapmatcher:
    def transform(self, point):
        return DistanceCalculator.convert_cell_to_point(
            (116.20287663548845, 39.75112986803514), point)

    def mapmatch(self):
        graph = load_graphml(filepath='data/InnerBBB.graphml')
        print('Epic win')
        
        print('Loading rsk data')
        with open("data/City area/All/AllcityRSK.json", "r") as rskinfile:
            json_data = json.load(rskinfile)
        data = [self.transform(eval(x)) for x in json_data]
        
        process_count = mp.cpu_count()
        splits = CollectionUtils.split(data, process_count)
        tasks = []
        pipe_list = []

        for split in splits:
            if split != []:
                recv_end, send_end = mp.Pipe(False)
                t = mp.Process(target=self.find_nearest_edge, args=(graph, split, send_end))
                tasks.append(t)
                pipe_list.append(recv_end)
                t.start()

        perp_dist = []
        for (i, task) in enumerate(tasks):
            d = pipe_list[i].recv()
            task.join()
            perp_dist.append(d)

        with open("data/perpendicular_distance.json", "w") as pdout:
            json.dump(perp_dist, pdout)    

        for x in perp_dist:
            print(x)
            
        #df = pd.DataFrame(data, columns=['longitude', 'latitude'])
        print('BData loaded and spungit')

    def find_nearest_edge(self, graph, data, send_end):
        perp_dist = list()
                
        for long, lat in data:
            dist = nearest_edges(graph, long, lat, return_dist=True)
            perp_dist.append((long, lat, dist))
        
        send_end.send(perp_dist)

    def save_model_locally(self):
        north = 40.0245
        south = 39.7513
        east = 116.5334
        west = 116.2031
        
        graph = graph_from_bbox(bbox=(north, south, east, west), network_type='drive')
        save_graphml(graph, filepath='data/InnerBBB.graphml')
        print("Saved Inner City BBB Graph")

if __name__ == '__main__':
    mm = mapmatcher()
    
    if (not os.path.exists('data/InnerBBB.graphml')):
        print('Epic fail')
        mm.save_model_locally()
    
    mm.mapmatch()
