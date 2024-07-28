
import sys, os, glob, shutil, json, math, re, random, copy
import ROOT
import analyzer as an
import analyzer2D as an2D
import analyzeTracking1D as anT
import config_TR as config
import functions

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


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

    xMin, xMax = -5000, 5000
    
    for i in range(0, h.GetNbinsX()+1):
    
        if h.GetBinContent(i) != 0:
            xMin = h.GetBinCenter(i)
            break
            
    for i in range(h.GetNbinsX()+1, 0, -1):
    
        if h.GetBinContent(i) != 0:
            xMax = h.GetBinCenter(i)
            break
            
            
    return xMin, xMax

def doTimeProfilePlot(h, fOut, label):

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
    fitParams.DrawLatex(0.16, 0.9, "%s %d" % (label, h.GetEntries()))
    fitParams.DrawLatex(0.16, 0.85, "#color[2]{Peak mean: %.2f ns}" % mean)
    fitParams.DrawLatex(0.16, 0.80, "#color[2]{Peak width (#sigma): %.2f ns}" % sigma)
            


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


if __name__ == "__main__":

    scanid = 4769
    HVPoint = 1
    

    # SOURCE OFF
    # - BARC 8     4933             T1S1 TDC2A
    # - BARC 9     4934             T1S2 TDC2B 9850
    # - CERN 165   4931             T1S3 TDC2D
    # - CERN 166   4932             T1S3 TDC2C



    
    ## dir: ROOT directory of all raw data files 
    dir = "/Users/thiagorangel/GIFpp_Analysis_Apr24" 
    

    
   
    
    
    tagChamber = "GT_TRACKING"
    
    #probeChamber, scanid, probeStripNo = "RE4_2_CERN_166_C", 4932, 15
    #probeChamber, scanid, probeStripNo = "RE2_2_NPD_BARC_8_C", 4933, 15
    #probeChamber, scanid, probeStripNo = "RE2_2_NPD_BARC_9_C", 4934, 16

    
    
    '''
    Procedure:
        1) find good tracking strips in beam center
        2) locate the max bins for GTx, GTy and probe
        
    '''
    
    if True: # ABS 4.6
    
        probeChamber, scanid = "RE4_2_CERN_165_C", 4983
    
        strips_GT_x = [15]
        strips_GT_y = [17]
    
        probeStripNo = 14
        trxStripNo = 15
        tryStripNo = 16
    
    
    if False: # SOURCE OFF
    
        probeChamber, scanid = "RE4_2_CERN_165_C", 4931
    
        strips_GT_x = [14, 15, 16]
        strips_GT_y = [16, 17, 18]
    
        probeStripNo = 14
        trxStripNo = 15
        tryStripNo = 16
        
    if False: # ABS 10
    
        probeChamber, scanid = "RE4_2_CERN_165_C", 4982
    
        strips_GT_x = [14, 15, 16]
        strips_GT_y = [16, 17, 18]
    
        probeStripNo = 14
        trxStripNo = 14
        tryStripNo = 16
    
    
    if False:
    
        probeChamber, scanid = "RE4_2_CERN_166_C", 4932
    
        strips_GT_x = [15]
        strips_GT_y = [17]
    
        probeStripNo = 14
        trxStripNo = 15 # 15
        tryStripNo = 17
    
    if False:
    
        probeChamber, scanid = "RE2_2_NPD_BARC_8_C", 4933
    
        strips_GT_x = [14, 15, 16]
        strips_GT_y = [16, 17, 18]
    
        probeStripNo = 15
        trxStripNo = 15 # 15
        tryStripNo = 17
    
    
    
    ########################################################
   
    
    
    #config.GT2p0_1['TDC_strips_mask'] = copy.deepcopy(config.GT2p0_1['TDC_strips'])
    #for s in strips_GT_x: config.GT2p0_1['TDC_strips_mask'].remove(s)
    
    # do full cluster analysis for GT_y, as the clusters depend on 
    #config.GT2p0_2['TDC_strips_mask'] = copy.deepcopy(config.GT2p0_2['TDC_strips'])
    #for s in strips_GT_y: config.GT2p0_2['TDC_strips_mask'].remove(s)


    tag = "RPCTracking1D_GT"
    basedir = "/Users/thiagorangel/GIFpp_Analysis_Apr24" 
    if os.path.exists("%s/ANALYSIS/" % basedir): shutil.rmtree("%s/ANALYSIS/" % basedir) # delete output dir, if exists
    
    outputdir = "%s/ANALYSIS/%s/" % (basedir, tag)
    if os.path.exists(outputdir): shutil.rmtree(outputdir) # delete output dir, if exists
    if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir
    
    saveDir = outputdir + "HV%d/" % HVPoint
    if os.path.exists(saveDir): shutil.rmtree(saveDir) # delete output dir, if exists
    if not os.path.exists(saveDir):os.makedirs(saveDir) # make output dir
    
    textHeader = "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}"

    tr = anT.RPCTracking1D(basedir, saveDir, scanid, HVPoint, config, textHeader) # pass the config as object
    tr.setTagChamber(tagChamber) # first the tagging chamber
    tr.addProbeChamber(probeChamber) # then add probe chambers
    tr.collectClusters()
    tr.createTracks()
    tr.eventDisplay()
    tr.efficiency(1) # infinite tolerance
    
    cluster_collection, cluster_time_collection, cluster_barycenter_collection = tr.exportProbeClusters()
    cluster_collection_trx, cluster_time_collection_trx, cluster_barycenter_collection_trx, cluster_collection_try, cluster_time_collection_try, cluster_barycenter_collection_try = tr.exportTrackingClusters()
    #analyzer_tr = tr.analyzer_tr
    #tr.write()
    del tr
    

   
   
    
    nBins = 2*10*5000 # 100 ps resolution
    timeProfile_probe = ROOT.TH1D("timeProfile_probe", "", nBins, -5000, 5000)
    
    
    dt_probe_trx = ROOT.TH1D("dt_probe_trx", "", nBins, -5000, 5000)
    dt_probe_try = ROOT.TH1D("dt_probe_try", "", nBins, -5000, 5000)
    dt_trx_try = ROOT.TH1D("dt_trx_try", "", nBins, -5000, 5000)
    
    dt_probe_trg = ROOT.TH1D("dt_probe_trg", "", nBins, -5000, 5000)
    dt_try_trg = ROOT.TH1D("dt_try_trg", "", nBins, -5000, 5000)
    dt_trx_trg = ROOT.TH1D("dt_trx_trg", "", nBins, -5000, 5000)
    
    
    xBeamMin, xBeamMax, = -20, 20
    nBeamBins = (xBeamMax - xBeamMin)/2 # 1 cm bins
    beamProfile_tag = ROOT.TH1D("beamProfile_tag", "", nBeamBins, xBeamMin, xBeamMax)
    beamProfile_probe = ROOT.TH1D("beamProfile_probe", "", nBeamBins, xBeamMin, xBeamMax)
    beamProfile_probe_trcuts = ROOT.TH1D("beamProfile_probe_trcuts", "", nBeamBins, xBeamMin, xBeamMax) # after tracking cuts
    
    probeStripProfile = ROOT.TH1D("probeStripProfile", "", 32, 1, 33)
    trackingXStripProfile = ROOT.TH1D("trackingXStripProfile", "", 32, 1, 33)
    trackingYStripProfile = ROOT.TH1D("trackingYStripProfile", "", 32, 1, 33)
    
    for i in range(1, 33): 
        probeStripProfile.GetXaxis().SetBinLabel(i, str(i))
        trackingXStripProfile.GetXaxis().SetBinLabel(i, str(i))
        trackingYStripProfile.GetXaxis().SetBinLabel(i, str(i))
    
    xTimeMin, xTimeMax = 1e9, -1e9
    
    nTriggers, nHits = 0, 0
    for iEv in range(0, len(cluster_collection)):
    
        
    
        # tracking chambers: one cluster and MAX CLS of 3
        if len(cluster_collection_trx[iEv]) != 1: continue
        if len(cluster_collection_try[iEv]) != 1: continue
        
        if len(cluster_collection_trx[iEv][0]) > 4: continue
        if len(cluster_collection_try[iEv][0]) > 3: continue 
        
        
        
        # fill 
        for t in cluster_barycenter_collection[iEv][1]: beamProfile_probe.Fill(t)
        beamProfile_tag.Fill(cluster_barycenter_collection_try[iEv][0])
        

        # check strips in x
        stripFound = False
        for strip in strips_GT_x:
        
            if strip in cluster_collection_trx[iEv][0]: 
                stripFound = True
                break
        if not stripFound: continue    


        
        # check strips in y
        stripFound = False
        for strip in strips_GT_y:
        
            if strip in cluster_collection_try[iEv][0]: 
                stripFound = True
                break
        if not stripFound: continue  
        
        
        nTriggers += 1 # valid tracking triggers
        if len(cluster_barycenter_collection[iEv][1]) != 1: continue # only one cluster for probe
        
        nHits += 1
        
        # fill profile histograms
        beamProfile_probe_trcuts.Fill(cluster_barycenter_collection_try[iEv][0])
        for strip in cluster_collection[iEv][1][0]: probeStripProfile.Fill(strip)
        for strip in cluster_collection_trx[iEv][0]: trackingXStripProfile.Fill(strip)
        for strip in cluster_collection_try[iEv][0]: trackingYStripProfile.Fill(strip)
        
        
        
        
        
        ## do time profiles: require hits in x, y and probe chambers
        
        if not probeStripNo in cluster_collection[iEv][1][0]: continue
        probeStrip_idx = cluster_collection[iEv][1][0].index(probeStripNo)
        probeStrip_time = cluster_time_collection[iEv][1][0][probeStrip_idx]
        dt_probe_trg.Fill(probeStrip_time)
          

        if not trxStripNo in cluster_collection_trx[iEv][0]: continue
        trxStrip_idx = cluster_collection_trx[iEv][0].index(trxStripNo)
        trxStrip_time = cluster_time_collection_trx[iEv][0][trxStrip_idx]
        dt_trx_trg.Fill(trxStrip_time)
        
        
        if not tryStripNo in cluster_collection_try[iEv][0]: continue
        tryStrip_idx = cluster_collection_try[iEv][0].index(tryStripNo)
        tryStrip_time = cluster_time_collection_try[iEv][0][tryStrip_idx]
        dt_try_trg.Fill(tryStrip_time)
        
        
        
        dt_probe_trx.Fill(probeStrip_time-trxStrip_time)
        dt_probe_try.Fill(probeStrip_time-tryStrip_time)
        dt_trx_try.Fill(trxStrip_time-tryStrip_time)
        
        
        
        
              

        
        
    
    

    
    eff = 1.0*nHits / nTriggers
    
    
    
    doTimeProfilePlot(dt_probe_trg, saveDir+"/dt_probe_trg", "#Delta(T_{probe} #minus T_{trigger})")
    doTimeProfilePlot(dt_trx_trg, saveDir+"/dt_trx_trg", "#Delta(T_{GTx} #minus T_{trigger})")
    doTimeProfilePlot(dt_try_trg, saveDir+"/dt_try_trg", "#Delta(T_{GTy} #minus T_{trigger})")
    
    
    doTimeProfilePlot(dt_probe_trx, saveDir+"/dt_probe_trx", "#Delta(T_{probe} #minus T_{GTx})")
    doTimeProfilePlot(dt_probe_try, saveDir+"/dt_probe_try", "#Delta(T_{probe} #minus T_{GTy})")
    doTimeProfilePlot(dt_trx_try, saveDir+"/dt_trx_try", "#Delta(T_{GTx} #minus T_{GTy})")
    

    

    
    
    
    
    
    
    
    
    
    
    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    c1.SetLeftMargin(0.12)
    c1.SetRightMargin(0.05)
    c1.SetTopMargin(0.05)
    c1.SetBottomMargin(0.1)
    

    
    
    

    ## beam profile
    c1.cd()
    c1.Clear()

    beamProfile_tag.GetYaxis().SetNoExponent()
    beamProfile_tag.SetLineColor(ROOT.kBlack)
    beamProfile_tag.SetLineWidth(2)
    beamProfile_tag.Draw("HIST")
    
    beamProfile_probe.SetLineColor(ROOT.kBlue)
    beamProfile_probe.SetLineWidth(2)
    beamProfile_probe.Draw("SAME HIST")
    
    beamProfile_probe_trcuts.SetLineColor(ROOT.kRed)
    beamProfile_probe_trcuts.SetLineWidth(2)
    beamProfile_probe_trcuts.Draw("SAME HIST")
    
    
            
    beamProfile_tag.GetYaxis().SetRangeUser(0, 1.3*max([beamProfile_tag.GetMaximum(), beamProfile_probe.GetMaximum(), beamProfile_probe_trcuts.GetMaximum()]))
    beamProfile_tag.GetXaxis().SetTitle("Beam profile (cm)")
    beamProfile_tag.GetXaxis().SetTitleOffset(1.2)
    beamProfile_tag.GetXaxis().SetLabelOffset(0.005)
    beamProfile_tag.GetXaxis().SetLabelSize(0.04)

    beamProfile_tag.GetYaxis().SetTitle("Number of hits")   
    beamProfile_tag.GetYaxis().SetTitleOffset(1.8)
    beamProfile_tag.GetYaxis().SetLabelOffset(0.005)    

            
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()
    tLatex.DrawLatex(0.16, 0.9, "Tracking profile (y)")  
    tLatex.DrawLatex(0.16, 0.85, "#color[4]{Probe chamber profile}" )
    tLatex.DrawLatex(0.16, 0.80, "#color[2]{Probe chamber profile after tracking cuts}")

    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/beamProfile.png" % saveDir) 
    c1.SaveAs("%s/beamProfile.pdf" % saveDir)   
  
  
  

    
    
    
    ## probe hit profile
    c1.cd()
    c1.Clear()

    probeStripProfile.GetYaxis().SetNoExponent()
    probeStripProfile.SetFillStyle(3354)
    probeStripProfile.SetFillColor(ROOT.kBlue)
    probeStripProfile.SetFillColorAlpha(ROOT.kBlue, 0.35)
    probeStripProfile.SetLineColor(ROOT.kBlue)
    probeStripProfile.SetLineWidth(2)
    probeStripProfile.Draw("HIST")
            
    probeStripProfile.GetYaxis().SetRangeUser(0, 1.3*probeStripProfile.GetMaximum())
    probeStripProfile.GetXaxis().SetTitle("Strip number")
    probeStripProfile.GetXaxis().SetTitleOffset(1.2)
    probeStripProfile.GetXaxis().SetLabelOffset(0.005)
    probeStripProfile.GetXaxis().SetLabelSize(0.04)

    probeStripProfile.GetYaxis().SetTitle("Number of hits")   
    probeStripProfile.GetYaxis().SetTitleOffset(1.8)
    probeStripProfile.GetYaxis().SetLabelOffset(0.005)    

            
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()
    tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % getattr(config, probeChamber)["chamberName"])  
    tLatex.DrawLatex(0.16, 0.85, "Hit profile after tracking cuts")
    tLatex.DrawLatex(0.16, 0.80, "Eff. %.2f %% (%s/%d)" % (100.*eff, nHits, nTriggers))
           
    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/probeHitProfile.png" % saveDir) 
    c1.SaveAs("%s/probeHitProfile.pdf" % saveDir)   



    ## tracking X hit profile
    c1.cd()
    c1.Clear()

    trackingXStripProfile.GetYaxis().SetNoExponent()
    trackingXStripProfile.SetFillStyle(3354)
    trackingXStripProfile.SetFillColor(ROOT.kBlue)
    trackingXStripProfile.SetFillColorAlpha(ROOT.kBlue, 0.35)
    trackingXStripProfile.SetLineColor(ROOT.kBlue)
    trackingXStripProfile.SetLineWidth(2)
    trackingXStripProfile.Draw("HIST")
            
    trackingXStripProfile.GetYaxis().SetRangeUser(0, 1.3*trackingXStripProfile.GetMaximum())
    trackingXStripProfile.GetXaxis().SetTitle("Strip number")
    trackingXStripProfile.GetXaxis().SetTitleOffset(1.2)
    trackingXStripProfile.GetXaxis().SetLabelOffset(0.005)
    trackingXStripProfile.GetXaxis().SetLabelSize(0.04)

    trackingXStripProfile.GetYaxis().SetTitle("Number of hits")   
    trackingXStripProfile.GetYaxis().SetTitleOffset(1.8)
    trackingXStripProfile.GetYaxis().SetLabelOffset(0.005)    

            
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()
    tLatex.DrawLatex(0.16, 0.9, "#bf{GT Tracking (x)}")  
    tLatex.DrawLatex(0.16, 0.85, "Hit profile after tracking cuts")
           
    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/trackingXHitProfile.png" % saveDir) 
    c1.SaveAs("%s/trackingXHitProfile.pdf" % saveDir)   



    ## tracking Y hit profile
    c1.cd()
    c1.Clear()

    trackingYStripProfile.GetYaxis().SetNoExponent()
    trackingYStripProfile.SetFillStyle(3354)
    trackingYStripProfile.SetFillColor(ROOT.kBlue)
    trackingYStripProfile.SetFillColorAlpha(ROOT.kBlue, 0.35)
    trackingYStripProfile.SetLineColor(ROOT.kBlue)
    trackingYStripProfile.SetLineWidth(2)
    trackingYStripProfile.Draw("HIST")
            
    trackingYStripProfile.GetYaxis().SetRangeUser(0, 1.3*trackingYStripProfile.GetMaximum())
    trackingYStripProfile.GetXaxis().SetTitle("Strip number")
    trackingYStripProfile.GetXaxis().SetTitleOffset(1.2)
    trackingYStripProfile.GetXaxis().SetLabelOffset(0.005)
    trackingYStripProfile.GetXaxis().SetLabelSize(0.04)

    trackingYStripProfile.GetYaxis().SetTitle("Number of hits")   
    trackingYStripProfile.GetYaxis().SetTitleOffset(1.8)
    trackingYStripProfile.GetYaxis().SetLabelOffset(0.005)    

            
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()
    tLatex.DrawLatex(0.16, 0.9, "#bf{GT Tracking (y)}")  
    tLatex.DrawLatex(0.16, 0.85, "Hit profile after tracking cuts")
           
    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/trackingYHitProfile.png" % saveDir) 
    c1.SaveAs("%s/trackingYHitProfile.pdf" % saveDir)   

    

    
    
    