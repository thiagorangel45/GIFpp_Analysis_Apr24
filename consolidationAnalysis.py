
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzer as an
import config
import functions
import config

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

rate_scans =    [4313,  4428,  4427,   4373,   4317,   4426,   4316,   4372,   4292,   4291,   4293,   4294,   4362,   4485]
rate_hvpoints = [9,     9,     9,      9,      9,      9,      9,      9,      9,      9,      9,      9,      9,      9]
rate_absup =    [0,     220,   100,    69,     46,     33,     22,     10,     6.9,    4.6,    3.3,    2.2,    1.5,    1]
rate_absdw =    [0,     46000, 46000,  46000,  46000,  46000,  46000,  46000,  1,      1,      1,      1,      46000,  46000]

eff_scans =     [4492,  4471,  4453,   4456,   4457,   4454,   4447,   4467,   4470,   4468,   4463,   4469,   4460,   4461]
eff_hvpoints =  [9,     9,     9,      9,      9,      9,      9,      9,      9,      9,      9,      10,     12,     12]
eff_absup =     [0,     220,   100,    69,     46,     33,     22,     10,     6.9,    4.6,    3.3,    2.2,    1.5,    1]
eff_absdw =     [0,     46,    46,     33,     22,     4.6,    46000,  6.9,    22,     10,     4.6,    33,     6.9,    10]



def getGap(chamber):

    if chamber == "RE2_2_NPD_BARC_8_C": return "RE2-2-NPD-BARC-8-BOT"
    if chamber == "RE2_2_NPD_BARC_9_C": return "RE2-2-NPD-BARC-9-BOT"
    if chamber == "RE4_2_CERN_166_C": return "RE4-2-CERN-166-BOT"
    if chamber == "RE4_2_CERN_165_C": return "RE4-2-CERN-165-BOT"
    
def getMinMax(chamber):

    if chamber == "RE2_2_NPD_BARC_8_C": return 9400, 10200
    if chamber == "RE2_2_NPD_BARC_9_C": return 9500, 10600
    if chamber == "RE4_2_CERN_166_C": return 9300, 10800
    if chamber == "RE4_2_CERN_165_C": return 9400, 10400

def getIdx(scanid):

    if scanid in rate_scans: return rate_scans.index(scanid)
    elif scanid in eff_scans: return eff_scans.index(scanid)
    else: return 999;


def getDir(scanid, chamber, HV=-1):

    basedir = "/var/webdcs/HVSCAN/%06d/ANALYSIS/%s/" % (scanid, chamber)
    if HV == -1: return basedir
    return "%s/HV%d/" % (basedir, HV)

