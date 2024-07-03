
import sys, os, glob, shutil, json, math, re, random
import ROOT
import networkx as nx # graph tools needed for clusterization

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


class Analyzer():


    fIn = None  # pointer to ROOT file
    t = None    # raw data tree
    
    tag = ""
    savePath = "" # path where the plots and results will be stored
    basePath = "" # path where the raw ROOT files are stored, set by constructor
    
    scanid = -1
    HVPoint = -1
    
    verbose = 0

    
    # list of all free parameters in the analysis
    noiseOffsetFromMuonWindow = 20 # time between muon window and noise window (for efficiency scans)
    
    
    ## list of parameters loaded from the config
    muonTriggerWindow = -1
    noiseTriggerWindow = -1
    timeWindowReject = -1
    muonWindowWidth = -1
    
    nStrips = -1
    stripArea = -1
    
    TDC_strips = []
    TDC_strips_mask = []
    TDC_channels = []
    TDC_channels_PMT = []
    
    ## list of parameters calculated by the analyzer
    muonWindowSigma = -1        # time profile width, obtained by Gaussian fit or given by user
    muonWindowMean = -1         # time profile mean, obtained by Gaussian by fit or given by user
    muonTimeWindowBegin = -1
    muonTimeWindowEnd = -1
    muonTimeWindow = -1         # length of muon time window
    noiseTimeWindowBegin = -1
    noiseTimeWindow = -1        # length of noise time window
    noiseTimeWindowEnd = -1
    triggerWindow = -1          # either muonTimewindow or noiseTimeWindow (600 or 10000 ns, depending on scan type)
    

    
    ## results from noise calculation
    noiseRate = -1
    
    
    
    # drawing options (see function __drawAux())
    c1 = None # default square canvas
    c2 = None # default rectangular canvas
    textCMS = "#bf{GIF++} #scale[0.75]{ #it{Preliminary}}" # CMS GIF++ TLatex (top left on canvas)
    textAux = None # auxiliary info (top right on canvas)


    def __init__(self, dir, savePath, scanid, HVPoint, scanType):
    
        self.scanid = scanid
        self.HVPoint = HVPoint
        self.basePath = dir
        self.savePath = savePath
        
        if not os.path.exists(self.savePath): os.makedirs(self.savePath)
    
        # get the raw data
        self.fIn = ROOT.TFile("%s/Scan%.6d_HV%d_DAQ.root" % (dir, scanid, HVPoint))
        self.t = self.fIn.Get("RAWData")
        
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
        

        
    def setVerbose(self, verbose):
    
        self.verbose = verbose
        
        
    def loadConfig(self, cfg):
    
        self.noiseTriggerWindow = cfg["noiseTriggerWindow"]
        self.timeWindowReject = cfg["timeWindowReject"]
        
        self.stripArea = cfg["stripArea"]
        self.nStrips = len(cfg["TDC_channels"]) # correction for masked strips needed ?
        
        self.TDC_strips = cfg["TDC_strips"]
        self.TDC_strips_mask = cfg["TDC_strips_mask"]
        self.TDC_channels = cfg["TDC_channels"]
        
        if self.scanType == "efficiency": self.triggerWindow = self.muonTriggerWindow
        
        self.chamberName = cfg["chamberName"]

        

    def timeStripProfile2D(self):
    
        #ROOT.gStyle.SetPalette(ROOT.kDarkRainBow)

        self.c2.cd()
        self.c2.Clear() 


        scale = 1000. # convert ns to us
        timeStart = self.noiseTimeWindowBegin
        timeEnd = self.noiseTimeWindowEnd 
        width = self.noiseTimeWindow
            
       
        
        # make 2D histogram (x-axis time, y-axis strips)
        timeStripProfile = ROOT.TH2D("timeStripProfile", "Time-strip profile", width, int(timeStart/scale), int(timeEnd/scale), self.nStrips, min(self.TDC_strips), max(self.TDC_strips)+1)
        
        for evNum in range(0, self.t.GetEntries()+1):
        
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
                        
            firedStrips, timeStamps = self.__groupAndOrder(self.t.TDC_channel, self.t.TDC_TimeStamp, -1e5, 1e5)
            for i,ch in enumerate(firedStrips): timeStripProfile.Fill(timeStamps[i]/scale, self.TDC_strips[ch])
        
        # loop over all strips: set the y-axis label and set all bin contents to zero          
        for i in range(1, self.nStrips+1):
        
            #print "Parse strip %d with TDC channel %d" % (i, cfg.TDC_strips[i-1])
            timeStripProfile.GetYaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))
            #for j in range(0, self.triggerWindow): timeStripProfile.SetBinContent(j, i, 0.0)
            


        timeStripProfile.GetXaxis().SetRangeUser(int(timeStart/scale), int(timeEnd/scale))
        timeStripProfile.GetXaxis().SetTitle("Time (#mus)")
        timeStripProfile.GetXaxis().SetTitleOffset(1.0)
        timeStripProfile.GetXaxis().SetLabelOffset(0.0)

        timeStripProfile.GetYaxis().SetTitle("Strip number")   
        timeStripProfile.GetYaxis().SetTitleOffset(1.3)
        timeStripProfile.GetYaxis().SetLabelOffset(0.005)
        
        timeStripProfile.Draw("COLZ")
        
        self.__drawAux(self.c2)
        self.c2.RedrawAxis()
        self.c2.Modify()    
        if self.verbose > 0:
            self.c2.SaveAs("%stimeStripProfile2D.png" % self.savePath) 
            self.c2.SaveAs("%stimeStripProfile2D.pdf" % self.savePath) 


    def timeProfile(self):

        self.noiseTimeWindowBegin = self.timeWindowReject # start at rejection time
        self.noiseTimeWindowEnd = self.noiseTriggerWindow
        self.noiseTimeWindow = self.noiseTimeWindowEnd - self.noiseTimeWindowBegin   

        scale = 1000. # convert ns to us
        timeStart = self.noiseTimeWindowBegin
        timeEnd = self.noiseTimeWindowEnd 
        width = self.noiseTimeWindow
            
            
        timeProfile = ROOT.TH1D("timeProfile", "Time profile", width, int(timeStart/scale), int(timeEnd/scale))
        for evNum in range(0, self.t.GetEntries()+1):
        
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
  
            firedStrips, timeStamps = self.__groupAndOrder(self.t.TDC_channel, self.t.TDC_TimeStamp, timeStart, timeEnd)
            for i,ch in enumerate(firedStrips): timeProfile.Fill(timeStamps[i]/scale)
        

        # draw raw profile
        self.c1.cd()
        self.c1.Clear()     

            
        timeProfile.Draw("HIST")
        timeProfile.GetYaxis().SetRangeUser(0, 1.3*timeProfile.GetMaximum())
        timeProfile.SetLineColor(ROOT.kBlack)

        timeProfile.GetXaxis().SetTitle("Time (#mus)")
        timeProfile.GetXaxis().SetTitleOffset(1.2)
        timeProfile.GetXaxis().SetLabelOffset(0.005)

        timeProfile.GetYaxis().SetTitle("Hits")   
        timeProfile.GetYaxis().SetTitleOffset(1.8)
        timeProfile.GetYaxis().SetLabelOffset(0.005)
        
        tLatex = ROOT.TLatex()
        tLatex.SetTextFont(42)
        tLatex.SetTextSize(0.03)
        tLatex.SetNDC()
        tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)
        tLatex.DrawLatex(0.16, 0.85, "Time profile")

        self.__drawAux(self.c1)
        self.c1.RedrawAxis()
        self.c1.Modify()
        if self.verbose > 0:
            self.c1.SaveAs("%stimeProfile.png" % self.savePath) 
            self.c1.SaveAs("%stimeProfile.pdf" % self.savePath)             

   
    def stripProfile(self):
    
        nValidatedEvents = 0
        stripProfileNoise = ROOT.TH1D("stripProfileNoise", "Strip profile (noise)", self.nStrips, min(self.TDC_strips), max(self.TDC_strips)+1)

        for i in range(1, self.nStrips+1):
        
            stripProfileNoise.GetXaxis().SetBinLabel(i, str(self.TDC_strips[i-1]))
        
  
        # loop over all events    
        for evNum in range(0, self.t.GetEntries()+1):
            
            self.t.GetEntry(evNum)
            #if not self.validateEvent(): continue
            nValidatedEvents += 1
              
            # probe noise time window
            if self.scanType == "noise":
                firedStrips, timeStamps = self.__groupAndOrder(self.t.TDC_channel, self.t.TDC_TimeStamp, self.noiseTimeWindowBegin, self.noiseTimeWindowEnd)
                for ch in firedStrips: stripProfileNoise.Fill(self.TDC_strips[ch])              

            
        ## all hit profile
        self.c1.cd()
        self.c1.Clear()

        stripProfileNoise.GetYaxis().SetNoExponent()
        stripProfileNoise.SetFillStyle(3354)
        stripProfileNoise.SetFillColor(ROOT.kBlue)
        stripProfileNoise.SetFillColorAlpha(ROOT.kBlue, 0.35)
        stripProfileNoise.SetLineColor(ROOT.kBlue)
        stripProfileNoise.SetLineWidth(2)
        stripProfileNoise.Draw("HIST")
        
        stripProfileNoise.GetYaxis().SetRangeUser(0, 1.3*stripProfileNoise.GetMaximum())
        stripProfileNoise.GetXaxis().SetTitle("Strip number")
        stripProfileNoise.GetXaxis().SetTitleOffset(1.2)
        stripProfileNoise.GetXaxis().SetLabelOffset(0.005)
        stripProfileNoise.GetXaxis().SetLabelSize(0.04)

        stripProfileNoise.GetYaxis().SetTitle("Number of hits")   
        stripProfileNoise.GetYaxis().SetTitleOffset(1.8)
        stripProfileNoise.GetYaxis().SetLabelOffset(0.005)    
        
        tLatex = ROOT.TLatex()
        tLatex.SetTextFont(42)
        tLatex.SetTextSize(0.03)
        tLatex.SetNDC()
        tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)
        tLatex.DrawLatex(0.16, 0.85, "Hit profile (all hits)")

        self.__drawAux(self.c1)
        self.c1.RedrawAxis()
        self.c1.Modify()        
        self.c1.SaveAs("%sallHitProfile.png" % self.savePath) 
        self.c1.SaveAs("%sallHitProfile.pdf" % self.savePath)   

        
        
        
        # nosie profile: to proper scaling of the hit profile
        
        meanNoise = stripProfileNoise.GetEntries() # total amount of hits
        norm = self.stripArea * self.noiseTimeWindow * nValidatedEvents * 1e-9
        stripProfileNoise.Scale(1./norm)
        meanNoise /= (norm * (len(self.TDC_strips)-len(self.TDC_strips_mask))) # re-correct for masked strips
        self.noiseRate = meanNoise
        
        self.minNoise, self.maxNoise = 1e5, -1e5
        for i in range(1, stripProfileNoise.GetNbinsX()+1):
        
            tmp = stripProfileNoise.GetBinContent(i)
            if tmp > 1e-5 and tmp < self.minNoise: self.minNoise = tmp
            if tmp > self.maxNoise: self.maxNoise = tmp

        self.c1.cd()
        self.c1.Clear()

        stripProfileNoise.SetFillStyle(3354)
        stripProfileNoise.SetFillColor(ROOT.kBlue)
        stripProfileNoise.SetFillColorAlpha(ROOT.kBlue, 0.35)
        stripProfileNoise.SetLineColor(ROOT.kBlue)
        stripProfileNoise.SetLineWidth(2)
        stripProfileNoise.Draw("HIST")
            
        stripProfileNoise.GetYaxis().SetRangeUser(0, 1.3*stripProfileNoise.GetMaximum())
        stripProfileNoise.GetXaxis().SetTitle("Strip number")
        stripProfileNoise.GetXaxis().SetTitleOffset(1.2)
        stripProfileNoise.GetXaxis().SetLabelOffset(0.005)
        stripProfileNoise.GetXaxis().SetLabelSize(0.04)

        stripProfileNoise.GetYaxis().SetTitle("Noise rate (Hz/cm^{2})")   
        stripProfileNoise.GetYaxis().SetTitleOffset(1.8)
        stripProfileNoise.GetYaxis().SetLabelOffset(0.005)    
            
        tLatex = ROOT.TLatex()
        tLatex.SetTextFont(42)
        tLatex.SetTextSize(0.03)
        tLatex.SetNDC()
        tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.chamberName)
        tLatex.DrawLatex(0.16, 0.85, "Mean noise rate: %.2f Hz/cm^{2}" % meanNoise)
        tLatex.DrawLatex(0.16, 0.80, "Min/max: %.2f/%.2f Hz/cm^{2}" % (self.minNoise, self.maxNoise))

        self.__drawAux(self.c1)
        self.c1.RedrawAxis()
        self.c1.Modify()        
        self.c1.SaveAs("%snoiseProfile.png" % self.savePath) 
        self.c1.SaveAs("%snoiseProfile.pdf" % self.savePath)        

    
        
    def clusterization(self, clusterTimeWindow = 10, clusterTimeWindowUp = -1, clusterTimeWindowDown = -1):

        
        # perform clusterization
        cls, cmp = self._clusterization(clusterTimeWindow)
        self.gammaCLS, self.gammaCMP = cls, cmp
        
        # calculate clusterization error
        clsErr, cmpErr = -1, -1
        if clusterTimeWindowUp != -1 and clusterTimeWindowDown != -1:
                    
            self.setVerbose(0) # turn of verbosity
            clsUp, cmpUp = self._clusterization(clusterTimeWindowUp) # up variation
            clsDown, cmpDown = self._clusterization(clusterTimeWindowDown) # down variation
            
            #clsErr = (abs(clsUp-cls) + abs(clsDown-cls)) / 2.0
            #cmpErr = (abs(cmpUp-cls) + abs(cmpDown-cmp)) / 2.0
            
            # define the error as the MAX between the variations
            clsErr = max([abs(clsUp-cls), abs(clsDown-cls)])
            cmpErr = max([abs(cmpUp-cmp), abs(cmpDown-cmp)])
            
            self.gammaCLS_err, self.gammaCMP_err = clsErr, cmpErr
            self.setVerbose(1)
        
        return cls, cmp
        
        
    
    def _clusterization(self, clusterTimeWindow = 10):

        self.clusterTimeWindow = clusterTimeWindow
    
        h_clustersize = ROOT.TH1D("clustersize", "Cluster size", 1000, 0, 1000)
        h_clustermultiplicity = ROOT.TH1D("clustermultiplicity", "Cluster multiplicity", 1000, 0, 1000)
    
        # select the time window based on the mode
        tMin, tMax = self.muonTriggerWindow, self.noiseTriggerWindow
        
        maxCLS = -99
        maxCMP = -99
        

        for evNum in range(0, self.t.GetEntries()+1):
            
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            #if evNum > 1000: break
           
            firedStrips, timeStamps = self.__groupAndOrder(self.t.TDC_channel, self.t.TDC_TimeStamp, tMin, tMax)
            #print "----------- %d" % evNum, firedStrips, timeStamps
    
            #if len(firedStrips) == 0: continue
    
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
                    
                    if abs(DS) == 1 and abs(DT) < self.clusterTimeWindow: # if pair conditions satisfied
                        #print "pair", ch1, ch2
                        G.add_edge(i,j)
                        
            #print "Graph nodes:", G.number_of_nodes(), "Edges:", G.number_of_edges()
            #print "MP", len(list(nx.connected_components(G)))
            MP = len(list(nx.connected_components(G)))
            if MP > maxCMP: maxCMP = MP
            h_clustermultiplicity.Fill(MP)
            
            
            if len(firedStrips) == 0: continue # if empty event, do not count for calculation of CLS
            for k in nx.connected_components(G): 
                CLS = len(k)
                if CLS > maxCLS: maxCLS = CLS
                h_clustersize.Fill(CLS)
            


        # store the mean CLS BEFORE change of axis range!
        cls, cmp = h_clustersize.GetMean(), h_clustermultiplicity.GetMean()   

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


        h_clustermultiplicity.GetXaxis().SetTitle("Gamma cluster multiplicity")
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
        params.DrawLatex(0.16, 0.85, "Mean gamma cluster multiplicity (CMP): %.2f" % cmp)
        

        self.__drawAux(self.c1)
        self.c1.RedrawAxis()
        self.c1.Modify()
        if self.verbose > 0:
            self.c1.SaveAs("%sCMP_gamma.png" % self.savePath) 
            self.c1.SaveAs("%sCMP_gamma.pdf" % self.savePath)   
            
            
        


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

        h_clustersize.GetXaxis().SetTitle("Gamma cluster size")
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
        params.DrawLatex(0.16, 0.85, "Mean gamma cluster size (CLS): %.2f" % cls)
        

        self.__drawAux(self.c1)
        self.c1.RedrawAxis()
        self.c1.Modify()
        if self.verbose > 0:
            self.c1.SaveAs("%sCLS_gamma.png" % self.savePath) 
            self.c1.SaveAs("%sCLS_gamma.pdf" % self.savePath)   
            
            
                      
        h_clustersize.Delete()
        h_clustermultiplicity.Delete()  
        
        
        
    
        
        return cls, cmp
         

 
    def eventDisplay(self, maxEvents):
    
        #ROOT.gStyle.SetPalette(ROOT.kDarkRainBow)
        
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


        
        if self.scanType == "noise" or self.scanType == "rate":
            
            scale = 1000.
            timeStart = self.timeWindowReject
            timeEnd = self.noiseTriggerWindow
            
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
            timeStart = self.noiseTimeWindowBegin
            timeEnd = self.noiseTimeWindowEnd
            width = 10*int(self.noiseTimeWindow+1)
            width = self.noiseTimeWindow+1
    
    
        for evNum in evToPlot:
    
            self.t.GetEntry(evNum)
            if not self.validateEvent(): continue
            
            
            #firedStrips, timeStamps = self.__groupAndOrder(self.t.TDC_channel, self.t.TDC_TimeStamp, timeStart, timeEnd)
            firedStrips, timeStamps = self.__groupAndOrder(self.t.TDC_channel, self.t.TDC_TimeStamp, -1e5, 1e5)
            if self.scanType == "noise" and len(firedStrips) == 0: continue
            if len(firedStrips) == 0: continue
            
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
                    
                    if abs(DS) == 1 and abs(DT) < self.clusterTimeWindow: # if pair conditions satisfied
                        #print "pair", ch1, ch2
                        G.add_edge(i,j)
                        
            MP = len(list(nx.connected_components(G)))
            outStr += "MP=%d, CLS=(" % MP
            for k in nx.connected_components(G): 
                CLS = len(k)
                outStr += "%d," % CLS
            
            if MP != 0: outStr = outStr[:-1]
            outStr += "), #Deltat = %d ns" % self.clusterTimeWindow
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
        textLeft.DrawLatex(c.GetLeftMargin(), 0.96, self.textCMS)
        
        textRight = ROOT.TLatex()
        textRight.SetNDC()
        textRight.SetTextFont(42)
        textRight.SetTextSize(0.04)
        textRight.SetTextAlign(31)
        if aux == "": textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, "S%d/HV%d" % (self.scanid, self.HVPoint))
        else: textRight.DrawLatex(1.0-c.GetRightMargin(), 0.96, "S%d/HV%d/%s" % (self.scanid, self.HVPoint, aux))

        
    def validateEvent(self):
    
        
        return True

        ## Quality flag validation 
        # see implementation Alexis: https://github.com/afagot/GIF_OfflineAnalysis/blob/master/src/utils.cc
        qFlag = self.t.Quality_flag
        tmpflag = qFlag
        
        IsCorrupted = False
        nDigits = 0
        while tmpflag / int(math.pow(10, nDigits)) != 0: nDigits += 1;
        
        while not IsCorrupted and nDigits != 0:
        
            tdcflag = tmpflag / int(math.pow(10, nDigits-1))

            if tdcflag == 2: 
                IsCorrupted = True

            tmpflag = tmpflag % int(math.pow(10,nDigits-1))
            nDigits -= 1
        
        return not IsCorrupted
        

        
    # Input: raw TDC channel/time vectors,
    # Output: converted TDC channels to strip numbers, within the optinally given time window
    def __groupAndOrder(self, TDC_CH, TDC_TS, windowStart = -1e9, windowEnd = 1e9):
    
        STRIP = []
        TS = []
        for i,ch in enumerate(TDC_CH):
            if not ch in self.TDC_channels: continue # only consider channels from chamber
            if TDC_TS[i] < windowStart: continue # min time window
            if TDC_TS[i] > windowEnd: continue # max time window
            if self.TDC_strips[self.TDC_channels.index(ch)] in self.TDC_strips_mask: continue
            
            
            
            #if TDC_TS[i] < self.timeWindowReject: continue # reject TDC first events
            #stripNo = cfg.TDC_strips[cfg.TDC_channels.index(ch)]
            stripNo = self.TDC_channels.index(ch)
            STRIP.append(stripNo)
            TS.append(TDC_TS[i])
        
        return STRIP, TS
        
 
    def write(self):
    
        print("Write output JSON file")
        
        out = {}
        
        param_input = {
        
            "scanType"                  : self.scanType,
            "scanid"                    : self.scanid,
            "HVPoint"                   : self.HVPoint,
        
            "noiseTriggerWindow"        : self.noiseTriggerWindow,
            "timeWindowReject"          : self.timeWindowReject, 

        }

        param_output = {
        
            "noiseTimeWindowBegin"      : self.noiseTimeWindowBegin,
            "noiseTimeWindow"           : self.noiseTimeWindow,
            "noiseTimeWindowEnd"        : self.noiseTimeWindowEnd,
    
            
            "noiseRate"                 : self.noiseRate,  
            "minNoise"                  : self.minNoise,  
            "maxNoise"                  : self.maxNoise,  
            
            "gammaCLS"                  : self.gammaCLS,  
            "gammaCMP"                  : self.gammaCMP,  
            "gammaCLS_err"              : self.gammaCLS_err,  
            "gammaCMP_err"              : self.gammaCMP_err,  
        }        

   
        data = {
        
            "input_parameters"          :  param_input, 
            "output_parameters"         :  param_output, 
        }
    
        with open("%soutput.json" % self.savePath, 'w') as fp: json.dump(data, fp, indent=4)
    


