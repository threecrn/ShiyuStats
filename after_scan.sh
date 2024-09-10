#!/bin/bash

set -e # Stop on error

cd Comps
python hash.py &
python comp_rates.py -w &
python comp_rates.py -a