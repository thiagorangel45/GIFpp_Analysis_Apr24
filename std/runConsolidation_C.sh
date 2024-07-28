#!/bin/bash





cd /home/webdcs/software/webdcs/ANALYSIS/GIFpp_Analysis_Apr24

# 4339 = source OFF reference scan
effcans=( 4796 4797 4798 4799 4800 4801 4802 4803 4804 4805 4806 4807 4808 4810 4813 4814 4815 4816 4817 4818 4821 4826 4827 4828 4829 4830 4831 4832 4833 4835 4837 4839 4844 4846 4847 4848 4849 4851 4853 4854 4855 4857 4858 4859 )
for i in "${effcans[@]}"
do : 


    python analyzeNoiseRateRun.py $i RE2_2_NPD_BARC_8_C
    python analyzeNoiseRateRun.py $i RE2_2_NPD_BARC_9_C
    python analyzeNoiseRateRun.py $i RE4_2_CERN_166_C
    python analyzeNoiseRateRun.py $i RE4_2_CERN_165_C
    
done



