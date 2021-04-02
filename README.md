## WRF-Chem, University of Leeds, UK
### Python scripts

#### Contributors
- Ben Silver, Luke Conibear, Helen Burns, and Ailish Graham.  
  
#### Contents
- [Introduction to Python](https://www.lukeconibear.com/introduction_to_scientific_computing/index.html) focusing on Python, Linux, and GitHub.  
- Python setup using conda (follow steps in conda.md)  
- Plot domains from namelist (`plot_wrf_domains.py`)  
- Concatenate and regrid WRF-Chem output (`wrfout_concat_regrid.py`)  
- Regrid WRF-Chem output and see map distortion (`wrfout_regrid.py`)  
- Evaluate WRF-Chem output to ground measurements (`interpolated_model_timeseries.py` and `get_modmeas_pickles.py`)  
- A collection of scripts using the NCAR python package wrf-python, including:  
  - Example plotting of basic variables (`basic_plots.py`)  
  - Indepth look at domains (`domain_inspector.py`)  
  - Generic plot grids tool (`plot_grids.py`)  
- An alternative to parallelise post.bash (`post.bash_split.py`)  
- Script for merging TNO and NAEI emission files (`combine_emissions.py`)  
- Correct air quality measurements in China due to protocol change (`correct_china_measurements.py`).  
