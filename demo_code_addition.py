# (c) Heiko Hoffmann
# This python code demonstrates the emerging correlations from adding two population codes

import numpy as np
import math
import matplotlib.pyplot as plt
import random
from matplotlib.patches import Ellipse
from matplotlib.ticker import MultipleLocator
from scipy.stats import multivariate_normal
from scipy.stats import pearsonr
from tqdm import tqdm
import model

# Compute distribution of firing rates
def firing_rate(spike_train, bin_size):
    N = spike_train.shape[0]
    num_steps = spike_train.shape[1]
    firing_rates = []
    
    for i in range(N):
        spike_binary = spike_train[i,:]
        
        # Calculate the number of bins
        num_bins = len(spike_binary) // bin_size

        # Truncate the array to ensure it's evenly divisible by bin_size
        arr = spike_binary[:num_bins * bin_size]

        # Reshape the array into a 2D array with each row representing a bin
        split_arr = arr.reshape((num_bins, bin_size))

        # Sum each row (bin) along axis 1 to get an array of sums
        bin_sums = np.sum(split_arr, axis=1)

        firing_rates.append(bin_sums/bin_size)
        
    return firing_rates


# Compute the theoretically expected activity distribution for a population code
def theoretical_code(x, mu, sigma):
    C = 1.0 / (sigma * math.sqrt(2*math.pi))
    dx = x - mu
    return np.exp(- dx*dx / (2 * sigma**2))*C
    

# Parameters for the simulation
N = 51
num_steps = 2000000
histogram_steps = 1000
a = -0.2
a_sig = 0.2
b = 0.2
b_sig = 0.3
firing_rate_bin = 500

# Initialize population codes A, B, and C
A = np.zeros((N, num_steps))
B = np.zeros((N, num_steps))
C = np.zeros((N, num_steps))

for t in tqdm(range(num_steps)):
    A[:,t] = model.create_code(a,a_sig,N)
    B[:,t] = model.create_code(b,b_sig,N)
    C[:,t] = model.compute(A[:,t], B[:,t])

# Compute total activation
A_act = np.sum(A)
B_act = np.sum(B)
C_act = np.sum(C)

print(f"A total activation: {A_act}")
print(f"B total activation: {B_act}")
print(f"C total activation: {C_act}")
    
# Compute histograms
x = np.arange(0, N)/((N-1)/2)-1
hA = np.sum(A[:,0:histogram_steps], axis=1)/histogram_steps
hB = np.sum(B[:,0:histogram_steps], axis=1)/histogram_steps
hC = np.sum(C[:,0:histogram_steps], axis=1)/histogram_steps

rf_A = firing_rate(A,firing_rate_bin)
rf_B = firing_rate(B,firing_rate_bin)
rf_C = firing_rate(C,firing_rate_bin)

theo_A = theoretical_code(x, a, a_sig)/N*2
theo_B = theoretical_code(x, b, b_sig)/N*2
theo_C = theoretical_code(x, a+b, math.sqrt(a_sig**2 + b_sig**2))/N*2

# Create figure of spike trains
fig, axes = plt.subplots(3, 1, figsize=(6, 6))
plot_steps = 201

# Plot each spike train in a separate subplot
axes[0].imshow(A[:,:plot_steps], cmap='gray_r', interpolation='nearest', aspect=0.8)
axes[0].spines['top'].set_visible(False)
axes[0].spines['right'].set_visible(False)
axes[0].set_title('Code A', fontsize=16)
axes[0].set_ylabel('Neuron ID', fontsize=14)
axes[0].tick_params(axis='both', which='both', labelsize=14)
axes[0].xaxis.set_major_locator(MultipleLocator(100))
axes[0].yaxis.set_major_locator(MultipleLocator(25))

axes[1].imshow(B[:,:plot_steps], cmap='gray_r', interpolation='nearest', aspect=0.8)
axes[1].spines['top'].set_visible(False)
axes[1].spines['right'].set_visible(False)
axes[1].set_title('Code B', fontsize=16)
axes[1].set_ylabel('Neuron ID', fontsize=14)
axes[1].tick_params(axis='both', which='both', labelsize=14)
axes[1].xaxis.set_major_locator(MultipleLocator(100))
axes[1].yaxis.set_major_locator(MultipleLocator(25))

axes[2].imshow(C[:,:plot_steps], cmap='gray_r', interpolation='nearest', aspect=0.8)
axes[2].spines['top'].set_visible(False)
axes[2].spines['right'].set_visible(False)
axes[2].set_title('Code A + B', fontsize=16)
axes[2].set_xlabel('Time Step', fontsize=14)
axes[2].set_ylabel('Neuron ID', fontsize=14)
axes[2].tick_params(axis='both', which='both', labelsize=14)
axes[2].xaxis.set_major_locator(MultipleLocator(100))
axes[2].yaxis.set_major_locator(MultipleLocator(25))

