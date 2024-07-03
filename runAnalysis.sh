#!/bin/bash

SECONDS=0

cd /home/webdcs/software/webdcs/ANALYSIS/GIFpp_Analysis_Apr24


if [ "$2" == "efficiency" ]; then

        python analyzeEfficiencyRun.py $1 RE2_2_NPD_BARC_8_C
        python analyzeEfficiencyRun.py $1 RE2_2_NPD_BARC_9_C
        python analyzeEfficiencyRun.py $1 RE4_2_CERN_165_C
        python analyzeEfficiencyRun.py $1 RE4_2_CERN_166_C

	python analyzeEfficiencyRun.py $1 KODELE

else

        python analyzeNoiseRateRun.py $1 RE2_2_NPD_BARC_9_A
        python analyzeNoiseRateRun.py $1 RE2_2_NPD_BARC_9_B
        python analyzeNoiseRateRun.py $1 RE2_2_NPD_BARC_9_C

        python analyzeNoiseRateRun.py $1 RE4_2_CERN_166_A
        python analyzeNoiseRateRun.py $1 RE4_2_CERN_166_B
        python analyzeNoiseRateRun.py $1 RE4_2_CERN_166_C

        python analyzeNoiseRateRun.py $1 RE4_2_CERN_165_A
        python analyzeNoiseRateRun.py $1 RE4_2_CERN_165_B
        python analyzeNoiseRateRun.py $1 RE4_2_CERN_165_C

	python analyzeNoiseRateRun.py $1 KODELE

fi

duration=$SECONDS

echo $duration
