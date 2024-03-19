import json
import os
import shutil
from pathlib import Path


def augment_data(input_json_path, output_dir, target_rating, num_copies):
    """
    Augments data by duplicating entries with a specified rating.

    :param input_json_path: Path to the input JSON file.
    :param output_dir: Directory where the augmented JSON file will be saved.
    :param target_rating: The rating to filter and duplicate data for.
    :param num_copies: Number of copies to make for each data point with the target rating.
    """

    # Load the data from the input JSON file
    with open(input_json_path, "r") as file:
        data = json.load(file)

    # Prepare the augmented data dictionary
    augmented_data = {}

    # Iterate over the data to find entries with the target rating
    for key, value in data.items():
        if value["rating"][target_rating - 1] == 1:  # Adjust for zero-based indexing
            # Duplicate the entry num_copies times
            for i in range(1, num_copies + 1):
                new_key = (
                    f"{key[:-4]}_copy{i}.jpg"  # Modify the key to indicate it's a copy
                )
                augmented_data[new_key] = value
        else:
            # Include the original data if it doesn't match the target rating
            augmented_data[key] = value

    # Save the augmented data to a new JSON file in the output directory
    with open(output_dir, "w") as file:
        json.dump(augmented_data, file, indent=4)

    print(f"Augmented data saved to {output_dir}")


if __name__ == "__main__":
    # Example usage
    input_json_path = "datav2_augmented.json"  # Update this path
    output_dir = "datav2_augmented.json"  # Update this path
    target_rating = 5  # The rating you want to augment
    num_copies = 8  # Number of copies to make for each matching data point

    augment_data(input_json_path, output_dir, target_rating, num_copies)