def extractRate(scanid, chamber):

    basedir = getDir(scanid, chamber)
    with open("%s/output.json" % (basedir)) as f_in: analyzerResults = json.load(f_in)
    
    cfg = getattr(config, chamber)
    gap = getGap(chamber)
    idx = getIdx(scanid)
    g_eff = ROOT.TGraphErrors()
    g_rate = ROOT.TGraphErrors()
    
    # get rates from eff scan
    for HV in range(1, eff_hvpoints[idx]+1):
    
        rate = analyzerResults["HV%d" % HV]["noiseGammaRate"]
        rate_err = analyzerResults["HV%d" % HV]["noiseGammaRate_err"]
        HVeff = analyzerResults["HV%d" % HV]["hveff_%s" % gap]
        
        g_eff.SetPoint(HV-1, HVeff, rate)
        g_eff.SetPointError(HV-1, 0, rate_err)
        
    # get rates from rate scan
    with open("%s/output.json" % getDir(rate_scans[idx], chamber)) as f_in: analyzerResults = json.load(f_in)
    for HV in range(1, rate_hvpoints[idx]+1):
    
        rate = analyzerResults["HV%d" % HV]["noiseGammaRate"]
        rate_err = analyzerResults["HV%d" % HV]["noiseGammaRate_err"]
        HVeff = analyzerResults["HV%d" % HV]["hveff_%s" % gap]
        
        g_rate.SetPoint(HV-1, HVeff, rate)
        g_rate.SetPointError(HV-1, 0, rate_err)


    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()    
    
    leg = ROOT.TLegend(.15, 0.67, .4, .82)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    
    g_eff.SetLineWidth(2)
    g_eff.SetLineColor(ROOT.kBlue)
    g_eff.SetMarkerStyle(20)
    g_eff.SetMarkerColor(ROOT.kBlue)
    
    g_rate.SetLineWidth(2)
    g_rate.SetLineColor(ROOT.kBlack)
    g_rate.SetMarkerStyle(20)
    g_rate.SetMarkerColor(ROOT.kBlack)
    
    leg.AddEntry(g_rate, "Rates from rate scan (U%s/D%s)" % (rate_absup[idx], rate_absdw[idx]), "LP")
    leg.AddEntry(g_eff, "Rates from eff. scan (U%s/D%s)" % (eff_absup[idx], eff_absdw[idx]), "LP")
    
    
    c.Clear()
    yMax = math.ceil(1.5/2*ROOT.TMath.MaxElement(g_eff.GetN(), g_eff.GetY()))*2
    yMin = 0
    xMax = ROOT.TMath.MaxElement(g_eff.GetN(), g_eff.GetX())
    xMin = ROOT.TMath.MinElement(g_eff.GetN(), g_eff.GetX())
    dummy = functions.dummyHist("HV_{eff} (V)", "Gamma rate (Hz/cm^{2})", xMin, xMax, yMin, yMax)
    dummy.Draw("HIST")
    g_rate.Draw("SAME LP")
    g_eff.Draw("SAME LP")
    
    
    # do fit
    fitMin, fitMax = getMinMax(chamber)
    #fit = ROOT.TF1("fit", "[0]*exp(x/[1])", xMin, xMax)
    #f_exp.SetParameters(1, 9500)
    #fit = ROOT.TF1("fit", "[0]*x*x*x*x + [1]*x*x*x + [2]*x*x + [3]*x", fitMin, fitMax)
    #fit.SetParameters(1, 1, 1)
    fit = ROOT.TF1("fit", "[0]*x + [1]", fitMin, fitMax)
    fit.SetParameters(1, 1)
    g_eff.Fit("fit", "R", "", fitMin, fitMax)
    leg.AddEntry(fit, "Fit to eff. scan rates", "L")
    
    fit.SetLineColor(ROOT.kRed)
    fit.GetXaxis().SetRangeUser(fitMin, fitMax)
    fit.SetLineWidth(2)
    fit.Draw("L SAME")
    
    leg.Draw()
    
    params.DrawLatex(0.16, 0.9, "#bf{%s}" % cfg['chamberName'])
    params.DrawLatex(0.16, 0.85, "Gamma rate (Hz/cm^{2})")
    functions.drawAux(c, cfg['textHeader'], "S%d" % (scanid))
    c.SaveAs("%s/rate_analysis.png" % basedir)
    c.SaveAs("%s/rate_analysis.pdf" % basedir)
    
def getWPTracking(scanid, chamber):

    basedir = getDir(scanid, chamber)
    basedir = basedir.replace(chamber, "RPCTracking1D_GT")
    with open("%s/output_%s.json" % (basedir, chamber)) as f_in: analyzerResults = json.load(f_in)
    return analyzerResults['WP_tracking'], analyzerResults['WP_err_tracking']
    
def getClusterRate(scanid, chamber, WP):

    idx = getIdx(scanid)
    
    basedir_rate = getDir(rate_scans[idx], chamber)
    with open("%s/output.json" % (basedir_rate)) as f_in: analyzerResults_rate = json.load(f_in)
    

    gap = getGap(chamber)
    g_crate = ROOT.TGraphErrors()
    
    for HV in range(1, rate_hvpoints[idx]+1):
    
        rate = analyzerResults_rate["HV%d" % HV]["noiseGammaRate"]
        cls = analyzerResults_rate["HV%d" % HV]["gammaCLS"]
        crate = rate / cls
        HVeff = analyzerResults_rate["HV%d" % HV]["hveff_%s" % gap]
        
        g_crate.SetPoint(HV-1, HVeff, crate)

    crate_WP = g_crate.Eval(WP) 
    return crate_WP
    

