
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzer as an
import config
import functions

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


if __name__ == "__main__":

    header = "#bf{CMS GIF++}, #scale[0.75]{ #it{Preliminary}}"
    headerText = "#bf{CMS iRPC} (1.4 mm) - KODEL-C"
    outputdir = "/var/webdcs/HVSCAN/ANALYSIS/KODELC"
   

    # all runs
    '''
    4796 OFF
    4798 460
    4806 100
    4803 46
    4800 22
    4799 10
    4801 6.9
    4802 4.6
    4804 3.3
    4805 2.2
    '''
    runIds = [4796, 4798, 4806, 4803, 4800, 4799, 4801, 4802, 4804, 4805]
    
    
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
    c.SetGrid()
    
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.035)
    params.SetNDC()
    
    graphs = {}
    graphs_ = ["wp", "gamma_cls", "muon_cls", "gamma_cmp", "muon_cmp", "imon_top", "imon_bot", "charge", "emax", "eff_wp"]
    for g in graphs_:
    
        color = ROOT.kBlue
        if "gamma" in g or "imon_top" in g: color = ROOT.kRed
        g_ = ROOT.TGraphErrors()
        g_.SetName(g)
        g_.SetLineWidth(2)
        g_.SetLineColor(color)
        g_.SetMarkerStyle(20)
        g_.SetMarkerColor(color)
        graphs[g] = g_
    
    i = -1
    for runId in runIds:
        
        fIn = "/var/webdcs/HVSCAN/%.6d/ANALYSIS/KODELC/output.json" % runId
        if not os.path.exists(fIn): continue
        i += 1
        
        fIn_m = open("/var/webdcs/HVSCAN/%.6d/ANALYSIS/KODELC/output.json" % runId, 'r')
        js_m = json.load(fIn_m)
        
        fIn_r = open("/var/webdcs/HVSCAN/%.6d/ANALYSIS/KODELC_RATE/output.json" % runId, 'r')
        js_r = json.load(fIn_r)
 
        
        wp = js_m['WP_muon']
        muon_cls = js_m['muon_CLS_WP_muon']
        muon_cmp = js_m['muon_CMP_WP_muon']
        muon_emax = js_m['emax_muon']
        muon_wp_eff = js_m['eff_WP_muon']
        print(muon_emax)
        
        g_gamma_cls, g_gamma_cmp = ROOT.TGraph(), ROOT.TGraph()
        g_hitrate = ROOT.TGraph()
        for hv_ in range(1, 15):
        
            hv = "HV%d" % hv_
            if not hv in js_r: continue
            hv__ = js_r[hv]['hveff_KODELC-TOP']
            g_gamma_cls.SetPoint(hv_-1, hv__, js_r[hv]['gammaCLS'])
            g_gamma_cmp.SetPoint(hv_-1, hv__, js_r[hv]['gammaCMP'])
            g_hitrate.SetPoint(hv_-1, hv__, js_r[hv]['noiseGammaRate'])
    
  
        gamma_cls = g_gamma_cls.Eval(wp) #js_m['gamma_CLS_WP_muon']
        gamma_cmp = g_gamma_cmp.Eval(wp) #js_m['gamma_CMP_WP_muon']
        hit_rate = g_hitrate.Eval(wp) #js_m['noiseGammaRate_WP_muon']
        cluster_rate = hit_rate / gamma_cls
        
        imon_top = js_m['imon_KODELC-TOP_WP_muon']
        imon_bot = js_m['imon_KODELC-BOT_WP_muon']
        imon_avg = 0.5*(imon_top+imon_bot)
        charge = 1e6*imon_avg / (cluster_rate*7000.)
       

        
        graphs['imon_top'].SetPoint(i, cluster_rate, imon_top)
        graphs['imon_bot'].SetPoint(i, cluster_rate, imon_bot)
        
        if i != 0:
        
            graphs['gamma_cls'].SetPoint(i-1, cluster_rate, gamma_cls)
            graphs['gamma_cmp'].SetPoint(i-1, cluster_rate, gamma_cmp)
            graphs['charge'].SetPoint(i-1, cluster_rate, charge)
            
        graphs['muon_cls'].SetPoint(i, cluster_rate, muon_cls)
        graphs['muon_cmp'].SetPoint(i, cluster_rate, muon_cmp)
        
        graphs['wp'].SetPoint(i, cluster_rate, wp)
        graphs['emax'].SetPoint(i, cluster_rate, muon_emax)
        graphs['eff_wp'].SetPoint(i, cluster_rate, muon_wp_eff)
       

    # Working point
    dummy = functions.dummyHist("Gamma background cluster rate (Hz/cm^{2})", "HV_{eff} (V)", 0, 2200, 7000, 8000)
    dummy.Draw("HIST")
    graphs['wp'].Draw("SAME P")
    functions.drawAux(c, header, "")
    c.SaveAs("%s/clrate_wp.png" % outputdir)
    c.SaveAs("%s/clrate_wp.pdf" % outputdir)
    
    
    # cluster size
    dummy = functions.dummyHist("Gamma background cluster rate (Hz/cm^{2})", "Cluster size", 0, 2200, 0, 3)
    dummy.Draw("HIST")
    graphs['muon_cls'].Draw("SAME P")
    graphs['gamma_cls'].Draw("SAME P")
    params.DrawLatex(0.17, 0.9, headerText)
    functions.drawAux(c, header, "")
    
    leg = ROOT.TLegend(.2, 0.72, .63, .84)
    leg.SetTextSize(0.035)
    leg.SetMargin(0.1)
    leg.AddEntry(graphs['muon_cls'], "Muon cluster size", "P")
    leg.AddEntry(graphs['gamma_cls'], "Gamma cluster size", "P")
    leg.Draw()

    c.SaveAs("%s/clrate_cls.png" % outputdir)
    c.SaveAs("%s/clrate_cls.pdf" % outputdir)
    
    
    # cluster multiplicity
    dummy = functions.dummyHist("Gamma background cluster rate (Hz/cm^{2})", "Cluster multiplicity", 0, 2200, 0, 70)
    dummy.Draw("HIST")
    graphs['muon_cmp'].Draw("SAME P")
    graphs['gamma_cmp'].Draw("SAME P")
    params.DrawLatex(0.17, 0.9, headerText)
    functions.drawAux(c, header, "")
    
    leg = ROOT.TLegend(.2, 0.72, .63, .84)
    leg.SetTextSize(0.035)
    leg.SetMargin(0.1)
    leg.AddEntry(graphs['muon_cmp'], "Muon cluster multiplicity", "P")
    leg.AddEntry(graphs['gamma_cmp'], "Gamma cluster multiplicity", "P")
    leg.Draw()

    c.SaveAs("%s/clrate_cmp.png" % outputdir)
    c.SaveAs("%s/clrate_cmp.pdf" % outputdir)
    
    
    # currents
    dummy = functions.dummyHist("Gamma background cluster rate (Hz/cm^{2})", "Current (#uA)", 0, 2200, 0, 200)
    dummy.Draw("HIST")
    graphs['imon_top'].Draw("SAME P")
    graphs['imon_bot'].Draw("SAME P")
    params.DrawLatex(0.17, 0.9, headerText)
    functions.drawAux(c, header, "")
    
    leg = ROOT.TLegend(.2, 0.72, .63, .84)
    leg.SetTextSize(0.035)
    leg.SetMargin(0.1)
    leg.AddEntry(graphs['imon_top'], "Top gap", "P")
    leg.AddEntry(graphs['imon_bot'], "Bottom gap", "P")
    leg.Draw()

    c.SaveAs("%s/clrate_imon.png" % outputdir)
    c.SaveAs("%s/clrate_imon.pdf" % outputdir)
    
    
    # Working point
    dummy = functions.dummyHist("Gamma background cluster rate (Hz/cm^{2})", "Average charge per gamma cluster (pC)", 0, 2200, 0, 30)
    dummy.Draw("HIST")
    graphs['charge'].Draw("SAME P")
    functions.drawAux(c, header, "")
    params.DrawLatex(0.17, 0.9, headerText)
    c.SaveAs("%s/clrate_charge.png" % outputdir)
    c.SaveAs("%s/clrate_charge.pdf" % outputdir)
    
    
    # efficiency
    '''
    dummy = functions.dummyHist("Gamma background cluster rate (Hz/cm^{2})", "Muon efficiency (%)", 0, 2200, 60, 120)
    dummy.Draw("HIST")
    graphs['charge'].Draw("SAME LP")
    functions.drawAux(c, header, "")
    
    leg = ROOT.TLegend(.2, 0.72, .63, .84)
    leg.SetTextSize(0.035)
    leg.SetMargin(0.1)
    leg.AddEntry(graphs['eff_wp'], "Working point", "P")
    leg.AddEntry(graphs['emax'], "#epsilon_{max}", "P")
    leg.Draw()
    
    params.DrawLatex(0.17, 0.9, headerText)
    c.SaveAs("%s/clrate_eff.png" % outputdir)
    c.SaveAs("%s/clrate_eff.pdf" % outputdir)
    '''