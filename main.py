""" Program entrypoint """
import sys
from DTC.dtc_executor import DTCExecutor

INIT_DB = False
for arg in sys.argv:
    if arg == "--fresh-db":
        INIT_DB = True

dtc_executor = DTCExecutor(INIT_DB)
dtc_executor.execute_dtc_with_n_points(20000)

#TODO: Add visualizer here
