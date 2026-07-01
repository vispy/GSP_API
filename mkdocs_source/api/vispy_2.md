# VisPy 2 API Reference

The VisPy 2 package provides a high-level producer facade for GSP protocol scenes.
2D interaction is owned by canonical GSP `View2D` navigation, not by the removed
legacy `vispy2.axes` pan/zoom helpers.

## Overview

::: vispy2
    handler: python
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Axes Module

The axes module contains tick utility helpers only. Legacy `AxesDisplay`, `AxesPanZoom`,
and `AxesManaged` were removed in favor of canonical `View2D` navigation and semantic guides.

::: vispy2.axes
    handler: python
    options:
      show_root_heading: true
      show_source: true
      members_order: source
