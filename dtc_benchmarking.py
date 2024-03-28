from DTC import dtc_executor

executor = dtc_executor.DTCExecutor(False)

print("DTC model creation with a million points:")
executor.execute_dtc_with_n_points(1000000)
