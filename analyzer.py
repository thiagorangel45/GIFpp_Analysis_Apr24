
import sys, os, glob, shutil, json, math, re, random, copy
import ROOT
import numpy as np
import networkx as nx # graph tools needed for clusterization

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


class Analyzer():


    
    # drawing options (see function __drawAux())
    c1 = None # default square canvas
    c2 = None # default rectangular canvas
    c3 = None

    def __init__(self, dir, savePath, scanid, HVPoint, scanType):
    
        fIn = None  # pointer to ROOT file
        t_orig = None
        t = None    # raw data tree
       

        
        self.verbose = 0

       
        
        ## list of parameters loaded from the config
        self.muonTriggerWindow = -1
        self.noiseRateTriggerWindow = -1
        self.timeWindowReject = -1
        self.muonWindowWidth = -1 # sigmas
        
        self.nStrips = -1
        self.stripArea = -1
        
        self.TDC_strips = []
        self.TDC_strips_mask = []
        self.TDC_channels = []
        self.TDC_channels_PMT = []
        

        
        ## results from gamma calculation
        self.gammaRate = -1
        self.gammaRate_err = -1
        self.noiseGammaRate = -1
        self.noiseGammaRate_err = -1
        
        self.beamMean = -1
        self.beamSigma = -1
        
        self.PMT_mean = 0
        self.PMT_sigma = 0
        self.PMTValidation = False
        
    
        self.scanid = scanid
        self.HVPoint = HVPoint
        self.basePath = dir
        self.savePath = savePath
        
        self.CMP = {}
        self.CLS = {}
        
        if not os.path.exists(self.savePath): os.makedirs(self.savePath)
   
        
        
        
        # trigger window
        self.scanType = scanType
        
        
        # default square canvas
        self.c1 = ROOT.TCanvas("c1", "c1", 800, 800)
        self.c1.SetLeftMargin(0.12)
        self.c1.SetRightMargin(0.05)
        self.c1.SetTopMargin(0.05)
        self.c1.SetBottomMargin(0.1)
        
        # default rectangular canvas
        self.c2 = ROOT.TCanvas("c2", "c2", 900, 1200)
        self.c2.SetLeftMargin(0.12)
        self.c2.SetRightMargin(0.13)
        self.c2.SetTopMargin(0.05)
        self.c2.SetBottomMargin(0.1)
        
        # rectangular canvas, 2D plots
        self.c3 = ROOT.TCanvas("c3", "c3", 800, 800)
        self.c3.SetLeftMargin(0.12)
        self.c3.SetRightMargin(0.12)
        self.c3.SetTopMargin(0.05)
        self.c3.SetBottomMargin(0.1)
        
        
        ## list of parameters calculated by the analyzer
        self.muonWindowSigma = -1        # time profile width, obtained by Gaussian fit or given by user
        self.muonWindowMean = -1         # time profile mean, obtained by Gaussian by fit or given by user
        self.muonTimeWindowBegin = -1
        self.muonTimeWindowEnd = -1
        self.muonTimeWindow = -1         # length of muon time window
        self.noiseGammaTimeWindowBegin = -1
        self.noiseGammaTimeWindow = -1        # length of gamma time window
        self.noiseGammaTimeWindowEnd = -1
        self.triggerWindow = -1          # either muonTimewindow or noiseGammaTimeWindow (600 or 10000 ns, depending on scan type)
        
        self.outDict = {}
        
        CMP = {}
        CLS = {}
        
    
    def __del__(self):
        if self.slimFile != None and os.path.isfile(self.slimFile): os.remove(self.slimFile) 
    
    def setVerbose(self, verbose):
        self.verbose = verbose
        
        
    def loadConfig(self, cfg):
    
        self.muonTriggerWindow = cfg["muonTriggerWindow"]
        self.noiseRateTriggerWindow = cfg["noiseRateTriggerWindow"]
        self.timeWindowReject = cfg["timeWindowReject"]
        self.muonWindowWidth = cfg["muonWindowWidth"]
        self.TDC_channel_PMT = cfg["TDC_channel_PMT"]
        self.chamberName = cfg["chamberName"]
        self.chamberId = cfg["chamberId"] 
        
        #self.stripArea = cfg["stripArea"]
        #self.nStrips = len(cfg["TDC_channels"]) # correction for masked strips needed ?
        
        self.muonClusterTimeWindow = cfg["muonClusterTimeWindow"]
        self.muonClusterTimeWindowUp = cfg["muonClusterTimeWindowUp"]
        self.muonClusterTimeWindowDw = cfg["muonClusterTimeWindowDw"]
        
        self.gammaClusterTimeWindow = cfg["gammaClusterTimeWindow"]
        self.gammaClusterTimeWindowUp = cfg["gammaClusterTimeWindowUp"]
        self.gammaClusterTimeWindowDw = cfg["gammaClusterTimeWindowDw"]
            
        self.clusterSizeCut = cfg['clusterSizeCut']
        
        self.TDC_strips = cfg["TDC_strips"]
        self.TDC_strips_mask = cfg["TDC_strips_mask"]
        self.TDC_channels = cfg["TDC_channels"]
        

        
        # geometry/tracking parameters
        if "nStrips" in cfg: self.nStrips = cfg["nStrips"]
        if "stripPitch" in cfg: self.stripPitch = cfg["stripPitch"]
        if "stripArea" in cfg: self.stripArea = cfg["stripArea"]
        if "xPos" in cfg: self.xPos = cfg["xPos"]
        if "zPos" in cfg: self.zPos = cfg["zPos"]

        
        
        if "textHeader" in cfg: self.textHeader = cfg["textHeader"]
        else: self.textHeader = ""
        
        
        if self.scanType == "efficiency": self.triggerWindow = self.muonTriggerWindow
        if self.scanType == "rate": self.triggerWindow = self.noiseRateTriggerWindow

        self.slimTree()

    def slimTree(self):
    
        # slim the tree: only allow events with given TDC channels + PMT ones
        fIn = ROOT.TFile("%s/Scan%.6d_HV%d_DAQ.root" % (self.basePath, self.scanid, self.HVPoint))
        t_orig = fIn.Get("RAWData")
    
    
        chs_save = copy.deepcopy(self.TDC_channels)
        if self.TDC_channel_PMT != -1: chs_save.append(self.TDC_channel_PMT)

        self.slimFile = "%s_HV%d.root" %(self.chamberId, self.HVPoint)
        fOut = ROOT.TFile(self.slimFile, "recreate")
        t_slim = ROOT.TTree("RAWData", "RAWData")
        
        EventNumber = np.zeros(1, dtype=int)
        number_of_hits = np.zeros(1, dtype=int)
        Quality_flag = np.zeros(1, dtype=int)
        TDC_channel = ROOT.vector('double')()
        TDC_TimeStamp = ROOT.vector('double')()
        TriggerTag = np.zeros(1, dtype=int)

        t_slim.Branch("EventNumber", EventNumber, "EventNumber/I")
        t_slim.Branch("number_of_hits", number_of_hits, "number_of_hits/I")
        t_slim.Branch("Quality_flag", Quality_flag, "Quality_flag/I")
        t_slim.Branch("TDC_channel", TDC_channel)
        t_slim.Branch("TDC_TimeStamp", TDC_TimeStamp)
        t_slim.Branch("TriggerTag", TriggerTag, "Quality_flag/I")
        
        
        for evNum in range(0, t_orig.GetEntries()):
        
            t_orig.GetEntry(evNum)

            EventNumber[0] = evNum
            number_of_hits[0] = t_orig.number_of_hits
            Quality_flag[0] = t_orig.Quality_flag
            TriggerTag[0] = t_orig.TriggerTag

            
            for i,ch in enumerate(t_orig.TDC_channel):
                
                if ch in chs_save:
                    TDC_channel.push_back(t_orig.TDC_channel[i])
                    TDC_TimeStamp.push_back(t_orig.TDC_TimeStamp[i])

            t_slim.Fill()
            TDC_channel.clear()
            TDC_TimeStamp.clear()
            
        t_slim.AutoSave()
        fIn.Close()
        fOut.Close()
        
        # load new Tree to analyzer
        self.fIn = ROOT.TFile(self.slimFile)
        self.t = self.fIn.Get("RAWData")  

    def timeStripProfile2D(self):
    
        ROOT.gStyle.SetPalette(ROOT.kDarkRainBow)

        self.c2.cd()
        self.c2.Clear()


        nBins = self.muonTriggerWindow # 1 ns resolution, scale in us
        timeStripProfile_spill = ROOT.TH2D("timeStripProfile_spill", "", nBins, 0, int(self.muonTriggerWindow)/1000, self.nStrips, min(self.TDC_strips), max(self.TDC_strips)+1)
            
        nBins = 5*self.muonTriggerWindow # 500 ps resolution, scale in ns
        timeStripProfile_spill_zoom = ROOT.TH2D("timeStripProfile_spill_zoom", "", nBins, 0, int(self.muonTriggerWindow), self.nStrips, min(self.TDC_strips), max(self.TDC_strips)+1)  
        
        
        
        
        # loop over all strips: set the y-axis label and set all bin contents to zero          
        for i in range(1, self.nStrips+1):
        
            timeStripProfile_spill.GetYaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))
            timeStripProfile_spill_zoom.GetYaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))
        
        for evNum in range(0, self.t.GetEntries()):
        
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            
            if self.isBeamTrigger():
            
                firedStrips, timeStamps = self.__groupAndOrder()
                for i,ch in enumerate(firedStrips): timeStripProfile_spill.Fill(timeStamps[i]/1000, self.TDC_strips[ch])
                for i,ch in enumerate(firedStrips): timeStripProfile_spill_zoom.Fill(timeStamps[i], self.TDC_strips[ch])
                        
            
        

        timeStripProfile_spill.GetXaxis().SetTitle("Time (#mus)")
        timeStripProfile_spill.GetXaxis().SetTitleOffset(1.0)
        timeStripProfile_spill.GetXaxis().SetLabelOffset(0.0)

        timeStripProfile_spill.GetYaxis().SetTitle("Strip number")   
        timeStripProfile_spill.GetYaxis().SetTitleOffset(1.3)
        timeStripProfile_spill.GetYaxis().SetLabelOffset(0.005)
        
        timeStripProfile_spill.Draw("COLZ")
        
        self.__drawAux(self.c2)
        self.c2.RedrawAxis()
        self.c2.Modify()    
        if self.verbose > 0:
            self.c2.SaveAs("%stimeStripProfile2D_spill.png" % self.savePath) 
            self.c2.SaveAs("%stimeStripProfile2D_spill.pdf" % self.savePath) 
            
            
        ## zoomed plot   
        delta = 20
        xMin_ = self.muonWindowMean - delta
        xMax_ = self.muonWindowMean + delta
        
        
        timeStripProfile_spill_zoom.GetXaxis().SetRangeUser(xMin_, xMax_)
        timeStripProfile_spill_zoom.GetXaxis().SetTitle("Time (ns)")
        timeStripProfile_spill_zoom.GetXaxis().SetTitleOffset(1.0)
        timeStripProfile_spill_zoom.GetXaxis().SetLabelOffset(0.0)

        timeStripProfile_spill_zoom.GetYaxis().SetTitle("Strip number")   
        timeStripProfile_spill_zoom.GetYaxis().SetTitleOffset(1.3)
        timeStripProfile_spill_zoom.GetYaxis().SetLabelOffset(0.005)
        
        timeStripProfile_spill_zoom.Draw("COLZ")
        
        self.__drawAux(self.c2)
        self.c2.RedrawAxis()
        self.c2.Modify()    
        if self.verbose > 0:
            self.c2.SaveAs("%stimeStripProfile2D_spill_zoomed.png" % self.savePath) 
            self.c2.SaveAs("%stimeStripProfile2D_spill_zoomed.pdf" % self.savePath)             
            

    def timeProfileChannels(self, peakMean = -1, peakWidth = -1, plotSpill = True, plotNoSpill = True, xMin=-1000, xMax=1000):

        self.noiseGammaTimeWindowBegin = self.timeWindowReject # start at rejection time
        self.noiseGammaTimeWindowEnd = self.noiseRateTriggerWindow
        self.noiseGammaTimeWindow = self.noiseGammaTimeWindowEnd - self.noiseGammaTimeWindowBegin
            
        self.muonTimeWindowBegin = self.timeWindowReject # start at rejection time
        self.muonTimeWindowEnd = self.muonTriggerWindow
        self.muonTimeWindow = self.muonTimeWindowEnd - self.muonTimeWindowBegin
       

        nBins = (xMax-xMin)*10
        timeProfiles = {}
        for ch in self.TDC_channels:
            strp = self.TDC_strips[self.TDC_channels.index(ch)]
            timeProfiles[strp] = ROOT.TH1D("timeProfile%d"%strp, "Time profile spill strip %d"%strp, nBins, xMin, xMax)
            

        for evNum in range(0, self.t.GetEntries()):
        
            self.t.GetEntry(evNum)
            if not self.isBeamTrigger(): continue
            if not self.validateEvent(): continue
               
            firedStrips, timeStamps = self.__groupAndOrder()
            for i,ch in enumerate(firedStrips): timeProfiles[ch].Fill(timeStamps[i])


        # do fits for all time profiles
        for strp,timeProfile in timeProfiles.items():
        
            xMaximum = timeProfile.GetBinCenter(timeProfile.GetMaximumBin())
            delta = 50
            xMin_ = xMaximum - delta
            xMax_ = xMaximum + delta
            
            # fit the peak with a Gaussian
            peakFit = ROOT.TF1("peakFit%d"%strp, "gaus", xMin, xMax)
            peakFit.SetParameters(timeProfile.GetMaximum(), xMaximum, timeProfile.GetRMS())
            timeProfile.Fit("peakFit%d"%strp, "RW", "", xMin_, xMax_)

            # get fit parameters
            offset_ = peakFit.GetParameter(0)
            self.muonWindowMean = peakFit.GetParameter(1)
            self.muonWindowSigma = peakFit.GetParameter(2)
                

            self.muonTimeWindowBegin = self.muonWindowMean - self.muonWindowWidth*self.muonWindowSigma
            self.muonTimeWindowEnd = self.muonWindowMean + self.muonWindowWidth*self.muonWindowSigma
            self.muonTimeWindow = self.muonTimeWindowEnd - self.muonTimeWindowBegin
            

            
            
            # draw raw profile and fit
            self.c1.cd()
            self.c1.Clear()     

            timeProfile.Draw("HIST")
            timeProfile.GetYaxis().SetRangeUser(0, 1.3*timeProfile.GetMaximum())
            timeProfile.SetLineColor(ROOT.kBlack)
            



            timeProfile.GetXaxis().SetTitle("#Delta(hit-trg) (ns)")
            timeProfile.GetXaxis().SetTitleOffset(1.2)
            timeProfile.GetXaxis().SetLabelOffset(0.005)

            timeProfile.GetYaxis().SetTitle("Hits / ns")   
            timeProfile.GetYaxis().SetTitleOffset(1.8)
            timeProfile.GetYaxis().SetLabelOffset(0.005)
            
            
            muonTimeWindowArea = ROOT.TGraph(4)
            muonTimeWindowArea.SetPoint(0, self.muonTimeWindowBegin, 0)
            muonTimeWindowArea.SetPoint(1, self.muonTimeWindowEnd, 0)
            muonTimeWindowArea.SetPoint(2, self.muonTimeWindowEnd, 0.3*timeProfile.GetMaximum())
            muonTimeWindowArea.SetPoint(3, self.muonTimeWindowBegin, 0.3*timeProfile.GetMaximum())
            muonTimeWindowArea.SetFillStyle(3354)
            muonTimeWindowArea.SetFillColor(ROOT.kRed)
            muonTimeWindowArea.SetLineColor(ROOT.kRed)
            muonTimeWindowArea.SetFillColorAlpha(ROOT.kRed, 0.5)
            muonTimeWindowArea.Draw("F SAME")        
            
            
            fitParams = ROOT.TLatex()
            fitParams.SetTextFont(42)
            fitParams.SetTextSize(0.03)
            fitParams.SetNDC()
            fitParams.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
            fitParams.DrawLatex(0.16, 0.85, "Hits inside muon spill")
            fitParams.DrawLatex(0.16, 0.80, "#color[2]{Peak mean: %.2f ns}" % self.muonWindowMean)
            fitParams.DrawLatex(0.16, 0.75, "#color[2]{Peak width (#sigma): %.2f ns}" % self.muonWindowSigma)
            fitParams.DrawLatex(0.16, 0.70, "#color[2]{Muon window (2#times%d#sigma): %.2f ns}" % (self.muonWindowWidth, 6.0*self.muonWindowSigma))
            
    
            peakFit.SetLineColor(ROOT.kRed)
            #peakFitDraw.GetXaxis().SetRangeUser(self.muonTimeWindowBegin, self.muonTimeWindowEnd)
            peakFit.SetLineWidth(2)
            peakFit.Draw("L SAME")
            
            fitParams = ROOT.TLatex()
            fitParams.SetTextFont(42)
            fitParams.SetTextSize(0.03)
            fitParams.SetNDC()
            fitParams.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)
            fitParams.DrawLatex(0.16, 0.85, "Hits inside muon spill")
 
            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()
            self.c1.SaveAs("%stimeProfile_strip%d.png" % (self.savePath, strp))
            self.c1.SaveAs("%stimeProfile_strip%d.pdf" % (self.savePath, strp))
                
            
            
        
   




    def timeProfile(self, peakMean = -1, peakWidth = -1, plotSpill = True, plotNoSpill = True):

        self.noiseGammaTimeWindowBegin = self.timeWindowReject # start at rejection time
        self.noiseGammaTimeWindowEnd = self.noiseRateTriggerWindow
        self.noiseGammaTimeWindow = self.noiseGammaTimeWindowEnd - self.noiseGammaTimeWindowBegin
            
        self.muonTimeWindowBegin = self.timeWindowReject # start at rejection time
        self.muonTimeWindowEnd = self.muonTriggerWindow
        self.muonTimeWindow = self.muonTimeWindowEnd - self.muonTimeWindowBegin
       
            
        nBins = self.muonTriggerWindow # 1 ns resolution, scale in us
        timeProfile_spill = ROOT.TH1D("timeProfile_spill", "Time profile spill", nBins, 0, int(self.muonTimeWindowEnd)/1000)
            
        nBins = 5*self.muonTriggerWindow # 500 ps resolution, scale in ns
        timeProfile_spill_zoom = ROOT.TH1D("timeProfile_spill_zoom", "Time profile spill (zoomed)", nBins, 0, int(self.muonTimeWindowEnd))
        
        # us resolution
        nBins = self.noiseRateTriggerWindow # 1 ns resolution, scale in us
        timeProfile_nospill = ROOT.TH1D("timeProfile_nospill", "Time profile no spill", nBins, 0, int(self.noiseGammaTimeWindowEnd)/1000)
            
        

        for evNum in range(0, self.t.GetEntries()):
        
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
                
            if self.isBeamTrigger(): 
             
                firedStrips, timeStamps = self.__groupAndOrder()
                for i,ch in enumerate(firedStrips): timeProfile_spill.Fill(timeStamps[i]/1000)
                for i,ch in enumerate(firedStrips): timeProfile_spill_zoom.Fill(timeStamps[i])

            else:
                
                firedStrips, timeStamps = self.__groupAndOrder()
                for i,ch in enumerate(firedStrips): timeProfile_nospill.Fill(timeStamps[i]/1000)
                
        
        if peakWidth == -1 and peakMean == -1:
            
            xMaximum = timeProfile_spill_zoom.GetBinCenter(timeProfile_spill_zoom.GetMaximumBin())
            delta = 50
            xMin_ = xMaximum - delta
            xMax_ = xMaximum + delta
            
            # fit the peak with a Gaussian
            peakFit = ROOT.TF1("peakFit", "gaus", self.muonTimeWindowBegin, self.muonTimeWindowEnd)
            peakFit.SetParameters(timeProfile_spill_zoom.GetMaximum(), xMaximum, timeProfile_spill_zoom.GetRMS())
            timeProfile_spill_zoom.Fit("peakFit", "RW", "", xMin_, xMax_)

            # get fit parameters
            offset_ = peakFit.GetParameter(0)
            self.muonWindowMean = peakFit.GetParameter(1)
            self.muonWindowSigma = peakFit.GetParameter(2)
                
        else:
            
            self.muonWindowMean = peakMean
            self.muonWindowSigma = peakWidth
                

        # update the muon time windows
        self.muonTimeWindowBegin = self.muonWindowMean - self.muonWindowWidth*self.muonWindowSigma
        self.muonTimeWindowEnd = self.muonWindowMean + self.muonWindowWidth*self.muonWindowSigma
        self.muonTimeWindow = self.muonTimeWindowEnd - self.muonTimeWindowBegin
            

        if plotSpill:
        
            delta = 50
            xMin_ = self.muonTimeWindowBegin - delta
            xMax_ = self.muonTimeWindowEnd + delta
            
            
            # draw raw profile and fit
            self.c1.cd()
            self.c1.Clear()     

            timeProfile_spill.Draw("HIST")
            timeProfile_spill.GetYaxis().SetRangeUser(0, 1.3*timeProfile_spill.GetMaximum())
            timeProfile_spill.SetLineColor(ROOT.kBlack)
            

            # set x-axis ranges, make dynamically if PMT correction is enabled
            xMin__, xMax__ = 0, self.muonTriggerWindow 
            

            timeProfile_spill.GetXaxis().SetTitle("Time (#mus)")
            timeProfile_spill.GetXaxis().SetTitleOffset(1.2)
            timeProfile_spill.GetXaxis().SetLabelOffset(0.005)

            timeProfile_spill.GetYaxis().SetTitle("Hits / ns")   
            timeProfile_spill.GetYaxis().SetTitleOffset(1.8)
            timeProfile_spill.GetYaxis().SetLabelOffset(0.005)
            
            fitParams = ROOT.TLatex()
            fitParams.SetTextFont(42)
            fitParams.SetTextSize(0.03)
            fitParams.SetNDC()
            fitParams.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)
            fitParams.DrawLatex(0.16, 0.85, "Hits inside muon spill")
 
            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()
            if self.verbose > 0:
                self.c1.SaveAs("%stimeProfile_spill.png" % self.savePath) 
                self.c1.SaveAs("%stimeProfile_spill.pdf" % self.savePath) 
                
            
            # draw zoomed profile
            self.c1.cd()
            self.c1.Clear()     

            leg = ROOT.TLegend(.65, 0.80, .95, .93)
            leg.SetBorderSize(0)
            leg.SetTextSize(0.03)
            leg.SetFillStyle(0)
            
            timeProfile_spill_zoom.GetXaxis().SetRangeUser(xMin_, xMax_)
            timeProfile_spill_zoom.Draw("HIST")
            timeProfile_spill_zoom.GetYaxis().SetRangeUser(0, 1.3*timeProfile_spill_zoom.GetMaximum())
            timeProfile_spill_zoom.SetLineColor(ROOT.kBlack)

            

            muonTimeWindowArea = ROOT.TGraph(4)
            muonTimeWindowArea.SetPoint(0, self.muonTimeWindowBegin, 0)
            muonTimeWindowArea.SetPoint(1, self.muonTimeWindowEnd, 0)
            muonTimeWindowArea.SetPoint(2, self.muonTimeWindowEnd, 0.3*timeProfile_spill_zoom.GetMaximum())
            muonTimeWindowArea.SetPoint(3, self.muonTimeWindowBegin, 0.3*timeProfile_spill_zoom.GetMaximum())
            muonTimeWindowArea.SetFillStyle(3354)
            muonTimeWindowArea.SetFillColor(ROOT.kRed)
            muonTimeWindowArea.SetLineColor(ROOT.kRed)
            muonTimeWindowArea.SetFillColorAlpha(ROOT.kRed, 0.5)
            muonTimeWindowArea.Draw("F SAME")        
            
            timeProfile_spill_zoom.GetXaxis().SetTitle("Time (ns)")
            timeProfile_spill_zoom.GetXaxis().SetTitleOffset(1.2)
            timeProfile_spill_zoom.GetXaxis().SetLabelOffset(0.005)

            timeProfile_spill_zoom.GetYaxis().SetTitle("Hits / 500 ps")   
            timeProfile_spill_zoom.GetYaxis().SetTitleOffset(1.8)
            timeProfile_spill_zoom.GetYaxis().SetLabelOffset(0.005)
            
            fitParams = ROOT.TLatex()
            fitParams.SetTextFont(42)
            fitParams.SetTextSize(0.03)
            fitParams.SetNDC()
            fitParams.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
            fitParams.DrawLatex(0.16, 0.85, "Hits inside muon spill")
            fitParams.DrawLatex(0.16, 0.80, "#color[2]{Peak mean: %.2f ns}" % self.muonWindowMean)
            fitParams.DrawLatex(0.16, 0.75, "#color[2]{Peak width (#sigma): %.2f ns}" % self.muonWindowSigma)
            fitParams.DrawLatex(0.16, 0.70, "#color[2]{Muon window (2#times%d#sigma): %.2f ns}" % (self.muonWindowWidth, 6.0*self.muonWindowSigma))
            
            if peakWidth == -1 and peakMean == -1: # draw Gaussian
            
                peakFitDraw = peakFit.Clone("tmp2")
                peakFitDraw.SetLineColor(ROOT.kRed)
                #peakFitDraw.GetXaxis().SetRangeUser(self.muonTimeWindowBegin, self.muonTimeWindowEnd)
                peakFitDraw.SetLineWidth(2)
                peakFitDraw.Draw("L SAME")
            
            leg.AddEntry(timeProfile_spill_zoom, "Raw data", "L")
            leg.AddEntry(muonTimeWindowArea, "Muon window", "F")
            leg.Draw()
            
            
            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()
            if self.verbose > 0:
                self.c1.SaveAs("%stimeProfile_spill_zoomed.png" % self.savePath) 
                self.c1.SaveAs("%stimeProfile_spill_zoomed.pdf" % self.savePath)                 
                

        if plotNoSpill:
        
            # draw raw profile
            self.c1.cd()
            self.c1.Clear()     

            
            timeProfile_nospill.Draw("HIST")
            timeProfile_nospill.GetYaxis().SetRangeUser(0, 1.3*timeProfile_nospill.GetMaximum())
            timeProfile_nospill.SetLineColor(ROOT.kBlack)

            timeProfile_nospill.GetXaxis().SetTitle("Time (#mus)")
            timeProfile_nospill.GetXaxis().SetTitleOffset(1.2)
            timeProfile_nospill.GetXaxis().SetLabelOffset(0.005)

            timeProfile_nospill.GetYaxis().SetTitle("Hits / ns")   
            timeProfile_nospill.GetYaxis().SetTitleOffset(1.8)
            timeProfile_nospill.GetYaxis().SetLabelOffset(0.005)
            
            fitParams = ROOT.TLatex()
            fitParams.SetTextFont(42)
            fitParams.SetTextSize(0.03)
            fitParams.SetNDC()
            fitParams.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
            fitParams.DrawLatex(0.16, 0.85, "Hits outside muon spill")


            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()
            if self.verbose > 0:
                self.c1.SaveAs("%stimeProfile_nospill.png" % self.savePath) 
                self.c1.SaveAs("%stimeProfile_nospill.pdf" % self.savePath)             
                
                
        return self.muonWindowMean, self.muonWindowSigma
   
    def stripProfile(self, plotSpill = True, plotNoSpill = True):
    
        nValidatedEvents_muon, nValidatedEvents_rate = 0, 0
        
        stripProfileAll_nospill = ROOT.TH1D("stripProfileAll_nospill", "Strip profile (all)", self.nStrips, 1, self.nStrips+1)
        stripProfileAll_spill = ROOT.TH1D("stripProfileAll_spill", "Strip profile (all)", self.nStrips, 1, self.nStrips+1)
        stripProfileMuon = ROOT.TH1D("stripProfileMuon", "Strip profile (muon)", self.nStrips, 1, self.nStrips+1)
        

        for i in range(1, self.nStrips+1):
        
            stripProfileAll_nospill.GetXaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))
            stripProfileAll_spill.GetXaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))
            stripProfileMuon.GetXaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))
            
        
        # loop over all events    
        for evNum in range(0, self.t.GetEntries()):
            
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            if self.isStreamer(evNum): continue
            if self.isBeamTrigger():
            
                nValidatedEvents_muon += 1
            
                # all hits
                firedStrips, timeStamps = self.__groupAndOrder()
                for ch in firedStrips: stripProfileAll_spill.Fill(self.TDC_strips[ch])   
                    
                # probe muon time window
                if self.scanType == "efficiency":
                    firedStrips, timeStamps = self.__groupAndOrder(self.muonTimeWindowBegin, self.muonTimeWindowEnd)
                    for ch in firedStrips: stripProfileMuon.Fill(self.TDC_strips[ch])

            else:
 
                nValidatedEvents_rate += 1
                # probe gamma time window
                firedStrips, timeStamps = self.__groupAndOrder(self.timeWindowReject, self.noiseRateTriggerWindow)
                for ch in firedStrips: stripProfileAll_nospill.Fill(self.TDC_strips[ch])    
 
 
 
        # muon hit profile
        if plotSpill:
        
            ## all hit profile
            self.c1.cd()
            self.c1.Clear()

            stripProfileAll_spill.GetYaxis().SetNoExponent()
            stripProfileAll_spill.SetFillStyle(3354)
            stripProfileAll_spill.SetFillColor(ROOT.kBlue)
            stripProfileAll_spill.SetFillColorAlpha(ROOT.kBlue, 0.35)
            stripProfileAll_spill.SetLineColor(ROOT.kBlue)
            stripProfileAll_spill.SetLineWidth(2)
            stripProfileAll_spill.Draw("HIST")
            
            stripProfileAll_spill.GetYaxis().SetRangeUser(0, 1.3*stripProfileAll_spill.GetMaximum())
            stripProfileAll_spill.GetXaxis().SetTitle("Strip number")
            stripProfileAll_spill.GetXaxis().SetTitleOffset(1.2)
            stripProfileAll_spill.GetXaxis().SetLabelOffset(0.005)
            stripProfileAll_spill.GetXaxis().SetLabelSize(0.04)

            stripProfileAll_spill.GetYaxis().SetTitle("Number of hits")   
            stripProfileAll_spill.GetYaxis().SetTitleOffset(1.8)
            stripProfileAll_spill.GetYaxis().SetLabelOffset(0.005)    
            
            tLatex = ROOT.TLatex()
            tLatex.SetTextFont(42)
            tLatex.SetTextSize(0.03)
            tLatex.SetNDC()
            tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
            tLatex.DrawLatex(0.16, 0.85, "Hit profile (all hits inside muon spill)")
            tLatex.DrawLatex(0.16, 0.80, "Eff. raw %.2f %%" % (100.*self.outDict['efficiencyRaw']))
           
            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()        
            self.c1.SaveAs("%sallHitProfile_spill.png" % self.savePath) 
            self.c1.SaveAs("%sallHitProfile_spill.pdf" % self.savePath)   
        
        
        
        
            self.c1.cd()
            self.c1.Clear()

            stripProfileMuon.GetYaxis().SetNoExponent()
            stripProfileMuon.SetFillStyle(3354)
            stripProfileMuon.SetFillColor(ROOT.kBlue)
            stripProfileMuon.SetFillColorAlpha(ROOT.kBlue, 0.35)
            stripProfileMuon.SetLineColor(ROOT.kBlue)
            stripProfileMuon.SetLineWidth(2)
            stripProfileMuon.Draw("HIST")
            
            stripProfileMuon.GetYaxis().SetRangeUser(0, 1.3*stripProfileMuon.GetMaximum())
            stripProfileMuon.GetXaxis().SetTitle("Strip number")
            stripProfileMuon.GetXaxis().SetTitleOffset(1.2)
            stripProfileMuon.GetXaxis().SetLabelOffset(0.005)
            stripProfileMuon.GetXaxis().SetLabelSize(0.04)

            stripProfileMuon.GetYaxis().SetTitle("Number of hits")   
            stripProfileMuon.GetYaxis().SetTitleOffset(1.8)
            stripProfileMuon.GetYaxis().SetLabelOffset(0.005)    
            
            tLatex = ROOT.TLatex()
            tLatex.SetTextFont(42)
            tLatex.SetTextSize(0.03)
            tLatex.SetNDC()
            tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
            tLatex.DrawLatex(0.16, 0.85, "Muon hit profile (hits inside muon window)")
            tLatex.DrawLatex(0.16, 0.8, "Eff. muon %.2f %%" % (100.*self.outDict['efficiencyMuon']))
            

            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()        
            self.c1.SaveAs("%smuonHitProfile.png" % self.savePath) 
            self.c1.SaveAs("%smuonHitProfile.pdf" % self.savePath)           
        
        
            # beam fit
            self.c1.cd()
            self.c1.Clear()

            stripProfileMuon.GetYaxis().SetNoExponent()
            stripProfileMuon.SetFillStyle(3354)
            stripProfileMuon.SetFillColor(ROOT.kBlue)
            stripProfileMuon.SetFillColorAlpha(ROOT.kBlue, 0.35)
            stripProfileMuon.SetLineColor(ROOT.kBlue)
            stripProfileMuon.SetLineWidth(2)
            stripProfileMuon.Draw("HIST")
            
            stripProfileMuon.GetYaxis().SetRangeUser(0, 1.5*stripProfileMuon.GetMaximum())
            stripProfileMuon.GetXaxis().SetTitle("Strip number")
            stripProfileMuon.GetXaxis().SetTitleOffset(1.2)
            stripProfileMuon.GetXaxis().SetLabelOffset(0.005)
            stripProfileMuon.GetXaxis().SetLabelSize(0.04)

            stripProfileMuon.GetYaxis().SetTitle("Number of hits")   
            stripProfileMuon.GetYaxis().SetTitleOffset(1.8)
            stripProfileMuon.GetYaxis().SetLabelOffset(0.005)    
            
            xMaximum = stripProfileMuon.GetBinCenter(stripProfileMuon.GetMaximumBin())
            xMin_ = stripProfileMuon.GetBinLowEdge(0)
            xMax_ = stripProfileMuon.GetBinLowEdge(stripProfileMuon.GetNbinsX())+1
            
           
            
            # fit the peak with a Gaussian
            beamFit_ = ROOT.TF1("beamFit_", "gaus", xMin_, xMax_)
            beamFit_.SetParameters(stripProfileMuon.Integral(), xMaximum, stripProfileMuon.GetRMS())
            
            # Poissonian
            #beamFit_ = ROOT.TF1("beamFit_", "[0]*TMath::Power(([1]/[2]),(x/[2]))*(TMath::Exp(-([1]/[2])))/TMath::Gamma((x/[2])+1.)", xMin_, xMax_)
            #beamFit_.SetParameters(stripProfileMuon.Integral(), xMaximum, 1)
            
            # CrystalBall
            #beamFit_ = ROOT.TF1("beamFit_", "crystalball", xMin_, xMax_)
            #beamFit_.SetParameters(1, xMaximum, 0.3, 2, 1.5);
            stripProfileMuon.Fit("beamFit_", "WR", "", xMin_, xMax_) # W: ignore empty bins

            # get fit parameters
            offset_ = beamFit_.GetParameter(0)
            beamMean = beamFit_.GetParameter(1)
            beamSigma = beamFit_.GetParameter(2)
            
            self.outDict['beamMean'] = beamMean
            self.outDict['beamSigma'] = beamSigma 
            
            
            beamFit_.SetLineColor(ROOT.kRed)
            beamFit_.GetXaxis().SetRangeUser(xMin_, xMax_)
            beamFit_.SetLineWidth(2)
            beamFit_.Draw("L SAME")
            
            tLatex = ROOT.TLatex()
            tLatex.SetTextFont(42)
            tLatex.SetTextSize(0.03)
            tLatex.SetNDC()
            tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
            tLatex.DrawLatex(0.16, 0.85, "Muon hit profile (hits inside muon window)")
            tLatex.DrawLatex(0.16, 0.8, "Eff. muon %.2f %%" % (100.*self.outDict['efficiencyMuon']))
            tLatex.DrawLatex(0.16, 0.75, "Beam mean pos. %.2f" % (beamMean))
            tLatex.DrawLatex(0.16, 0.70, "Beam width %.2f" % (beamSigma))
            

            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()        
            self.c1.SaveAs("%smuonHitProfile_beamFit.png" % self.savePath) 
            self.c1.SaveAs("%smuonHitProfile_beamFit.pdf" % self.savePath)           
                    
         
        if plotNoSpill:
            
            # plot hits in gamma profile
            self.c1.cd()
            self.c1.Clear()

            stripProfileAll_nospill.SetFillStyle(3354)
            stripProfileAll_nospill.SetFillColor(ROOT.kBlue)
            stripProfileAll_nospill.SetFillColorAlpha(ROOT.kBlue, 0.35)
            stripProfileAll_nospill.SetLineColor(ROOT.kBlue)
            stripProfileAll_nospill.SetLineWidth(2)
            stripProfileAll_nospill.Draw("HIST")
            
            stripProfileAll_nospill.GetYaxis().SetRangeUser(0, 1.3*stripProfileAll_nospill.GetMaximum())
            stripProfileAll_nospill.GetXaxis().SetTitle("Strip number")
            stripProfileAll_nospill.GetXaxis().SetTitleOffset(1.2)
            stripProfileAll_nospill.GetXaxis().SetLabelOffset(0.005)
            stripProfileAll_nospill.GetXaxis().SetLabelSize(0.04)

            stripProfileAll_nospill.GetYaxis().SetTitle("Number of hits")   
            stripProfileAll_nospill.GetYaxis().SetTitleOffset(1.8)
            stripProfileAll_nospill.GetYaxis().SetLabelOffset(0.005)    
            
            tLatex = ROOT.TLatex()
            tLatex.SetTextFont(42)
            tLatex.SetTextSize(0.03)
            tLatex.SetNDC()
            tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)
            tLatex.DrawLatex(0.16, 0.85, "Gamma hit profile (hits outside muon spill)")
            tLatex.DrawLatex(0.16, 0.80, "Eff. fake/gamma %.2f %%" % (100.*self.outDict['efficiencyFake']))
            
            

            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()        
            self.c1.SaveAs("%sallHitProfile_nospill.png" % self.savePath) 
            self.c1.SaveAs("%sallHitProfile_nospill.pdf" % self.savePath)     
            
            
            
            # plot gamma rate profile
            norm = self.stripArea * self.noiseGammaTimeWindow * nValidatedEvents_rate * 1e-9
            if norm != 0: stripProfileAll_nospill.Scale(1./norm)
            
            #print(self.stripArea, self.noiseGammaTimeWindow, nValidatedEvents_rate)

            tmp_mean, tmp_err = [], []
            for i in range(1, stripProfileAll_nospill.GetNbinsX()+1):
                
                stripNo = self.TDC_strips[i-1]
                if(stripNo) in self.TDC_strips_mask: continue
                tmp_mean.append(stripProfileAll_nospill.GetBinContent(i))
                if stripProfileAll_nospill.GetBinContent(i) >= 0: tmp_err.append(math.sqrt(stripProfileAll_nospill.GetBinContent(i)))
                else: tmp_err.append(0)
            
            self.noiseGammaRate = np.mean(tmp_mean)
            self.noiseGammaRate_err = np.mean(tmp_err)
            
            self.outDict['noiseGammaRate'] = self.noiseGammaRate
            self.outDict['noiseGammaRate_err'] = self.noiseGammaRate_err
            
            #sys.exit()
            self.c1.cd()
            self.c1.Clear()

            stripProfileAll_nospill.SetFillStyle(3354)
            stripProfileAll_nospill.SetFillColor(ROOT.kBlue)
            stripProfileAll_nospill.SetFillColorAlpha(ROOT.kBlue, 0.35)
            stripProfileAll_nospill.SetLineColor(ROOT.kBlue)
            stripProfileAll_nospill.SetLineWidth(2)
            stripProfileAll_nospill.Draw("HIST")
            
            stripProfileAll_nospill.GetYaxis().SetRangeUser(0, 1.3*stripProfileAll_nospill.GetMaximum())
            stripProfileAll_nospill.GetXaxis().SetTitle("Strip number")
            stripProfileAll_nospill.GetXaxis().SetTitleOffset(1.2)
            stripProfileAll_nospill.GetXaxis().SetLabelOffset(0.005)
            stripProfileAll_nospill.GetXaxis().SetLabelSize(0.04)

            stripProfileAll_nospill.GetYaxis().SetTitle("Gamma rate (Hz/cm^{2})")   
            stripProfileAll_nospill.GetYaxis().SetTitleOffset(1.8)
            stripProfileAll_nospill.GetYaxis().SetLabelOffset(0.005)    
            
            tLatex = ROOT.TLatex()
            tLatex.SetTextFont(42)
            tLatex.SetTextSize(0.03)
            tLatex.SetNDC()
            tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)
            tLatex.DrawLatex(0.16, 0.85, "Gamma rate hit profile (hits outside muon spill)")
            tLatex.DrawLatex(0.16, 0.80, "Mean gamma rate: %.2f #pm %.2f Hz/cm^{2}" % (self.noiseGammaRate, self.noiseGammaRate_err))

            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()        
            self.c1.SaveAs("%srateProfile.png" % self.savePath) 
            self.c1.SaveAs("%srateProfile.pdf" % self.savePath)     
        
            
        

    
    def clusterization(self, clusterType):
    
        # select the time window based on the mode
        if clusterType == "muon":
            clusterTimeWindow = self.muonClusterTimeWindow
            clusterTimeWindowUp = self.muonClusterTimeWindowUp
            clusterTimeWindowDown = self.muonClusterTimeWindowDw
        elif clusterType == "gamma":
            clusterTimeWindow = self.gammaClusterTimeWindow
            clusterTimeWindowUp = self.gammaClusterTimeWindowUp
            clusterTimeWindowDown = self.gammaClusterTimeWindowDw
        else: sys.exit("Cluster type must be gamma or muon")
       
        cls, cmp = self._clusterization(clusterTimeWindow, clusterType)
        if clusterType == "muon":
            self.outDict['muonCLS'], self.outDict['muonCMP'] = cls, cmp
        elif clusterType == "gamma":
            self.outDict['gammaCLS'], self.outDict['gammaCMP'] = cls, cmp
        
        # calculate clusterization error
        clsErr, cmpErr = -1, -1
        if clusterTimeWindowUp != -1 and clusterTimeWindowDown != -1:
                    
            self.setVerbose(0) # turn of verbosity
            clsUp, cmpUp = self._clusterization(clusterTimeWindowUp, clusterType, pert=True) # up variation
            clsDown, cmpDown = self._clusterization(clusterTimeWindowDown, clusterType, pert=True) # down variation
            
            #clsErr = (abs(clsUp-cls) + abs(clsDown-cls)) / 2.0
            #cmpErr = (abs(cmpUp-cls) + abs(cmpDown-cmp)) / 2.0
            
            # define the error as the MAX between the variations
            clsErr = max([abs(clsUp-cls), abs(clsDown-cls)])
            cmpErr = max([abs(cmpUp-cmp), abs(cmpDown-cmp)])
            
            if clusterType == "muon":
                self.outDict['muonCLS_err'], self.outDict['muonCMP_err'] = clsErr, cmpErr
            elif clusterType == "gamma":
                self.outDict['gammaCLS_err'], self.outDict['gammaCMP_err'] = clsErr, cmpErr
            
            self.setVerbose(1)
        
        return cls, cmp
        
            

    
    def _clusterization(self, clusterTimeWindow, clusterType, pert=False):

        h_clustersize = ROOT.TH1D("clustersize", "Cluster size", 1000, 0, 1000)
        h_clustersize_cmp = ROOT.TH1D("clustersize_cmp1", "Cluster size (CMP==1)", 1000, 0, 1000)
        h_clustermultiplicity = ROOT.TH1D("clustermultiplicity", "Cluster multiplicity", 1000, 0, 1000)
    
        # select the time window based on the mode
        if clusterType == "muon":
            tMin, tMax = self.muonTimeWindowBegin, self.muonTimeWindowEnd
        elif clusterType == "gamma":
            tMin, tMax = self.noiseGammaTimeWindowBegin, self.noiseGammaTimeWindowEnd
            tMin, tMax = self.timeWindowReject, self.noiseRateTriggerWindow
        
        maxCLS = -99
        maxCMP = -99
        
        for evNum in range(0, self.t.GetEntries()):
            
            self.t.GetEntry(evNum)
            #if not pert and (evNum in self.CMP and evNum in self.CLS): continue # if cluster already done (and 
            if not self.validateEvent(): continue
            if not self.isBeamTrigger() and clusterType == "muon": continue
            if self.isBeamTrigger() and clusterType == "gamma": continue
           
            firedStrips, timeStamps = self.__groupAndOrder(tMin, tMax)
            
            # make graph from all hits
            G = nx.Graph()
                
            # add node for each hit
            for i,ch in enumerate(firedStrips): G.add_node(i)
                
            # add edges between nodes
            # and edge connect the nodes based on space and time constraints
            for i, ch1 in enumerate(firedStrips):
                for j, ch2 in enumerate(firedStrips):
                        
                    if j <= i: continue # avoid double counting
                    DT = (timeStamps[i]-timeStamps[j])
                    DS = (firedStrips[i] - firedStrips[j])
                        
                    if abs(DS) == 1 and abs(DT) < clusterTimeWindow: # if pair conditions satisfied
                        G.add_edge(i,j)
                            
            #print "Graph nodes:", G.number_of_nodes(), "Edges:", G.number_of_edges()
            #print "CMP", len(list(nx.connected_components(G)))
            CMP = len(list(nx.connected_components(G)))
            CLS = []
            for k in nx.connected_components(G): CLS.append(len(k))
            
            if not pert: # save clusterization to dict
                self.CMP[evNum] = CMP
                self.CLS[evNum] = CLS

            if self.isStreamer(evNum): continue
            if CMP > maxCMP: maxCMP = CMP
            if CMP != 0: h_clustermultiplicity.Fill(CMP) # do not fill the zero bin
            
            for x in CLS:
                if x > maxCLS: maxCLS = x
                h_clustersize.Fill(x)
            if CMP == 1: h_clustersize_cmp.Fill(CLS[0]) # histogram for CMP == 1
            


        # store the mean CLS BEFORE change of axis range!
        cls, cmp = h_clustersize.GetMean(), h_clustermultiplicity.GetMean()   
        cls_cmp1 = h_clustersize_cmp.GetMean()

        # draw the CLS and CMP distributions
        self.c1.cd()
        self.c1.Clear()

        leg = ROOT.TLegend(.15, 0.75, .4, .93)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.03)
        leg.SetFillStyle(0)
        
        if h_clustermultiplicity.Integral() > 1: h_clustermultiplicity.Scale(1.0/h_clustermultiplicity.Integral())
        
        h_clustermultiplicity.Draw("HIST ")
        h_clustermultiplicity.SetLineColor(ROOT.kBlue)
        h_clustermultiplicity.GetYaxis().SetRangeUser(0, 1.3*h_clustermultiplicity.GetMaximum())
        h_clustermultiplicity.GetXaxis().SetRangeUser(0, 1.1*maxCMP)
        h_clustermultiplicity.SetLineWidth(2)  


        h_clustermultiplicity.GetXaxis().SetTitle("Cluster multiplicity")
        h_clustermultiplicity.GetXaxis().SetTitleOffset(1.2)
        h_clustermultiplicity.GetXaxis().SetLabelOffset(0.005)

        h_clustermultiplicity.GetYaxis().SetTitle("Events (normalized)")   
        h_clustermultiplicity.GetYaxis().SetTitleOffset(1.8)
        h_clustermultiplicity.GetYaxis().SetLabelOffset(0.005)
        
        params = ROOT.TLatex()
        params.SetTextFont(42)
        params.SetTextSize(0.03)
        params.SetNDC()
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
        params.DrawLatex(0.16, 0.85, "Mean %s cluster multiplicity (CMP): %.2f" % (clusterType, cmp))
        

        self.__drawAux(self.c1)
        self.c1.RedrawAxis()
        self.c1.Modify()
        if self.verbose > 0:
            self.c1.SaveAs("%sCMP_%s.png" % (self.savePath, clusterType)) 
            self.c1.SaveAs("%sCMP_%s.pdf" % (self.savePath, clusterType)) 
            
            
        


        # draw the CLS and CMP distributions
        self.c1.cd()
        self.c1.Clear()

        leg = ROOT.TLegend(.15, 0.75, .4, .93)
        leg.SetBorderSize(0)
        leg.SetTextSize(0.03)
        leg.SetFillStyle(0)
        
        if h_clustersize.Integral() > 1: h_clustersize.Scale(1.0/h_clustersize.Integral())
        
        h_clustersize.Draw("HIST ")
        h_clustersize.SetLineColor(ROOT.kBlue)
        h_clustersize.GetYaxis().SetRangeUser(0, 1.3*h_clustersize.GetMaximum())
        h_clustersize.GetXaxis().SetRangeUser(0, 1.1*maxCLS)
        h_clustersize.SetLineWidth(2)  
        
        h_clustersize.Draw("HIST SAME")
        h_clustersize.SetLineWidth(2)  
        h_clustersize.SetLineColor(ROOT.kBlue)

        h_clustersize.GetXaxis().SetTitle("Cluster size")
        h_clustersize.GetXaxis().SetTitleOffset(1.2)
        h_clustersize.GetXaxis().SetLabelOffset(0.005)

        h_clustersize.GetYaxis().SetTitle("Events (normalized)")   
        h_clustersize.GetYaxis().SetTitleOffset(1.8)
        h_clustersize.GetYaxis().SetLabelOffset(0.005)
        
        params = ROOT.TLatex()
        params.SetTextFont(42)
        params.SetTextSize(0.03)
        params.SetNDC()
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
        params.DrawLatex(0.16, 0.85, "Mean %s cluster size (CLS): %.2f" % (clusterType, cls))
        

        self.__drawAux(self.c1)
        self.c1.RedrawAxis()
        self.c1.Modify()
        if self.verbose > 0:
            self.c1.SaveAs("%sCLS_%s.png" % (self.savePath, clusterType)) 
            self.c1.SaveAs("%sCLS_%s.pdf" % (self.savePath, clusterType)) 
 
            
            
                      
        h_clustersize.Delete()
        h_clustermultiplicity.Delete()  
        
        
        
        # draw CMP==1 distribution (only for muons)
        if clusterType == "muon":
            self.c1.cd()
            self.c1.Clear()

            leg = ROOT.TLegend(.15, 0.75, .4, .93)
            leg.SetBorderSize(0)
            leg.SetTextSize(0.03)
            leg.SetFillStyle(0)
            
            if h_clustersize_cmp.Integral() > 1: h_clustersize_cmp.Scale(1.0/h_clustersize_cmp.Integral())
            
            h_clustersize_cmp.Draw("HIST ")
            h_clustersize_cmp.SetLineColor(ROOT.kBlue)
            h_clustersize_cmp.GetYaxis().SetRangeUser(0, 1.3*h_clustersize_cmp.GetMaximum())
            h_clustersize_cmp.GetXaxis().SetRangeUser(0, 1.1*maxCLS)
            h_clustersize_cmp.SetLineWidth(2)  
            
            h_clustersize_cmp.Draw("HIST SAME")
            h_clustersize_cmp.SetLineWidth(2)  
            h_clustersize_cmp.SetLineColor(ROOT.kBlue)

            h_clustersize_cmp.GetXaxis().SetTitle("Cluster size (CMP==1)")
            h_clustersize_cmp.GetXaxis().SetTitleOffset(1.2)
            h_clustersize_cmp.GetXaxis().SetLabelOffset(0.005)

            h_clustersize_cmp.GetYaxis().SetTitle("Events (normalized)")   
            h_clustersize_cmp.GetYaxis().SetTitleOffset(1.8)
            h_clustersize_cmp.GetYaxis().SetLabelOffset(0.005)
            
            params = ROOT.TLatex()
            params.SetTextFont(42)
            params.SetTextSize(0.03)
            params.SetNDC()
            params.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)  
            params.DrawLatex(0.16, 0.85, "Mean muon cluster size (CLS): %.2f" % cls_cmp1)
            params.DrawLatex(0.16, 0.8, "Cluster Multiplicity = 1")
            

            self.__drawAux(self.c1)
            self.c1.RedrawAxis()
            self.c1.Modify()
            if self.verbose > 0:
                self.c1.SaveAs("%sCMP_%s_CMP1.png" % (self.savePath, clusterType)) 
                self.c1.SaveAs("%sCMP_%s_CMP1.pdf" % (self.savePath, clusterType)) 

            
                      
        #h_clustersize_cmp.Delete()
        #h_clustermultiplicity.Delete()  
        
        
        return cls, cmp
  

    def clusterEvents(self, muonClusterTimeWindow = -1):
    
        # clusters, barycenters, barycenters_err
    
        if muonClusterTimeWindow == -1: muonClusterTimeWindow = self.muonClusterTimeWindow
    
        cluster_collection, cluster_time_collection, barycenters_collection, barycenters_err_collection = [], [], [], []
        for evNum in range(0, self.t.GetEntries()):
            
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            if not self.isBeamTrigger(): continue
            clusters, clusters_time, barycenters, barycenters_err = self.clusterEvent(evNum, muonClusterTimeWindow)
            cluster_collection.append(clusters)
            cluster_time_collection.append(clusters_time)
            barycenters_collection.append(barycenters)
            barycenters_err_collection.append(barycenters_err)
            
        return cluster_collection, cluster_time_collection, barycenters_collection, barycenters_err_collection
        
    def clusterEvent(self, evNum, muonClusterTimeWindow = -1):
    
        if muonClusterTimeWindow == -1: muonClusterTimeWindow = self.muonClusterTimeWindow
        tMin, tMax = self.muonTimeWindowBegin, self.muonTimeWindowEnd
    
        if not self.validateEvent(): return [], [], [], []
        if not self.isBeamTrigger(): return [], [], [], []
        if self.isStreamer(evNum): return [], [], [], []
           
        firedStrips, timeStamps = self.__groupAndOrder(tMin, tMax)
        clusters, clusters_time, barycenters, barycenters_err = [], [], [], []
    
        # make graph from all hits
        G = nx.Graph()
            
        # add node for each hit
        for i,ch in enumerate(firedStrips): G.add_node(i)
            
        # add edges between nodes
        # and edge connect the nodes based on space and time constraints
        for i, ch1 in enumerate(firedStrips):
            for j, ch2 in enumerate(firedStrips):
                    
                if j <= i: continue # avoid double counting
                DT = (timeStamps[i]-timeStamps[j]) # time constraint
                DS = (firedStrips[i] - firedStrips[j]) # space constraint
                    
                if abs(DS) == 1 and abs(DT) < muonClusterTimeWindow: # if pair conditions satisfied
                    #print "pair", ch1, ch2
                    G.add_edge(i,j)
                        
        #print "Graph nodes:", G.number_of_nodes(), "Edges:", G.number_of_edges()
        #print "MP", len(list(nx.connected_components(G)))
        MP = len(list(nx.connected_components(G)))
            
            
        if len(firedStrips) == 0: return [], [], [], [] # if empty event, do not count for calculation of CLS
        for k in nx.connected_components(G): # loop over clusters
            CLS = len(k)
            cluster = []
            cluster_time = []
            for j in k: 
            
                cluster.append(firedStrips[j])
                cluster_time.append(timeStamps[j])
                
            clusters.append(cluster)
            clusters_time.append(cluster_time)
            
            barycenter, err = self.clusterBarycenter(cluster)
            barycenters.append(barycenter)
            barycenters_err.append(err)

        return clusters, clusters_time, barycenters, barycenters_err
   

    def getStripPos(self, nStrip):
        
        '''
        Returns x position of strip in given chamber
        '''
    
        stripPitch = self.stripPitch
        stripWidth = stripPitch # *0.95 # assume gap between strips is 5%... not really important
        
        tmp = self.stripPitch*(nStrip-1)
        x0 = (self.xPos + tmp)
        x1 = (self.xPos + tmp + stripWidth)
        return (x0+x1)/2., x0, x1 # return middle, left and right coordinate
        
    def clusterBarycenter(self, cluster, algo="geometric"):
    
        self.cluster_barycenter_algo = algo
    
        if algo == "geometric":
        
            x = []
            for strip in cluster: 
                xc, xl, xr = self.getStripPos(strip)
                x.append(xc)
            barycenter = sum(x)/len(x)
            
            err = (self.stripPitch) / math.sqrt(12) # assume single strip uncertainty
            
            return barycenter, err
            
        
        elif algo == "first_strip":
        
            pass
            
        
        else: sys.exit("Barycenter algorithm %s not found" % algo)
        

    def streamerProbability(self):
    
        nStreamersMuonWindow, nStreamersGammaWindow = 0, 0
        nHitsMuonWindow, nHitsGammaWindow = 0, 0
        for evNum in range(0, self.t.GetEntries()):
            
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            x = self.isStreamer(evNum)
            
            if self.isBeamTrigger():
                nHitsMuonWindow += 1
                if x: nStreamersMuonWindow += 1
                
            else:
                nHitsGammaWindow += 1
                if x: nStreamersGammaWindow += 1

        
        self.outDict['muonStreamerProbability'] = (1.0*nStreamersMuonWindow) / (1.0*nHitsMuonWindow)
        self.outDict['gammaStreamerProbability'] = (1.0*nStreamersGammaWindow) / (1.0*nHitsGammaWindow)
        
    def efficiency(self):

        nHitsRaw = 0
        nHitsMuonWindow = 0
        nHitsGammaWindow = 0
        nTrig = 0
        for evNum in range(0, self.t.GetEntries()):
            
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            if not self.isBeamTrigger(): continue
            if self.isStreamer(evNum): continue
            nTrig +=1
            
            # probe the entire time window
            firedStrips, timeStamps = self.__groupAndOrder()
            if len(firedStrips) > 0: nHitsRaw +=1

            # probe the muon window
            firedStrips, timeStamps = self.__groupAndOrder(self.muonTimeWindowBegin, self.muonTimeWindowEnd)
            if len(firedStrips) > 0: nHitsMuonWindow += 1
            
            # probe the gamma window
            firedStrips, timeStamps = self.__groupAndOrder(self.noiseGammaTimeWindowBegin, self.noiseGammaTimeWindowEnd)
            if len(firedStrips) > 0: nHitsGammaWindow += 1
    
        if nTrig > 0:
            efficiencyRaw = 1.0*nHitsRaw / nTrig
            efficiencyMuon = 1.0*nHitsMuonWindow / nTrig
            efficiencyFake = 1.0*nHitsGammaWindow * (self.muonTimeWindow/self.noiseGammaTimeWindow) / nTrig # re-scale gamma hits w.r.t. same muon trigger window
            efficiencyMuon_corrected = (efficiencyMuon - efficiencyFake) / (1.0 - efficiencyFake)
            if efficiencyMuon_corrected < 0: efficiencyMuon_corrected = 0.
            
            efficiencyRaw_err = math.sqrt(efficiencyRaw*(1.0-efficiencyRaw)/nTrig)
            efficiencyMuon_err = math.sqrt(efficiencyMuon*(1.0-efficiencyMuon)/nTrig)
            efficiencyFake_err = math.sqrt(efficiencyFake*(1.0-efficiencyFake)/nTrig)
            efficiencyMuon_corrected_err = math.sqrt(efficiencyMuon_corrected*(1.0-efficiencyMuon_corrected)/nTrig)
            
            self.outDict['efficiencyRaw'] = efficiencyRaw
            self.outDict['efficiencyMuon'] = efficiencyMuon
            self.outDict['efficiencyFake'] = efficiencyFake
            self.outDict['efficiencyMuon_corrected'] = efficiencyMuon_corrected
            self.outDict['efficiencyRaw_err'] = efficiencyRaw_err
            self.outDict['efficiencyMuon_err'] = efficiencyMuon_err
            self.outDict['efficiencyFake_err'] = efficiencyFake_err
            self.outDict['efficiencyMuon_corrected_err'] = efficiencyMuon_corrected_err

  

    # a la 2D event display, but vertical strips are all occupied (only strips in horizontal direciton for 1D
    # needed for alignment/orientation
    def eventDisplay2D(self, maxEvents, direction="y"):
    
        ROOT.gStyle.SetPalette(ROOT.kDarkRainBow)
        path = self.savePath + "eventDisplay/"
        if os.path.isdir(path): shutil.rmtree(path)
        os.mkdir(path)
    
        nStrips = self.nStrips
        strips = self.TDC_strips
        stripMin = min(self.TDC_strips)
        stripMax = max(self.TDC_strips)
        
        stripProfileMuon = ROOT.TH2D("stripProfileMuon", "Strip profile (muon)", nStrips, stripMin, stripMax+1, nStrips, stripMin, stripMax+1)
        
        
        for i in range(1, nStrips+1):
        
            if direction == "y": stripProfileMuon.GetXaxis().SetBinLabel(i, "")
            else: stripProfileMuon.GetXaxis().SetBinLabel(i, str(strips[i-1]))
            
        for i in range(1, nStrips+1):
        
            if direction == "x": stripProfileMuon.GetYaxis().SetBinLabel(i, "")
            else: stripProfileMuon.GetYaxis().SetBinLabel(i, str(strips[i-1]))
        
        
                
        if direction == "x": stripProfileMuon.GetXaxis().SetTitle("Strips %s" % self.chamberName)
        stripProfileMuon.GetXaxis().SetTitleOffset(1.3)
        stripProfileMuon.GetXaxis().SetLabelOffset(0.005)

        if direction == "y": stripProfileMuon.GetYaxis().SetTitle("Strips %s" % self.chamberName)
        stripProfileMuon.GetYaxis().SetTitleOffset(1.3)
        stripProfileMuon.GetYaxis().SetLabelOffset(0.005)

        # loop over all events    
        evts = 0
        for evNum in range(0, self.t.GetEntries()):
        
            
            
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            if not self.isBeamTrigger(): continue
            
            
            
            # reset the histogram contents
            for i in range(1, nStrips+1):
                for j in range(1, nStrips+1):
                    stripProfileMuon.SetBinContent(i,j,0.001)
            

            firedStrips, timeStamps = self.__groupAndOrder(self.muonTimeWindowBegin, self.muonTimeWindowEnd)
            
            
            if len(firedStrips) < 10: continue
            evts += 1

            if direction == "x":
                for ch_x in firedStrips: 
                    for ch_y in range(1, nStrips+1): 
                        stripProfileMuon.Fill(strips[ch_x], strips[ch_y-1])
            
            if direction == "y":
                for ch_x in range(1, nStrips+1): 
                    for ch_y in firedStrips: 
                        stripProfileMuon.Fill(strips[ch_x-1], strips[ch_y])   
     
            self.c3.cd()
            self.c3.Clear()
            stripProfileMuon.Draw("COLZ")
            
            tLatex = ROOT.TLatex()
            tLatex.SetTextFont(42)
            tLatex.SetTextSize(0.03)
            tLatex.SetNDC()
            #tLatex.DrawLatex(0.02, 0.02, )

            self.__drawAux(self.c3, "EV%d" %evNum)
            self.c3.RedrawAxis()
            self.c3.Modify()        
            self.c3.SaveAs("%seventDisplay/event_%d.png" % (self.savePath, evNum)) 
            
            if evts > maxEvents: break
     
  
 
    def eventDisplay(self, maxEvents):
    
        ROOT.gStyle.SetPalette(ROOT.kDarkRainBow)
        
        # select random numbers
        #random.seed(0) # fix seed of random generator in order to display the same events
        evToPlot = []
        if maxEvents == -1:
        
            for j in range(self.t.GetEntries()+1): evToPlot.append(j)
            
        else:

            for j in range(maxEvents):
                evToPlot.append(random.randint(0, self.t.GetEntries()+1)) 
                
        path = self.savePath + "eventDisplay/"
        if os.path.isdir(path): shutil.rmtree(path)
        os.mkdir(path)


        
        if self.scanType == "rate":
            
            scale = 1000.
            timeStart = self.timeWindowReject
            timeEnd = self.noiseRateTriggerWindow
            
        elif self.scanType == "efficiency":
            
            scale = 1.
            timeStart = self.timeWindowReject
            timeEnd = self.muonTriggerWindow        
         
        width = timeEnd - timeStart
        
        
        
        # make 2D histogram (x-axis time, y-axis strips)
        timeStripProfile = ROOT.TH2D("timeStripProfile", "Time-strip profile", width, int(timeStart/scale), int(timeEnd/scale), self.nStrips, min(self.TDC_strips), max(self.TDC_strips)+1)
              

        if self.scanType == "efficiency": 
        
            scale = 1.
            timeStart = self.muonTimeWindowBegin
            timeEnd = self.muonTimeWindowEnd
            width = 10*int(self.muonTimeWindow+1)
            
        else:
            
            scale = 1000.
            timeStart = self.noiseGammaTimeWindowBegin
            timeEnd = self.noiseGammaTimeWindowEnd
            width = 10*int(self.noiseGammaTimeWindow+1)
            width = self.noiseGammaTimeWindow+1
    
    
        for evNum in evToPlot:
        
           
    
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            if not self.isBeamTrigger(): continue
            
            
            #firedStrips, timeStamps = self.__groupAndOrder(self.t.TDC_channel, self.t.TDC_TimeStamp, timeStart, timeEnd)
            #firedStrips, timeStamps = self.__groupAndOrder(self.t.TDC_channel, self.t.TDC_TimeStamp, -1e5, 1e5)
            firedStrips, timeStamps = self.__groupAndOrder(self.muonTimeWindowBegin, self.muonTimeWindowEnd)
            if self.scanType == "rate" and len(firedStrips) == 0: continue
            if len(firedStrips) == 0: continue
            
            if len(firedStrips) < 20: continue
            
            # store hits in 2D histo (100 ps accuracy for timing)
            eventHist = ROOT.TH2D("eventHist%d" % evNum, "Event %d" % evNum, width, int(timeStart/scale), int(timeEnd/scale), self.nStrips, min(self.TDC_strips), max(self.TDC_strips)+1)
            eventHist_ext = ROOT.TH2D("eventHist%d_ext" % evNum, "Event %d" % evNum, width, int(timeStart/scale), 600, self.nStrips, min(self.TDC_strips), max(self.TDC_strips)+1)
            
            
            for i,ch in enumerate(firedStrips): 
                eventHist.Fill(timeStamps[i]/scale, self.TDC_strips[ch])     
                eventHist_ext.Fill(timeStamps[i]/scale, self.TDC_strips[ch]) 
                
                
                
            ## CALCULATE CLUSTERS
            
            outStr = "" 
            '''
            G = nx.Graph() # make graph from all hits
            for i,ch in enumerate(firedStrips): G.add_node(i) # add node for each hit
            
            # add edges between nodes
            # and edge connect the nodes based on space and time constraints
            for i, ch1 in enumerate(firedStrips):
                for j, ch2 in enumerate(firedStrips):
                    
                    if j <= i: continue # avoid double counting
                    DT = (timeStamps[i]-timeStamps[j])
                    DS = (firedStrips[i] - firedStrips[j])
                    
                    if abs(DS) == 1 and abs(DT) < self.muonClusterTimeWindow: # if pair conditions satisfied
                        #print "pair", ch1, ch2
                        G.add_edge(i,j)
                        
            MP = len(list(nx.connected_components(G)))
            outStr += "MP=%d, CLS=(" % MP
            for k in nx.connected_components(G): 
                CLS = len(k)
                outStr += "%d," % CLS
            
            if MP != 0: outStr = outStr[:-1]
            outStr += "), #Deltat = %d ns" % self.muonClusterTimeWindow
            '''
            
            ROOT.gStyle.SetPalette(56) # see https://root.cern.ch/doc/master/classTColor.html
     
            # draw it
            self.c2.cd()
            self.c2.SetRightMargin(0.05)
            self.c2.Clear()  
            
            for i in range(1, self.nStrips+1): eventHist.GetYaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))

            eventHist.GetXaxis().SetTitle("Time (ns)")
            eventHist.GetXaxis().SetTitleOffset(1.0)
            eventHist.GetXaxis().SetLabelOffset(0.0)

            eventHist.GetYaxis().SetTitle("Strip number")   
            eventHist.GetYaxis().SetTitleOffset(1.3)
            eventHist.GetYaxis().SetLabelOffset(0.005)
            
            
            
            eventHist.Draw("COL")
            
            txt = ROOT.TLatex()
            txt.SetTextFont(42)
            txt.SetTextSize(0.03)
            txt.SetNDC()
            txt.DrawLatex(self.c2.GetLeftMargin(), 0.035, outStr)
            
            self.__drawAux(self.c2, "EV%d" %evNum)
            self.c2.RedrawAxis()
            self.c2.Modify()    
            self.c2.SaveAs("%sevent_%d.png" % (path, evNum))    
            
            
            # draw it
            self.c2.cd()
            self.c2.Clear()  
            
            for i in range(1, self.nStrips+1): eventHist_ext.GetYaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))

            eventHist_ext.GetXaxis().SetTitle("Time (ns)")
            eventHist_ext.GetXaxis().SetTitleOffset(1.0)
            eventHist_ext.GetXaxis().SetLabelOffset(0.0)

            eventHist_ext.GetYaxis().SetTitle("Strip number")   
            eventHist_ext.GetYaxis().SetTitleOffset(1.3)
            eventHist_ext.GetYaxis().SetLabelOffset(0.005)
            
            eventHist_ext.Draw("COL")
            
            txt = ROOT.TLatex()
            txt.SetTextFont(42)
            txt.SetTextSize(0.03)
            txt.SetNDC()
            txt.DrawLatex(self.c2.GetLeftMargin(), 0.035, outStr)
            
            self.__drawAux(self.c2, "EV%d" %evNum)
            self.c2.RedrawAxis()
            self.c2.Modify()    
            self.c2.SaveAs("%sevent_ext_%d.png" % (path, evNum))  

        
    def __drawAux(self, c, aux = ""):
    
        textLeft = ROOT.TLatex()
        textLeft.SetTextFont(42)
        textLeft.SetTextSize(0.04)
        textLeft.SetNDC()
        textLeft.DrawLatex(c.GetLeftMargin(), 0.96, self.textHeader)
        
        textRight = ROOT.TLatex()
        textRight.SetNDC()
        textRight.SetTextFont(42)
        textRight.SetTextSize(0.04)
        textRight.SetTextAlign(31)
        if aux == "": textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, "S%d/HV%d" % (self.scanid, self.HVPoint))
        else: textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, "S%d/HV%d/%s" % (self.scanid, self.HVPoint, aux))



 
        
    def isBeamTrigger(self):
    
        trg = self.t.TriggerTag
        if trg == 1: return True
        return False
    
    def isStreamer(self, evNum):
    
        # cut on cluster size
        if evNum in self.CLS and evNum in self.CMP: CLS, CMP = self.CLS[evNum], self.CMP[evNum]
        else: sys.exit("Perform first clusterizations, cannot find event %d" % evNum)
            
        ret = False
        for x in CLS:
            if x > self.clusterSizeCut: 
                ret = True
                break
            
        return ret
            
    
    def validateEvent(self):
    
        #if not self.TDC_channel_PMT in self.t.TDC_channel: return False
        return True
        
    def getPMTTime(self):
        return 0
        #if not self.doPMTCorrection(): return 0
        #if self.TDC_channel_PMT == -1: return 0
        #if not self.TDC_channel_PMT  in list(self.t.TDC_channel): return 0
        idx = list(self.t.TDC_channel).index(self.TDC_channel_PMT)
        return self.t.TDC_TimeStamp[idx]
        
        
    # Input: raw TDC channel/time vectors,
    # Output: converted TDC channels to strip numbers, within the optinally given time window
    
    def groupAndOrder(self, windowStart = -1e9, windowEnd = 1e9): 
        return self.__groupAndOrder(windowStart, windowEnd)
        
    def __groupAndOrder(self, windowStart = -1e9, windowEnd = 1e9):
    
        trgTime = self.getPMTTime()
    
        STRIP = []
        TS = []
        for i,ch in enumerate(self.t.TDC_channel):
        
            if self.t.TDC_TimeStamp[i] < self.timeWindowReject: continue # reject TDC first events (based on uncorrected timing)
            
            if not ch in self.TDC_channels: continue # only consider channels from chamber
            if self.TDC_strips[self.TDC_channels.index(ch)] in self.TDC_strips_mask: continue
            
            
            t = self.t.TDC_TimeStamp[i] - trgTime# corrected time w.r.t. PMT (if enabled)
            if t < windowStart: continue # min time window
            if t > windowEnd: continue # max time window
            
            
            stripNo = self.TDC_channels.index(ch)
            STRIP.append(stripNo)
            TS.append(t)
        
        return STRIP, TS
        
    def getGeometry(self):
    
        return self.nStrips, self.stripPitch, self.stripArea, self.xPos, self.zPos
            
      
    
 
    def write(self):
    
        print("Write output JSON file")
        
        out = {}
        
        param_input = {
        
            "scanType"                      : self.scanType,
            "scanid"                        : self.scanid,
            "HVPoint"                       : self.HVPoint,
            
            "chamberName"                   : self.chamberName,
            
            "TDC_channel_PMT"               : self.TDC_channel_PMT,
        
            "muonTriggerWindow"             : self.muonTriggerWindow,
            "noiseRateTriggerWindow"        : self.noiseRateTriggerWindow,
            "timeWindowReject"              : self.timeWindowReject,
            "triggerWindow"                 : self.triggerWindow, 
            "muonWindowWidth"               : self.muonWindowWidth,
            
            "muonClusterTimeWindow"         : self.muonClusterTimeWindow,
            "muonClusterTimeWindowUp"       : self.muonClusterTimeWindowUp,
            "muonClusterTimeWindowDw"       : self.muonClusterTimeWindowDw,
            
            
            "stripArea"                     : self.stripArea,
            "nStrips"                       : self.nStrips,


        }
        
        param_output = {
        
            "muonWindowSigma"               : self.muonWindowSigma,
            "muonWindowMean"                : self.muonWindowMean, 
            "muonTimeWindowBegin"           : self.muonTimeWindowBegin,
            "muonTimeWindowEnd"             : self.muonTimeWindowEnd,
            "muonTimeWindow"                : self.muonTimeWindow,
            "noiseGammaTimeWindowBegin"     : self.noiseGammaTimeWindowBegin,
            "noiseGammaTimeWindow"          : self.noiseGammaTimeWindow,
            "noiseGammaTimeWindowEnd"       : self.noiseGammaTimeWindowEnd,
        }  

        param_output.update(self.outDict)
   
        data = {
        
            "input_parameters"          :  param_input, 
            "output_parameters"         :  param_output, 
        }
    
        with open("%soutput.json" % self.savePath, 'w') as fp: json.dump(data, fp, indent=4)
    


