#!/bin/sh
# Run everything in order. Order matters: Part D first (Part A reuses the bubble chart).
set -e
cd "$(dirname "$0")"
python3 partD_bubble.py
python3 partD_pcp.py
python3 partD_choropleth.py
python3 partB_decisions.py > /dev/null
python3 partC_maps.py
python3 partA_charts.py > /dev/null
python3 build_partA_diagnosis.py
python3 build_partE.py
echo "all done"
