from matplotlib import font_manager

for font in font_manager.fontManager.ttflist:
    print(font.name)
