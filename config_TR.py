
import copy




GT2p0_1 = {

    "TDC_channels":             list(range(5112, 5128)) + list(range(5096, 5112)),
    #"TDC_channels":             list(range(5111, 5095, -1)) + list(range(5127,5111, -1)), # range(5096, 5128)
    "TDC_strips":               list(range(1, 33)), #range(1, 33),
    "TDC_strips_mask":          [], 


    "muonTriggerWindow":        5000,    # DAQ setting for efficiency scans
    "noiseRateTriggerWindow":   5000,  # DAQ setting for noise/rate scans
    "timeWindowReject":         100,    # reject first 100 ns due to bad TDC data
    "muonWindowWidth":          3,      # amount of one-sided sigmas for the time window
    
    # clusterization
    "muonClusterTimeWindow":    15,
    "muonClusterTimeWindowUp":  10,
    "muonClusterTimeWindowDw":  20,
    
    "gammaClusterTimeWindow":   15,
    "gammaClusterTimeWindowUp": 10,
    "gammaClusterTimeWindowDw": 20,

    "stripArea":                109.375,  # active strip area in cm2
    
    "TDC_channel_PMT":          5003, # 5005
    
    "gapIds":                   ["GT2p0_1-TOP", "GT2p0_1-BOT"],
    "gapNames":                 ["TOP", "BOT"],
    "chamberName":              "GT 2mm 1 (vertical strips)",
    "chamberId":                "GT2p0_1",
    
    "sigmoid_HV50pct":          8900,
    "sigmoid_lambda":           0.008,
    "sigmoid_emax":             0.98,
    "sigmoid_HVmin":            8400,
    "sigmoid_HVmax":            12000,
    
    "trigger_config_veto":      {},  
    "trigger_config":           {},
    
    # tracking and geometry
    "nStrips":                  32,
    "stripPitch":               1.452,
    "stripArea":                109.375,
    "xPos":                     -17.66*2.0, # beam-center*pitch
    "zPos":                     1,
                            
    "textHeader":               "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",

}



GT2p0_2 = {



    "TDC_channels":             list(range(5079, 5063, -1)) + list(range(5095,5079, -1)),
    "TDC_strips":               list(range(1, 33)), #range(1, 33),
    "TDC_strips_mask":          [], 


    "muonTriggerWindow":        5000,    # DAQ setting for efficiency scans
    "noiseRateTriggerWindow":   5000,  # DAQ setting for noise/rate scans
    "timeWindowReject":         100,    # reject first 100 ns due to bad TDC data
    "muonWindowWidth":          3,      # amount of one-sided sigmas for the time window


    
    # clusterization
    # clusterization
    "muonClusterTimeWindow":    15,
    "muonClusterTimeWindowUp":  10,
    "muonClusterTimeWindowDw":  20,
    
    "gammaClusterTimeWindow":    15,
    "gammaClusterTimeWindowUp":  10,
    "gammaClusterTimeWindowDw":  20,
    
    "TDC_channel_PMT":          5003, # 5005
    
    "gapIds":                   ["GT2p0_2-TOP", "GT2p0_2-BOT"],
    "gapNames":                 ["TOP", "BOT"],
    "chamberName":              "GT 2mm 2 (horizontal strips)",
    "chamberId":                "GT2p0_2",
    
    "sigmoid_HV50pct":          9100,
    "sigmoid_lambda":           0.008,
    "sigmoid_emax":             0.98,
    "sigmoid_HVmin":            8400,
    "sigmoid_HVmax":            12000,
    
    "trigger_config_veto":      {},
    "trigger_config":           {},

    # tracking and geometry
    "nStrips":                  32,
    "stripPitch":               1.452,
    "stripArea":                109.375,
    "xPos":                     -19.21*1.452, # beam-center*pitch
    "zPos":                     1,
    
    "textHeader":               "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",
}





