
import sys, os, glob, shutil, json, math, re, random, copy
import ROOT
import numpy as np
import networkx as nx # graph tools needed for clusterization
import config
import analyzer as an

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

class Analyzer2D():

    savePath = ""
    basePath = ""
    
    scanid = -1
    HVPoint = -1
    
    verbose = 0
    
    # results from efficiency
    efficiencyRaw = -1
    efficiencyMuon = -1
    efficiencyRaw_err = -1
    efficiencyMuon_err = -1

    # analyzer objects
    analyzer_x = None
    analyzer_y = None
    
    
    # drawing
    c1 = None # default square canvas
    c2 = None # default rectangular canvas
    c3 = None 
    
    
    def __init__(self, dir, savePath, scanid, HVPoint, scanType):
    
        self.scanid = scanid
        self.HVPoint = HVPoint
        self.basePath = dir
        self.savePath = savePath
        
        if not os.path.exists(self.savePath): os.makedirs(self.savePath)
        
        # default square canvas
        self.c1 = ROOT.TCanvas("c1_Analyzer2D", "c1_Analyzer2D", 800, 800)
        self.c1.SetLeftMargin(0.12)
        self.c1.SetRightMargin(0.05)
        self.c1.SetTopMargin(0.05)
        self.c1.SetBottomMargin(0.1)
        
        # default rectangular canvas
        self.c2 = ROOT.TCanvas("c2_Analyzer2D", "c2_Analyzer2D", 900, 1200)
        self.c2.SetLeftMargin(0.12)
        self.c2.SetRightMargin(0.13)
        self.c2.SetTopMargin(0.05)
        self.c2.SetBottomMargin(0.1)
        
        # rectangular canvas, 2D plots
        self.c3 = ROOT.TCanvas("c3_Analyzer2D", "c3_Analyzer2D", 800, 800)
        self.c3.SetLeftMargin(0.12)
        self.c3.SetRightMargin(0.12)
        self.c3.SetTopMargin(0.05)
        self.c3.SetBottomMargin(0.1)
        
        
     
    def __del__(self):
    
        if self.analyzer_x != None: del self.analyzer_x
        if self.analyzer_y != None: del self.analyzer_y
     
    def setVerbose(self, verbose):
    
        self.verbose = verbose
        
        
    def loadConfig(self, cfg, cfg_x, cfg_y):
    
        self.chamberName = cfg["chamberName"]
        self.chamberId = cfg["chamberId"]
        if "textHeader" in cfg: self.textHeader = cfg["textHeader"]
        else: self.textHeader = ""
  
        self.cfg_x = cfg_x
        self.cfg_y = cfg_y
        #self.cfg_x = getattr(config, cfg["chamber_x"])
        #self.cfg_y = getattr(config, cfg["chamber_y"])
        
        
    
    def set1DAnalyzers(self, muonWindowMean_x, muonWindowSigma_x, muonWindowMean_y, muonWindowSigma_y):
   
        # do x
        saveDir_x = self.savePath.replace(self.chamberId, self.cfg_x["chamberId"])
        if not os.path.exists(saveDir_x): os.makedirs(saveDir_x)
        self.analyzer_x = an.Analyzer(self.basePath, saveDir_x, self.scanid, self.HVPoint, "efficiency")
        self.analyzer_x.loadConfig(self.cfg_x)
        self.analyzer_x.setVerbose(1)
        self.analyzer_x.timeProfile(muonWindowMean_x, muonWindowSigma_x)
        self.analyzer_x.timeStripProfile2D()
        self.analyzer_x.clusterization("muon")
        self.analyzer_x.clusterization("gamma")
        self.analyzer_x.efficiency()
        self.analyzer_x.stripProfile(plotNoSpill = False)
        self.analyzer_x.write() # write all results to JSON file

        self.muonWindowMean_x = muonWindowMean_x
        self.muonWindowSigma_x = muonWindowSigma_x
        self.muonWindowMean_y = muonWindowMean_y
        self.muonWindowSigma_y = muonWindowSigma_y
        
        self.stripMin_x = min(self.analyzer_x.TDC_strips)
        self.stripMax_x = max(self.analyzer_x.TDC_strips) 
        self.nstrips_x = self.analyzer_x.nStrips
        self.stripArea_x = self.analyzer_x.stripArea
        self.muonTimeWindowBegin_x = self.analyzer_x.muonTimeWindowBegin
        self.muonTimeWindowEnd_x = self.analyzer_x.muonTimeWindowEnd
        self.noiseGammaTimeWindowBegin_x = self.analyzer_x.noiseGammaTimeWindowBegin
        self.noiseGammaTimeWindowEnd_x = self.analyzer_x.noiseGammaTimeWindowEnd
        self.TDC_strips_x = self.analyzer_x.TDC_strips
        self.TDC_strips_mask_x = self.analyzer_x.TDC_strips_mask
        self.noiseGammaTimeWindow_x = self.analyzer_x.noiseGammaTimeWindow
        
        
        # do y
        saveDir_y = self.savePath.replace(self.chamberId, self.cfg_y["chamberId"])
        if not os.path.exists(saveDir_y): os.makedirs(saveDir_y)
        self.analyzer_y = an.Analyzer(self.basePath, saveDir_y, self.scanid, self.HVPoint, "efficiency")
        self.analyzer_y.loadConfig(self.cfg_y)
        self.analyzer_y.setVerbose(1)
        self.analyzer_y.timeProfile(muonWindowMean_y, muonWindowSigma_y)
        self.analyzer_y.timeStripProfile2D()
        self.analyzer_y.clusterization("muon")
        self.analyzer_y.clusterization("gamma")
        self.analyzer_y.efficiency()
        self.analyzer_y.stripProfile(plotNoSpill = False)
        self.analyzer_y.write() # write all results to JSON file
    

        self.stripMin_y = min(self.analyzer_y.TDC_strips)
        self.stripMax_y = max(self.analyzer_y.TDC_strips) 
        self.nstrips_y = self.analyzer_y.nStrips
        self.stripArea_y = self.analyzer_y.stripArea
        self.muonTimeWindowBegin_y = self.analyzer_y.muonTimeWindowBegin
        self.muonTimeWindowEnd_y = self.analyzer_y.muonTimeWindowEnd
        self.noiseGammaTimeWindowBegin_y = self.analyzer_y.noiseGammaTimeWindowBegin
        self.noiseGammaTimeWindowEnd_y = self.analyzer_y.noiseGammaTimeWindowEnd
        self.TDC_strips_y = self.analyzer_y.TDC_strips
        self.TDC_strips_mask_y = self.analyzer_y.TDC_strips_mask
        self.noiseGammaTimeWindow_y = self.analyzer_y.noiseGammaTimeWindow        
  

    def stripProfile2D(self):
    
        
        stripProfileAll = ROOT.TH2D("stripProfileAll", "Strip profile (all hits)", self.nstrips_x, self.stripMin_x, self.stripMax_x+1, self.nstrips_y, self.stripMin_y, self.stripMax_y+1)
        stripProfileMuon = ROOT.TH2D("stripProfileMuon", "Strip profile (hits inside muon window)", self.nstrips_x, self.stripMin_x, self.stripMax_x+1, self.nstrips_y, self.stripMin_y, self.stripMax_y+1)

        for i in range(1, self.nstrips_x+1):
        
            stripProfileAll.GetXaxis().SetBinLabel(i, str(self.TDC_strips_x[i-1]))
            stripProfileMuon.GetXaxis().SetBinLabel(i, str(self.TDC_strips_x[i-1]))
            
        for i in range(1, self.nstrips_y+1):
        
            stripProfileAll.GetYaxis().SetBinLabel(i, str(self.TDC_strips_y[i-1]))
            stripProfileMuon.GetYaxis().SetBinLabel(i, str(self.TDC_strips_y[i-1]))
        
        for i in range(1, self.nstrips_x+1):
            for j in range(1, self.nstrips_y+1):
                stripProfileAll.SetBinContent(i,j,0.01)
                stripProfileMuon.SetBinContent(i,j,0.01)

        # loop over all events    
        for evNum in range(0, self.analyzer_x.t.GetEntries()):
            
            self.analyzer_x.t.GetEntry(evNum)
            self.analyzer_y.t.GetEntry(evNum)
            if not self.analyzer_x.validateEvent(): continue
            if not self.analyzer_y.validateEvent(): continue
            if not self.analyzer_x.isBeamTrigger(): continue
            if not self.analyzer_y.isBeamTrigger(): continue
            

            # probe all hits time window
            firedStrips_x, timeStamps_x = self.analyzer_x.groupAndOrder()
            firedStrips_y, timeStamps_y = self.analyzer_y.groupAndOrder()
            for ch_x in firedStrips_x: # need to loop over all permutations of hits in X and Y
                for ch_y in firedStrips_y: 
                    stripProfileAll.Fill(self.TDC_strips_x[ch_x], self.TDC_strips_y[ch_y])   
                   
            # probe muon time window
            firedStrips_x, timeStamps_x = self.analyzer_x.groupAndOrder(self.muonTimeWindowBegin_x, self.muonTimeWindowEnd_x)
            firedStrips_y, timeStamps_y = self.analyzer_y.groupAndOrder(self.muonTimeWindowBegin_y, self.muonTimeWindowEnd_y)
            for ch_x in firedStrips_x: # need to loop over all permutations of hits in X and Y
                for ch_y in firedStrips_y: 
                    stripProfileMuon.Fill(self.TDC_strips_x[ch_x], self.TDC_strips_y[ch_y])   
           
           
        self.c3.cd()
        self.c3.Clear()
        
        ROOT.gStyle.SetPalette(ROOT.kDarkRainBow)
        
       
        stripProfileMuon.GetXaxis().SetTitle("Strips %s" % self.analyzer_x.chamberName)
        stripProfileMuon.GetXaxis().SetTitleOffset(1.3)
        stripProfileMuon.GetXaxis().SetLabelOffset(0.005)
        stripProfileMuon.GetYaxis().SetTitle("Strips %s" % self.analyzer_y.chamberName)
        stripProfileMuon.GetYaxis().SetTitleOffset(1.3)
        stripProfileMuon.GetYaxis().SetLabelOffset(0.005)
        stripProfileMuon.Draw("COLZ")
        
        tLatex = ROOT.TLatex()
        tLatex.SetTextFont(42)
        tLatex.SetTextSize(0.03)
        tLatex.SetNDC()
        tLatex.DrawLatex(0.02, 0.01, "#bf{%s}" % self.chamberName)
        tLatex.DrawLatex(0.02, 0.045, "Muon window, eff. muon %.2f%%" % (100.*self.efficiencyMuon))

        self.__drawAux(self.c3)
        self.c3.RedrawAxis()
        self.c3.Modify()        
        self.c3.SaveAs("%smuonHitProfile.png" % (self.savePath)) 
        self.c3.SaveAs("%smuonHitProfile.pdf" % (self.savePath))   


        self.c3.Clear()
        stripProfileAll.GetXaxis().SetTitle("Strips %s" % self.analyzer_x.chamberName)
        stripProfileAll.GetXaxis().SetTitleOffset(1.3)
        stripProfileAll.GetXaxis().SetLabelOffset(0.005)
        stripProfileAll.GetYaxis().SetTitle("Strips %s" % self.analyzer_y.chamberName)
        stripProfileAll.GetYaxis().SetTitleOffset(1.3)
        stripProfileAll.GetYaxis().SetLabelOffset(0.005)
        stripProfileAll.Draw("COLZ")
        
        tLatex = ROOT.TLatex()
        tLatex.SetTextFont(42)
        tLatex.SetTextSize(0.03)
        tLatex.SetNDC()
        tLatex.DrawLatex(0.02, 0.01, "#bf{%s}" % self.chamberName)
        tLatex.DrawLatex(0.02, 0.045, "All hits, eff. abs %.2f%%" % (100.*self.efficiencyRaw))

        self.__drawAux(self.c3)
        self.c3.RedrawAxis()
        self.c3.Modify()        
        self.c3.SaveAs("%sallHitProfile.png" % (self.savePath)) 
        self.c3.SaveAs("%sallHitProfile.pdf" % (self.savePath))       
        

   
  
  
    
         
         
    def clusterEvents(self, direction):
    
    
        # return event clusters when both (!) x and y are fired
        clusters, clusters_time, barycenters, barycenters_err = [], [], [], []
        clusters_x, clusters_time_x, barycenters_x, barycenters_err_x = self.analyzer_x.clusterEvents()
        clusters_y, clusters_time_y, barycenters_y, barycenters_err_y = self.analyzer_y.clusterEvents()
        
        print(len(clusters_x), len(clusters_y))
        for iEv, cluster_x in enumerate(clusters_x):

            if len(clusters_x[iEv]) == 0 or len(clusters_y[iEv]) == 0: # require both directions to be fired
            
                clusters.append([])
                clusters_time.append([])
                barycenters.append([])
                barycenters_err.append([])
        
            else:
            
                if direction == "x":
                    clusters.append(clusters_x[iEv])
                    clusters_time.append(clusters_time_x[iEv])
                    barycenters.append(barycenters_x[iEv])
                    barycenters_err.append(barycenters_err_x[iEv])
            
                else:
                
                    clusters.append(clusters_y[iEv])
                    clusters_time.append(clusters_time_y[iEv])
                    barycenters.append(barycenters_y[iEv])
                    barycenters_err.append(barycenters_err_y[iEv])
    
        return clusters, clusters_time, barycenters, barycenters_err

    def efficiency(self):     
        print("test")
        nHitsAbs = 0
        nHitsMuonWindow = 0
        nTrig = 0
        for evNum in range(0, self.analyzer_x.t.GetEntries()):
            
            self.analyzer_x.t.GetEntry(evNum)
            self.analyzer_y.t.GetEntry(evNum)
            if not self.analyzer_x.validateEvent(): continue
            if not self.analyzer_y.validateEvent(): continue
            if not self.analyzer_x.isBeamTrigger(): continue
            if not self.analyzer_y.isBeamTrigger(): continue
            nTrig +=1
            
            
            # probe all hits time window
            firedStrips_x, timeStamps_x = self.analyzer_x.groupAndOrder()
            firedStrips_y, timeStamps_y = self.analyzer_y.groupAndOrder()
            if len(firedStrips_x) > 0 and len(firedStrips_y) > 0: nHitsAbs +=1
                   
                
            # probe muon time window
            firedStrips_x, timeStamps_x = self.analyzer_x.groupAndOrder(self.muonTimeWindowBegin_x, self.muonTimeWindowEnd_x)
            firedStrips_y, timeStamps_y = self.analyzer_y.groupAndOrder(self.muonTimeWindowBegin_y, self.muonTimeWindowEnd_y)
            if len(firedStrips_x) > 0 and len(firedStrips_y) > 0: nHitsMuonWindow +=1

        
        
        # calculate the efficiency and store in class members
        if nTrig > 0:
            self.efficiencyRaw = 1.0*nHitsAbs / nTrig
            self.efficiencyMuon = 1.0*nHitsMuonWindow / nTrig
            
            self.efficiencyRaw_err = math.sqrt(self.efficiencyRaw*(1.0-self.efficiencyRaw)/nTrig)
            self.efficiencyMuon_err = math.sqrt(self.efficiencyMuon*(1.0-self.efficiencyMuon)/nTrig)
                 
        

    def eventDisplay2D(self, maxEvents):
    
        ROOT.gStyle.SetPalette(ROOT.kDarkRainBow)
        path = self.savePath + "eventDisplay/"
        if os.path.isdir(path): shutil.rmtree(path)
        os.mkdir(path)

        stripProfileMuon = ROOT.TH2D("stripProfileMuon", "Strip profile (muon)", self.nstrips_x, self.stripMin_x, self.stripMax_x+1, self.nstrips_y, self.stripMin_y, self.stripMax_y+1)
        for i in range(1, self.nstrips_x+1):
        
            stripProfileMuon.GetXaxis().SetBinLabel(i, str(self.TDC_strips_x[i-1]))
            
        for i in range(1, self.nstrips_y+1):
        
            stripProfileMuon.GetYaxis().SetBinLabel(i, str(self.TDC_strips_y[i-1]))
        
        
                
        stripProfileMuon.GetXaxis().SetTitle("Strips %s" % self.analyzer_x.chamberName)
        stripProfileMuon.GetXaxis().SetTitleOffset(1.3)
        stripProfileMuon.GetXaxis().SetLabelOffset(0.005)

        stripProfileMuon.GetYaxis().SetTitle("Strips %s" % self.analyzer_y.chamberName)
        stripProfileMuon.GetYaxis().SetTitleOffset(1.3)
        stripProfileMuon.GetYaxis().SetLabelOffset(0.005)

        # loop over all events    
        evts = 0
        for evNum in range(0, self.analyzer_x.t.GetEntries()):
            
            self.analyzer_x.t.GetEntry(evNum)
            self.analyzer_y.t.GetEntry(evNum)
            if not self.analyzer_x.validateEvent(): continue
            if not self.analyzer_y.validateEvent(): continue
            if not self.analyzer_x.isBeamTrigger(): continue
            if not self.analyzer_y.isBeamTrigger(): continue
            
            evts += 1
            
            # reset the histogram contents
            for i in range(1, self.nstrips_x+1):
                for j in range(1, self.nstrips_y+1):
                    stripProfileMuon.SetBinContent(i,j,0.001)
            

            firedStrips_x, timeStamps_x = self.analyzer_x.groupAndOrder(self.muonTimeWindowBegin_x, self.muonTimeWindowEnd_x)
            firedStrips_y, timeStamps_y = self.analyzer_y.groupAndOrder(self.muonTimeWindowBegin_y, self.muonTimeWindowEnd_y)
            
            # need to loop over all permutations of hits in X and Y
            for ch_x in firedStrips_x: 
                for ch_y in firedStrips_y: 
                    stripProfileMuon.Fill(self.TDC_strips_x[ch_x], self.TDC_strips_y[ch_y])   
                   
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


    
    
    def getStripPos(self, direction, strip):
        
        if direction == "x": return self.analyzer_x.getStripPos(strip)
        if direction == "y": return self.analyzer_y.getStripPos(strip)

    def getGeometry(self, direction):
    
        if direction == "x":
        
            return self.analyzer_x.nStrips, self.analyzer_x.stripPitch, self.analyzer_x.stripArea, self.analyzer_x.xPos, self.analyzer_x.zPos
            
        else: return self.analyzer_y.nStrips, self.analyzer_y.stripPitch, self.analyzer_y.stripArea, self.analyzer_y.xPos, self.analyzer_y.zPos
    

        
   
    def write(self):
    
        print ("Write output JSON file")
        
        out = {}
        
        param_input = {}
        
        param_output = {

            "efficiencyRaw"             : self.efficiencyRaw,
            "efficiencyMuon"            : self.efficiencyMuon,  
            "efficiencyRaw_err"         : self.efficiencyRaw_err,
            "efficiencyMuon_err"        : self.efficiencyMuon_err, 
            

            # store all vars, useful later for e.g. tracking etc.
            "muonWindowMean_x"          : self.muonWindowMean_x, 
            "muonWindowSigma_x"         : self.muonWindowSigma_x, 
            "muonWindowMean_y"          : self.muonWindowMean_y, 
            "muonWindowSigma_y"         : self.muonWindowSigma_y, 
         

        }        
   
        data = {
        
            "input_parameters"          :  param_input, 
            "output_parameters"         :  param_output, 
        }
    
        with open("%soutput.json" % self.savePath, 'w') as fp: json.dump(data, fp, indent=4)
    


