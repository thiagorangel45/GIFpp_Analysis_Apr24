
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzer as an
import config
import functions

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


if __name__ == "__main__":

    scanid =  int(sys.argv[1])
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
    if not os.path.exists(outputdir): os.makedirs(outputdir) # make output dir
    
    
    HVeff, HVPoint = [], [] # storage of HV eff points
    out = {}
    out["chamberName"] = cfg['chamberName']
    out["scanid"] = scanid
    
    iMonMax = -999

    # prepare TGraphs
    graphs, graphs_err = {}, {} # graphs holding the parameters as function of HVeff or the HVPoint
    graphNames = ["muonCLS", "muonCMP", "gammaCLS", "gammaCMP", "efficiencyRaw", "efficiencyMuon", "efficiencyFake", "efficiencyMuon_corrected", "noiseGammaRate", "muonStreamerProbability", "gammaStreamerProbability"]

    for gr in graphNames:
    
        graphs[gr + "_HVPoint"] = ROOT.TGraphErrors()
        graphs_err[gr + "_HVPoint"] = ROOT.TGraphErrors()
        
        graphs[gr + "_HVeff"] = ROOT.TGraphErrors()
        graphs_err[gr + "_HVeff"] = ROOT.TGraphErrors()
        
    for gr in graphs:
    
        graphs[gr].SetLineWidth(2)
        graphs[gr].SetLineColor(ROOT.kBlue)
        graphs[gr].SetMarkerStyle(20)
        graphs[gr].SetMarkerColor(ROOT.kBlue)
    
    graphs_iMon, graphs_iMon_err  = {}, {}
    for k,gap in enumerate(cfg['gapIds']):
    
        graphs_iMon["imon_%s_HVPoint" % gap] = ROOT.TGraphErrors()
        graphs_iMon_err["imon_%s_HVPoint" % gap] = ROOT.TGraphErrors()
        
        graphs_iMon["imon_%s_HVeff" % gap] = ROOT.TGraphErrors()
        graphs_iMon_err["imon_%s_HVeff" % gap] = ROOT.TGraphErrors()
        
        graphs_iMon["imon_%s_HVPoint" % gap].SetLineWidth(2)
        graphs_iMon["imon_%s_HVPoint" % gap].SetLineColor(functions.colors[k])
        graphs_iMon["imon_%s_HVPoint" % gap].SetMarkerStyle(20)
        graphs_iMon["imon_%s_HVPoint" % gap].SetMarkerColor(functions.colors[k])
        
        graphs_iMon["imon_%s_HVeff" % gap].SetLineWidth(2)
        graphs_iMon["imon_%s_HVeff" % gap].SetLineColor(functions.colors[k])
        graphs_iMon["imon_%s_HVeff" % gap].SetMarkerStyle(20)
        graphs_iMon["imon_%s_HVeff" % gap].SetMarkerColor(functions.colors[k])
        


    CAEN_files = glob.glob("%s/Scan%06d_HV*_CAEN.root" % (dir, scanid))
    if len(CAEN_files) == 0: sys.exit("No CAEN ROOT files in directory") 
    CAEN_files.sort(key=functions.natural_keys) # sort on file name, i.e. according to HV points

    ## analyze highest point for time window correction
    HVPoint_ = int(os.path.basename(CAEN_files[-1]).split("_")[1][2:])
    muonWindowMean, muonWindowSigma = functions.getMuonTimeWindowHV(scanid, HVPoint_, tag)
    print(muonWindowMean, muonWindowSigma)

    i=-1
    for j,CAENFile in enumerate(CAEN_files):
        #if j != 5: continue
        #if j == 2 or j == 4: continue
        #if j != 11: continue
        i += 1
        #if i == 1: continue
        
        HVPoint_ = int(os.path.basename(CAENFile).split("_")[1][2:])
        print("Analyze HV point %d " % HVPoint_)
        #if HVPoint_ != 9: continue
        #if HVPoint_ == 3 or HVPoint_ == 5: continue
       
        saveDir = outputdir + "HV%d/" % HVPoint_
        if not os.path.exists(saveDir): os.makedirs(saveDir)
        out["HV%d" % HVPoint_] = {}

        if not os.path.exists("%s/output.json" % (saveDir)) or True:
        
            analyzer = an.Analyzer(dir, saveDir, scanid, HVPoint_, "efficiency")
            analyzer.loadConfig(cfg)
            analyzer.setVerbose(1)
            
            #analyzer.timeProfileChannels(xMin=-300, xMax=0)
            analyzer.timeProfile(muonWindowMean, muonWindowSigma)
            #analyzer.timeProfile()
            analyzer.timeStripProfile2D()
            analyzer.clusterization("muon") # do first clusterization
            analyzer.clusterization("gamma")
            analyzer.streamerProbability()
            analyzer.efficiency()
            analyzer.stripProfile(True) # arg = beamFit
            #analyzer.eventDisplay2D(100, "y")
            analyzer.eventDisplay(-1) # args: amount of events to be plotted (randomly). -1: all events
            analyzer.write() # write all results to JSON file
            del analyzer
    
      
        # load CAEN for HV and currents
        CAEN = ROOT.TFile(CAENFile)
        HVeff_ = -999 # SG mode: HV can be low, so search for the max HV
        for k,gap in enumerate(cfg['gapIds']):
        
            try: CAEN.Get("Imon_%s" % gap).GetMean()
            except: continue
        
            imon = CAEN.Get("Imon_%s" % gap).GetMean()
            imon_err = CAEN.Get("Imon_%s" % gap).GetStdDev()
            hv_ = CAEN.Get("HVeff_%s" % gap).GetMean()
            if hv_ > HVeff_: HVeff_ = hv_
            if imon > iMonMax: iMonMax = imon
  
            graphs_iMon["imon_%s_HVeff" % gap].SetPoint(i, hv_, imon)
            graphs_iMon["imon_%s_HVeff" % gap].SetPointError(i, 0, imon_err)
            graphs_iMon_err["imon_%s_HVeff" % gap].SetPoint(i, hv_, imon_err)
            
            graphs_iMon["imon_%s_HVPoint" % gap].SetPoint(i, HVPoint_, imon)
            graphs_iMon["imon_%s_HVPoint" % gap].SetPointError(i, 0, imon_err)
            graphs_iMon_err["imon_%s_HVPoint" % gap].SetPoint(i, HVPoint_, imon_err)
            
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
            if "StreamerProbability" in gr: a = 100.
          
            if not gr in analyzerResults: continue
            graphs[gr + "_HVeff"].SetPoint(i, HVeff_, a*analyzerResults[gr])
            graphs[gr + "_HVPoint"].SetPoint(i, HVPoint_, a*analyzerResults[gr])
            out["HV%d" % HVPoint_][gr] = a*analyzerResults[gr]
            
            
            if not gr + "_err" in analyzerResults: continue
            graphs[gr + "_HVeff"].SetPointError(i, 0, a*analyzerResults[gr + "_err"])
            graphs_err[gr + "_HVeff"].SetPoint(i, HVeff_, a*analyzerResults[gr + "_err"])
            graphs[gr + "_HVPoint"].SetPointError(i, 0, a*analyzerResults[gr + "_err"])
            graphs_err[gr + "_HVPoint"].SetPoint(i, HVeff_, a*analyzerResults[gr + "_err"])
            out["HV%d" % HVPoint_][gr + "_err"] = a*analyzerResults[gr + "_err"]
            

        
        
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()


   

    # check if HVeff are all the same --> if so, plot all quantities vs. HV point
    if HVeff[0] != HVeff[-1]:
    
        xMin_, xMax_ = min(HVeff), max(HVeff)
    
        ############################
        # muon efficiency + fit
        ############################  
        c.Clear()
        g = graphs['efficiencyMuon_HVeff']
        dummy = functions.dummyHist("HV_{eff} (V)", "Muon efficiency (%)", xMin_, xMax_, 0, 100)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        fitted_muon, emax_muon, lam_muon, hv50_muon, WP_muon, emax_err_muon, lam_err_muon, hv50_err_muon, WP_err_muon = functions.sigmoidFit(cfg, g)

        out["emax_muon"] = emax_muon
        out["lam_muon"] = lam_muon
        out["hv50_muon"] = hv50_muon
        out["WP_muon"] = WP_muon
        out["emax_err_muon"] = emax_err_muon
        out["lam_err_muon"] = lam_err_muon
        out["hv50_err_muon"] = hv50_err_muon
        out["WP_err_muon"] = WP_err_muon
        out["eff_WP_muon"] = fitted_muon.Eval(WP_muon)
        
        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.035)
        latex.SetTextColor(1)
        latex.SetTextAlign(13)
        latex.DrawLatex(0.6, 0.5, "#epsilon_{max} = %.1f %%" % (emax_muon))
        latex.DrawLatex(0.6, 0.45, "#lambda = %.3f" % lam_muon)
        latex.DrawLatex(0.6, 0.4, "HV_{50%%} = %.1f V" % hv50_muon)
        latex.DrawLatex(0.6, 0.35, "WP = %.1f V" % WP_muon)
        latex.DrawLatex(0.6, 0.3, "eff(WP) = %.1f %%" % (fitted_muon.Eval(WP_muon)))
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Muon efficiency")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/efficiencyMuon.png" % outputdir)
        c.SaveAs("%s/efficiencyMuon.pdf" % outputdir)
        
        
    
        ############################
        # raw efficiency + fit
        ############################    
        c.Clear()
        g = graphs['efficiencyRaw_HVeff']
        dummy = functions.dummyHist("HV_{eff} (V)", "Raw efficiency (%)", xMin_, xMax_, 0, 100)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        fitted_raw, emax_raw, lam_raw, hv50_raw, WP_raw, emax_err_raw, lam_err_raw, hv50_err_raw, WP_err_raw = functions.sigmoidFit(cfg, g)
        
        out["emax_raw"] = emax_raw
        out["lam_raw"] = lam_raw
        out["hv50_raw"] = hv50_raw
        out["WP_raw"] = WP_raw
        out["emax_err_raw"] = emax_err_raw
        out["lam_err_raw"] = lam_err_raw
        out["hv50_err_raw"] = hv50_err_raw
        out["WP_err_raw"] = WP_err_raw
        out["eff_WP_raw"] = fitted_raw.Eval(WP_raw)

        
        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.035)
        latex.SetTextColor(1)
        latex.SetTextAlign(13)
        latex.DrawLatex(0.6, 0.5, "#epsilon_{max} = %.1f %%" % (emax_raw))
        latex.DrawLatex(0.6, 0.45, "#lambda = %.3f" % lam_raw)
        latex.DrawLatex(0.6, 0.4, "HV_{50%%} = %.1f V" % hv50_raw)
        latex.DrawLatex(0.6, 0.35, "WP = %.1f V" % WP_raw)
        latex.DrawLatex(0.6, 0.3, "eff(WP) = %.1f %%" % (fitted_raw.Eval(WP_raw)))
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Raw efficiency")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/efficiencyRaw.png" % outputdir)
        c.SaveAs("%s/efficiencyRaw.pdf" % outputdir)
        
        
        ############################
        # muon corrected efficiency
        ############################      
        c.Clear()
        g = graphs['efficiencyMuon_corrected_HVeff']
        dummy = functions.dummyHist("HV_{eff} (V)", "Muon efficiency, corrected (%)", xMin_, xMax_, 0, 100)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        fitted_muon_corr, emax_muon_corr, lam_muon_corr, hv50_muon_corr, WP_muon_corr, emax_err_muon_corr, lam_err_muon_corr, hv50_err_muon_corr, WP_err_muon_corr = functions.sigmoidFit(cfg, g)
        
                
        out["emax_muon_corr"] = emax_muon_corr
        out["lam_muon_corr"] = lam_muon_corr
        out["hv50_muon_corr"] = hv50_muon_corr
        out["WP_muon_corr"] = WP_muon_corr
        out["emax_err_muon_corr"] = emax_err_muon_corr
        out["lam_err_muon_corr"] = lam_err_muon_corr
        out["hv50_err_muon_corr"] = hv50_err_muon_corr
        out["WP_err_muon_corr"] = WP_err_muon_corr
        out["eff_WP_muon_corr"] = fitted_muon_corr.Eval(WP_muon_corr)


        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.035)
        latex.SetTextColor(1)
        latex.SetTextAlign(13)
        latex.DrawLatex(0.6, 0.5, "#epsilon_{max} = %.1f %%" % (emax_muon_corr))
        latex.DrawLatex(0.6, 0.45, "#lambda = %.3f" % lam_muon_corr)
        latex.DrawLatex(0.6, 0.4, "HV_{50%%} = %.1f V" % hv50_muon_corr)
        latex.DrawLatex(0.6, 0.35, "WP = %.1f V" % WP_muon_corr)
        latex.DrawLatex(0.6, 0.3, "eff(WP) = %.1f %%" % (fitted_muon_corr.Eval(WP_muon_corr)))
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Muon efficiency, corrected")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/efficiencyMuon_corrected.png" % outputdir)
        c.SaveAs("%s/efficiencyMuon_corrected.pdf" % outputdir)
        
        
        ############################
        # fake efficiency
        ############################    
        c.Clear()
        g = graphs['efficiencyFake_HVeff']
        yMax = math.ceil(1.2/2*ROOT.TMath.MaxElement(g.GetN(), g.GetY()))*2
        yMin = math.floor(0.8/2*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*2
        dummy = functions.dummyHist("HV_{eff} (V)", "Fake/gamma efficiency (%)", xMin_, xMax_, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        out["eff_fake_WP_raw"] = g.Eval(WP_raw)
        out["eff_fake_WP_muon"] = g.Eval(WP_muon)
        out["eff_fake_WP_muon_corr"] = g.Eval(WP_muon_corr)
        
        out["eff_fake_err_WP_raw"] = graphs_err['efficiencyFake_HVeff'].Eval(WP_raw)
        out["eff_fake_err_WP_muon"] = graphs_err['efficiencyFake_HVeff'].Eval(WP_muon)
        out["eff_fake_err_WP_muon_corr"] = graphs_err['efficiencyFake_HVeff'].Eval(WP_muon_corr)

        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Fake/gamma efficiency")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/efficiencyFake.png" % outputdir)
        c.SaveAs("%s/efficiencyFake.pdf" % outputdir)
        
        
        ############################
        # streamer probability
        ############################    
        c.Clear()
        g_muon = graphs['muonStreamerProbability_HVeff']
        g_gamma = graphs['gammaStreamerProbability_HVeff']
        g_gamma.SetLineColor(ROOT.kRed)
        g_gamma.SetMarkerColor(ROOT.kRed)
        yMax = math.ceil(1.5/2*max([ROOT.TMath.MaxElement(g_muon.GetN(), g_muon.GetY()), ROOT.TMath.MaxElement(g_gamma.GetN(), g_gamma.GetY())]))*2
        if yMax > 100: yMax=100
        yMin = 0
        yMin = 0
        dummy = functions.dummyHist("HV_{eff} (V)", "Streamer probability (%)", xMin_, xMax_, yMin, yMax)
        dummy.Draw("HIST")
        g_muon.Draw("SAME LP")
        g_gamma.Draw("SAME LP")
        
        leg = ROOT.TLegend(0.15, 0.75, 0.6, 0.88)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetFillColor(0)
        leg.SetTextSize(0.035)
        
        leg.AddEntry(g_muon, "Muon streamer probability", "LP")
        leg.AddEntry(g_gamma, "Gamma streamer probability", "LP")
        leg.Draw("SAME")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/streamerProbability.png" % outputdir)
        c.SaveAs("%s/streamerProbability.pdf" % outputdir)
        
        ############################
        # gamma rate
        ############################    
        c.Clear()
        g = graphs['noiseGammaRate_HVeff']
        yMax = math.ceil(1.5/2*ROOT.TMath.MaxElement(g.GetN(), g.GetY()))*2
        yMin = math.floor(0.5/2*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*2
        dummy = functions.dummyHist("HV_{eff} (V)", "Gamma rate (Hz/cm^{2})", xMin_, xMax_, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        out["noiseGammaRate_WP_raw"] = g.Eval(WP_raw)
        out["noiseGammaRate_WP_muon"] = g.Eval(WP_muon)
        out["noiseGammaRate_WP_muon_corr"] = g.Eval(WP_muon_corr)
        

        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Gamma rate")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/noiseGammaRate.png" % outputdir)
        c.SaveAs("%s/noiseGammaRate.pdf" % outputdir)
        
        
        ############################
        # gap currents
        ############################
        c.Clear()
        dummy = functions.dummyHist("HV_{eff} (V)", "Current (#muA)", xMin_, xMax_, 0, 2*iMonMax)
        dummy.Draw("HIST")
        
        leg = ROOT.TLegend(0.15, 0.88-0.05*len(cfg['gapIds']), 0.9, 0.9)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetFillColor(0)
        leg.SetTextSize(0.035)
        
        for k,gap in enumerate(cfg['gapIds']):
       
            graphs_iMon["imon_%s_HVeff" % gap].Draw("SAME LP")
            
            
            out["imon_%s" % gap + "_WP_raw"] = graphs_iMon["imon_%s_HVeff" % gap].Eval(WP_raw)
            out["imon_%s" % gap + "_WP_muon"] = graphs_iMon["imon_%s_HVeff" % gap].Eval(WP_muon)
            out["imon_%s" % gap + "_WP_muon_corr"] = graphs_iMon["imon_%s_HVeff" % gap].Eval(WP_muon_corr)
            
            leg.AddEntry(graphs_iMon["imon_%s_HVeff" % gap], "%s (WP %.2f #muA)" % (cfg['gapNames'][k], out["imon_%s" % gap + "_WP_muon"]), "LP")
        
        leg.Draw("SAME")
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/gapCurrents.png" % outputdir)
        c.SaveAs("%s/gapCurrents.pdf" % outputdir)
           
           

        
        ############################
        # muon cluster size
        ############################
        c.Clear()
        g = graphs['muonCLS_HVeff']
        yMax = 1.5*ROOT.TMath.MaxElement(g.GetN(), g.GetY())
        yMin = 0.5*ROOT.TMath.MinElement(g.GetN(), g.GetY())
        dummy = functions.dummyHist("HV_{eff} (V)", "Muon cluster size", xMin_, xMax_, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        out["muon_CLS_WP_raw"] = g.Eval(WP_raw)
        out["muon_CLS_WP_muon"] = g.Eval(WP_muon)
        out["muon_CLS_WP_muon_corr"] = g.Eval(WP_muon_corr)
        
        out["muon_CLS_WP_err_raw"] = graphs_err['muonCLS_HVeff'].Eval(WP_raw)
        out["muon_CLS_WP_err_muon"] = graphs_err['muonCLS_HVeff'].Eval(WP_muon)
        out["muon_CLS_WP_err_muon_corr"] = graphs_err['muonCLS_HVeff'].Eval(WP_muon_corr)
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Muon cluster size")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/muonCLS.png" % outputdir)
        c.SaveAs("%s/muonCLS.pdf" % outputdir)
        
        
        
        ############################
        # muon cluster multiplicity
        ############################
        c.Clear()
        g = graphs['muonCMP_HVeff']
        yMax = 1.5*ROOT.TMath.MaxElement(g.GetN(), g.GetY())
        yMin = 0.5*ROOT.TMath.MinElement(g.GetN(), g.GetY())
        dummy = functions.dummyHist("HV_{eff} (V)", "Muon cluster multiplicity", xMin_, xMax_, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        out["muon_CMP_WP_raw"] = g.Eval(WP_raw)
        out["muon_CMP_WP_muon"] = g.Eval(WP_muon)
        out["muon_CMP_WP_muon_corr"] = g.Eval(WP_muon_corr)
        
        out["muon_CMP_WP_err_raw"] = graphs_err['muonCMP_HVeff'].Eval(WP_raw)
        out["muon_CMP_WP_err_muon"] = graphs_err['muonCMP_HVeff'].Eval(WP_muon)
        out["muon_CMP_WP_err_muon_corr"] = graphs_err['muonCMP_HVeff'].Eval(WP_muon_corr)
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Muon cluster multiplicity")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/muonCMP.png" % outputdir)
        c.SaveAs("%s/muonCMP.pdf" % outputdir)
          
          
        ############################
        # gamma cluster size
        ############################
        c.Clear()
        g = graphs['gammaCLS_HVeff']
        yMax = 1.5*ROOT.TMath.MaxElement(g.GetN(), g.GetY())
        yMin = 0.5*ROOT.TMath.MinElement(g.GetN(), g.GetY())
        dummy = functions.dummyHist("HV_{eff} (V)", "Gamma cluster size", xMin_, xMax_, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        out["gamma_CLS_WP_raw"] = g.Eval(WP_raw)
        out["gamma_CLS_WP_muon"] = g.Eval(WP_muon)
        out["gamma_CLS_WP_muon_corr"] = g.Eval(WP_muon_corr)
        
        out["gamma_CLS_WP_err_raw"] = graphs_err['gammaCLS_HVeff'].Eval(WP_raw)
        out["gamma_WP_err_muon"] = graphs_err['gammaCLS_HVeff'].Eval(WP_muon)
        out["gamma_WP_err_muon_corr"] = graphs_err['gammaCLS_HVeff'].Eval(WP_muon_corr)
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Gamma cluster size")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/gammaCLS.png" % outputdir)
        c.SaveAs("%s/gammaCLS.pdf" % outputdir)
        
        
        
        ############################
        # gamma cluster multiplicity
        ############################
        c.Clear()
        g = graphs['gammaCMP_HVeff']
        yMax = 1.5*ROOT.TMath.MaxElement(g.GetN(), g.GetY())
        yMin = 0.5*ROOT.TMath.MinElement(g.GetN(), g.GetY())
        dummy = functions.dummyHist("HV_{eff} (V)", "Gamma cluster multiplicity", xMin_, xMax_, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        out["gamma_CMP_WP_raw"] = g.Eval(WP_raw)
        out["gamma_CMP_WP_muon"] = g.Eval(WP_muon)
        out["gamma_CMP_WP_muon_corr"] = g.Eval(WP_muon_corr)
        
        out["gamma_CMP_WP_err_raw"] = graphs_err['gammaCMP_HVeff'].Eval(WP_raw)
        out["gamma_CMP_WP_err_muon"] = graphs_err['gammaCMP_HVeff'].Eval(WP_muon)
        out["gamma_CMP_WP_err_muon_corr"] = graphs_err['gammaCMP_HVeff'].Eval(WP_muon_corr)
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Gamma cluster multiplicity")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/gammaCMP.png" % outputdir)
        c.SaveAs("%s/gammaCMP.pdf" % outputdir)
                    
          
        # write results to file
        with open("%s/output.json" % outputdir, 'w') as fp: json.dump(out, fp, indent=4)
    
    else:
    
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
        
        
        ############################
        # muon corrected efficiency
        ############################    
        c.Clear()
        g = graphs['efficiencyMuon_corrected_HVPoint']
        yMin = math.floor(0.8/10*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*10
        dummy = functions.dummyHist("HV Point", "Muon efficiency, corrected (%)", xMin_HVPoint, xMax_HVPoint, yMin, 110)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        line = ROOT.TLine(xMin_HVPoint, 100, xMax_HVPoint, 100)
        line.SetLineColor(ROOT.kRed)
        line.SetLineWidth(2)
        line.Draw("SAME")  

        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Muon efficiency, corrected")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/efficiencyMuon_corrected.png" % outputdir)
        c.SaveAs("%s/efficiencyMuon_corrected.pdf" % outputdir)
        
        
        ############################
        # fake efficiency
        ############################    
        c.Clear()
        g = graphs['efficiencyFake_HVPoint']
        yMax = math.ceil(1.2/2*ROOT.TMath.MaxElement(g.GetN(), g.GetY()))*2
        yMin = math.floor(0.8/2*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*2
        dummy = functions.dummyHist("HV Point", "Fake/gamma efficiency (%)", xMin_HVPoint, xMax_HVPoint, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Fake/gamma efficiency")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/efficiencyFake.png" % outputdir)
        c.SaveAs("%s/efficiencyFake.pdf" % outputdir)
        
        
        ############################
        # streamer probability
        ############################    
        c.Clear()
        g_muon = graphs['muonStreamerProbability_HVPoint']
        g_gamma = graphs['gammaStreamerProbability_HVPoint']
        g_gamma.SetLineColor(ROOT.kRed)
        g_gamma.SetMarkerColor(ROOT.kRed)
        yMax = math.ceil(1.5/2*max([ROOT.TMath.MaxElement(g_muon.GetN(), g_muon.GetY()), ROOT.TMath.MaxElement(g_gamma.GetN(), g_gamma.GetY())]))*2
        if yMax > 100: yMax=100
        yMin = 0
        dummy = functions.dummyHist("HV Point", "Streamer probability (%)", xMin_HVPoint, xMax_HVPoint, yMin, yMax)
        dummy.Draw("HIST")
        g_muon.Draw("SAME LP")
        g_gamma.Draw("SAME LP")
        
        leg = ROOT.TLegend(0.15, 0.75, 0.6, 0.88)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetFillColor(0)
        leg.SetTextSize(0.035)
        
        leg.AddEntry(g_muon, "Muon streamer probability", "LP")
        leg.AddEntry(g_gamma, "Gamma streamer probability", "LP")
        leg.Draw("SAME")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/streamerProbability.png" % outputdir)
        c.SaveAs("%s/streamerProbability.pdf" % outputdir)
        
        
        ############################
        # gamma rate
        ############################    
        c.Clear()
        g = graphs['noiseGammaRate_HVPoint']
        yMax = math.ceil(1.5/2*ROOT.TMath.MaxElement(g.GetN(), g.GetY()))*2
        yMin = math.floor(0.5/2*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*2
        dummy = functions.dummyHist("HV Point", "Gamma rate (Hz/cm^{2})", xMin_HVPoint, xMax_HVPoint, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Gamma rate")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/noiseGammaRate.png" % outputdir)
        c.SaveAs("%s/noiseGammaRate.pdf" % outputdir)
        
           
        
        ############################
        # gap currents
        ############################
        c.Clear()
        dummy = functions.dummyHist("HV Point", "Current (#muA)", xMin_HVPoint, xMax_HVPoint, 0, 2*iMonMax)
        dummy.Draw("HIST")
        
        leg = ROOT.TLegend(0.15, 0.88-0.05*len(cfg['gapIds']), 0.9, 0.9)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetFillColor(0)
        leg.SetTextSize(0.035)
        
        for k,gap in enumerate(cfg['gapIds']):
       
            graphs_iMon["imon_%s_HVPoint" % gap].Draw("SAME LP")
            leg.AddEntry(graphs_iMon["imon_%s_HVPoint" % gap], cfg['gapNames'][k], "LP")
        
        leg.Draw("SAME")
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/gapCurrents.png" % outputdir)
        c.SaveAs("%s/gapCurrents.pdf" % outputdir)
        

        ############################
        # muon cluster size
        ############################
        c.Clear()
        g = graphs['muonCLS_HVPoint']
        yMax = 1.5*ROOT.TMath.MaxElement(g.GetN(), g.GetY())
        yMin = 0.5*ROOT.TMath.MinElement(g.GetN(), g.GetY())
        dummy = functions.dummyHist("HV Point", "Muon cluster size", xMin_HVPoint, xMax_HVPoint, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Muon cluster size")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/muonCLS.png" % outputdir)
        c.SaveAs("%s/muonCLS.pdf" % outputdir)
        
        
        
        ############################
        # muon cluster multiplicity
        ############################
        c.Clear()
        g = graphs['muonCMP_HVPoint']
        yMax = 1.5*ROOT.TMath.MaxElement(g.GetN(), g.GetY())
        yMin = 0.5*ROOT.TMath.MinElement(g.GetN(), g.GetY())
        dummy = functions.dummyHist("HV Point", "Muon cluster multiplicity", xMin_HVPoint, xMax_HVPoint, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Muon cluster multiplicity")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/muonCMP.png" % outputdir)
        c.SaveAs("%s/muonCMP.pdf" % outputdir)
        
        
        ############################
        # gamma cluster size
        ############################
        c.Clear()
        g = graphs['gammaCLS_HVPoint']
        yMax = 1.5*ROOT.TMath.MaxElement(g.GetN(), g.GetY())
        yMin = 0.5*ROOT.TMath.MinElement(g.GetN(), g.GetY())
        dummy = functions.dummyHist("HV Point", "Gamma cluster size", xMin_HVPoint, xMax_HVPoint, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Gamma cluster size")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/gammaCLS.png" % outputdir)
        c.SaveAs("%s/gammaCLS.pdf" % outputdir)
        
        
        
        ############################
        # gamma cluster multiplicity
        ############################
        c.Clear()
        g = graphs['gammaCMP_HVPoint']
        yMax = 1.5*ROOT.TMath.MaxElement(g.GetN(), g.GetY())
        yMin = 0.5*ROOT.TMath.MinElement(g.GetN(), g.GetY())
        dummy = functions.dummyHist("HV Point", "Gamma cluster multiplicity", xMin_HVPoint, xMax_HVPoint, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Gamma cluster multiplicity")
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/gammaCMP.png" % outputdir)
        c.SaveAs("%s/gammaCMP.pdf" % outputdir)


        # write results to file
        with open("%s/output.json" % outputdir, 'w') as fp: json.dump(out, fp, indent=4)
        
        
