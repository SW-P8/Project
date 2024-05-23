from DTC.dtc_executor import DTCExecutor
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.trajectory import TrajectoryPointCloud, Trajectory
from DTC.construct_safe_area import SafeArea
from DTC.distance_calculator import DistanceCalculator
from onlinedtc.onlinerunner import RunCleaning
from math import ceil
from folium.features import CustomIcon

import pytest
import config
import pandas as pd
import folium


@pytest.fixture
def setup_point_clouds():
    exec = DTCExecutor(False)
    p1 = exec.create_point_cloud_with_n_points(2000000, city=True)
    model_set = extract_subset(exec.create_point_cloud_with_n_points(1000000, city=True))
    print(len(p1.trajectories))
    print(len(model_set.trajectories))
    half = len(p1.trajectories)//2
    train_trajectories = p1.trajectories[half:]
    train_set = TrajectoryPointCloud()
    for t in train_trajectories:
        train_set.add_trajectory(t)
    print(len(train_set.trajectories))
    return p1, model_set, train_set

@pytest.mark.skip
def test_discover_subset(setup_point_clouds):
    # Arrange
    point_cloud, model_data, train_data = setup_point_clouds
    gs = GridSystem(point_cloud)
    gs2 = GridSystem(model_data)
    ske = RouteSkeleton()

    gs.create_grid_system()
    gs2.create_grid_system()

    gs.extract_main_route()
    gs2.extract_main_route()

    gs.extract_route_skeleton()
    smr = ske.smooth_main_route(gs2.main_route)
    min_pts = ceil(len(gs2.main_route) * config.min_pts_from_mr)
    fmr = ske.graph_based_filter(smr, min_pts=min_pts)
    gs2.route_skeleton = ske.filter_sparse_points(fmr)

    gs.construct_safe_areas()
    gs2.construct_safe_areas()

    plot_safe_areas(gs.safe_areas, gs.initialization_point, "original")
    plot_safe_areas(gs2.safe_areas, gs2.initialization_point, "pre_increment")

    cleaner = RunCleaning(gs2.safe_areas, gs2.initialization_point)
    cleaner.read_trajectories(train_data)

    # Act
    cleaner.clean_and_increment()

    # Assert
    plot_safe_areas(cleaner.safe_areas, cleaner.initialization_point, "incremented")


def plot_safe_areas(safe_areas: dict, init_point: tuple[float, float], fig_name: str):
    data = convert_to_df(safe_areas, init_point)

    # Check if DataFrame is empty
    if data.empty:
        print("No safe areas to plot.")
        return

    # Create a map centered around the first point
    first_point = data.iloc[0]
    m = folium.Map(location=[first_point['latitude'],
                   first_point['longitude']], zoom_start=13)

    image = "orange_triangle.png"

    # Plot each safe area on the map as a marker
    for _, row in data.iterrows():
        icon = CustomIcon(icon_image=image,
                          icon_size=(20, 20),
                          icon_anchor=(10, 19))

        folium.Marker(
            location=[row['latitude'], row['longitude']],  # Correct order
            popup=f"Latitude: {row['latitude']}, Longitude: {row['longitude']}",
            icon=icon
        ).add_to(m)

    # Save the map to an HTML file
    m.save(fig_name + ".html")
    print(f"Map saved to {fig_name}.html")


def convert_to_df(safe_areas: dict[SafeArea], init_point):
    data = []
    for safe_area in safe_areas.values():
        (long, lat) = DistanceCalculator.convert_cell_to_point(init_point, safe_area.anchor)

        data.append({
            "longitude": long,
            "latitude": lat,
            "raidus": safe_area.radius
        })

    df = pd.DataFrame(data)
    return df


def extract_subset(point_cloud: TrajectoryPointCloud):
    pc = TrajectoryPointCloud()

    def is_inside(coordinate):
        min_lat, min_long = (39.8940652, 116.2648773)
        max_lat, max_long = (39.9238239, 116.3531113)
        long, lat = coordinate

        result = min_lat <= lat <= max_lat and min_long <= long <= max_long
        return result
    true_count = 0
    for trajectory in point_cloud.trajectories:
        t = Trajectory()
        for point in trajectory.points:
            coordinate = point.longitude, point.latitude
            if is_inside(coordinate) is False:
                t.add_point(point.longitude, point.latitude, point.timestamp)
            else:
                true_count += 1

        if len(t.points) != 0:
            pc.add_trajectory(t)
    sum = 0
    for x in point_cloud.trajectories:
        sum += len(x.points)
    sum2 = 0
    for x in pc.trajectories:
        sum2 += len(x.points)
    print(len(point_cloud.trajectories), " : ", sum)
    print(len(pc.trajectories), " : ", sum2)
    print("so many remove: ", true_count)
    return pc
