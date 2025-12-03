from PyQt5.QtWidgets import QApplication

app = QApplication([])
screen = app.primaryScreen()
assert screen is not None, "screen MUST NOT be None"

print(f"physical DotsPerInch: {screen.physicalDotsPerInch()}")
print(f"physical DotsPerInchX: {screen.physicalDotsPerInchX()}")
print(f"physical DotsPerInchY: {screen.physicalDotsPerInchY()}")
print(f"logical  DotsPerInch: {screen.logicalDotsPerInch()}")
print(f"logical  DotsPerInchX: {screen.logicalDotsPerInchX()}")
print(f"logical  DotsPerInchY: {screen.logicalDotsPerInchY()}")
print(f"------------------------------------")

print(f"Device Pixel Ratio: {screen.devicePixelRatio()}")
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
