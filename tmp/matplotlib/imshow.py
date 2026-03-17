"""This example demonstrates how to load and display an image using Matplotlib's `imshow` function with pan and zoom capabilities."""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pathlib

# Load image from file
image_path = pathlib.Path(__file__).parent / "../.." / "examples" / "images" / "image.png"
image_numpy = mpimg.imread(image_path)

# Display it
fig, ax = plt.subplots()
ax.imshow(image_numpy)
ax.axis("off")

# The toolbar includes pan and zoom buttons by default
plt.show()
