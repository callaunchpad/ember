import json
import os
import numpy as np


def add_noise(value):
    """Add random noise to a numerical value."""
    noise = np.random.normal(0, 0.05 * value)  # 5% of the value as noise
    return value + noise


def augment_data(input_path, output_path, rating_to_augment, copies):

    with open(input_path, "r") as file:
        data = json.load(file)

    augmented_data = {}
    for key, value in data.items():
        # Check if the current data point has the specified rating
        if value["rating"] == [
            1 if i == rating_to_augment - 1 else 0 for i in range(5)
        ]:
            for copy in range(copies):
                new_key = f"{key}_copy_{copy}"
                new_value = value.copy()

                # Add noise to numerical data points
                for num_key in [
                    "temp",
                    "humidity",
                    "dew",
                    "precip",
                    "snow",
                    "snowdepth",
                    "windspeed",
                    "pressure",
                    "cloudcover",
                    "solarradiation",
                    "solarenergy",
                ]:
                    if num_key in new_value:
                        # If a value for this exists, add noise to it (but if it's None or something, just don't do anything and keep as is).
                        if new_value[num_key]:
                            new_value[num_key] = add_noise(new_value[num_key])

                augmented_data[new_key] = new_value
        else:
            augmented_data[key] = value

    with open(output_path, "w") as file:
        json.dump(augmented_data, file, indent=4)

    print(f"Augmented data saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    input_path = "json_data/datav2_augmented_noisy.json"
    output_path = "json_data/datav2_augmented_noisy_more_2s.json"
    rating_to_augment = 2  # For example, augment data with a 4/5 rating
    copies_to_make = (
        2  # Number of copies to make for each data point with the specified rating
    )

    augment_data(input_path, output_path, rating_to_augment, copies_to_make)
