from PyQt5.QtWidgets import QApplication

app = QApplication([])
screen = app.primaryScreen()
assert screen is not None
dpi = screen.physicalDotsPerInch()
print(f"DPI: {dpi}")
