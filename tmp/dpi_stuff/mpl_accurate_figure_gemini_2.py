import matplotlib.pyplot as plt
import math

# ==========================================
# USER CONFIGURATION - UPDATE THESE VALUES
# ==========================================

# 1. Your Screen Hardware Specs (Example: MacBook Air M1/M2)
SCREEN_WIDTH_PX = 2560  # Native Hardware pixels (width)
SCREEN_HEIGHT_PX = 1600  # Native Hardware pixels (height)
DIAGONAL_INCH = 13.3  # Physical screen diagonal in inches

# 2. Desired Figure Dimensions
TARGET_WIDTH_INCH = 2.0
TARGET_HEIGHT_INCH = 3.0

# ==========================================
# LOGIC
# ==========================================


def calculate_ppi(width_px, height_px, diagonal_inch):
    """Calculates the Physical Pixels Per Inch."""
    diagonal_px = math.sqrt(width_px**2 + height_px**2)
    return diagonal_px / diagonal_inch


def cm_to_inch(cm):
    """Helper if you want to input metric sizes."""
    return cm / 2.54


# 1. Calculate the real hardware PPI
# On a MacBook Air 13", this is roughly 227 PPI.
MY_PPI = calculate_ppi(SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX, DIAGONAL_INCH)

print(f"Calculated Physical PPI: {MY_PPI:.2f}")

# 2. Create the figure
# Note: We must pass the calculated PPI to the figure initialization.
fig = plt.figure(figsize=(TARGET_WIDTH_INCH, TARGET_HEIGHT_INCH), dpi=MY_PPI)

# 3. Add content (simple plot for visibility)
ax = fig.add_axes((0, 0, 1, 1))  # Span the whole figure
ax.plot([0, 1], [0, 1], "r-", linewidth=3)
ax.text(0.5, 0.5, f'{TARGET_WIDTH_INCH}" x {TARGET_HEIGHT_INCH}"', ha="center", va="center", fontsize=20, transform=ax.transAxes)

# 4. Handle MacOS Window Backend behavior
# The MacOSX backend usually respects the 'dpi' argument for rasterization
# but might scale the window based on logical points (72 dpi).
# To ensure the window opens at the physical size, we rely on the backend
# using the pixel dimensions implied by (figsize * dpi).

plt.show()
