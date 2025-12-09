import matplotlib.pyplot as plt
import matplotlib.text
import numpy as np

# 1. Create a figure and an axes object
mpl_figure, mpl_axes = plt.subplots(figsize=(6, 6))

# Set axis limits
mpl_axes.set_xlim(0, 10)
mpl_axes.set_ylim(0, 10)

# =============================================================================
#
# =============================================================================
# mpl_axes.text(
#     3,
#     3,
#     "Rotated Text",
#     color="purple",
#     rotation=30,
#     ha="center",
#     va="center",
#     fontsize=11,
#     # fontweight="black",
#     fontfamily="sans-serif",  # https://matplotlib.org/stable/api/text_api.html#matplotlib.text.Text.set_fontfamily
# )  # Angle in degrees

# artist_text = matplotlib.text.Text(x=3, y=3, text="Artist Text Example", ha="center", va="center", fontsize=11, color="blue")
artist_text = matplotlib.text.Text()

artist_text.set_x(3)  # Change x position to 5
artist_text.set_y(3)  # Change y position to 5
artist_text.set_text("Updated Artist Text")  # Update the text content
artist_text.set_rotation(45)  # Rotate the text by 45 degrees
artist_text.set_horizontalalignment("center")  # Change horizontal alignment to left
artist_text.set_verticalalignment("center")  # Change vertical alignment to top
artist_text.set_fontfamily("sans-serif")  # Set font family to serif
artist_text.set_fontsize(14)  # Set font size to 14
artist_text.set_color("red")  # Change text color to red

# Add the artist to the axes
mpl_axes.add_artist(artist_text)

# Save the plot
# plt.savefig("matplotlib_text_example.png")
plt.show()  # In a real environment, you would use this to display the plot.