def getRateVal(scanid, chamber, tag, WP):
    
    '''
    Get a rate-computed value, evaluate at WP
    '''

    idx = getIdx(scanid)
    basedir_rate = getDir(rate_scans[idx], chamber)
    with open("%s/output.json" % (basedir_rate)) as f_in: analyzerResults_rate = json.load(f_in)
    
    gap = getGap(chamber)
    
    g = ROOT.TGraphErrors()
    for HV in range(1, rate_hvpoints[idx]+1):
    
        val = analyzerResults_rate["HV%d" % HV][tag]
        HVeff = analyzerResults_rate["HV%d" % HV]["hveff_%s" % gap]
        g.SetPoint(HV-1, HVeff, val)

    val_WP = g.Eval(WP)
    return val_WP
    
def getEffVal(scanid, chamber, tag, WP):
    
    '''
    Get a rate-computed value, evaluate at WP
    '''

    idx = getIdx(scanid)
    basedir_rate = getDir(scanid, chamber)
    with open("%s/output.json" % (basedir_rate)) as f_in: analyzerResults_eff = json.load(f_in)
    
    gap = getGap(chamber)
    
    g = ROOT.TGraphErrors()
    for HV in range(1, rate_hvpoints[idx]+1):
    
        val = analyzerResults_eff["HV%d" % HV][tag]
        HVeff = analyzerResults_eff["HV%d" % HV]["hveff_%s" % gap]
        g.SetPoint(HV-1, HVeff, val)

    val_WP = g.Eval(WP)
    return val_WP
    
def plotgammaCMPvsClusterRate(scanids, chamber):

    '''
    Plot gamma cluster multiplicity vs cluster rate
    '''
    
    leg = ROOT.TLegend(.20, 0.70, .70, .93)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    leg.SetHeader("#bf{Gamma cluster multiplicity}")

    graphs = []
    for i,ch in enumerate(chambers):
    
        cfg = getattr(config, ch)

        g = ROOT.TGraphErrors()
        for j,scanid in enumerate(scanids):
        
            WP, WP_err = getWPTracking(scanid, ch) # tracking WP
            crate_WP = getClusterRate(scanid, ch, WP)
            val_WP = getRateVal(scanid, ch, "gammaCMP", WP)
            val_err_WP = getRateVal(scanid, ch, "gammaCMP_err", WP)
        
            g.SetPoint(j, crate_WP, val_WP)
            g.SetPointError(j, 0, val_err_WP)

        
        g.SetLineWidth(2)
        g.SetLineColor(chambers_color[i])
        g.SetMarkerStyle(20)
        g.SetMarkerColor(chambers_color[i])
        leg.AddEntry(g, chambers_label[i], "LP")
        graphs.append(g)
    
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()        

    
    c.Clear()
    dummy = functions.dummyHist("Gamma cluster rate (Hz/cm^{2})", "Gamma cluster multiplicity", 0, 800, 0, 30)
    dummy.Draw("HIST")
    
    for g in graphs: g.Draw("SAME LP")
    leg.Draw()

    functions.drawAux(c, cfg['textHeader'], "")
    c.SaveAs("%s/gammaCMP_crate.png" % (savedir))
    c.SaveAs("%s/gammaCMP_crate.pdf" % (savedir))     
  


