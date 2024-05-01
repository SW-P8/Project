from DTC import dtc_executor, gridsystem, trajectory, noise_correction,distance_calculator
from DTC.construct_safe_area import SafeArea
from DTC.point import Point
from database.save_data import save_data
from database.db import init_db
from DTC.distance_calculator import DistanceCalculator

class CleanTraj:
    # TODO:
    # Tests should include - create a grid system based on a subset of the data-set t-drive
    # Take a trajectory from t drive non-cleaned and use as input here
    # Mock data to test each method individually, 
    # Merge update_safe_areas into what claes and arthur is doing

    def __init__(self, gridsystem : gridsystem.GridSystem) -> None:
        """
        Initializes the CleanTraj object with a specific grid system.

        Parameters:
        - gridsystem (gridsystem.GridSystem): An instance of GridSystem that defines the grid layout, safe areas, and
          other relevant parameters for trajectory cleaning.

        Attributes:
        - safe_areas (list): A list of safe areas derived from the grid system used to determine noise in trajectories.
        - noisy_points (set): A set to accumulate points identified as noisy during the trajectory cleaning process.
        """
        self.gridsystem = gridsystem
        self.safe_areas = self.gridsystem.safe_areas
    
    noisy_points = set()

    def clean(self, points: list):
        """
        Processes a list of trajectory points to identify and correct noise, refining the trajectory.

        This method executes several steps to refine given trajectory points by detecting noise, adjusting points based
        on the grid system initialization point, and applying corrections based on defined safe areas. It separates
        points into noisy and clear categories, then updates the trajectory accordingly.

        Parameters:
        - points (list[Point]): A list of trajectory points, where each point is an instance of the Point class, 
          containing GPS coordinates.

        Steps:
        1. Initializes a Trajectory object and sets its points.
        2. Uses a DistanceCalculator to refine the position of each point relative to the grid system's initial point.
        3. Applies a NoiseCorrection process to detect noisy points within the trajectory.
        4. Updates noisy points based on their proximity to safe areas defined within the grid system.
        5. Optionally records the noisy points in a specific set for further handling or analysis (see additional 
           methods for handling noisy points).

        Returns:
        None. This method modifies the trajectory's points in place and handles the classification of points internally.

        Side effects:
        - Modifies the internal state of the trajectory by updating its points attribute.
        - Adjusts the set of noisy points within the class based on proximity to safe areas.
        """
        traj = trajectory.Trajectory()
        traj.points = points
        distance_calc = distance_calculator.DistanceCalculator()
        for point in points:
            point = distance_calc.calculate_exact_index_for_point(point, self.gridsystem.initialization_point)
        noise_corrector = noise_correction.NoiseCorrection(self.gridsystem)
        try:
            noise_corrector.noise_detection(traj)
        except KeyError as e:
            print(f"Key error detected: {e}")
            return  # or continue based on your application's needs

        self.update_safe_areas() 


    # This is slow as FUUUUUUUUCK
    def incremental_refine(self, safe_area : SafeArea,point: Point, initialization_point):
        """
        Incrementally refines the classification of a point as noisy or clear by comparing its distance to the nearest 
        safe area neighbor against the safe area's radius.

        Parameters:
        - safe_area (SafeArea): The safe area to compare against.
        - point (Point): The point being evaluated.
        - initialization_point (Point): A reference point used for distance calculations.

        Side effects:
        - Updates the confidence level in a safe area based on the minimum distance.
        - Potentially adds the point to the noisy_points set if it is determined to be outside the safe area's radius.
        """

        (anchor, min_dist) = DistanceCalculator.find_nearest_neighbor_from_candidates(point, safe_area.center, initialization_point) 
        safe_area.update_confidence(min_dist, point)
        if ((min_dist > (safe_area.radius))):
            self.noisy_points.add(point)
    

    # this might not be smart
    def update_safe_areas(self):
        for k,v in self.gridsystem.safe_areas.items():
            if v.PointsInSafeArea is not None:
                for point in v.PointsInSafeArea:
                    self.incremental_refine(v, {point}, self.gridsystem.initialization_point)


    # noise set save in DB?
    # load when supposed to be used?
    def add_noisy_points_to_noise_set(self, noisy_points):
        conn = init_db()
        save_data(self.gridsystem, conn, noisy_point=True, points=noisy_points)

        # could ret



    

