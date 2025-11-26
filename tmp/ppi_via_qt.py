from PyQt5.QtWidgets import QApplication

app = QApplication([])
screen = app.primaryScreen()
assert screen is not None, "screen MUST NOT be None"


dpi = screen.physicalDotsPerInch()
print(f"DPI: {dpi}")

device_pixel_ratio = screen.devicePixelRatio()
print(f"Device Pixel Ratio: {device_pixel_ratio}")
