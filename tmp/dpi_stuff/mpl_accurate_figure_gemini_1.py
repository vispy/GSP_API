# from https://gemini.google.com/app/bf53f185ee3f725b

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- 1. CONFIGURATION ---

# INPUT: Update this value based on your hardware (see table above)
# This is the crucial link between software points and hardware reality.
MY_SCREEN_PPI = 254 / 2  # Example for MacBook Pro 16" Retina
MY_SCREEN_WIDTH_CM = 344.24470071231616 / 10
MY_SCREEN_HEIGHT_CM = 222.52391822665348 / 10

# Target physical dimensions
# TARGET_WIDTH_INCH = (MY_SCREEN_WIDTH_CM - 0.5) / 2.54
# TARGET_HEIGHT_INCH = (MY_SCREEN_HEIGHT_CM / 2) / 2.54

TARGET_WIDTH_INCH = 1
TARGET_HEIGHT_INCH = 1

# --- 2. LOGIC & CONVERSION ---


def cm_to_inch(cm):
    return cm / 2.54


def inch_to_cm(inch):
    return inch * 2.54


# --- 3. CREATING THE FIGURE ---

# We create the figure using our calibrated PPI.
# Matplotlib uses inches by default for figsize.
mpl_figure = plt.figure(figsize=(TARGET_WIDTH_INCH, TARGET_HEIGHT_INCH), dpi=MY_SCREEN_PPI)

# --- 4. VERIFICATION PLOT ---

# Create an axes that fills the whole figure (no margins)
mpl_axes = mpl_figure.add_axes((0, 0, 1, 1))

# Draw a rectangle that should fill the exact space
# (0,0) is bottom left, width=2, height=3
rect = patches.Rectangle((0, 0), TARGET_WIDTH_INCH, TARGET_HEIGHT_INCH, linewidth=4, edgecolor="r", facecolor="none")

mpl_axes.add_patch(rect)

# Set limits to match the size so the coordinates map 1:1 to inches
mpl_axes.set_xlim(0, TARGET_WIDTH_INCH)
mpl_axes.set_ylim(0, TARGET_HEIGHT_INCH)

# Remove ticks/labels for clean visualization
mpl_axes.axis("off")

# Add text to verify
mpl_axes.text(
    TARGET_WIDTH_INCH / 2,
    TARGET_HEIGHT_INCH / 2,
    f'Target: {TARGET_WIDTH_INCH}" x {TARGET_HEIGHT_INCH}"\n' f"PPI Set: {MY_SCREEN_PPI}",
    horizontalalignment="center",
    verticalalignment="center",
    fontsize=12,
)

# --- 5. DISPLAY ---
# Note: When the window opens, do NOT resize it.
# Depending on your backend (Qt, MacOSX), the window chrome (title bar)
# might add extra size, but the canvas inside should be accurate.
plt.show()