def plotgammaCLSvsClusterRate(scanids, chamber):

    '''
    Plot gamma cluster size vs cluster rate
    '''
    
    leg = ROOT.TLegend(.20, 0.70, .70, .93)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    leg.SetHeader("#bf{Gamma cluster size}")

    graphs = []
    for i,ch in enumerate(chambers):
    
        cfg = getattr(config, ch)

        g = ROOT.TGraphErrors()
        for j,scanid in enumerate(scanids):
        
            WP, WP_err = getWPTracking(scanid, ch) # tracking WP
            crate_WP = getClusterRate(scanid, ch, WP)
            val_WP = getRateVal(scanid, ch, "gammaCLS", WP)
            val_err_WP = getRateVal(scanid, ch, "gammaCLS_err", WP)
        
            g.SetPoint(j, crate_WP, val_WP)
            g.SetPointError(j, 0, val_err_WP)

        
        g.SetLineWidth(2)
        g.SetLineColor(chambers_color[i])
        g.SetMarkerStyle(20)
        g.SetMarkerColor(chambers_color[i])
        leg.AddEntry(g, chambers_label[i], "LP")
        graphs.append(g)
    
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()        

    
    c.Clear()
    dummy = functions.dummyHist("Gamma cluster rate (Hz/cm^{2})", "Gamma cluster size", 0, 800, 0, 5)
    dummy.Draw("HIST")
    
    for g in graphs: g.Draw("SAME LP")
    leg.Draw()

    functions.drawAux(c, cfg['textHeader'], "")
    c.SaveAs("%s/gammaCLS_crate.png" % (savedir))
    c.SaveAs("%s/gammaCLS_crate.pdf" % (savedir))     
      

def plotmuonCMPvsClusterRate(scanids, chamber):

    '''
    Plot muon cluster multiplicity vs cluster rate
    '''
    
    leg = ROOT.TLegend(.20, 0.70, .70, .93)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    leg.SetHeader("#bf{Muon cluster multiplicity}")

    graphs = []
    for i,ch in enumerate(chambers):
    
        cfg = getattr(config, ch)

        g = ROOT.TGraphErrors()
        for j,scanid in enumerate(scanids):
        
            WP, WP_err = getWPTracking(scanid, ch) # tracking WP
            crate_WP = getClusterRate(scanid, ch, WP)
            val_WP = getEffVal(scanid, ch, "muonCMP", WP)
            val_err_WP = getEffVal(scanid, ch, "muonCMP_err", WP)
        
            g.SetPoint(j, crate_WP, val_WP)
            g.SetPointError(j, 0, val_err_WP)

        
        g.SetLineWidth(2)
        g.SetLineColor(chambers_color[i])
        g.SetMarkerStyle(20)
        g.SetMarkerColor(chambers_color[i])
        leg.AddEntry(g, chambers_label[i], "LP")
        graphs.append(g)
    
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()        

    
    c.Clear()
    dummy = functions.dummyHist("Gamma cluster rate (Hz/cm^{2})", "Muon cluster multiplicity", 0, 800, 0, 3)
    dummy.Draw("HIST")
    
    for g in graphs: g.Draw("SAME LP")
    leg.Draw()

    functions.drawAux(c, cfg['textHeader'], "")
    c.SaveAs("%s/muonCMP_crate.png" % (savedir))
    c.SaveAs("%s/muonCMP_crate.pdf" % (savedir))     
  

