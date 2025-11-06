import gsp_matplotlib.extra.bufferx

# re-export Bufferx here
# LATER: copy methods from gsp.types.bufferx.Bufferx
# - for now, just re-export, thus no code duplication
# - we dont want to force users to handle numpy, so it is in gsp_extra
Bufferx = gsp_matplotlib.extra.bufferx.Bufferx
