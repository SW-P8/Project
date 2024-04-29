from DTC import dtc_executor, gridsystem, trajectory, noise_correction,distance_calculator
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
        self.gridsystem = gridsystem


    def clean(self, points: list):
        """
        Processes a list of points to identify and corrects noise, refining the trajectory.

        This method takes a list of points representing a trajectory, calculates their exact indices in relation to a
        defined grid system's initialization point, and applies noise correction techniques. The goal is to distinguish
        between noisy points and clear points, updating the trajectory accordingly.

        Parameters:
        - points (list): A list of points (e.g., GPS coordinates or spatial data points) that make up a trajectory.

        Steps:
        1. Initializes a Trajectory object and sets its points.
        2. Uses a DistanceCalculator to refine the position of each point relative to the grid system's initial point.
        3. Applies a NoiseCorrection process to detect noisy points within the trajectory.
        4. Separates the points into noisy and clear categories.
        5. Updates the noisy points based on their proximity to safe areas defined within the grid system.
        6. Records the noisy points in a specific set for further handling or analysis.

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
        points_sorted = noise_corrector.noise_detection(traj)
        
        noisy_points = [x for xs, _ in points_sorted for x in xs]
        clear_points = [y for _, ys in points_sorted for y in ys]

        noisy_points = self.update_safe_areas(noisy_points, self.gridsystem) 
        self.add_noisy_points_to_noise_set(noisy_points) # - noisy_points should hold coordinates of closest safe_area 


    # this might not be smart
    def update_safe_areas(self, traj, safe_areas):
        pass
        #noise = call_lasses_insert_function(traj, safe_areas) #- this should maybe return points outside SA before cleaning them 
        #recalculate_safe_aread(noise, safe_areas) # magic function arthur cook


    # noise set save in DB?
    # load when supposed to be used?
    def add_noisy_points_to_noise_set(self, noisy_points):
        conn = init_db()
        save_data(self.gridsystem, conn, noisy_point=True, points=noisy_points)

        # could ret



    

