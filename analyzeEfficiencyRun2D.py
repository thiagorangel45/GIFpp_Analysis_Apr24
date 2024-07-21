
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzer2D as an2D
import analyzer as an
import config
import functions

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


if __name__ == "__main__":

    scanid = int(sys.argv[1])
    chamber = sys.argv[2]

    ## tag: all the plots and results will be saved in a directory with its tagname
    tag = sys.argv[2]
    
    try:
        cfg = getattr(config, tag)
    except:
        sys.exit("Tag %s not found in config file" % tag)
    
    
    ## dir: ROOT directory of all raw data files 
    dir = "/Users/thiagorangel/GIFpp_Analysis_Apr24" 
    
    
    ##############################################################################################
    outputdir = "%s/ANALYSIS/%s/" % (dir, tag)
    if os.path.exists(outputdir): shutil.rmtree(outputdir) # delete output dir, if exists
    if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir
    
    
    HVeff, HVPoint = [], [] # storage of HV eff points
    out = {}
    out["chamberName"] = cfg['chamberName']
    out["scanid"] = scanid
    
    iMonMax = -999
    
    
    # prepare the graphs
    graphs = {}
    graphNames = ["efficiencyRaw", "efficiencyMuon"]

    for gr in graphNames:
    
        graphs[gr + "_HVPoint"] = ROOT.TGraphErrors()
        graphs[gr + "_HVPoint"].SetLineWidth(2)
        graphs[gr + "_HVPoint"].SetLineColor(ROOT.kBlue)
        graphs[gr + "_HVPoint"].SetMarkerStyle(20)
        graphs[gr + "_HVPoint"].SetMarkerColor(ROOT.kBlue)


        

    
    CAEN_files = glob.glob("%s/Scan%06d_HV*_CAEN.root" % (dir, scanid))
    if len(CAEN_files) == 0: sys.exit("No CAEN ROOT files in directory") 
    CAEN_files.sort(key=functions.natural_keys) # sort on file name, i.e. according to HV points

    ## analyze highest point for time window correction (for both directions)
    HVPoint_ = int(os.path.basename(CAEN_files[-1]).split("_")[1][2:])
    muonWindowMean_x, muonWindowSigma_x = functions.getMuonTimeWindowHV(scanid, HVPoint_, cfg["chamber_x"])
    muonWindowMean_y, muonWindowSigma_y = functions.getMuonTimeWindowHV(scanid, HVPoint_, cfg["chamber_y"])
    
    
    cfg_x = getattr(config, cfg["chamber_x"])
    cfg_y = getattr(config, cfg["chamber_y"])

    i = -1
    for j,CAENFile in enumerate(CAEN_files):
    
        i += 1
        #if i == 1: continue
        
        HVPoint_ = int(os.path.basename(CAENFile).split("_")[1][2:])
        print("Analyze", HVPoint_)
        HVPoint.append(HVPoint_)
        saveDir = outputdir + "HV%d/" % HVPoint_
        if not os.path.exists(saveDir): os.makedirs(saveDir)
        out["HV%d" % HVPoint_] = {}
        
        if not os.path.exists("%s/output.json" % (saveDir)) and True:
        
            analyzer = an2D.Analyzer2D(dir, saveDir, scanid, HVPoint_, "efficiency")
            analyzer.loadConfig(cfg, cfg_x, cfg_y)
            analyzer.setVerbose(1)
            analyzer.set1DAnalyzers(muonWindowMean_x, muonWindowSigma_x, muonWindowMean_y, muonWindowSigma_y)
            analyzer.efficiency()
            analyzer.stripProfile2D()
            analyzer.eventDisplay2D(100)
            analyzer.write()
            del analyzer
        
        
        # load CAEN for HV and currents
        CAEN = ROOT.TFile(CAENFile)
        HVeff_ = -999 # SG mode: HV can be low, so search for the max HV
        for k,gap in enumerate(getattr(config, cfg["chamber_x"])['gapIds']):  
        
            imon = CAEN.Get("Imon_%s" % gap).GetMean()
            imon_err = CAEN.Get("Imon_%s" % gap).GetStdDev()
            hv_ = CAEN.Get("HVeff_%s" % gap).GetMean()
            if hv_ > HVeff_: HVeff_ = hv_
            if imon > iMonMax: iMonMax = imon
            
            out["HV%d" % HVPoint_]["imon_%s" % gap] = imon
            out["HV%d" % HVPoint_]["imon_err_%s" % gap] = imon_err
            out["HV%d" % HVPoint_]["hveff_%s" % gap] = hv_
        
        for k,gap in enumerate(getattr(config, cfg["chamber_y"])['gapIds']):  
        
            imon = CAEN.Get("Imon_%s" % gap).GetMean()
            imon_err = CAEN.Get("Imon_%s" % gap).GetStdDev()
            hv_ = CAEN.Get("HVeff_%s" % gap).GetMean()
            if hv_ > HVeff_: HVeff_ = hv_
            if imon > iMonMax: iMonMax = imon
            
            out["HV%d" % HVPoint_]["imon_%s" % gap] = imon
            out["HV%d" % HVPoint_]["imon_err_%s" % gap] = imon_err
            out["HV%d" % HVPoint_]["hveff_%s" % gap] = hv_
        
        CAEN.Close()  
        HVPoint.append(HVPoint_)
        HVeff.append(HVeff_)


        # load analyzer results
        with open("%s/output.json" % (saveDir)) as f_in: analyzerResults = json.load(f_in)
        analyzerResults = analyzerResults['output_parameters']
        
        for gr in graphNames:
        
            a = 1.
            if "efficiency" in gr: a = 100.
            
            if not gr in analyzerResults: continue
            graphs[gr + "_HVPoint"].SetPoint(i, HVPoint_, a*analyzerResults[gr])
            graphs[gr + "_HVPoint"].SetPointError(i, 0, a*analyzerResults[gr + "_err"])
            
            out["HV%d" % HVPoint_][gr] = a*analyzerResults[gr]
            out["HV%d" % HVPoint_][gr + "_err"] = a*analyzerResults[gr + "_err"]
      
    # pltos vs HFeff to be implemented
    # plot all vs. HVPoint
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()

 
    xMin_HVPoint = 0
    xMax_HVPoint = max(HVPoint)+1
        
    ############################
    # muon efficiency
    ############################  
    c.Clear()
    g = graphs['efficiencyMuon_HVPoint']
    yMin = math.floor(0.8/10*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*10
    dummy = functions.dummyHist("HV Point", "Muon efficiency (%)", xMin_HVPoint, xMax_HVPoint, yMin, 110)
    dummy.Draw("HIST")
    g.Draw("SAME LP")
        
    line = ROOT.TLine(xMin_HVPoint, 100, xMax_HVPoint, 100)
    line.SetLineColor(ROOT.kRed)
    line.SetLineWidth(2)
    line.Draw("SAME")  

    params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
    params.DrawLatex(0.16, 0.85, "Muon efficiency")
    functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
    c.SaveAs("%s/efficiencyMuon.png" % outputdir)
    c.SaveAs("%s/efficiencyMuon.pdf" % outputdir)


    ############################
    # raw efficiency
    ############################    
    c.Clear()
    g = graphs['efficiencyRaw_HVPoint']
    yMin = math.floor(0.8/10*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*10
    dummy = functions.dummyHist("HV Point", "Raw efficiency (%)", xMin_HVPoint, xMax_HVPoint, yMin, 110)
    dummy.Draw("HIST")
    g.Draw("SAME LP")
        
    line = ROOT.TLine(xMin_HVPoint, 100, xMax_HVPoint, 100)
    line.SetLineColor(ROOT.kRed)
    line.SetLineWidth(2)
    line.Draw("SAME")  

    params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
    params.DrawLatex(0.16, 0.85, "Raw efficiency")
    functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
    c.SaveAs("%s/efficiencyRaw.png" % outputdir)
    c.SaveAs("%s/efficiencyRaw.pdf" % outputdir)

    # write results to file
    with open("%s/output.json" % outputdir, 'w') as fp: json.dump(out, fp, indent=4)
