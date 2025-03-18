#!/bin/bash

set -e # Stop on error

cd Comps
python hash.py

echo ""
echo "SD"
python comp_rates.py -w &
python comp_rates.py -f &
python comp_rates.py -a
echo ""
echo "Move SD"
python move.py
python combine_char.py

echo ""
echo "DA"
python comp_rates.py -da -w &
python comp_rates.py -da -f &
python comp_rates.py -da -a
echo ""
echo "Move DA"
python move.py -da
python combine_char.py -da