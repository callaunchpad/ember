import tkinter as tk
from tkinter import PhotoImage, Toplevel, Label
from PIL import Image, ImageTk
import json
import os
from pathlib import Path

# Load JSON data
data_path = Path("json_data/datav2.json")
with open(data_path, "r") as file:
    data = json.load(file)

# List of image paths
image_paths = list(data.keys())
current_image_index = 0


def update_json():
    """Function to update the JSON file with the current data."""
    with open(data_path, "w") as file:
        json.dump(data, file, indent=4)


def set_rating(rating):
    """Function to set the rating for the current image."""
    global current_image_index
    image_path = image_paths[current_image_index]
    data[image_path]["rating"] = [1 if i == rating - 1 else 0 for i in range(5)]
    update_json()
    update_rating_label()
    next_image()


def next_image(event=None):
    """Function to display the next image."""
    global current_image_index
    current_image_index = (current_image_index + 1) % len(image_paths)
    show_image()


def previous_image(event=None):
    """Function to display the previous image."""
    global current_image_index
    current_image_index = (current_image_index - 1) % len(image_paths)
    show_image()


def jump_to_unrated():
    """Jump to the first image without a rating."""
    global current_image_index
    for index, path in enumerate(image_paths):
        if "rating" not in data[path] or 1 not in data[path]["rating"]:
            current_image_index = index
            break
    show_image()


def show_image():
    """Function to display the current image."""
    global current_image_index
    image_path = image_paths[current_image_index]
    date_str = image_path.split("_")[1] + " " + image_path.split("_")[2]
    img = Image.open(Path("../") / image_path)
    # img = img.resize((800, 600), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.photo = photo
    window.title(f"Sunset Image Rating - {date_str}")
    update_rating_label()


def update_rating_label():
    """Update the rating label with the current image's rating."""
    global current_image_index
    image_path = image_paths[current_image_index]
    rating = data.get(image_path, {}).get("rating")
    if rating:
        rating_str = f"Rating: {rating.index(1) + 1}"
    else:
        rating_str = "Rating: None"
    rating_label.config(text=rating_str)


def on_key_press(event):
    """Handle key press events for ratings and navigation."""
    if event.char.isdigit() and event.char in "12345":
        set_rating(int(event.char))
    elif event.keysym == "Right":
        next_image()
    elif event.keysym == "Left":
        previous_image()


# Create the main window
window = tk.Tk()
window.geometry("800x600")
window.bind("<Key>", on_key_press)

# Create a label to display images
image_label = Label(window)
image_label.pack()

# Create buttons for rating
for i in range(1, 6):
    button = tk.Button(window, text=str(i), command=lambda i=i: set_rating(i))
    button.pack(side="left", padx=10, pady=10)

# Create a label to display the current rating
rating_label = tk.Label(window, text="Rating: None")
rating_label.pack(side="bottom", anchor="e")

# Create a button to jump to the first unrated image
jump_button = tk.Button(window, text="Jump to Unrated", command=jump_to_unrated)
jump_button.pack(side="bottom", pady=10)

show_image()

window.mainloop()
