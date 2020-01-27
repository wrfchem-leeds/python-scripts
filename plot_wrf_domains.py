#!/usr/bin/env python3
from salem import geogrid_simulator
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

# plot the wrf domains over a natural earth
namelist_path = 'demo_files/namelist.wps.demo' # ensure no comments in namelist
g, maps = geogrid_simulator(namelist_path)

fig = plt.figure(1, figsize=(5, 5))
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])
maps[0].set_rgb(natural_earth='lr')
maps[0].visualize()

gs.tight_layout(fig)
plt.savefig('demo_files/wrf_domains.png', dpi=700, alpha=True, bbox_inches='tight')
plt.show()
