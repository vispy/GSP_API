import matplotlib.pyplot as plt
import numpy as np

# 1. Create a figure and an axes object
fig, ax = plt.subplots(figsize=(10, 6))

# Set axis limits
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# Add standard labels and title
ax.set_xlabel("X-Axis")
ax.set_ylabel("Y-Axis")
ax.set_title("Demonstration of Matplotlib Text Features", fontsize=16, fontweight="bold")

# 2. Basic Text with Data Coordinates
# The default uses data coordinates (x, y)
ax.text(1, 8, "Basic Text", fontsize=12)

# 3. Custom Styled Text
# Set color, font size, and font style
ax.text(2, 6.5, "Colored and Styled Text", color="blue", fontsize=14, style="italic")

# 4. Text with a Bounding Box (bbox)
# Use the bbox argument to draw a box around the text
ax.text(3, 5, "Text with a Box", fontsize=10, bbox={"facecolor": "lightgreen", "alpha": 0.7, "pad": 5})

# 5. Mathematical Expressions (using LaTeX syntax)
# Enclose the expression in raw strings (r'') and dollar signs ($$)
ax.text(4, 3.5, r"An equation: $E=mc^2$", fontsize=18, color="red")

# 6. Text with Axes Coordinates and Alignment
# Use 'transform=ax.transAxes' to place text relative to the Axes (0,0 is bottom-left, 1,1 is top-right).
# Use horizontalalignment (ha) and verticalalignment (va) to anchor the text.
ax.text(
    0.95,
    0.05,
    "Axes Coords (Bottom Right)",
    transform=ax.transAxes,
    ha="right",  # Horizontal alignment
    va="bottom",  # Vertical alignment
    fontsize=9,
    color="gray",
)

# 7. Rotated Text
ax.text(7, 8, "Rotated Text", rotation=30, fontsize=11, ha="center", va="center")  # Angle in degrees

# 8. Annotate a point with an arrow
ax.plot([8], [2], "ro")  # Plot a red point
ax.annotate(
    "Annotated Point",
    xy=(8, 2),  # The point being annotated (data coords)
    xytext=(6, 2.5),  # The text position (data coords)
    arrowprops=dict(facecolor="black", shrink=0.05),  # Arrow style
    fontsize=10,
)

# Save the plot
# plt.savefig("matplotlib_text_example.png")
plt.show()  # In a real environment, you would use this to display the plot.