def plotmuonCLSvsClusterRate(scanids, chamber):

    '''
    Plot muon cluster size vs cluster rate
    '''
    
    leg = ROOT.TLegend(.20, 0.70, .70, .93)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    leg.SetHeader("#bf{Muon cluster size}")

    graphs = []
    for i,ch in enumerate(chambers):
    
        cfg = getattr(config, ch)

        g = ROOT.TGraphErrors()
        for j,scanid in enumerate(scanids):
        
            WP, WP_err = getWPTracking(scanid, ch) # tracking WP
            crate_WP = getClusterRate(scanid, ch, WP)
            val_WP = getEffVal(scanid, ch, "muonCLS", WP)
            val_err_WP = getEffVal(scanid, ch, "muonCLS_err", WP)
        
            g.SetPoint(j, crate_WP, val_WP)
            g.SetPointError(j, 0, val_err_WP)

        
        g.SetLineWidth(2)
        g.SetLineColor(chambers_color[i])
        g.SetMarkerStyle(20)
        g.SetMarkerColor(chambers_color[i])
        leg.AddEntry(g, chambers_label[i], "LP")
        graphs.append(g)
    
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()        

    
    c.Clear()
    dummy = functions.dummyHist("Gamma cluster rate (Hz/cm^{2})", "Muon cluster size", 0, 800, 0, 5)
    dummy.Draw("HIST")
    
    for g in graphs: g.Draw("SAME LP")
    leg.Draw()

    functions.drawAux(c, cfg['textHeader'], "")
    c.SaveAs("%s/muonCLS_crate.png" % (savedir))
    c.SaveAs("%s/muonCLS_crate.pdf" % (savedir))     
      

def plotEmaxvsClusterRate(scanids, chamber):

    '''
    Plot emax (tracking) vs cluster rate
    '''
    
    leg = ROOT.TLegend(.20, 0.70, .70, .93)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    leg.SetHeader("#bf{Plateau efficiency, tracking (#varepsilon_{max})}")

    graphs = []
    for i,ch in enumerate(chambers):
    
        cfg = getattr(config, ch)

        g = ROOT.TGraphErrors()
        for j,scanid in enumerate(scanids):
        
            WP, WP_err = getWPTracking(scanid, ch) # tracking WP
            crate_WP = getClusterRate(scanid, ch, WP)
            
            basedir = getDir(scanid, ch)
            basedir = basedir.replace(ch, "RPCTracking1D_GT")
            with open("%s/output_%s.json" % (basedir, ch)) as f_in: analyzerResults = json.load(f_in)
            val = analyzerResults['emax_tracking']
            val_err = analyzerResults['emax_err_tracking']    
            
            g.SetPoint(j, crate_WP, val)
            g.SetPointError(j, 0, val_err)

        
        g.SetLineWidth(2)
        g.SetLineColor(chambers_color[i])
        g.SetMarkerStyle(20)
        g.SetMarkerColor(chambers_color[i])
        leg.AddEntry(g, chambers_label[i], "LP")
        graphs.append(g)
    
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()        

    
    c.Clear()
    dummy = functions.dummyHist("Gamma cluster rate (Hz/cm^{2})", "#varepsilon_{max} (%)", 0, 800, 90, 105)
    dummy.Draw("HIST")
    
    for g in graphs: g.Draw("SAME LP")
    leg.Draw()

    functions.drawAux(c, cfg['textHeader'], "")
    c.SaveAs("%s/emax_crate.png" % (savedir))
    c.SaveAs("%s/emax_crate.pdf" % (savedir))     
    

def plotTrackingdEmaxvsClusterRate(scanids, chamber):

    '''
    Plot Emax difference between tracking and muon
    '''
    
    leg = ROOT.TLegend(.20, 0.70, .70, .93)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    leg.SetHeader("#bf{#Delta#varepsilon_{max}(muon-tracking)}")

    graphs = []
    for i,ch in enumerate(chambers):
    
        cfg = getattr(config, ch)

        g = ROOT.TGraphErrors()
        for j,scanid in enumerate(scanids):
        
            WP, WP_err = getWPTracking(scanid, ch) # tracking WP
            crate_WP = getClusterRate(scanid, ch, WP)
            
            basedir = getDir(scanid, ch)
            basedir = basedir.replace(ch, "RPCTracking1D_GT")
            with open("%s/output_%s.json" % (basedir, ch)) as f_in: analyzerResults = json.load(f_in)
            emax_tr = analyzerResults['emax_tracking']
            emax_tr_err = analyzerResults['emax_err_tracking']
            
            emax_mu = analyzerResults['emax_muon']
            emax_mu_err = analyzerResults['emax_err_muon']    
                        
            dE = emax_mu - emax_tr
            dE_err = math.sqrt(emax_tr_err**2 + emax_mu_err**2)
                       
            g.SetPoint(j, crate_WP, dE)
            g.SetPointError(j, 0, dE_err)

        
        g.SetLineWidth(2)
        g.SetLineColor(chambers_color[i])
        g.SetMarkerStyle(20)
        g.SetMarkerColor(chambers_color[i])
        leg.AddEntry(g, chambers_label[i], "LP")
        graphs.append(g)
    
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()        

    
    c.Clear()
    dummy = functions.dummyHist("Gamma cluster rate (Hz/cm^{2})", "#Delta#varepsilon_{max}(muon-tracking) (%)", 0, 800, 0, 5)
    dummy.Draw("HIST")
    
    for g in graphs: g.Draw("SAME LP")
    leg.Draw()

    functions.drawAux(c, cfg['textHeader'], "")
    c.SaveAs("%s/dE_crate.png" % (savedir))
    c.SaveAs("%s/dE_crate.pdf" % (savedir))


