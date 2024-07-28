
import copy

RE2_2_NPD_BARC_8_C = {

     "TDC_channels":             range(2000, 2032),
     "TDC_strips":               list(range(1, 33)), #range(1, 33),
     "TDC_strips_mask":          [14, 32], # 14=dead, 32=HV noise

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

     "TDC_channel_PMT":          -1,
     "clusterSizeCut":           6, # streamer probability 

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
     "xPos":                     -15.47*1.94+1.27+0.15, # beam-center*pitch + residual correction
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
RE2_2_NPD_BARC_8_A["TDC_channels"] = list(range(31, 15, -1)) #list(range(15, -1, -1)) + list(range(31, 15, -1))
RE2_2_NPD_BARC_8_A["TDC_strips"] = list(range(1, 17))
RE2_2_NPD_BARC_8_A["TDC_strips_mask"] = [21] # 21=dead
RE2_2_NPD_BARC_8_A["chamberName"] = "RE2-2-NPD-BARC-8 A"
RE2_2_NPD_BARC_8_A["chamberId"] = "RE2_2_NPD_BARC_8_A"
RE2_2_NPD_BARC_8_A["stripArea"] = 157.8


RE2_2_NPD_BARC_9_C = {

    "TDC_channels":             list(range(2063, 2031, -1)),
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

    "TDC_channel_PMT":          -1,
    "clusterSizeCut":           6, # streamer probability 
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
    "xPos":                     -15.47*1.94+1.12-0.03, # beam-center*pitch + residual correction
    "zPos":                     4,

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

    "TDC_channels":             range(2064, 2096),
    "TDC_strips":               list(range(1, 33)), #range(1, 33),
    "TDC_strips_mask":          [26], # seems also 19 was dead for some time, but recovered... do not mask here

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

    "clusterSizeCut":           6, # streamer probability 

    "TDC_channel_PMT":          -1,

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
    "xPos":                     -15.47*1.94+0.93+0.31+0.04, # beam-center*pitch + residual correction
    "zPos":                     3,

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

    "TDC_channels":             list(range(2127, 2095, -1)), # range(2096, 2128),
    "TDC_strips":               list(range(1, 33)), #range(1, 33),
    "TDC_strips_mask":          [22], # 22=dead

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

    "clusterSizeCut":           6, # streamer probability 

    "TDC_channel_PMT":          -1,

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
    "xPos":                     -15.47*1.94+0.77+0.36-0.05, # beam-center*pitch + residual correction
    "zPos":                     5,

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
#RE4_2_CERN_165_A["TDC_channels"] = list(range(111, 95, -1)) + list(range(127, 111, -1))
#RE4_2_CERN_165_A["TDC_strips"] = list(range(1, 33))
# Two lines above are modified since partition A1 is connected to KODEL E
# Only partition A2 is connected, so partition A of CERN 165 has 16 strips only
RE4_2_CERN_165_A["TDC_channels"] = list(range(127, 111, -1))
RE4_2_CERN_165_A["TDC_strips"] = list(range(1, 17))
RE4_2_CERN_165_A["TDC_strips_mask"] = [] # 32=HV noise
RE4_2_CERN_165_A["chamberName"] = "RE4-2-CERN-165 A"
RE4_2_CERN_165_A["chamberId"] = "RE4_2_CERN_165_A"
RE4_2_CERN_165_A["stripArea"] = 157.8

KODELE = {

    "TDC_channels":             list(range(5064, 5064+16)),
    #"TDC_channels":             list(range(5032+15, 5031, -1)) + list(range(5063,5032+15, -1)),
    "TDC_strips":               range(1, 17), #range(1, 33), 17
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

    "clusterSizeCut":           6, # streamer probability 

    "TDC_channel_PMT":          -1.,

    "gapIds":                   ["KODELE-TOP", "KODELE-BOT"],
    "gapNames":                 ["TOP", "BOT"],
    "chamberName":              "KODEL-E (1.4 mm)",
    "chamberId":                "KODELE",


    "sigmoid_HV50pct":          -1,
    "sigmoid_lambda":           0.0051,
    "sigmoid_emax":             -1,
    "sigmoid_HVmin":            5800,
    "sigmoid_HVmax":            10000,

    # tracking and geometry
    "nStrips":                  16,
    "stripPitch":               2.0,
    #"stripWidth":               1.8,
    "stripArea":                110.25, #128 # active strip area in cm2
    #"xPos":                     -21.76-1.25, # beam-center*pitch + residual correction
    #"zPos":                     2,

    "trigger_config_veto":      {},
    "trigger_config":           {},

    "textHeader":           "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",

}



KODELH = { # TDC4 A1 and TDC4 D2

    "TDC_channels":             list(range(4000,4000+16))+list(range(4112, 4112+16)),     
    #Lista dos canais TDC (Time Digital Converter) utilizados por essa camara que vai de 0 - 4127.
    
    "TDC_strips":               list(range(1, 33)),
    #Define quais strips do detector estão sendo lidas de 1 a 32.
    
    "TDC_strips_mask":          [],
    #Define quais strips do detector estão sendo ignoradas ou filtradas (eu acho).
    
    "muonTriggerWindow":        5000,    
    #Define o intervalo de tempo em que um evento de múon pode ser registrado, tipo no experimento de meia vida do múon
    #nesse caso é de 5000 nanosegundos (eu acho que deve ser o mesmo que o do CBPF) e é um valor fixo.
    
    "noiseRateTriggerWindow":   5000,  
    #Define o intervalo de tempo em que um evento de um ruido, mas acho que esse valor deveria ser maior não? 
    #pq caso contrário o ruído vai ter a mesma janela de tempo do múon?

    "timeWindowReject":         100,        
    #Ignora um período inicial de dados que pode conter erros, como está na apresentação.

    "muonWindowWidth":          3,      
    #valor fixo para a janela de múon que será feita usando o 6 vezes o desvio padrão, de um lado e do outro.
    
    # clusterization
    "muonClusterTimeWindow":    15,
    #Define o intervalo de tempo para agrupar sinais de múons próximos no detector.

    "muonClusterTimeWindowUp":  10,
    #??

    "muonClusterTimeWindowDw":  20,
    #??

    "gammaClusterTimeWindow":    15,
    #Define o intervalo de tempo para agrupar sinais de gamas próximos.
    
    "gammaClusterTimeWindowUp":  10,
    #deve ser o msm q o outro??

    "gammaClusterTimeWindowDw":  20,
    #deve ser o msm q o outro??

    "TDC_channel_PMT":          -1, # 5005
    #Canal TDC associado ao PMT (Photomultiplier Tube).

    "gapIds":                   ["KODEL-H-TOP", "KODEL-H-BOT"],
    "gapNames":                 ["KODEL-H TOP", "KODEL-H BOT"],
    "gapAreas":                 [50*50,50*50],
    "chamberName":              "KODEL-H (1.4 mm)",
    "chamberId":                "KODELH",

    "sigmoid_HV50pct":          -1, # parametro que deve ser alterado depois e que varia com cada tomada de dados
    "sigmoid_lambda":           0.006, # parametro da inclinaçao da funcao sigmoid
    "sigmoid_emax":             -1, # parametro que deve ser alterado depois e que varia com cada tomada de dados
    "sigmoid_HVmin":            4000, # representa os valore mínimo de alta tensão (HV) que são aplicados as câmaras. 
    "sigmoid_HVmax":            10000, # representa os valore máximo de alta tensão (HV) que são aplicados as câmaras.

    "trigger_config_veto":      {}, #?
    "trigger_config":           {}, #?

    # tracking and geometry
    "nStrips":                  32,
    "stripPitch":               1.27,
    "stripArea":                77.7,
    "xPos":                     -16.11*0.5-3.17, # beam-center*pitch
    "zPos":                     5,
    
    "textHeader":               "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",
    "clusterSizeCut":           6, # streamer prob
}


KODEL2D_X = { #TDC4 B1 adn TDC3 B2

    "TDC_channels":             range(4032, 4032+32), # left -> right
    "TDC_strips":               range(1, 33), #range(1, 33), 17
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

    "stripArea":                64,  # active strip area in cm2
    "nStrips"                   : 32,

    "TDC_channel_PMT":          -1,

    "gapIds":                   ["KODEL-2D-DG"],
    "gapAreas":                 [2866.36],
    "gapNames":                 ["KODEL2D GAP"],
    "chamberName":              "KODEL2D X (vertical strips)",
    "chamberId":                "KODEL2D_X",

    "sigmoid_HV50pct":          -1,
    "sigmoid_lambda":           0.0051,
    "sigmoid_emax":             0.98,
    "sigmoid_HVmin":            6000,
    "sigmoid_HVmax":            8000,

    # tracking and geometry
    "nStrips":                  32,
    "stripPitch":               1,
    "stripArea":                64,
    "xPos":                     -15.37*1, # beam-center*pitch
    "zPos":                     1,

    "trigger_config_veto":      {},
    "trigger_config":           {},

    "textHeader":               "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}",
}

