
import sys, os, glob, shutil, json, math, re, random, copy
import ROOT
import config as config
import analyzer as an
import functions


ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


def plotDS(h, fOut, label, tagStrip):
 
    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    c1.SetLeftMargin(0.12)
    c1.SetRightMargin(0.05)
    c1.SetTopMargin(0.05)
    c1.SetBottomMargin(0.1)

    

    h.GetXaxis().SetRangeUser(-5, 5)
    h.Draw("HIST")
    h.GetYaxis().SetRangeUser(0, 1.3*h.GetMaximum())
    h.SetLineColor(ROOT.kBlack)
    
    h.GetXaxis().SetTitle("dS")
    h.GetXaxis().SetTitleOffset(1.2)
    h.GetXaxis().SetLabelOffset(0.005)

    h.GetYaxis().SetTitle("Events")   
    h.GetYaxis().SetTitleOffset(1.8)
    h.GetYaxis().SetLabelOffset(0.005)
            
    fitParams = ROOT.TLatex()
    fitParams.SetTextFont(42)
    fitParams.SetTextSize(0.03)
    fitParams.SetNDC()
    fitParams.DrawLatex(0.16, 0.90, "%s (%d entries)" % (label, h.GetEntries()))
    fitParams.DrawLatex(0.16, 0.85, "Tag strip no. %d" % tagStrip)
            

    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s.png" % fOut) 
    c1.SaveAs("%s.pdf" % fOut) 
    
     
    del c1


def doTimeFit(h, fOut, label, tagStrip):

    xTimeMin, xTimeMax = getMinMax(h)
        
    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    c1.SetLeftMargin(0.12)
    c1.SetRightMargin(0.05)
    c1.SetTopMargin(0.05)
    c1.SetBottomMargin(0.1)

    
    xMaximum = h.GetBinCenter(h.GetMaximumBin())
    h_fit = ROOT.TF1("h_fit", "gaus", xTimeMin, xTimeMax)
    h_fit.SetParameters(h.Integral(), xMaximum, h.GetRMS())
    h.Fit("h_fit", "RW", "", xTimeMin, xTimeMax)

    mean = h_fit.GetParameter(1)
    sigma = h_fit.GetParameter(2)
    sigma_err = h_fit.GetParError(2)

    h.GetXaxis().SetRangeUser(xTimeMin-5, xTimeMax+5)
    h.Draw("HIST")
    h.GetYaxis().SetRangeUser(0, 1.3*h.GetMaximum())
    h.SetLineColor(ROOT.kBlack)
    
    h.GetXaxis().SetTitle("Time (ns)")
    h.GetXaxis().SetTitleOffset(1.2)
    h.GetXaxis().SetLabelOffset(0.005)

    h.GetYaxis().SetTitle("Hits / 100 ps")   
    h.GetYaxis().SetTitleOffset(1.8)
    h.GetYaxis().SetLabelOffset(0.005)
            
    fitParams = ROOT.TLatex()
    fitParams.SetTextFont(42)
    fitParams.SetTextSize(0.03)
    fitParams.SetNDC()
    fitParams.DrawLatex(0.16, 0.90, "%s (%d entries)" % (label, h.GetEntries()))
    fitParams.DrawLatex(0.16, 0.85, "Tag strip no. %d" % tagStrip)
    fitParams.DrawLatex(0.16, 0.80, "#color[2]{Peak mean: %.2f ns}" % mean)
    fitParams.DrawLatex(0.16, 0.75, "#color[2]{Peak width (#sigma): %.2f #pm %.2f ns}" % (sigma, sigma_err))
    fitParams.DrawLatex(0.16, 0.70, "#chi^{2}/ndof = %.2f %.2f" % (h_fit.GetChisquare(), h_fit.GetNDF()))        


    h_fit.SetLineColor(ROOT.kRed)
    #peakFitDraw.GetXaxis().SetRangeUser(xTimeMin-5, xTimeMax+5)
    h_fit.SetLineWidth(3)
    h_fit.Draw("L SAME")
            

    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s.png" % fOut) 
    c1.SaveAs("%s.pdf" % fOut) 


    del c1
    del h_fit
    
    return sigma, sigma_err

