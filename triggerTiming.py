
import sys, os, glob, shutil, json, math, re, random, copy
import ROOT
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

def groupAndOrder(tree, windowStart = -1e9, windowEnd = 1e9):
    
    trgTime = self.getPMTTime()
    
    STRIP = []
    TS = []
    for i,ch in enumerate(self.t.TDC_channel):
        
        if self.t.TDC_TimeStamp[i] < self.timeWindowReject: continue # reject TDC first events (based on uncorrected timing)
            
        if not ch in self.TDC_channels: continue # only consider channels from chamber
        if self.TDC_strips[self.TDC_channels.index(ch)] in self.TDC_strips_mask: continue
            
            
        t = self.t.TDC_TimeStamp[i]-trgTime # corrected time w.r.t. PMT (if enabled)
        if t < windowStart: continue # min time window
        if t > windowEnd: continue # max time window
            
            
        stripNo = self.TDC_channels.index(ch)
        STRIP.append(stripNo)
        TS.append(t)
        
    return STRIP, TS
    
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
    xMin = h.GetBinCenter(binMax) - 50
    xMax = h.GetBinCenter(binMax) + 50
    return xMin, xMax

if __name__ == "__main__":

    strips = list(range(1, 33))
    x = list(range(5112, 5128)) + list(range(5096, 5112))
    y = list(range(5079, 5063, -1)) + list(range(5095,5079, -1))
    
    gt_x = [15, 16, 17]
    gt_y = [16, 17, 18]
    
    ch_x = [x[strips.index(ch)] for ch in gt_x]
    ch_y = [y[strips.index(ch)] for ch in gt_y]
    
    print(ch_x)
    print(ch_y)
    

    scanid = 4950
    HVPoint = 1
    saveDir = "/var/webdcs/HVSCAN/%06d/ANALYSIS/TRG_TIMING/HV%d/" % (scanid, HVPoint)
    textHeader = "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}"
    
    fIn = ROOT.TFile("/var/webdcs/HVSCAN/%06d/Scan%06d_HV%d_DAQ.root" % (scanid, scanid, HVPoint))
    tree = fIn.Get("RAWData")
    
    
    xWindowMin = -5000
    xWindowMax = 5000
    nBins = 5000*2*10 # resolution of 100 ps
    timeProfile_int1 = ROOT.TH1D("timeProfile_int1", "", nBins, xWindowMin, xWindowMax)
    timeProfile_int2 = ROOT.TH1D("timeProfile_int2", "", nBins, xWindowMin, xWindowMax)
    timeProfile_ext1 = ROOT.TH1D("timeProfile_ext1", "", nBins, xWindowMin, xWindowMax)
    timeProfile_ext2 = ROOT.TH1D("timeProfile_ext2", "", nBins, xWindowMin, xWindowMax)
    timeProfile_all = ROOT.TH1D("timeProfile_ext2", "", nBins, xWindowMin, xWindowMax)  
        

    counts = 0
    for evNum in range(0, tree.GetEntries()+1):
        
        tree.GetEntry(evNum)
        if tree.TriggerTag != 1: continue # muon spill
        
        
        if not 5003 in tree.TDC_channel: continue # coincidence = INT X
        #if not 5004 in tree.TDC_channel: continue # EXT 1
        #if not 5005 in tree.TDC_channel: continue # EXT 2
        if not 5006 in tree.TDC_channel: continue # INT 1
        if not 5007 in tree.TDC_channel: continue # INT 2
        
        # reference time = trigger time (5003)
        c = 0
        trgTime = 0
        refTime = 0
        for i,ch in enumerate(tree.TDC_channel):
            if ch == 5003: # 5007
                c += 1
                trgTime = tree.TDC_TimeStamp[i]
                
            if ch == 5006: # 5007
                refTime = tree.TDC_TimeStamp[i]
 
        if c != 1: continue
        
        
        #if not 5127 in tree.TDC_channel: continue
        #if not 5095 in tree.TDC_channel: continue
        
        counts += 1
        
        #if not 5096 in tree.TDC_channel: continue # gt x
        #if not 5095 in tree.TDC_channel: continue # gt x
        #if not 5098 in tree.TDC_channel: continue # gt x
        
        #if not 5095 in tree.TDC_channel: continue # gt y
        #if not 5094 in tree.TDC_channel: continue # gt y
        #if not 5096 in tree.TDC_channel: continue # gt y
        
        #if len(tree.TDC_channel) != 11: continue
        #if len(tree.TDC_channel) > 10: continue
        
        #print(tree.TDC_channel)
        
      
        
        #print(idx, trgTime)
            

        for i,ch in enumerate(tree.TDC_channel):
        
            if ch == 5003: c += 1
            if ch == 5004: timeProfile_ext1.Fill(tree.TDC_TimeStamp[i]-trgTime)
            if ch == 5005: timeProfile_ext2.Fill(tree.TDC_TimeStamp[i]-trgTime)
            if ch == 5006: timeProfile_int1.Fill(tree.TDC_TimeStamp[i]-trgTime)
            if ch == 5007: timeProfile_int2.Fill(tree.TDC_TimeStamp[i]-trgTime)
    
    print counts

    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    c1.SetLeftMargin(0.12)
    c1.SetRightMargin(0.05)
    c1.SetTopMargin(0.05)
    c1.SetBottomMargin(0.1)
    
    tLatex = ROOT.TLatex()
    tLatex.SetTextFont(42)
    tLatex.SetTextSize(0.03)
    tLatex.SetNDC()

    
    


    
    ## EXT1
    c1.cd()
    c1.Clear()

    xTimeMin, xTimeMax = getMinMax(timeProfile_ext1)
    timeProfile_ext1.GetXaxis().SetRangeUser(xTimeMin, xTimeMax)
    timeProfile_ext1.Draw("HIST")
    timeProfile_ext1.GetYaxis().SetRangeUser(0, 1.3*timeProfile_ext1.GetMaximum())
    timeProfile_ext1.SetLineColor(ROOT.kBlack)
    
    timeProfile_ext1.GetXaxis().SetTitle("Time (ns)")
    timeProfile_ext1.GetXaxis().SetTitleOffset(1.2)
    timeProfile_ext1.GetXaxis().SetLabelOffset(0.005)

    timeProfile_ext1.GetYaxis().SetTitle("Hits / 100 ps")   
    timeProfile_ext1.GetYaxis().SetTitleOffset(1.8)
    timeProfile_ext1.GetYaxis().SetLabelOffset(0.005)
    
    xMaximum = timeProfile_ext1.GetBinCenter(timeProfile_ext1.GetMaximumBin())
    timeProfile_ext1_fit = ROOT.TF1("timeProfile_ext1_fit", "gaus", xTimeMin, xTimeMax)
    timeProfile_ext1_fit.SetParameters(timeProfile_ext1.Integral(), xMaximum, timeProfile_ext1.GetRMS())
    timeProfile_ext1.Fit("timeProfile_ext1_fit", "RW", "", xTimeMin, xTimeMax)
    
    fitParams = ROOT.TLatex()
    fitParams.SetTextFont(42)
    fitParams.SetTextSize(0.03)
    fitParams.SetNDC()
    fitParams.DrawLatex(0.16, 0.9, "#bf{EXTERNAL 1}")
    fitParams.DrawLatex(0.16, 0.85, "#color[2]{Peak mean: %.2f ns}" % timeProfile_ext1_fit.GetParameter(1))
    fitParams.DrawLatex(0.16, 0.80, "#color[2]{Peak width (#sigma): %.2f ns}" % timeProfile_ext1_fit.GetParameter(2))
    
    peakFitDraw = timeProfile_ext1_fit.Clone("tmp1")
    peakFitDraw.SetLineColor(ROOT.kRed)
    peakFitDraw.SetLineWidth(3)
    peakFitDraw.Draw("L SAME")


    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/timeProfile_ext1.png" % saveDir) 
    c1.SaveAs("%s/timeProfile_ext1.pdf" % saveDir) 

   
   
   

    ## EXT2
    c1.cd()
    c1.Clear()

    xTimeMin, xTimeMax = getMinMax(timeProfile_ext2)
    
    
    timeProfile_ext2.GetXaxis().SetRangeUser(xTimeMin, xTimeMax)
    timeProfile_ext2.Draw("HIST")
    timeProfile_ext2.GetYaxis().SetRangeUser(0, 1.3*timeProfile_ext2.GetMaximum())
    timeProfile_ext2.SetLineColor(ROOT.kBlack)
    
    timeProfile_ext2.GetXaxis().SetTitle("Time (ns)")
    timeProfile_ext2.GetXaxis().SetTitleOffset(1.2)
    timeProfile_ext2.GetXaxis().SetLabelOffset(0.005)

    timeProfile_ext2.GetYaxis().SetTitle("Hits / 100 ps")   
    timeProfile_ext2.GetYaxis().SetTitleOffset(1.8)
    timeProfile_ext2.GetYaxis().SetLabelOffset(0.005)
     
    xMaximum = timeProfile_ext2.GetBinCenter(timeProfile_ext2.GetMaximumBin())
    timeProfile_ext2_fit = ROOT.TF1("timeProfile_ext2_fit", "gaus", xTimeMin, xTimeMax)
    timeProfile_ext2_fit.SetParameters(timeProfile_ext2.Integral(), xMaximum, timeProfile_ext1.GetRMS())
    timeProfile_ext2.Fit("timeProfile_ext2_fit", "RW", "", xTimeMin, xTimeMax)
    
    fitParams = ROOT.TLatex()
    fitParams.SetTextFont(42)
    fitParams.SetTextSize(0.03)
    fitParams.SetNDC()
    fitParams.DrawLatex(0.16, 0.9, "#bf{EXTERNAL 2}")
    fitParams.DrawLatex(0.16, 0.85, "#color[2]{Peak mean: %.2f ns}" % timeProfile_ext2_fit.GetParameter(1))
    fitParams.DrawLatex(0.16, 0.80, "#color[2]{Peak width (#sigma): %.2f ns}" % timeProfile_ext2_fit.GetParameter(2))
    
    peakFitDraw = timeProfile_ext2_fit.Clone("tmp2")
    peakFitDraw.SetLineColor(ROOT.kRed)
    peakFitDraw.SetLineWidth(3)
    peakFitDraw.Draw("L SAME")


    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/timeProfile_ext2.png" % saveDir) 
    c1.SaveAs("%s/timeProfile_ext2.pdf" % saveDir) 




    xTimeMin, xTimeMax = -50, 50

    ## INT1
    c1.cd()
    c1.Clear()

    xTimeMin, xTimeMax = getMinMax(timeProfile_int1)
    xTimeMin += 46
    xTimeMax -= 46
    
    timeProfile_int1.GetXaxis().SetRangeUser(xTimeMin, xTimeMax)
    timeProfile_int1.Draw("HIST")
    timeProfile_int1.GetYaxis().SetRangeUser(0, 1.3*timeProfile_int1.GetMaximum())
    timeProfile_int1.SetLineColor(ROOT.kBlack)
    
    timeProfile_int1.GetXaxis().SetTitle("Time (ns)")
    timeProfile_int1.GetXaxis().SetTitleOffset(1.2)
    timeProfile_int1.GetXaxis().SetLabelOffset(0.005)

    timeProfile_int1.GetYaxis().SetTitle("Hits / 100 ps")   
    timeProfile_int1.GetYaxis().SetTitleOffset(1.8)
    timeProfile_int1.GetYaxis().SetLabelOffset(0.005)
     
    xMaximum = timeProfile_int1.GetBinCenter(timeProfile_int1.GetMaximumBin())
    timeProfile_int1_fit = ROOT.TF1("timeProfile_ext1_fit", "gaus", xTimeMin, xTimeMax)
    timeProfile_int1_fit.SetParameters(timeProfile_int1.Integral(), xMaximum, timeProfile_ext1.GetRMS())
    timeProfile_int1.Fit("timeProfile_ext1_fit", "RW", "", xTimeMin, xTimeMax)
    
    fitParams = ROOT.TLatex()
    fitParams.SetTextFont(42)
    fitParams.SetTextSize(0.03)
    fitParams.SetNDC()
    fitParams.DrawLatex(0.16, 0.9, "#bf{INTERNAL 1}")
    fitParams.DrawLatex(0.16, 0.85, "#color[2]{Peak mean: %.2f ns}" % timeProfile_int1_fit.GetParameter(1))
    fitParams.DrawLatex(0.16, 0.80, "#color[2]{Peak width (#sigma): %.2f ns}" % timeProfile_int1_fit.GetParameter(2))
    
    peakFitDraw = timeProfile_int1_fit.Clone("tmp3")
    peakFitDraw.SetLineColor(ROOT.kRed)
    peakFitDraw.SetLineWidth(3)
    peakFitDraw.Draw("L SAME")


    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/timeProfile_int1.png" % saveDir) 
    c1.SaveAs("%s/timeProfile_int1.pdf" % saveDir) 


    ## INT 2
    c1.cd()
    c1.Clear()

    xTimeMin, xTimeMax = getMinMax(timeProfile_int2)
    timeProfile_int2.GetXaxis().SetRangeUser(xTimeMin, xTimeMax)
    timeProfile_int2.Draw("HIST")
    timeProfile_int2.GetYaxis().SetRangeUser(0, 1.3*timeProfile_int2.GetMaximum())
    timeProfile_int2.SetLineColor(ROOT.kBlack)
    
    timeProfile_int2.GetXaxis().SetTitle("Time (ns)")
    timeProfile_int2.GetXaxis().SetTitleOffset(1.2)
    timeProfile_int2.GetXaxis().SetLabelOffset(0.005)

    timeProfile_int2.GetYaxis().SetTitle("Hits / 100 ps")   
    timeProfile_int2.GetYaxis().SetTitleOffset(1.8)
    timeProfile_int2.GetYaxis().SetLabelOffset(0.005)
     
    xMaximum = timeProfile_int2.GetBinCenter(timeProfile_int2.GetMaximumBin())
    timeProfile_int2_fit = ROOT.TF1("timeProfile_ext2_fit", "gaus", xTimeMin, xTimeMax)
    timeProfile_int2_fit.SetParameters(timeProfile_int1.Integral(), xMaximum, timeProfile_ext1.GetRMS())
    timeProfile_int2.Fit("timeProfile_ext2_fit", "RW", "", xTimeMin, xTimeMax)
    
    fitParams = ROOT.TLatex()
    fitParams.SetTextFont(42)
    fitParams.SetTextSize(0.03)
    fitParams.SetNDC()
    fitParams.DrawLatex(0.16, 0.9, "#bf{INTERNAL 2}")
    fitParams.DrawLatex(0.16, 0.85, "#color[2]{Peak mean: %.2f ns}" % timeProfile_int2_fit.GetParameter(1))
    fitParams.DrawLatex(0.16, 0.80, "#color[2]{Peak width (#sigma): %.2f ns}" % timeProfile_int2_fit.GetParameter(2))
    
    peakFitDraw = timeProfile_int2_fit.Clone("tmp4")
    peakFitDraw.SetLineColor(ROOT.kRed)
    peakFitDraw.SetLineWidth(3)
    peakFitDraw.Draw("L SAME")

    drawAux(c1)
    c1.RedrawAxis()
    c1.Modify()        
    c1.SaveAs("%s/timeProfile_int2.png" % saveDir) 
    c1.SaveAs("%s/timeProfile_int2.pdf" % saveDir)     
   
    
    