from DTC import trajectory, noise_correction, distance_calculator
from DTC.trajectory import Trajectory
from DTC.construct_safe_area import SafeArea
from DTC.route_skeleton import RouteSkeleton
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator


class CleanTraj:

    def __init__(self, safe_areas: set[SafeArea], route_skeleton: RouteSkeleton, init_point: tuple[float, float]) -> None:
        """
        Initializes the CleanTraj object with a specific grid system.

        Parameters:
        - gridsystem (gridsystem.GridSystem): An instance of GridSystem that defines the grid layout, safe areas, and
          other relevant parameters for trajectory cleaning.

        Attributes:
        - safe_areas (list): A list of safe areas derived from the grid system used to determine noise in trajectories.
        - noisy_points (set): A set to accumulate points identified as noisy during the trajectory cleaning process.
        """
        self.route_skeleton = route_skeleton
        self.initialization_point = init_point
        self.safe_areas = safe_areas

    def clean(self, input_trajectory: Trajectory):
        """
        Processes a list of trajectory points to identify and correct noise, refining the trajectory.

        This method executes several steps to refine given trajectory points by detecting noise, adjusting points based
        on the grid system initialization point, and applying corrections based on defined safe areas. It separates
        points into noisy and clear categories, then updates the trajectory accordingly.

        Parameters:
        - input_trajectory (Trajectory): A trajectory of points, where each point is an instance of the Point class, 
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
        if len(input_trajectory.points) is 0:
            pass
        else:
            noise_corrector = noise_correction.NoiseCorrection(
                self.safe_areas, self.route_skeleton, self.initialization_point)
            noise_corrector.noise_detection(input_trajectory)
