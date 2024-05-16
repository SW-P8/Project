import os
import json

import multiprocessing as mp
from osmnx.graph import graph_from_bbox
from osmnx.io import save_graphml, load_graphml
from osmnx.distance import nearest_edges
from osmnx.projection import project_graph, project_geometry
from DTC.distance_calculator import DistanceCalculator
from DTC.collection_utils import CollectionUtils
from shapely.geometry import Point
from progress.bar import Bar

class mapmatcher:
    def transform(self, point):
        return DistanceCalculator.convert_cell_to_point(
            (116.20287663548845, 39.75112986803514), point)

    def project_points_to_graph(self, projected_graph, points):
        projected_points = []
        bar = Bar('Projecting points', max=len(points), suffix=' %(index)d/%(max)d - %(percent).1f%% - avg %(avg).1fs - elapsed %(elapsed)ds - ETA %(eta)ds')
        for point in points:
            projected_point, _ = project_geometry(Point(point), to_crs=projected_graph.graph['crs'])
            projected_points.append((point, (projected_point.x, projected_point.y)))
            bar.next()
        bar.finish()
        
        return projected_points

    def mapmatch(self):
        graph = load_graphml(filepath='data/InnerBBB.graphml')
        
        print('Loading rsk data')
        with open("Outputs/RouteSkeletons/AllcityRSK252020.json", "r") as rskinfile:
            json_data = json.load(rskinfile)
        data = [self.transform(eval(x)) for x in json_data]
        projected_graph = project_graph(graph)
        
        projected_data = self.project_points_to_graph(projected_graph, data)
        process_count = mp.cpu_count()
        splits = CollectionUtils.split(projected_data, process_count)
        tasks = []
        pipe_list = []
                
        for split in splits:
            if split != []:
                recv_end, send_end = mp.Pipe(False)
                t = mp.Process(target=self.find_nearest_edge, args=(projected_graph, split, send_end))
                tasks.append(t)
                pipe_list.append(recv_end)
                t.start()

        perp_dist = []
        for (i, task) in enumerate(tasks):
            dists = pipe_list[i].recv()
            task.join()
            for dist in dists:
                perp_dist.append(dist)
        
        with open("Outputs/PerpendicularDistances/DistanceTest.json", "w") as pdout:
            pdout.write(json.dumps(perp_dist))

    def find_nearest_edge(self, graph, data, send_end):        
        coords = [(long, lat) for (long, lat), _ in data]
        xs = [x for _, (x, _) in data]
        ys = [y for _, (_, y) in data]
        _, distances = nearest_edges(graph, xs, ys, return_dist=True)
        perp_distances = [(coord[0], coord[1], dist) for coord,dist in zip(coords, distances)]
        send_end.send(perp_distances)

    def save_model_locally(self):
        north = 40.0245
        south = 39.7513
        east = 116.5334
        west = 116.2031
        
        graph = graph_from_bbox(bbox=(north, south, east, west), network_type='drive', simplify=False)
        save_graphml(graph, filepath='data/InnerBBB.graphml')
        print("Saved Inner City BBB Graph")

if __name__ == '__main__':
    mm = mapmatcher()
    
    if (not os.path.exists('data/InnerBBB.graphml')):
        print('Local model not found')
        mm.save_model_locally()
    
    mm.mapmatch()