RE2_2_NPD_BARC_8_C = {

    "TDC_channels":             range(5000+32, 5000+64),
    "TDC_strips":               list(range(1, 33)), #range(1, 33),
    "TDC_strips_mask":          [], # 14=dead, 32=HV noise

    "muonTriggerWindow":        5000,    # DAQ setting for efficiency scans
    "noiseRateTriggerWindow":   5000,  # DAQ setting for noise/rate scans
    "timeWindowReject":         100,    # reject first 100 ns due to bad TDC data
    "muonWindowWidth":          3,      # amount of one-sided sigmas for the time window
    
    "muonClusterTimeWindow":    15,
    "muonClusterTimeWindowUp":  10,
    "muonClusterTimeWindowDw":  20,
    
    "gammaClusterTimeWindow":    15,
    "gammaClusterTimeWindowUp":  10,
    "gammaClusterTimeWindowDw":  20,

    "TDC_channel_PMT":          5003,
    
    "gapIds":                   ["RE2-2-NPD-BARC-8-TN", "RE2-2-NPD-BARC-8-TW", "RE2-2-NPD-BARC-8-BOT"],
    "gapNames":                 ["TN", "TW", "BOT"],
    "chamberName":              "RE2-2-NPD-BARC-8 C",
    "chamberId":                "RE2_2_NPD_BARC_8_C",
    
    "sigmoid_HV50pct":          -1,
    "sigmoid_lambda":           0.007,
    "sigmoid_emax":             -1,
    "sigmoid_HVmin":            8400,
    "sigmoid_HVmax":            12000,
    
    "trigger_config_veto":      {}, 
    "trigger_config":           {},
    
    # tracking and geometry
    "nStrips":                  32,
    "stripPitch":               1.94,
    "stripArea":                93.03,
    "xPos":                     -15.99*1.94, # beam-center*pitch + residual correction
    "zPos":                     2,
    
    "textHeader":               "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",
}


RE2_2_NPD_BARC_8_B = copy.deepcopy(RE2_2_NPD_BARC_8_C)
RE2_2_NPD_BARC_8_B["TDC_channels"] = list(range(1015, 999, -1)) + list(range(1031, 1015, -1))
RE2_2_NPD_BARC_8_B["TDC_strips"] = list(range(1, 33))
RE2_2_NPD_BARC_8_B["TDC_strips_mask"] = [] 
RE2_2_NPD_BARC_8_B["chamberName"] = "RE2-2-NPD-BARC-8 B"
RE2_2_NPD_BARC_8_B["chamberId"] = "RE2_2_NPD_BARC_8_B"
RE2_2_NPD_BARC_8_B["stripArea"] = 121.69



RE2_2_NPD_BARC_8_A = copy.deepcopy(RE2_2_NPD_BARC_8_C)
RE2_2_NPD_BARC_8_A["TDC_channels"] = list(range(15, -1, -1)) + list(range(31, 15, -1))
RE2_2_NPD_BARC_8_A["TDC_strips"] = list(range(1, 33))
RE2_2_NPD_BARC_8_A["TDC_strips_mask"] = [21] # 21=dead
RE2_2_NPD_BARC_8_A["chamberName"] = "RE2-2-NPD-BARC-8 A"
RE2_2_NPD_BARC_8_A["chamberId"] = "RE2_2_NPD_BARC_8_A"
RE2_2_NPD_BARC_8_A["stripArea"] = 157.8



RE2_2_NPD_BARC_9_C = {

    "TDC_channels":             list(range(5063, 5031, -1)),
    "TDC_strips":               list(range(1, 33)), #range(1, 33),
    "TDC_strips_mask":          [], 


    "muonTriggerWindow":        5000,    # DAQ setting for efficiency scans
    "noiseRateTriggerWindow":   5000,  # DAQ setting for noise/rate scans
    "timeWindowReject":         100,    # reject first 100 ns due to bad TDC data
    "muonWindowWidth":          3,      # amount of one-sided sigmas for the time window
    
    "muonClusterTimeWindow":    15,
    "muonClusterTimeWindowUp":  10,
    "muonClusterTimeWindowDw":  20,
    
    "gammaClusterTimeWindow":    15,
    "gammaClusterTimeWindowUp":  10,
    "gammaClusterTimeWindowDw":  20,

    "TDC_channel_PMT":          5003,
    
    "gapIds":                   ["RE2-2-NPD-BARC-9-TN", "RE2-2-NPD-BARC-9-TW", "RE2-2-NPD-BARC-9-BOT"],
    "gapNames":                 ["TN", "TW", "BOT"],
    "chamberName":              "RE2-2-NPD-BARC-9 C",
    "chamberId":                "RE2_2_NPD_BARC_9_C",
    

    "sigmoid_HV50pct":          -1,
    "sigmoid_lambda":           0.007,
    "sigmoid_emax":             -1,
    "sigmoid_HVmin":            8400,
    "sigmoid_HVmax":            12000,
    
    "trigger_config_veto":      {},
    "trigger_config":           {},
    
    
    # tracking and geometry
    "nStrips":                  32,
    "stripPitch":               1.94,
    "stripArea":                93.03,
    "xPos":                     -16.78*1.94+1.32, # beam-center*pitch + residual correction
    "zPos":                     2,
    
    "textHeader":               "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",  
}

RE2_2_NPD_BARC_9_B = copy.deepcopy(RE2_2_NPD_BARC_9_C)
RE2_2_NPD_BARC_9_B["TDC_channels"] = list(range(1047, 1031, -1)) + list(range(1063, 1047, -1))
RE2_2_NPD_BARC_9_B["TDC_strips"] = list(range(1, 33))
RE2_2_NPD_BARC_9_B["TDC_strips_mask"] = [12, 32] # 12=dead, 32=HV noise
RE2_2_NPD_BARC_9_B["chamberName"] = "RE2-2-NPD-BARC-9 B"
RE2_2_NPD_BARC_9_B["chamberId"] = "RE2_2_NPD_BARC_9_B"
RE2_2_NPD_BARC_9_B["stripArea"] = 121.69

