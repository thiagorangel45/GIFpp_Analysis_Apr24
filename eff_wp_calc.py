import numpy as np
from scipy.optimize import curve_fit
import math
import csv
import os

from extract_data import load_data

def func(HV, E, L, H):
    return E / (1 + np.exp(L * (H - HV)))

def find_index_of_value(HV, target_value):
    rounded_HV = math.ceil(target_value / 100) * 100
    try:
        return HV.index(rounded_HV)
    except ValueError:
        print(f"Value {rounded_HV} not found in HV column.")
        decremented_value = target_value - 100
        while decremented_value >= min(HV):
            rounded_decremented_value = math.ceil(decremented_value / 100) * 100
            try:
                return HV.index(rounded_decremented_value)
            except ValueError:
                print(f"Value {rounded_decremented_value} not found in HV column.")
                decremented_value -= 100
        print("No corresponding value found in HV column.")
        return None

def calculate_WP_and_eff_WP(data):
    results = []

    for file_name in data['HV']:
        HV = data['HV'][file_name]
        eff = data['eff'][file_name]

        initial_guess = [0.98, 0.01, 7000]

        try:
            popt, pcov = curve_fit(func, HV, eff, p0=initial_guess, bounds=([0, -np.inf, -np.inf], [1.00, np.inf, np.inf]))
            E, L, H = popt

            knee = H - (np.log(1 / 0.95 - 1)) / L
            WP = knee + 120
            eff_WP = func(HV, E, L, H)

            index_WP = find_index_of_value(HV, WP)

            if index_WP is not None:
                eff_WP = eff[index_WP]
                results.append({'file_name': file_name, 'WP': WP, 'eff_WP': eff_WP})
            else:
                print(f"WP outside the HV range for file: {file_name}")

        except RuntimeError:
            print(f"Curve fitting failed for file: {file_name}")

    return results

def append_results_to_csv(results, existing_file, output_file):
    # Read existing CSV and prepare to merge
    with open(existing_file, 'r', newline='') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        existing_data = {row[0]: row[1:] for row in reader}  # Assuming first column is 'file_name'

    # Merge new results with existing data
    merged_data = []
    for result in results:
        file_name = result['file_name']
        if file_name in existing_data:
            merged_row = [file_name] + existing_data[file_name] + [str(result['WP']), str(result['eff_WP'])]
            merged_data.append(merged_row)

    # Write merged data back to CSV
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header + ['WP', 'eff_WP'])
        writer.writerows(merged_data)

# Load data from extract_data.py
data = load_data()

# Calculate WP and eff_WP for each file
results = calculate_WP_and_eff_WP(data)

# Append results to existing CSV file in the same directory
existing_file = 'background_rates_2024.csv'
output_file = 'updated_background_rates_2024.csv'
append_results_to_csv(results, existing_file, output_file)

print(f"Results appended to {output_file}")
