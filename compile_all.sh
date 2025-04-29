#!/bin/bash

set -e # Stop on error

if [[ -d "data/raw_csvs_real" ]]; then
  cd enka.network
  python combine.py
  cd ../Comps
  python combine_raw_chars.py
  python hash.py
else
  cd Comps
fi

echo ""
echo "SD"
python comp_rates.py -w &
python comp_rates.py -f &
python comp_rates.py -a
echo ""
echo "Move SD"
python move.py

echo ""
echo "DA"
python comp_rates.py -da -w &
python comp_rates.py -da -f &
python comp_rates.py -da -a
echo ""
echo "Move DA"
python move.py -da

echo ""
echo "SD stats"
cd ../enka.network
python stats.py
cd ../Comps
python move.py

echo ""
echo "DA stats"
cd ../enka.network
python stats.py -da
cd ../Comps
python move.py -da

python combine_char.py
python combine_char.py -da

python copyfiles.py
python copyfiles.py -da
