import matplotlib.pyplot as plt

# 1. Define the desired figure size in inches
# The tuple format is (width, height)


figure_inch_w = 10
figure_inch_h = 2

# 2. Create the figure and axes objects
# The 'figsize' parameter sets the dimensions of the figure
fig, ax = plt.subplots(figsize=(figure_inch_w, figure_inch_h), dpi=127.5)

# 3. Optional: Add a title to confirm the size
ax.set_title(f"2 in x 3 in Matplotlib Figure", fontsize=8)

# 4. Optional: Customize the plot (e.g., add labels and a simple line)
ax.set_xlabel("X-Axis", fontsize=7)
ax.set_ylabel("Y-Axis", fontsize=7)
ax.plot([0, 1], [0, 1])  # Plot a simple line for visual reference

# 5. Display the figure
plt.show()

# You can also save the figure to a file:
# fig.savefig('2in_x_3in_figure.png', dpi=300)
