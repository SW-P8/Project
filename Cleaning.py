import copy
from math import floor
import DTC.json_read_write as json_read_write
import pickle

for i in range(0,40):
    a = 3 if i < 10 else 1 if i < 20 else 2 if i < 30 else 3
    print("pickle done")
    files = ["AllcitySA01", "AllcitySA02", "AllcitySA05", "AllcitySA10"]
    safe_areas = json_read_write.read_safe_areas_from_json(f"{files[a]}.json")
    initialization_point = (116.20287663548845, 39.75112986803514)
    avg = 0
    maximum = 0
    i = 0
    list_of_points = []
    for v in safe_areas.values():
        list_of_points.append(copy.copy(v.radius))
        maximum = max(maximum, v.radius)
        avg += v.radius
        #if v.radius > 20:
        #    v.radius = 20
        i += 1
    print((avg/i),  "avg", "max", maximum)
    list_of_points.sort()
    print("25% ", list_of_points[floor(((len(list_of_points)) * 0.25))])
    print("50% ", list_of_points[floor(((len(list_of_points)) * 0.50))])
    print("75% ", list_of_points[floor(((len(list_of_points)) * 0.75))])
    name = f"{files[a]}"
    print(name)

    with open("./pc.pickle", "rb") as fh:
        pointcloud = pickle.load(fh)#json_read_write.read_point_cloud_from_json("AllcityPC.json")
        fh.close()


    import random
    from DTC.noise_correction import NoiseCorrection
    point_cloud = pointcloud
    randomly_elected_trajectories = random.sample(point_cloud.trajectories, 1467)
    noise_corrector = NoiseCorrection(safe_areas, initialization_point, False)

    points_cleaned = 0
    total_points = 0
    for trajectory in randomly_elected_trajectories:
        if len(trajectory.points) == 0:
            continue
        labels_of_cleaned_points = noise_corrector.noise_detection(trajectory)
        total_points += len(trajectory.points) 
        points_cleaned += len(labels_of_cleaned_points)
    print("Points in randomly elected trajectories: ", total_points)
    print("Points cleaned: ", points_cleaned)

    # use 5% of 52489 - or 5 % of all the points in the collective pointcloud for all trajectories
    from math import ceil
    amount_to_shift = ceil(total_points * 0.05)
    print("Amount of points to shift: ", amount_to_shift)

    list_of_points_in_randomly_elected_trajectories = []
    for trajectory in randomly_elected_trajectories:
        list_of_points_in_randomly_elected_trajectories.extend(trajectory.points)

    points_to_shift = random.sample(list_of_points_in_randomly_elected_trajectories, amount_to_shift)
    print("Amount of points actually shifted: ", len(points_to_shift))

    from DTC.distance_calculator import DistanceCalculator
    for point in points_to_shift:
        point.set_coordinates(DistanceCalculator.shift_point_with_bearing(point, random.randint(1,200), random.randint(0,359)))
        point.noise = True

    labels_of_cleaned_points = []
    for trajectory in randomly_elected_trajectories:
        if len(trajectory.points) == 0:
            continue
        labels_of_locally_cleaned_points = noise_corrector.noise_detection(trajectory)
        labels_of_cleaned_points.extend(labels_of_locally_cleaned_points)

    amount_of_cleaned_points = 0
    amount_of_noisy_points_cleaned = 0
    for label in labels_of_cleaned_points:
        amount_of_cleaned_points += 1
        if label == True:
            amount_of_noisy_points_cleaned += 1

    cleaned = ("Amount of cleaned points: ", amount_of_cleaned_points)
    noisy_points_cleaned = ("Amount of noisy points cleaned: ", amount_of_noisy_points_cleaned)
    not_noisy_cleaned = ("Amount of not noisy points cleaned: ", amount_of_cleaned_points - amount_of_noisy_points_cleaned)
    noisy_not_cleaned = ("Amount of noisy points not cleaned: ", amount_to_shift - amount_of_noisy_points_cleaned)

    #Calculate accuracy, precision and recall

    def precision(tp, fp):
        return(tp/(tp+fp))

    def recall(tp, fn):
        return(tp/(tp+fn))

    def accuracy(tp, tn, fp, fn ):
        return((tn+tp)/(tp+tn+fn+fp))

    #TOTAL - TP - FP - FN
    precision_ = (f"Precision = {precision(amount_of_noisy_points_cleaned, (amount_of_cleaned_points - amount_of_noisy_points_cleaned))}")
    recall_ = (f"Recall = {recall(amount_of_noisy_points_cleaned, (amount_to_shift-amount_of_noisy_points_cleaned))}")
    accuracy_ = (f"""Accuracy = {accuracy(amount_of_noisy_points_cleaned, (total_points - amount_of_noisy_points_cleaned - (amount_of_cleaned_points - amount_of_noisy_points_cleaned)
          - (amount_to_shift-amount_of_noisy_points_cleaned)), (amount_of_cleaned_points - amount_of_noisy_points_cleaned), (amount_to_shift-amount_of_noisy_points_cleaned))}""")

    #Output metrics to file
    output = f"""
    SA type {name} \n
    total points {total_points} \n
    points to shift {amount_to_shift} \n
    points shifted {len(points_to_shift)} \n
    points cleaned {cleaned} \n
    not noisy points cleaned {not_noisy_cleaned} \n 
    noisy points cleaned {noisy_points_cleaned} \n
    noisy points not cleaned {noisy_not_cleaned} \n 
    Metrics: \n
    Precision {precision_} \n
    Recall {recall_} \n
    Accuracy {accuracy_} \n
    """

    with open("./Test_results.txt", "a") as fh:
        fh.write(output)
        fh.close()
