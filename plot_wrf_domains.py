#!/usr/bin/env python3
from salem import geogrid_simulator
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

namelist_path = '.../namelist.wps' # ensure no comments in namelist
g, maps = geogrid_simulator(namelist_path)

fig = plt.figure(1, figsize=(5, 5))
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])
maps[0].set_rgb(natural_earth='lr')
maps[0].visualize()

gs.tight_layout(fig)
iplt.savefig('wrf_domains.png', dpi=700, alpha=True, bbox_inches='tight')
plt.show()