RE2_2_NPD_BARC_9_A = copy.deepcopy(RE2_2_NPD_BARC_9_C)
RE2_2_NPD_BARC_9_A["TDC_channels"] = list(range(47, 31, -1)) + list(range(63, 47, -1))
RE2_2_NPD_BARC_9_A["TDC_strips"] = list(range(1, 33))
RE2_2_NPD_BARC_9_A["TDC_strips_mask"] = [32] # 32=HV noise
RE2_2_NPD_BARC_9_A["chamberName"] = "RE2-2-NPD-BARC-9 A"
RE2_2_NPD_BARC_9_A["chamberId"] = "RE2_2_NPD_BARC_9_A"
RE2_2_NPD_BARC_9_A["stripArea"] = 157.8


RE4_2_CERN_166_C = {

    "TDC_channels":             list(range(5000+32, 5000+64)),
    "TDC_strips":               list(range(1, 33)), #range(1, 33),
    "TDC_strips_mask":          [], # seems also 19 was dead for some time, but recovered... do not mask here

    "muonTriggerWindow":        5000,    # DAQ setting for efficiency scans
    "noiseRateTriggerWindow":   5000,  # DAQ setting for noise/rate scans
    "timeWindowReject":         100,    # reject first 100 ns due to bad TDC data
    "muonWindowWidth":          3,      # amount of one-sided sigmas for the time window
    
    "muonClusterTimeWindow":    15,
    "muonClusterTimeWindowUp":  10,
    "muonClusterTimeWindowDw":  20,
    
    "gammaClusterTimeWindow":    15,
    "gammaClusterTimeWindowUp":  10,
    "gammaClusterTimeWindowDw":  20,

    "TDC_channel_PMT":          5003,
    
    "gapIds":                   ["RE4-2-CERN-166-TN", "RE4-2-CERN-166-TW", "RE4-2-CERN-166-BOT"],
    "gapNames":                 ["TN", "TW", "BOT"],
    "chamberName":              "RE4-2-CERN-166 C",
    "chamberId":                "RE4_2_CERN_166_C",
    
    "sigmoid_HV50pct":          -1,
    "sigmoid_lambda":           0.007,
    "sigmoid_emax":             -1,
    "sigmoid_HVmin":            8400,
    "sigmoid_HVmax":            12000,
    
    "trigger_config_veto":      {},
    "trigger_config":           {},

    # tracking and geometry
    "nStrips":                  32,
    "stripPitch":               1.94,
    "stripArea":                93.03,
    "xPos":                     -16.61*1.94+0.89, # beam-center*pitch + residual correction
    "zPos":                     2,
    
    "textHeader":               "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}", 
}


RE4_2_CERN_166_B = copy.deepcopy(RE4_2_CERN_166_C)
RE4_2_CERN_166_B["TDC_channels"] = list(range(1079, 1063, -1)) + list(range(1095, 1079, -1))
RE4_2_CERN_166_B["TDC_strips"] = list(range(1, 33))
RE4_2_CERN_166_B["TDC_strips_mask"] = []
RE4_2_CERN_166_B["chamberName"] = "RE4-2-CERN-166 B"
RE4_2_CERN_166_B["chamberId"] = "RE4_2_CERN_166_B"
RE4_2_CERN_166_B["stripArea"] = 121.69


RE4_2_CERN_166_A = copy.deepcopy(RE4_2_CERN_166_C)
RE4_2_CERN_166_A["TDC_channels"] = list(range(79, 63, -1)) + list(range(95, 79, -1))
RE4_2_CERN_166_A["TDC_strips"] = list(range(1, 33))
RE4_2_CERN_166_A["TDC_strips_mask"] = [] # 32=HV noise
RE4_2_CERN_166_A["chamberName"] = "RE4-2-CERN-166 A"
RE4_2_CERN_166_A["chamberId"] = "RE4_2_CERN_166_A"
RE4_2_CERN_166_A["stripArea"] = 157.8




