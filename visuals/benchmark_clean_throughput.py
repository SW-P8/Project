import matplotlib.pyplot as plt

# function to add value labels
def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i, y[i] + 50, round(y[i], 2), ha = 'center')

def addVerticalLines(min, max, stepsize):
    for i in range(min, max, stepsize):
        plt.axhline(i, linewidth=0.3, color="k", zorder=1)

steps = ["5%", "10%", "15%", "20%"]
time = [6171.15, 6257.98, 5824.31 , 6134.29]
addVerticalLines(1000, 7000 , 1000)
plt.bar(steps, time, width=0.4)
addlabels(steps, time)
plt.ylabel("Throughput (points per second)")
plt.xlabel("Noise frequency")
plt.savefig("visuals/BenchmarkCleaningThroughputPlot")