
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzer as an
import config
import functions

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


if __name__ == "__main__":

    HVPoint = 1
    timeWindow = "gamma" # muon noise gamma

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
    outputdir = "%s/ANALYSIS/%s/" % (dir, tag)
    if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir
    
    saveDir = outputdir + "HV%d/" % HVPoint
    if not os.path.exists(saveDir): os.makedirs(saveDir)

    g_cls = ROOT.TGraphErrors()
    g_cmp = ROOT.TGraphErrors()
    
    times = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40]
    
    # get the scan ID from the ROOT file
    files = glob.glob("%s/*CAEN.root" % dir)
    if len(files) == 0: sys.exit("No ROOT files in directory") 
    scanid = int(re.findall(r'\d+', files[0])[0])
    
    

    maxY = -999
    for i,t in enumerate(times):
    
        analyzer = an.Analyzer(dir, saveDir, scanid, HVPoint, "efficiency")
        analyzer.loadConfig(cfg)
        analyzer.setVerbose(0)
        analyzer.timeProfile()
        cls, cmp = analyzer._clusterization(t, timeWindow)
        g_cls.SetPoint(i, t, cls)
        g_cmp.SetPoint(i, t, cmp)
        if cls > maxY: maxY = cls
        if cmp > maxY: maxY = cmp
        del analyzer
        print cls, cmp

        
    # do plotting and fitting
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
    
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()
    
    leg = ROOT.TLegend(0.15, 0.8, 0.90, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetFillColor(0)
    leg.SetNColumns(2)
    
    c.Clear()
    dummy = functions.dummyHist("#DeltaT", "Clusterization outcome", min(times), max(times), 1, 1.15*maxY)
    dummy.Draw("HIST")

    g_cmp.SetLineWidth(2)
    g_cmp.SetLineColor(ROOT.kBlue)
    g_cmp.SetMarkerStyle(20)
    g_cmp.SetMarkerColor(ROOT.kBlue)
    g_cmp.Draw("SAME LP")
    
    g_cls.SetLineWidth(2)
    g_cls.SetLineColor(ROOT.kRed)
    g_cls.SetMarkerStyle(20)
    g_cls.SetMarkerColor(ROOT.kRed)
    g_cls.Draw("SAME LP")
    
    
    leg.AddEntry(g_cmp, "Cluster multiplicity %s" % timeWindow, "LP")
    leg.AddEntry(g_cls, "Cluster size %s" % timeWindow, "LP")
    leg.Draw("SAME")

    params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
    functions.drawAux(c, cfg['textHeader'], "S%d/HV%d" % (scanid, HVPoint))
    c.SaveAs("%s/clusterTime_%s.png" % (saveDir, timeWindow))
    c.SaveAs("%s/clusterTime_%s.pdf" % (saveDir, timeWindow))
    
        
        
        
    
