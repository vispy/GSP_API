import matplotlib.pyplot as plt

# ---- screen physical size (your values) ----
width_mm = 344.24470071231616
height_mm = 222.52391822665348
width_px = 3024
height_px = 1964

# compute screen PPI
one_inch_in_mm = 25.4
width_in = width_mm / one_inch_in_mm
height_in = height_mm / one_inch_in_mm

ppi_x = width_px / width_in
ppi_y = height_px / height_in
ppi = (ppi_x + ppi_y) / 2  # average, OK for MacBooks

print(f"Screen PPI: {ppi}")

# ---- desired physical figure size ----
W_in = 3  # width in inches
H_in = 2  # height in inches

W_mm = W_in * one_inch_in_mm
H_mm = H_in * one_inch_in_mm

# ---- Create the figure with correct physical DPI ----
fig = plt.figure(figsize=(W_in, H_in), dpi=ppi)

plt.plot([0, 1], [0, 1])
plt.title(f"Physically accurate figure ({W_in}×{H_in} inch)")
print(f"Figure size in mm: {W_mm:.2f}×{H_mm:.2f} mm")

# # Make window appear at the right pixel size
# mng = plt.get_current_fig_manager()
# try:
#     # Qt backend
#     mng.window.setFixedSize(int(W_in * ppi), int(H_in * ppi))
# except:
#     pass

plt.show()
