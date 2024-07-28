#!/bin/bash





cd /home/webdcs/software/webdcs/ANALYSIS/GIFpp_Analysis_Apr24


effcans=( 4796 4797 4798 4799 4800 4801 4802 4803 4804 4805 4806 4807 4808 4810 4813 4814 4815 4816 4817 4818 4821 4826 4827 4828 4829 4830 4831 4832 4833 4835 4837 4839 4844 4846 4847 4848 4849 4851 4853 4854 4855 4857 4858 4859 )
for i in "${effcans[@]}"
do : 

	#python analyzeEfficiencyRun.py $i SHIP_X
	#python analyzeEfficiencyRun.py $i SHIP_Y
    
	python analyzeNoiseRateRun.py $i SHIP_X
	python analyzeNoiseRateRun.py $i SHIP_Y
	
done
