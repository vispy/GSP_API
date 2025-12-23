# Porting pyramid.py example to GSP
- do PR to ./data repository with reasonable subset of images
- recode it in matplotlib to see how to do it
- early Image visual in GSP
- support axes with setLimits(xmin,xmax,ymin,ymax)
  - how to reuse the viewport ndc metric code ? fork it ?
- pan/zoom controls with viewportEvents -> axes.setLimits()
  - output a translation/scale matrix for the axes
- combine axes transform with visual model_matrix transform to get final position

## What is needed
- image visual
  - done in GSP. 
  - how to clip it to be inside the axes
    - what about axes create 2 viewports
      - one for the inside of the axes
      - one for the outside of the axes
  - may be done later. for now use basic segments
  - datoviz docs - https://datoviz.org/visuals/image/
- pan/zoom controls
  - not mandatory at first
  - done with viewportEvents + axes.setLimits()
- axes visual using x,y,width,height in pixels within the viewport
  - setLimits xmin,xmax,ymin,ymax in data space
    - this provide a transform from data space to viewport space
    - this axes transform will be combined with the visual model_matrix transform to get final position
  - display the axes itself
  - display ticks + labels
  - reuse `./examples/viewport_ndc_metric.py`