import matplotlib.pyplot as plt

# function to add value labels
def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i, y[i] + 1, round(y[i], 2), ha = 'center')

def addVerticalLines(min, max, stepsize):
    for i in range(min, max, stepsize):
        plt.axhline(i, linewidth=0.3, color="k", zorder=1)

steps = ["5%", "10%", "15%", "20%"]
time = [213, 112.1885, 64.7481, 86.8979]
addVerticalLines(20, 140, 20)
plt.bar(steps, time, width=0.4)
addlabels(steps, time)
plt.ylabel("Throughput (points per second)")
plt.savefig("BenchmarkCleaningThroughputPlot")