def drawAux(c, aux = ""):
    
    textLeft = ROOT.TLatex()
    textLeft.SetTextFont(42)
    textLeft.SetTextSize(0.04)
    textLeft.SetNDC()
    textLeft.DrawLatex(c.GetLeftMargin(), 0.96, textHeader)
        
    textRight = ROOT.TLatex()
    textRight.SetNDC()
    textRight.SetTextFont(42)
    textRight.SetTextSize(0.04)
    textRight.SetTextAlign(31)
    if aux == "": textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, "S%d/HV%d" % (scanid, HVPoint))
    else: textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, "S%d/HV%d/%s" % (scanid, HVPoint, aux))
 
def getMinMax(h):

    '''
    xMin, xMax = -5000, 5000
    
    for i in range(0, h.GetNbinsX()+1):
    
        if h.GetBinContent(i) != 0:
            xMin = h.GetBinCenter(i)
            break
            
    for i in range(h.GetNbinsX()+1, 0, -1):
    
        if h.GetBinContent(i) != 0:
            xMax = h.GetBinCenter(i)
            break
            
    
    '''
    
    binMax = h.GetMaximumBin()
    xMin = h.GetBinCenter(binMax) - 20
    xMax = h.GetBinCenter(binMax) + 20
    return xMin, xMax


