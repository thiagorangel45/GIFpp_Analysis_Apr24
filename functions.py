
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzer as an
import config

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)',text) ]

colors = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack]


def drawAux(c, headerLeft, headerRight):
    
    textLeft = ROOT.TLatex()
    textLeft.SetTextFont(42)
    textLeft.SetTextSize(0.04)
    textLeft.SetNDC()
    textLeft.DrawLatex(c.GetLeftMargin(), 0.96, headerLeft)
        
    textRight = ROOT.TLatex()
    textRight.SetNDC()
    textRight.SetTextFont(42)
    textRight.SetTextSize(0.04)
    textRight.SetTextAlign(31)
    textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, headerRight)
    
def setGraphStyle(g, xlabel, ylabel):

    g.SetLineWidth(2)
    g.SetLineColor(ROOT.kBlue)
    g.SetMarkerStyle(20)
    g.SetMarkerColor(ROOT.kBlue)
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.GetYaxis().SetTitleOffset(1.8)
    g.GetYaxis().SetLabelOffset(2.0*g.GetYaxis().GetLabelOffset())
    g.GetXaxis().SetTitleOffset(1.2)
    g.GetXaxis().SetLabelOffset(2.0*g.GetXaxis().GetLabelOffset())
        
    return g
    
def dummyHist(xlabel, ylabel, xMin, xMax, yMin, yMax):

    h = ROOT.TH1D("dummy", "dummy", 1, xMin, xMax)
    h.GetXaxis().SetTitle(xlabel)
    h.GetYaxis().SetTitle(ylabel)
    h.GetYaxis().SetTitleOffset(1.8)
    h.GetYaxis().SetLabelOffset(2.0*h.GetYaxis().GetLabelOffset())
    h.GetXaxis().SetTitleOffset(1.2)
    h.GetXaxis().SetLabelOffset(2.0*h.GetXaxis().GetLabelOffset())
    h.GetYaxis().SetRangeUser(yMin, yMax)
        
    return h
    
    
def estimate50pctEff(graph):

    ## try to estimate HV50
    HV_min = ROOT.TMath.MinElement(graph.GetN(), graph.GetX())
    HV_max = ROOT.TMath.MaxElement(graph.GetN(), graph.GetX())
    
        
    return sigmoid_HV50pct
    
    
def sigmoidFit(cfg, graph):

    HV_min = ROOT.TMath.MinElement(graph.GetN(), graph.GetX())
    HV_max = ROOT.TMath.MaxElement(graph.GetN(), graph.GetX())

    sigmoid = ROOT.TF1("sigmoid","[0]/(1+exp([1]*([2]-x)))", HV_min, HV_max)
    sigmoid.SetParName(0,"#epsilon_{max}")
    sigmoid.SetParName(1,"#lambda")
    sigmoid.SetParName(2,"HV_{50%}")
        
    if 'sigmoid_emax' in cfg: 
    
        sigmoid_emax = cfg['sigmoid_emax'] # default
        if sigmoid_emax < 0: # take highest point
        
            sigmoid_emax = ROOT.TMath.MaxElement(graph.GetN(), graph.GetY())
        
        sigmoid.SetParameter(0, sigmoid_emax)
        
    else: sigmoid.SetParameter(0, 0.98)
    
        
    if 'sigmoid_lambda' in cfg: sigmoid.SetParameter(1, cfg['sigmoid_lambda'])
    else: sigmoid.SetParameter(1, 0.011)
        
    if 'sigmoid_HV50pct' in cfg:
        
        sigmoid_HV50pct = cfg['sigmoid_HV50pct'] # default
        if sigmoid_HV50pct < 0: 
        
            HV_probe = HV_min
            sigmoid_HV50pct = -1
            while HV_probe <= HV_max:
                        
                eff_ = graph.Eval(HV_probe)
                if abs(eff_ - 50) < 1:
                    sigmoid_HV50pct = HV_probe
                    break       
                HV_probe += 1
        #print sigmoid_HV50pct
        sigmoid.SetParameter(2, sigmoid_HV50pct)
            
    else: sigmoid.SetParameter(2, 9400) # default 2mm gap
        
    if "sigmoid_HVmin" in cfg and "sigmoid_HVmax" in cfg: graph.Fit("sigmoid", "E", "", cfg['sigmoid_HVmin'], cfg['sigmoid_HVmax'])
    else: graph.Fit("sigmoid", "E", "")

    fitted = graph.GetFunction("sigmoid")
    emax = fitted.GetParameter(0)
    lam = fitted.GetParameter(1)
    hv50 = fitted.GetParameter(2)
        
    emax_err = fitted.GetParError(0)
    lam_err = fitted.GetParError(1)
    hv50_err = fitted.GetParError(2)
        

    WP = (math.log(19)/lam + hv50 + 150)
    dLambdaInverse = lam_err / (lam*lam) # error on 1/lambda
    WP_err = math.sqrt((math.log(19)*dLambdaInverse)*(math.log(19)*dLambdaInverse) + hv50_err*hv50_err) # total error on WP

        
    return fitted, emax, lam, hv50, WP, emax_err, lam_err, hv50_err, WP_err
    
def getMuonTimeWindowHV(scanid, HVPoint, tag):
    
    dir = "/Users/thiagorangel/GIFpp_Analysis_Apr24" 
    outputdir = "%s/ANALYSIS/%s/" % (dir, tag)
    
    cfg = getattr(config, tag)
    saveDir = outputdir + "HV%d/" % HVPoint
    if not os.path.exists(saveDir): os.makedirs(saveDir)
    analyzer = an.Analyzer(dir, saveDir, scanid, HVPoint, "efficiency")
    analyzer.loadConfig(cfg)
    analyzer.setVerbose(1)
    muonWindowMean, muonWindowSigma = analyzer.timeProfile()
    del analyzer
    
    return muonWindowMean, muonWindowSigma
    
