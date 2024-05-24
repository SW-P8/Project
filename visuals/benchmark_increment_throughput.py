import matplotlib.pyplot as plt

# function to add value labels
def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i, y[i] + 200, round(y[i], 2), ha = 'center')

def addVerticalLines(min, max, stepsize):
    for i in range(min, max, stepsize):
        plt.axhline(i, linewidth=0.3, color="k", zorder=1)

steps = ["100", "1000", "10000"]
time = [13235.29, 27380.26, 43795.62]
addVerticalLines(5000, 45000 , 5000)
plt.bar(steps, time, width=0.4)
addlabels(steps, time)
plt.ylabel("Throughput (points per second)")
plt.xlabel("Amount of points in each $SA_{i_{PC}}$")
plt.savefig("visuals/BenchmarkIncrementThroughputPlot")