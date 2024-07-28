#!/bin/bash





cd /home/webdcs/software/webdcs/ANALYSIS/GIFpp_Analysis_Apr24

# 4339 = source OFF reference scan
effcans=( 5658 )
for i in "${effcans[@]}"
do : 

	
    python analyzeNoiseRateRun.py $i RE2_2_NPD_BARC_8_A
    python analyzeNoiseRateRun.py $i RE2_2_NPD_BARC_9_A
    python analyzeNoiseRateRun.py $i RE4_2_CERN_166_A
    python analyzeNoiseRateRun.py $i RE4_2_CERN_165_A
    
    python analyzeNoiseRateRun.py $i RE2_2_NPD_BARC_8_B
    python analyzeNoiseRateRun.py $i RE2_2_NPD_BARC_9_B
    python analyzeNoiseRateRun.py $i RE4_2_CERN_166_B
    python analyzeNoiseRateRun.py $i RE4_2_CERN_165_B

    python analyzeNoiseRateRun.py $i RE2_2_NPD_BARC_8_C
    python analyzeNoiseRateRun.py $i RE2_2_NPD_BARC_9_C
    python analyzeNoiseRateRun.py $i RE4_2_CERN_166_C
    python analyzeNoiseRateRun.py $i RE4_2_CERN_165_C
    
done



