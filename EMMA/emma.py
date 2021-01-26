import tatapov

with open("EMMA_overhangs.txt", "r") as f:
    overhangs = f.read().splitlines()

# Potapov et al. 2018:
for temperature in ["25C", "37C"]:
    for time in ["01h", "18h"]:
        filename = "emma_crosstalk_" + temperature + "_" + time + "_BsaI_Potapov.png"
        data = tatapov.annealing_data[temperature][time]
        subset = tatapov.data_subset(data, overhangs, add_reverse=True)
        # Plot the data subset
        ax, _ = tatapov.plot_data(subset, figwidth=15, plot_color="Blues")
        ax.figure.tight_layout()
        ax.figure.savefig(filename)

# Pryor et al. 2020:
for enzyme in ["2020_01h_BsaI", "2020_01h_BsmBI", "2020_01h_Esp3I", "2020_01h_BbsI"]:
    filename = "emma_crosstalk_37C_" + enzyme + "_Pryor.png"
    data = tatapov.annealing_data["37C"][enzyme]  # all 37 C and 01h
    subset = tatapov.data_subset(data, overhangs, add_reverse=True)
    # Plot the data subset
    ax, _ = tatapov.plot_data(subset, figwidth=15, plot_color="Blues")
    ax.figure.tight_layout()
    ax.figure.savefig(filename)
