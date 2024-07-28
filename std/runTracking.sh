#!/bin/bash

SECONDS=0

cd /home/webdcs/software/webdcs/ANALYSIS/GIFpp_Analysis_Apr24

#python analyzeTracking1D.py 5326 # SOURCE OFF -- BAD 
python analyzeTracking1D.py 5311 # SOURCE OFF -- GOOD

#python analyzeTracking1D.py 5338 # ABS 1, als Downstream 1
#python analyzeTracking1D.py 5329 # ABS 1
#python analyzeTracking1D.py 5330 # ABS 1.5
#python analyzeTracking1D.py 5335 # ABS 2.2

#python analyzeTracking1D.py 5328 # ABS 3.3
#python analyzeTracking1D.py 5331 # ABS 4.6 
#python analyzeTracking1D.py 5332 # ABS 6.9
#python analyzeTracking1D.py 5327 # ABS 10
#python analyzeTracking1D.py 5334 # ABS 22
#python analyzeTracking1D.py 5337 # ABS 33 
#python analyzeTracking1D.py 5336 # ABS 69
#python analyzeTracking1D.py 5333 # ABS 100



#python analyzeTracking1D.py 5315 
#python analyzeTracking1D.py 5325
#python analyzeTracking1D.py 5350

#python analyzeTracking1D.py 4792

duration=$SECONDS

echo $duration