def plotWPvsClusterRate(scanids, chamber):

    '''
    Plot Emax difference between tracking and muon
    '''
    
    leg = ROOT.TLegend(.20, 0.70, .70, .93)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetFillStyle(0)
    leg.SetHeader("#bf{Working Point (HV_{eff})}")

    graphs = []
    for i,ch in enumerate(chambers):
    
        cfg = getattr(config, ch)

        g = ROOT.TGraphErrors()
        for j,scanid in enumerate(scanids):
        
            WP, WP_err = getWPTracking(scanid, ch) # tracking WP
            crate_WP = getClusterRate(scanid, ch, WP)
                
            g.SetPoint(j, crate_WP, WP/1000.)
            g.SetPointError(j, 0, WP_err/1000.)

        
        g.SetLineWidth(2)
        g.SetLineColor(chambers_color[i])
        g.SetMarkerStyle(20)
        g.SetMarkerColor(chambers_color[i])
        leg.AddEntry(g, chambers_label[i], "LP")
        graphs.append(g)
    
    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()        

    
    c.Clear()
    dummy = functions.dummyHist("Gamma cluster rate (Hz/cm^{2})", "Working Point (kV)", 0, 800, 9.4, 11.4)
    dummy.Draw("HIST")
    
    for g in graphs: g.Draw("SAME LP")
    leg.Draw()

    functions.drawAux(c, cfg['textHeader'], "")
    c.SaveAs("%s/WP_crate.png" % (savedir))
    c.SaveAs("%s/WP_crate.pdf" % (savedir))

if __name__ == "__main__":

    savedir = "/var/webdcs/ANALYSIS/jaeyserm/consolidation_tbjul21"
    crateMin, crateMax = 0, 800

    scanid = 4463
    chambers = ["RE2_2_NPD_BARC_8_C", "RE2_2_NPD_BARC_9_C", "RE4_2_CERN_166_C", "RE4_2_CERN_165_C"]
    chambers_label = ["RE2-2-NPD-BARC-8 C", "RE2-2-NPD-BARC-9 C", "RE4-2-CERN-166 C", "RE4-2-CERN-165 C"]
    chambers_color = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+1]

    '''
    for scanid in eff_scans:
        for ch in chambers:
            extractRate(scanid, ch)
    '''
    
    scanids = [4471,  4453,   4456,   4457,   4454,   4447, 4467,   4470,   4468,   4463,   4469,   4460,   4461]
    plotgammaCMPvsClusterRate(scanids, chambers)
    plotgammaCLSvsClusterRate(scanids, chambers)
    plotmuonCMPvsClusterRate(scanids, chambers)
    plotmuonCLSvsClusterRate(scanids, chambers)
    plotEmaxvsClusterRate(scanids, chambers)
    plotTrackingdEmaxvsClusterRate(scanids, chambers)
    plotWPvsClusterRate(scanids, chambers)

