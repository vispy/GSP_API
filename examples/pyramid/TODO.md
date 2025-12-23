# Porting pyramid.py example to GSP
- do PR to ./data repository with reasonable subset of images
- recode it in matplotlib to see how to do it

## What is needed
- pan/zoom controls
  - not mandatory at first
  - done with viewportEvents + axes.setLimits()
- image visual
  - done in GSP. may be done later. for now use basic segments
  - datoviz docs - https://datoviz.org/visuals/image/
- axes visual using x,y,width,height in pixels within the viewport
  - setLimits xmin,xmax,ymin,ymax in data space
    - this provide a transform from data space to viewport space
    - this axes transform will be combined with the visual model_matrix transform to get final position
  - display the axes itself
  - display ticks + labels
  - reuse `./examples/viewport_ndc_metric.py`