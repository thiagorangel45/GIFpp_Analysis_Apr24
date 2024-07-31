import csv
from extract_data import data
import numpy as np
import math
import matplotlib.pyplot as plt 
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoLocator, AutoMinorLocator
import os
import mplhep as hep
from datetime import datetime
from scipy.optimize import curve_fit


font0 = {'family': 'DejaVu Sans',
            'weight': 'bold',
            'size': 38,
            } # for plot title
font1 = {'family': 'DejaVu Sans',
            'weight': 'bold',
            'size': 18,
            } # for legend
mixtures = {"30CO2" : "30% CO2 + 1% SF6",
            "30CO205SF6" : "30% CO2 + 0.5% SF6",
            "40CO2" : "40% CO2 + 1% SF6",
            "STDMX" : "Standard Mixture"
}
markers = ['o', '^', 's', '*', 'd']
colors = ['black', 'magenta', 'red', 'blue', 'green']

def read_data(filename):
    background_rates = {}
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            scan_name, hv_str, background_rate_str, wp_str, eff_str, muoncs_str, gammacs_str, muoncs_err_str, gammacs_err_str = row
            wp = float(wp_str) / 1000
            background_rate = float(background_rate_str)
            if scan_name not in background_rates:
                background_rates[scan_name] = []
            background_rates[scan_name].append((wp, background_rate))
    return background_rates

def plot_scan(scan, wp):
    HV = np.array(data['HV'][scan])
    muon_cs = np.array(data['muon_cs'][scan])
    muon_cs_err =  np.array(data['muon_cs_err'][scan]) 
    wp = background_rates[scan][0][0]  # Get the wp for the current scan
    HV_adj = HV - (wp*1000)

    if scan not in plot_scan_colors:
        color = plot_scan_colors[scan] = colors[len(plot_scan_colors) % len(colors)]
    color = plot_scan_colors[scan]

    if scan not in plot_scan_markers:
        marker = plot_scan_markers[scan] = markers[len(plot_scan_markers) % len(markers)]
    marker = plot_scan_markers[scan]

    parts = scan.split("_")
    mixture = parts[0]
    d = mixtures.get(mixture, f"Gas mixture: {mixture}")
    labels = []

    for wp_scan, background_rate in background_rates.get(scan, []):
        labels.append(f"Gas mixture = {d}, WP = {wp_scan:.2f} kV")
    label = '\n'.join(labels)
    plt.errorbar(HV_adj, muon_cs, yerr=muon_cs_err, fmt=marker, markersize=9, color=color, label=label)

background_rates = read_data('2023_data_atWP_fullscans.csv')
plot_scan_colors = {}
plot_scan_markers = {}

#Setting the plot
hep.style.use("CMS")
figure, ax = plt.subplots(figsize=(14, 14))
plt.xlabel(r'HV$_{\mathrm{eff}}$ - HV$_{\mathrm{WP}}$ [V]', fontsize=38)
plt.ylabel('Muon cluster size', fontsize=38)
plt.grid(ls='--')

ax.xaxis.set_major_locator(AutoLocator())
ax.yaxis.set_major_locator(AutoLocator())
ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.tick_params(which='major', direction='in', length=10, width=2.0, labelsize=12)
ax.tick_params(which='minor', direction='in', length=5, width=1.0)
plt.yticks(fontproperties='DejaVu Sans', size=20, weight='bold')  
plt.xticks(fontproperties='DejaVu Sans', size=20, weight='bold') 
plt.xlim(-550, 450)
plt.ylim(0.8, 3.8)

# Input scan names from user
scans = input("Enter the names of the scans you want to plot, separated by commas: ").split(',')
#name =  datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
name = input("Enter a name for the plot: ")

for scan in scans:
    wp = background_rates.get(scan, [(None, None)])[0][0]
    plot_scan(scan.strip(), wp)

if not os.path.exists('Plots_2023/'):
    os.makedirs('Plots_2023/')

stdmx_background_rate = "N/A"
for scan in scans:
    scan = scan.strip()
    if 'STDMX' in scan:
        stdmx_background_rate = background_rates.get(scan, [(None, "N/A")])[0][1]
        break

# Plotting 
label = f"Background rate: {stdmx_background_rate:.2f} Hz/cm² \nTest Beam Apr + July 2023 \nThreshold: 60 fC \n1.4 mm double gap RPC" 
#label = f"No gamma background \nTest Beam April 2024 \nThreshold: 60 fC \n1.4 mm double gap RPC" 
ax.text(0.035, 0.8, label, transform=ax.transAxes, verticalalignment='top', horizontalalignment='left', fontsize=24, linespacing=1.5)

plt.text(300, 3.8+0.03, "GIF++", font0)
hep.cms.text("Preliminary", fontsize=32)
plt.legend(loc='upper left', prop=font1, frameon=False)
#plt.axhline(y=3.3, color='black', linestyle='--')
plt.savefig(os.path.join('Plots_2023/' + name + ".png"))
#plt.show()

