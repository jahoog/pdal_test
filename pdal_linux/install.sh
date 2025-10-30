#!/bin/bash
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p ~/miniconda
~/miniconda/bin/conda init bash

source ~/.bashrc

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Create your env
conda create -n prod -y
conda activate prod
conda install -c conda-forge pdal python-pdal gdal -y  # Add your packages

#Single File Conversion
wget -q https://giselevationingov.s3.amazonaws.com/las/statewide/2020/SPW/ql2/IN2020_26550965_12.las
wget -q https://raw.githubusercontent.com/jahoog/pdal_test/refs/heads/main/pdal_linux/las_to_copc.py
python3 las_to_copc.py IN2020_26550965_12.las

# Multi File Conversion from S3 to S3
wget -q https://raw.githubusercontent.com/jahoog/pdal_test/refs/heads/main/pdal_docker/run.py
export S3_SOURCE_BUCKET=jah-br-samp-docs
export S3_SOURCE_FOLDER=las/statewide/2020/SPW/ql2/
export S3_TARGET_BUCKET=jah-br-samp-docs
export S3_TARGET_FOLDER=copc/statewide/2020/SPW/ql2/
python3 run.py
