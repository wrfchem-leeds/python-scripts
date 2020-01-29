# WRF - Python Scripts

To replace [ncl](https://www.ncl.ucar.edu/) [NCAR](https://ncar.ucar.edu/) have been developing a python library called [wrf-python](https://wrf-python.readthedocs.io/en/latest/). This is under development but will eventually contain scripts to replace the standard ncl tools that accompany WRF.

The chemistry components are severely lacking

## Requirements

* python 2 or 3
* wrf-python

## Installation

### Conda

Either of (*yml contains all packages required to run*)

````bash
# install all dependencies
conda env create -f environment.yml
# or
# install just wrf-python
conda install -c conda-forge wrf-python
````

### Other

with out conda instructions for building from source are provided in [wrf-python documentation](https://wrf-python.readthedocs.io/en/latest/installation.html) and dependencies are listed in [requirements.txt](./requirements.txt)

## Scripts

Some example scripts show how to use the wrf-python packages.

### Plot grids replacements

1. [plot_grids.py](plot_grids.py) generic tool to nicely plot domains from geo_em files
2. [domain_inspector.py](domain_inspector.py) example script to plot domains to inspect topography

### Quick look results

1. [basic_plots.py](basic_plots.py) based of wrf-python example to plot dewpoint, slp and wind direction using wrf-python diagnostics.

Uses [inbuilt diagnostics available for wrfpython](https://wrf-python.readthedocs.io/en/latest/diagnostics.html). Currently meteorology only focused.
