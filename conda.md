### Python setup through conda
- Download the latest miniconda  
`get https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh  `
- Run bash script, read terms, and set path  
`bash Miniconda3-latest-Linux-x86_64.sh  `
- Create conda environment for python 3 with data science libraries used here  
`conda create -n python3 -c conda-forge -c oggm xarray salem xesmf wrf-python geopandas numpy scipy pandas netcdf4 matplotlib pyresample jupyter basemap rasterio affine regionmask pyhdf geoplot memory_profiler jupyterlab nodejs  `
- Activate conda environment  
`conda activate python3  `
- Run python ([Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html) is recommended)  
`jupyter lab  `
  
