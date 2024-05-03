import matplotlib.pyplot as plt

sample_sizes = [0.100000, 1.000000, 2.000000, 5.000000, 11.588461,16.138190]
sac = [0.3921, 4.2837, 8.4724, 24.3849, 62.4398, 86.8979]
sac_relaxed = [0.4425, 3.9245, 7.8600, 19.7705, 46.4750 , 64.7481]
plt.plot(sample_sizes, sac, "o-g")
plt.plot(sample_sizes, sac_relaxed, "v--m")
plt.xlabel("Points in grid (millions)")
plt.ylabel("Time cost (seconds)")
plt.grid(True)
plt.legend(["SAC", "$SAC_{relaxed}$"])
plt.ylim(0)
plt.xlim(0)
plt.savefig("SafeAreaScaling")