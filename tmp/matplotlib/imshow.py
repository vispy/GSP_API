"""This example demonstrates how to load and display an image using Matplotlib's `imshow` function. It reads an image from a file, converts it to a NumPy array, and then displays it without axes for a cleaner look."""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pathlib

# Load image from file
image_path = pathlib.Path(__file__).parent / "../.." / "examples" / "images" / "image.png"
image_numpy = mpimg.imread(image_path)

# Display it
plt.imshow(image_numpy)
plt.axis("off")  # hide axes for cleaner display
plt.show()
