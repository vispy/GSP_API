from PyQt5.QtWidgets import QApplication

app = QApplication([])
screen = app.primaryScreen()
assert screen is not None, "screen MUST NOT be None"


dpi = screen.physicalDotsPerInch()
print(f"physical DotsPerInch: {dpi}")
print(f"logical  DotsPerInch: {screen.logicalDotsPerInch()}")
print(f"------------------------------------")

device_pixel_ratio = screen.devicePixelRatio()
print(f"Device Pixel Ratio: {device_pixel_ratio}")
print(f"------------------------------------")

print(f"Available Geometry: {screen.availableGeometry()}")
print(f"Geometry: {screen.geometry()}")
print(f"Available Virtual Geometry: {screen.availableVirtualGeometry()}")
print(f"Virtual Geometry: {screen.virtualGeometry()}")
print(f"------------------------------------")

print(f"Physical Size (mm): {screen.physicalSize()}")
print(f"Virtual Size (pixels): {screen.virtualSize()}")
print(f"Size (pixels): {screen.size()}")
print(f"------------------------------------")

print(f"Depth: {screen.depth()}")
print(f"Refresh Rate: {screen.refreshRate()} Hz")
print(f"------------------------------------")

app.quit()
