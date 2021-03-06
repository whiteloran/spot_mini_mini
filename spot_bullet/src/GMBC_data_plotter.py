#!/usr/bin/env python

import numpy as np
import sys
import os
import argparse
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import norm
sns.set()

# ARGUMENTS
descr = "Spot Mini Mini ARS Agent Evaluator."
parser = argparse.ArgumentParser(description=descr)
parser.add_argument("-nep",
                    "--NumberOfEpisodes",
                    help="Number of Episodes to Plot Data For")
parser.add_argument("-maw",
                    "--MovingAverageWindow",
                    help="Moving Average Window for Plotting (Default: 150)")
parser.add_argument("-tr",
                    "--TrainingData",
                    help="Plot Training Curve instead of Survival Curve",
                    action='store_true')
parser.add_argument("-tot",
                    "--TotalReward",
                    help="Show Total Reward instead of Reward Per Timestep",
                    action='store_true')
parser.add_argument("-ar",
                    "--RandAgentNum",
                    help="Randomized Agent Number To Load")
parser.add_argument("-anor",
                    "--NoRandAgentNum",
                    help="Non-Randomized Agent Number To Load")
parser.add_argument("-raw",
                    "--Raw",
                    help="Plot Raw Data in addition to Moving Averaged Data")
parser.add_argument("-s", "--Seed", help="Seed (Default: 0).")
ARGS = parser.parse_args()

MA_WINDOW = 150
if ARGS.MovingAverageWindow:
    MA_WINDOW = ARGS.MovingAverageWindow


def moving_average(a, n=MA_WINDOW):
    MA = np.cumsum(a, dtype=float)
    MA[n:] = MA[n:] - MA[:-n]
    return MA[n - 1:] / n


def main():
    """ The main() function. """
    file_name = "spot_ars_"

    seed = 0
    if ARGS.Seed:
        seed = ARGS.Seed

    # Find abs path to this file
    my_path = os.path.abspath(os.path.dirname(__file__))
    results_path = os.path.join(my_path, "../results")

    if not os.path.exists(results_path):
        os.makedirs(results_path)

    vanilla_surv = np.random.randn(1000)
    agent_surv = np.random.randn(1000)

    nep = 1000

    if ARGS.NumberOfEpisodes:
        nep = ARGS.NumberOfEpisodes
    if ARGS.TrainingData:
        training = True
    else:
        training = False
    rand_agt = 579
    norand_agt = 569
    if ARGS.RandAgentNum:
        rand_agt = ARGS.RandAgentNum
    if ARGS.NoRandAgentNum:
        norand_agt = ARGS.NoRandAgentNum

    if not training:

        # Vanilla Data
        if os.path.exists(results_path + "/" + str(file_name) + "vanilla" +
                          '_survival_' + str(nep)):
            with open(
                    results_path + "/" + str(file_name) + "vanilla" +
                    '_survival_' + str(nep), 'rb') as filehandle:
                vanilla_surv = np.array(pickle.load(filehandle))

        # Rand Agent Data
        if os.path.exists(results_path + "/" + str(file_name) + "agent_" +
                          str(rand_agt) + '_survival_' + str(nep)):
            with open(
                    results_path + "/" + str(file_name) + "agent_" +
                    str(rand_agt) + '_survival_' + str(nep),
                    'rb') as filehandle:
                rand_agent_surv = np.array(pickle.load(filehandle))

        # NoRand Agent Data
        if os.path.exists(results_path + "/" + str(file_name) + "agent_" +
                          str(norand_agt) + '_survival_' + str(nep)):
            with open(
                    results_path + "/" + str(file_name) + "agent_" +
                    str(norand_agt) + '_survival_' + str(nep),
                    'rb') as filehandle:
                norand_agent_surv = np.array(pickle.load(filehandle))
                # print(norand_agent_surv[:, 0])

        # Extract useful values
        vanilla_surv_x = vanilla_surv[:1000, 0]
        rand_agent_surv_x = rand_agent_surv[:, 0]
        norand_agent_surv_x = norand_agent_surv[:, 0]
        # convert the lists to series
        data = {
            'Vanilla': vanilla_surv_x,
            'GMBC Rand': rand_agent_surv_x,
            'GMBC NoRand': norand_agent_surv_x
        }

        colors = ['r', 'g', 'b']

        # get dataframe
        df = pd.DataFrame(data)
        print(df)

        # Plot
        for i, col in enumerate(df.columns):
            sns.distplot(df[[col]], color=colors[i])

        plt.legend(labels=['GMBC NoRand', 'GMBC Rand', 'Vanilla'])
        plt.xlabel("Forward Survived Distance (m)")
        plt.ylabel("Kernel Density Estimate")
        plt.show()

        # Print AVG and STDEV
        norand_avg = np.average(norand_agent_surv_x)
        norand_std = np.std(norand_agent_surv_x)
        rand_avg = np.average(rand_agent_surv_x)
        rand_std = np.std(rand_agent_surv_x)
        vanilla_avg = np.average(vanilla_surv_x)
        vanilla_std = np.std(vanilla_surv_x)

        print("Vanilla: AVG [{}] | STD [{}]".format(vanilla_avg, vanilla_std))
        print("RANDOM: AVG [{}] | STD [{}]".format(rand_avg, rand_std))
        print("NOT RANDOM: AVG [{}] | STD [{}]".format(norand_avg, norand_std))

    else:
        # Training Data Plotter
        rand_data = np.load(results_path + "/spot_ars_rand_" + "seed" +
                            str(seed) + ".npy")
        norand_data = np.load(results_path + "/spot_ars_norand_" + "seed" +
                              str(seed) + ".npy")

        plt.plot()
        if ARGS.TotalReward:
            MA_rand_data = moving_average(rand_data[:, 0])
            MA_norand_data = moving_average(norand_data[:, 0])
            if ARGS.Raw:
                plt.plot(rand_data[:, 0],
                         label="Randomized (Total Reward)",
                         color='r')
                plt.plot(norand_data[:, 0],
                         label="Non-Randomized (Total Reward)",
                         color='g')
            plt.plot(MA_norand_data,
                     label="MA: Non-Randomized (Total Reward)",
                     color='r')
            plt.plot(MA_rand_data,
                     label="MA: Randomized (Total Reward)",
                     color='g')
        else:
            MA_rand_data = moving_average(rand_data[:, 1])
            MA_norand_data = moving_average(norand_data[:, 1])
            if ARGS.Raw:
                plt.plot(rand_data[:, 1],
                         label="Randomized (Reward/dt)",
                         color='r')
                plt.plot(norand_data[:, 1],
                         label="Non-Randomized (Reward/dt)",
                         color='g')
            plt.plot(MA_norand_data,
                     label="MA: Non-Randomized (Reward/dt)",
                     color='r')
            plt.plot(MA_rand_data,
                     label="MA: Randomized (Reward/dt)",
                     color='g')
        plt.xlabel("Epoch #")
        plt.ylabel("Reward")
        plt.title("Training Performance: Seed {}".format(seed))
        plt.legend()
        plt.show()


if __name__ == '__main__':
    main()
