
import sys, os, glob, shutil, json, math, re, random
import ROOT
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
    dir = "/var/webdcs/HVSCAN/%06d/" % scanid
    
    
    ##############################################################################################
    outputdir = "%s/ANALYSIS/%s_RATE/" % (dir, tag)
    if os.path.exists(outputdir): shutil.rmtree(outputdir) # delete output dir, if exists
    if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir
    
    
    HVeff, HVPoint = [], [] # storage of HV eff points
    out = {}
    out["chamberName"] = cfg['chamberName']
    out["scanid"] = scanid
    
    iMonMax = -999

    # prepare TGraphs
    graphs, graphs_err = {}, {} # graphs holding the parameters as function of HVeff or the HVPoint
    graphNames = ["gammaCLS", "gammaCMP", "noiseGammaRate"]

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
    
    for i,CAENFile in enumerate(CAEN_files):
        if i != 0: continue
        HVPoint_ = int(os.path.basename(CAENFile).split("_")[1][2:])
        print("Analyze HV point %d " % HVPoint_)

        saveDir = outputdir + "HV%d/" % HVPoint_
        if not os.path.exists(saveDir): os.makedirs(saveDir)
        out["HV%d" % HVPoint_] = {}

        analyzer = an.Analyzer(dir, saveDir, scanid, HVPoint_, "rate")
        analyzer.loadConfig(cfg)
        analyzer.setVerbose(1)
        analyzer.timeProfile()
        analyzer.timeStripProfile2D()
        analyzer.stripProfile()
        analyzer.clusterization("gamma")
        #analyzer.eventDisplay(-1) # args: amount of events to be plotted (randomly). -1: all events
        analyzer.write() # write all results to JSON file
        del analyzer

      
        # load CAEN for HV and currents
        CAEN = ROOT.TFile(CAENFile)
        HVeff_ = -999 # SG mode: HV can be low, so search for the max HV
        for k,gap in enumerate(cfg['gapIds']):
        
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
        # gamma rate
        ############################    
        c.Clear()
        g = graphs['noiseGammaRate_HVeff']
        yMax = math.ceil(1.5/2*ROOT.TMath.MaxElement(g.GetN(), g.GetY()))*2
        yMin = math.floor(0.5/2*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*2
        dummy = functions.dummyHist("HV_{eff} (V)", "Noise/gamma rate (Hz/cm^{2})", xMin_, xMax_, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Noise/gamma rate")
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
            leg.AddEntry(graphs_iMon["imon_%s_HVeff" % gap], cfg['gapNames'][k], "LP")
        
        leg.Draw("SAME")
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
        c.SaveAs("%s/gapCurrents.png" % outputdir)
        c.SaveAs("%s/gapCurrents.pdf" % outputdir)
           

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
        # gamma rate
        ############################    
        c.Clear()
        g = graphs['noiseGammaRate_HVPoint']
        yMax = math.ceil(1.5/2*ROOT.TMath.MaxElement(g.GetN(), g.GetY()))*2
        yMin = math.floor(0.5/2*ROOT.TMath.MinElement(g.GetN(), g.GetY()))*2
        dummy = functions.dummyHist("HV Point", "Noise/gamma rate (Hz/cm^{2})", xMin_HVPoint, xMax_HVPoint, yMin, yMax)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Noise/gamma rate")
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
        
        