def ToF(chambers, tag, label, scanid, HVPoint = 1):

    if len(chambers) != 2: return
    # first chamber is tag, second one is probe


    chambers_cfg = [getattr(config, x) for x in chambers]

    chambers_cluster_collection = []
    chambers_cluster_time_collection = []
    
    # histogram collections
    chambers_stripProfiles, chambers_stripProfiles_CLS, chambers_stripProfiles_allCuts = [], [], []
    
    tagStrips = list(range(1, 33)) # tag strips
    probeStrips = [-1]*32 # -1 means no constraint on the probe strip
    probeStrips = list(range(1, 33))

    dir = "/Users/thiagorangel/GIFpp_Analysis_Apr24" 
    saveDir = "%s/ANALYSIS/TOF_%s/HV%d/" % (dir, tag, HVPoint)
    os.system("mkdir -p %s" % saveDir)
    
    saveDir_dt = "%s/DT" % saveDir
    os.system("mkdir -p %s" % saveDir_dt)
    
    saveDir_ds = "%s/DS" % saveDir
    os.system("mkdir -p %s" % saveDir_ds)
    
    
    tagToProbe = {17 : 20}
    

    nBins = 2*10*5000 # 100 ps resolution
    
    meanRate = 0
    
    
    ds_hists, dt_hists = [], []
    for tagStrip in tagStrips:
    
        dt = ROOT.TH1D("dt_tagStrip%d" % tagStrip, "", nBins, -5000, 5000) # time difference
        ds = ROOT.TH1D("ds_tagStrip%d" % tagStrip, "", 10, -5, 5) # strip difference
        
        ds_hists.append(copy.deepcopy(ds))
        dt_hists.append(copy.deepcopy(dt))



    for i,cfg in enumerate(chambers_cfg):
    
        saveDir_ = "/Users/thiagorangel/GIFpp_Analysis_Apr24/%06d/ANALYSIS/%s/HV%d/" % (scanid, chambers[i], HVPoint)
        analyzer = an.Analyzer(dir, saveDir_, scanid, HVPoint, "efficiency")
        #print(cfg)  
        analyzer.loadConfig(cfg)
        analyzer.setVerbose(1)
        analyzer.timeProfile()
        analyzer.timeStripProfile2D()
        analyzer.clusterization("muon")
        analyzer.clusterization("gamma")
        analyzer.efficiency()
        analyzer.stripProfile(True)
        analyzer.clusterization("muon")
        cluster_collection, cluster_time_collection, barycenters_collection, barycenters_err_collection = analyzer.clusterEvents()
        
        chambers_cluster_collection.append(cluster_collection)
        chambers_cluster_time_collection.append(cluster_time_collection)
        
        
        # prepare the histograms
        stripProfile = ROOT.TH1D("stripProfile_%s" % chambers[i], "", 32, 1, 33)
        stripProfile_CLS = ROOT.TH1D("stripProfile_CLS_%s" % chambers[i], "", 32, 1, 33)
        stripProfile_allCuts = ROOT.TH1D("stripProfile_allCuts_%s" % chambers[i], "", 32, 1, 33)
        for i in range(1, 33): 
    
            stripProfile.GetXaxis().SetBinLabel(i, str(i))
            stripProfile_CLS.GetXaxis().SetBinLabel(i, str(i))
            stripProfile_allCuts.GetXaxis().SetBinLabel(i, str(i))
            
        chambers_stripProfiles.append(copy.deepcopy(stripProfile))
        chambers_stripProfiles_CLS.append(copy.deepcopy(stripProfile_CLS))
        chambers_stripProfiles_allCuts.append(copy.deepcopy(stripProfile_allCuts))
        

    nEvents = len(chambers_cluster_collection[0])
    nTriggers, nHits = 0, 0
    goodEvents = [True]*nEvents
    for iEv in range(0, nEvents):
    
        for iCh in range(0, len(chambers)):
       
            clusters = chambers_cluster_collection[iCh][iEv]
            for cluster in clusters:
                for strip in cluster:
                
                    chambers_stripProfiles[iCh].Fill(strip)
            
            #if len(clusters) == 1 and (len(clusters[0]) < 3): chambers_stripProfiles_CLS[iCh].Fill(clusters[0][0])
            #if len(clusters) == 1 and len(clusters[0]) == 1: # quality cut on cluster size
            if len(clusters) == 1:
                for strip in clusters[0]: chambers_stripProfiles_CLS[iCh].Fill(strip)
                
   
            else: goodEvents[iEv] = False
            
            if iCh == 0 and len(clusters) > 0 and len(clusters[0]) != 1: goodEvents[iEv] = False
            
            
            
   
   
       

    # loop over the good events = events where each chamber has 1 cluster (and eventually other cuts on the CLS)
    for iEv in range(0, nEvents):
    
        if not goodEvents[iEv]: continue # skip bad events
       
        timings = [-1]*len(chambers) # holds the time of the probe strips
        strips = [] # which strip is fired
        
        tagStrip = chambers_cluster_collection[0][iEv][0][0]
        tagStripTime = chambers_cluster_time_collection[0][iEv][0][0]
        
        probeStrip = chambers_cluster_collection[1][iEv][0][0]
        probeStrip_ = chambers_cluster_collection[1][iEv][0]
        probeStripTime = chambers_cluster_time_collection[1][iEv][0][0]
        
        
        ds = tagStrip - probeStrip
        dt = tagStripTime - probeStripTime
        
        
        
        
        # strip constraint on probe chamber
        if not tagStrip in tagStrips: continue
        if not probeStrip in probeStrips: continue
        
        if tagStrip in tagToProbe and tagToProbe[tagStrip] not in probeStrip_: continue
        
        if tagStrip in tagToProbe:
            idx = probeStrip_.index(tagToProbe[tagStrip])
            probeStripTime = chambers_cluster_time_collection[1][iEv][0][idx]
            
            dt = tagStripTime - probeStripTime
        
        #idx = tagStrips.index(tagStrip)      
        #if probeStrips[idx] != -1 and probeStrip != probeStrips[idx]: continue
        
        print(tagStrip, probeStrip, ds, dt)
        
        ds_hists[tagStrip-1].Fill(ds)
        dt_hists[tagStrip-1].Fill(dt)
        

    
    timeRes = ROOT.TGraphErrors()
    sigma_avg, sigma_err_avg = [], []
    c = 0
    for tagStrip in tagStrips:
    
        entries = dt_hists[tagStrip-1].GetEntries()
        
    
        sigma, sigma_err = doTimeFit(dt_hists[tagStrip-1], "%s/dt_tagStrip%d" % (saveDir_dt, tagStrip), "#Delta(T_{tag} #minus T_{probe})", tagStrip)
        plotDS(ds_hists[tagStrip-1], "%s/ds_tagStrip%d" % (saveDir_ds, tagStrip), "#Delta(S_{tag} #minus S_{probe})", tagStrip)
        
        #if entries < nStats: continue # need sufficient statistics
        
        
        timeRes.SetPoint(c, tagStrip, sigma/math.sqrt(2))
        timeRes.SetPointError(c, 0, sigma_err/math.sqrt(2))
        
        sigma_avg.append(sigma/math.sqrt(2))
        sigma_err_avg.append(sigma_err/math.sqrt(2))

        c += 1
       
    
    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    c1.SetLeftMargin(0.12)
    c1.SetRightMargin(0.05)
    c1.SetTopMargin(0.05)
    c1.SetBottomMargin(0.1)

    colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kGreen+1]
    
    
    # time res
    c1.cd()
    c1.Clear()
    
    timeRes.SetLineWidth(2)
    timeRes.SetLineColor(ROOT.kBlue)
    timeRes.SetMarkerStyle(20)
    timeRes.SetMarkerColor(ROOT.kBlue)
    
    #yMin = math.floor(0.8/10*ROOT.TMath.MinElement(timeRes.GetN(), timeRes.GetY()))*10
    #yMax = math.floor(1.2/10*ROOT.TMath.MaxElement(timeRes.GetN(), timeRes.GetY()))*10
  
    dummy = functions.dummyHist("Strip number", "Time resolution (ns)", 0, 32, 0, 2)
    dummy.Draw("HIST")
    
    timeRes.Draw("SAME LP")

            
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()
    tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % label)  
    #tLatex.DrawLatex(0.16, 0.85, "Time resolution %.2f #pm %.2f ns" % (sum(sigma_avg)/len(sigma_avg), sum(sigma_err_avg)/len(sigma_err_avg)))
    #tLatex.DrawLatex(0.16, 0.80, "Mean background rate %.2f Hz/cm^{2}" % meanRate)
           
    drawAux(c1, aux = "S%d" % scanid)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/timeRes_strip.png" % saveDir) 
    c1.SaveAs("%s/timeRes_strip.pdf" % saveDir)  
    

    
    
    
    ## probe hit profile
    c1.cd()
    c1.Clear()

    chambers_stripProfiles[0].GetYaxis().SetNoExponent()
    chambers_stripProfiles[0].SetLineColor(colors[0])
    chambers_stripProfiles[0].SetLineWidth(2)
    chambers_stripProfiles[0].Draw("HIST")
            
    chambers_stripProfiles[0].GetYaxis().SetRangeUser(0, 1.3*max(chambers_stripProfiles[i].GetMaximum() for i in range(0, len(chambers))))
    chambers_stripProfiles[0].GetXaxis().SetTitle("Strip number")
    chambers_stripProfiles[0].GetXaxis().SetTitleOffset(1.2)
    chambers_stripProfiles[0].GetXaxis().SetLabelOffset(0.005)
    chambers_stripProfiles[0].GetXaxis().SetLabelSize(0.04)

    chambers_stripProfiles[0].GetYaxis().SetTitle("Number of hits")   
    chambers_stripProfiles[0].GetYaxis().SetTitleOffset(1.8)
    chambers_stripProfiles[0].GetYaxis().SetLabelOffset(0.005)    
    
    for i in range(1, len(chambers)):
        chambers_stripProfiles[i].SetLineColor(colors[i])
        chambers_stripProfiles[i].SetLineWidth(2)
        chambers_stripProfiles[i].Draw("HIST SAME")

            
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()
    #tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % getattr(config, probeChamber)["chamberName"])  
    #tLatex.DrawLatex(0.16, 0.85, "Hit profile after tracking cuts")
    #tLatex.DrawLatex(0.16, 0.80, "Eff. %.2f %% (%s/%d)" % (100.*eff, nHits, nTriggers))
           
    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/hitProfiles.png" % saveDir) 
    c1.SaveAs("%s/hitProfiles.pdf" % saveDir)  


    
    
    ## probe hit profile
    c1.cd()
    c1.Clear()

    chambers_stripProfiles_CLS[0].GetYaxis().SetNoExponent()
    chambers_stripProfiles_CLS[0].SetLineColor(colors[0])
    chambers_stripProfiles_CLS[0].SetLineWidth(2)
    chambers_stripProfiles_CLS[0].Draw("HIST")
            
    chambers_stripProfiles_CLS[0].GetYaxis().SetRangeUser(0, 1.3*max(chambers_stripProfiles_CLS[i].GetMaximum() for i in range(0, len(chambers))))
    chambers_stripProfiles_CLS[0].GetXaxis().SetTitle("Strip number")
    chambers_stripProfiles_CLS[0].GetXaxis().SetTitleOffset(1.2)
    chambers_stripProfiles_CLS[0].GetXaxis().SetLabelOffset(0.005)
    chambers_stripProfiles_CLS[0].GetXaxis().SetLabelSize(0.04)

    chambers_stripProfiles_CLS[0].GetYaxis().SetTitle("Number of hits")   
    chambers_stripProfiles_CLS[0].GetYaxis().SetTitleOffset(1.8)
    chambers_stripProfiles_CLS[0].GetYaxis().SetLabelOffset(0.005)    
    
    for i in range(1, len(chambers)):
    

        chambers_stripProfiles_CLS[i].SetLineColor(colors[i])
        chambers_stripProfiles_CLS[i].SetLineWidth(2)
        chambers_stripProfiles_CLS[i].Draw("HIST SAME")

            
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()
    #tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % getattr(config, probeChamber)["chamberName"])  
    #tLatex.DrawLatex(0.16, 0.85, "Hit profile after tracking cuts")
    #tLatex.DrawLatex(0.16, 0.80, "Eff. %.2f %% (%s/%d)" % (100.*eff, nHits, nTriggers))
           
    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/hitProfiles_CLS.png" % saveDir) 
    c1.SaveAs("%s/hitProfiles_CLS.pdf" % saveDir) 
    
    
    
    ## probe hit profile
    c1.cd()
    c1.Clear()

    chambers_stripProfiles_allCuts[0].GetYaxis().SetNoExponent()
    chambers_stripProfiles_allCuts[0].SetLineColor(colors[0])
    chambers_stripProfiles_allCuts[0].SetLineWidth(2)
    chambers_stripProfiles_allCuts[0].Draw("HIST")
            
    chambers_stripProfiles_allCuts[0].GetYaxis().SetRangeUser(0, 1.3*chambers_stripProfiles_allCuts[0].GetMaximum())
    chambers_stripProfiles_allCuts[0].GetXaxis().SetTitle("Strip number")
    chambers_stripProfiles_allCuts[0].GetXaxis().SetTitleOffset(1.2)
    chambers_stripProfiles_allCuts[0].GetXaxis().SetLabelOffset(0.005)
    chambers_stripProfiles_allCuts[0].GetXaxis().SetLabelSize(0.04)

    chambers_stripProfiles_allCuts[0].GetYaxis().SetTitle("Number of hits")   
    chambers_stripProfiles_allCuts[0].GetYaxis().SetTitleOffset(1.8)
    chambers_stripProfiles_allCuts[0].GetYaxis().SetLabelOffset(0.005)    
    
    for i in range(1, len(chambers)):
    

        chambers_stripProfiles_allCuts[i].SetLineColor(colors[i])
        chambers_stripProfiles_allCuts[i].SetLineWidth(2)
        chambers_stripProfiles_allCuts[i].Draw("HIST SAME")

            
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()
    #tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % getattr(config, probeChamber)["chamberName"])  
    #tLatex.DrawLatex(0.16, 0.85, "Hit profile after tracking cuts")
    #tLatex.DrawLatex(0.16, 0.80, "Eff. %.2f %% (%s/%d)" % (100.*eff, nHits, nTriggers))
           
    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/hitProfiles_allCuts.png" % saveDir) 
    c1.SaveAs("%s/hitProfiles_allCuts.pdf" % saveDir) 
    
    
    
if __name__ == "__main__":

    textHeader = "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}"
    scanid = 5375
    HVPoint = 1
    
    nStats = 100 # number of events required for the fit
   

    
    fOut = "KODEL2D_X_KODELE"
    label = "KODEL2D_X_KODELE"
    chambers = ["KODEL2D_X", "KODELE"]
    ToF(chambers, fOut, label, scanid)
    
   
    
    
