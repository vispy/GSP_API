import matplotlib.colors as mcolors
import numpy as np

import datoviz as dvz


def main():
    app = dvz.App()
    figure = app.figure(100, 100)
    panel = figure.panel()
    panzoom = panel.panzoom()

    point_count = 10000
    positions = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions *= 0.9
    colors = np.array([[255, 0, 0, 255] * point_count], dtype=np.uint8).reshape(point_count, 4)

    # visual = app.pixel(position=position, color=color)
    visual = app.pixel(position=positions, color=colors)
    panel.add(visual)

    app.run()
    app.destroy()


if __name__ == "__main__":
    main()