RE4_2_CERN_165_C = {

    "TDC_channels":             list(range(5000+63, 5031, -1)), # list(range(5000+32, 5000+64))
    "TDC_strips":               list(range(1, 33)), #range(1, 33),
    "TDC_strips_mask":          [], # 22=dead

    "muonTriggerWindow":        5000,    # DAQ setting for efficiency scans
    "noiseRateTriggerWindow":   5000,  # DAQ setting for noise/rate scans
    "timeWindowReject":         100,    # reject first 100 ns due to bad TDC data
    "muonWindowWidth":          3,      # amount of one-sided sigmas for the time window
    
    "muonClusterTimeWindow":    15,
    "muonClusterTimeWindowUp":  10,
    "muonClusterTimeWindowDw":  20,
    
    "gammaClusterTimeWindow":   15,
    "gammaClusterTimeWindowUp": 10,
    "gammaClusterTimeWindowDw": 20,

    "TDC_channel_PMT":          5003,
    
    "gapIds":                   ["RE4-2-CERN-165-TN", "RE4-2-CERN-165-TW", "RE4-2-CERN-165-BOT"],
    "gapNames":                 ["TN", "TW", "BOT"],
    "chamberName":              "RE4-2-CERN-165 C",
    "chamberId":                "RE4_2_CERN_165_C",
    
    "sigmoid_HV50pct":          -1,
    "sigmoid_lambda":           0.007,
    "sigmoid_emax":             -1,
    "sigmoid_HVmin":            8400,
    "sigmoid_HVmax":            12000,
    
    "trigger_config_veto":      {},
    "trigger_config":           {},

    # tracking and geometry
    "nStrips":                  32,
    "stripPitch":               1.94,
    "stripArea":                93.03,
    "xPos":                     -16.38*1.94+0.51, # beam-center*pitch + residual correction
    "zPos":                     2,
    
    "textHeader":               "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",
}


RE4_2_CERN_165_B = copy.deepcopy(RE4_2_CERN_165_C)
RE4_2_CERN_165_B["TDC_channels"] = list(range(1111, 1095, -1)) + list(range(1127, 1111, -1))
RE4_2_CERN_165_B["TDC_strips"] = list(range(1, 33))
RE4_2_CERN_165_B["TDC_strips_mask"] = []
RE4_2_CERN_165_B["chamberName"] = "RE4-2-CERN-165 B"
RE4_2_CERN_165_B["chamberId"] = "RE4_2_CERN_165_B"
RE4_2_CERN_165_B["stripArea"] = 121.69

RE4_2_CERN_165_A = copy.deepcopy(RE4_2_CERN_165_C)
RE4_2_CERN_165_A["TDC_channels"] = list(range(111, 95, -1)) + list(range(127, 111, -1))
RE4_2_CERN_165_A["TDC_strips"] = list(range(1, 33))
RE4_2_CERN_165_A["TDC_strips_mask"] = [] # 32=HV noise
RE4_2_CERN_165_A["chamberName"] = "RE4-2-CERN-165 A"
RE4_2_CERN_165_A["chamberId"] = "RE4_2_CERN_165_A"
RE4_2_CERN_165_A["stripArea"] = 157.8





GT_TRACKING = {

    "chamber_x":            "GT2p0_1",
    "chamber_y":            "GT2p0_2",
    
    "chamberName":          "GT tracking",
    "chamberId":            "GT_TRACKING",
    
    "sigmoid_HV50pct":      -1,
    "sigmoid_lambda":       0.0051,
    "sigmoid_emax":         0.98,
    "sigmoid_HVmin":        6000,
    "sigmoid_HVmax":        8000,
    
    "trigger_config_veto":  {},  
    "trigger_config":       {},    

    # tracking and geometry
    "nStrips"               : 32,
    "stripArea"             : 64,  # active strip area in cm2
    "stripWidth"            : 1.1, # cm
    "stripSpace"            : (41.5-32*1.1)/31., # cm
    
    # tracking geometry
    "xPos"                  : 10., # cm #REFERENCE
    "yPos"                  : 0.0, # cm #REFERENCE
    "zPos"                  : 2, # cm #REFERENCE                  


    "textHeader":           "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",  
}



ALICE_TRACKING = {

    "chamber_x":            "ALICE_X",
    "chamber_y":            "ALICE_Y",
    
    "chamberName":          "ALICE tracking",
    "chamberId":            "ALICE_TRACKING",
    
    "sigmoid_HV50pct":      -1,
    "sigmoid_lambda":       0.0051,
    "sigmoid_emax":         0.98,
    "sigmoid_HVmin":        6000,
    "sigmoid_HVmax":        8000,
    
    "trigger_config_veto":  {},  
    "trigger_config":       {},    

    # tracking and geometry
    "nStrips"               : 32,
    "stripArea"             : 64,  # active strip area in cm2
    "stripWidth"            : 1.1, # cm
    "stripSpace"            : (41.5-32*1.1)/31., # cm
    
    # tracking geometry
    "xPos"                  : 10., # cm #REFERENCE
    "yPos"                  : 0.0, # cm #REFERENCE
    "zPos"                  : 100.0, # cm #REFERENCE
    "shelf"                 : 9,                            


    "textHeader":           "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",  
}