# Adjust layout and show the plot
plt.tight_layout()
plt.savefig('PC_main_sim_spike_trains.eps', format='eps')

# Create figure of activity distributions
fig, ax = plt.subplots()

# Remove the box around the plot
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

#ax.set_title('Population Codes', fontsize=16)
ax.plot(x, hA, label='Code A', color='blue')
ax.plot(x, theo_A, linestyle='--', color='blue')
ax.plot(x, hB, label='Code B', color='green')
ax.plot(x, theo_B, linestyle='--', color='green')
ax.plot(x, hC, label='Code A+B', color='red')
ax.plot(x, theo_C, linestyle='--', color='red')
ax.legend(fontsize=14)
ax.tick_params(axis='both', which='both', labelsize=14)
ax.set_xlabel("Preferred Value", fontsize=14)
ax.set_ylabel("Firing Rate [Spikes / Time Step]", fontsize=14)
plt.savefig('PC_main_sim_code_sample.eps', format='eps')

# Choose two neurons for computing the correlation
n1_C = int((a+b)*N/2+N/2)
n2_C = n1_C + 1

# Compute Pearson correlation coefficient
correlation_coefficient, p_value = pearsonr(rf_C[n1_C], rf_C[n2_C])
print(f"Correlation coefficient for A+B (bin size {firing_rate_bin}): {correlation_coefficient}")
correlation_coefficient, p_value = pearsonr(C[n1_C,:], C[n2_C,:])
print(f"Correlation coefficient for A+B (bin size 1): {correlation_coefficient}")

# Create figure showing firing rate distribution between the two neurons
fig, ax = plt.subplots()

# Remove the box around the plot
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_title('Neurons with nearby preferred values', fontsize=16)
ax.plot(rf_C[n1_C], rf_C[n2_C], '.', color='black', label = 'Code A+B')
ax.set_aspect('equal', adjustable='box')
ax.tick_params(axis='both', which='both', labelsize=14)
ax.set_xlabel("Firing Rate of Neuron 25", fontsize=14)
ax.set_ylabel("Firing Rate of Neuron 26", fontsize=14)
ax.set_xlim(0, 0.11)
ax.set_ylim(0, 0.11)
ax.xaxis.set_major_locator(MultipleLocator(0.05))
ax.yaxis.set_major_locator(MultipleLocator(0.05))

# Fit an ellipse to the C data
data_points = np.transpose(np.vstack((rf_C[n1_C], rf_C[n2_C])))
cov_matrix = np.cov(data_points, rowvar=False)
mean = np.mean(data_points, axis=0)
eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

# Get the angle of rotation and scale factors
angle = np.degrees(np.arctan2(*eigenvectors[:, 0][::-1]))
width, height = 4 * np.sqrt(eigenvalues)

# Create and plot the ellipse
ellipseC = Ellipse(xy=mean, width=width, height=height, angle=angle, edgecolor='k', fc='None', lw=2)


plt.gca().add_patch(ellipseC)
plt.savefig('PC_main_sim_corr_fire_rates_near.eps', format='eps')

# Choose another two neurons for the firing rate plot
n1_C = 10
n2_C = 40

# Create figure showing firing rate distribution between the two neurons
fig, ax = plt.subplots()

# Remove the box around the plot
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_title('Neurons with distant preferred values', fontsize=16)
ax.plot(rf_C[n1_C], rf_C[n2_C], '.', color='black', label = 'Code A+B')
ax.set_aspect('equal', adjustable='box')
ax.tick_params(axis='both', which='both', labelsize=14)
ax.set_xlabel("Firing Rate of Neuron 10", fontsize=14)
ax.set_ylabel("Firing Rate of Neuron 40", fontsize=14)
ax.set_xlim(0, 0.11)
ax.set_ylim(0, 0.11)
ax.xaxis.set_major_locator(MultipleLocator(0.05))
ax.yaxis.set_major_locator(MultipleLocator(0.05))

# Fit an ellipse to the C data
data_points = np.transpose(np.vstack((rf_C[n1_C], rf_C[n2_C])))
cov_matrix = np.cov(data_points, rowvar=False)
mean = np.mean(data_points, axis=0)
eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

# Get the angle of rotation and scale factors
angle = np.degrees(np.arctan2(*eigenvectors[:, 0][::-1]))
width, height = 4 * np.sqrt(eigenvalues)

# Create and plot the ellipse
ellipseC = Ellipse(xy=mean, width=width, height=height, angle=angle, edgecolor='k', fc='None', lw=2)

plt.gca().add_patch(ellipseC)
plt.savefig('PC_main_sim_corr_fire_rates_far.eps', format='eps')


plt.show()

