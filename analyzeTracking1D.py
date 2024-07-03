

import sys, os, glob, shutil, json, math, re, random, copy
import ROOT
import analyzer2D as an2D
import analyzer as an
import config
import functions
import networkx as nx 

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


      

class RPCTracking1D:


    geo_nLayers = 5 # number of layers (= chambers)
    geo_layer_height = 1.0
    geo_layer_width = 100 # shelf width, arbitrary

    analyzer_trx, analyzer_try = None, None
    analyzer_tr = None
    analyzers = [] # store the objects of the analyzers
    cfgs = [] # hold the configs
    
    def __init__(self, basedir, outputdir, scanid, HVPoint, config, textHeader):
    
        self.basedir = basedir
        self.outputdir = outputdir
        self.scanid = scanid
        self.HVPoint = HVPoint
        
        self.generateRandom = False

        self.random = ROOT.TRandom3(0)
        
        self.tagChamber = None              # tag chamber, provides the clusters (1D)
        # self.probeChambers = []             # list of all chambers to be probed
        self.chambers = []                  # list of all chambers, first one should be the tagging one
 
        self.cluster_collection = []                    # list of clusters for each chamber, for each event
        self.cluster_time_collection = []               # list of clusters for each chamber, for each event, time disributions
        self.cluster_barycenter_collection = []         # list of barycenters for each chamber for each cluster, for each event
        self.cluster_barycenter_err_collection = []     # list of barycenters for each chamber for each cluster, for each event
        
        self.cluster_collection_trx = []                    # list of clusters for each chamber, for each event
        self.cluster_time_collection_trx = []               # list of clusters for each chamber, for each event, time disributions
        self.cluster_barycenter_collection_trx = []         # list of barycenters for each chamber for each cluster, for each event
        self.cluster_barycenter_err_collection_trx = []     # list of barycenters for each chamber for each cluster, for each event
        
        self.cluster_collection_try = []                    # list of clusters for each chamber, for each event
        self.cluster_time_collection_try = []               # list of clusters for each chamber, for each event, time disributions
        self.cluster_barycenter_collection_try = []         # list of barycenters for each chamber for each cluster, for each event
        self.cluster_barycenter_err_collection_try = []     # list of barycenters for each chamber for each cluster, for each event
        
        self.config = config                # holds the entire config file
        self.textHeader = textHeader
        self.param_output = {}
        
        self.dR = -1
        self.cluster_barycenter_algo = ""
        self.stripClusterTolerance = 0
        self.bkg_poiss_mean = -1
        
        
    def setTagChamber(self, chamberCfg):
    
        self.tagChamber = chamberCfg
        if len(self.chambers) == 0: self.chambers.append(chamberCfg) # secure the tag chamber is always the first one
        else: self.chambers.insert(0, chamberCfg)
        
    def addProbeChamber(self, chamberCfg):
    
        self.addProbeChamber.append(chamberCfg)
        self.chambers.append(chamberCfg)
    
 
    def collectClusters(self):

        cluster_collection = []
        cluster_time_collection = []
        cluster_barycenter_collection = []
        cluster_barycenter_err_collection = []
        
        
        for chamberId, chamberName in enumerate(self.chambers):
    
            print("Collect clusters for %s" % chamberName)
            saveDir = self.basedir + "ANALYSIS/%s/HV%d/" % (chamberName, self.HVPoint)
            if not os.path.exists(saveDir): os.makedirs(saveDir)
            
            if chamberId == 0: # the tagging chamber (=2D)
            
                # get the time windows, assume those have been calculated before, otherwise -1
                jsname = "%s/output.json" % (saveDir)
                # print(jsname)
                if os.path.isfile(jsname):
                
                    with open(jsname) as f_in: analyzerResults = json.load(f_in)
                    analyzerResults = analyzerResults['output_parameters']
                    muonWindowMean_x = analyzerResults["muonWindowMean_x"]
                    muonWindowSigma_x = analyzerResults["muonWindowSigma_x"]
                    muonWindowMean_y = analyzerResults["muonWindowMean_y"]
                    muonWindowSigma_y = analyzerResults["muonWindowSigma_y"]
                    
                else:
                
                    muonWindowMean_x = -1
                    muonWindowSigma_x = -1
                    muonWindowMean_y = -1
                    muonWindowSigma_y = -1
                
                cfg = getattr(self.config, chamberName)
                cfg_x = getattr(self.config, cfg["chamber_x"])
                cfg_y = getattr(self.config, cfg["chamber_y"])
                analyzer = an2D.Analyzer2D(self.basedir, saveDir, self.scanid, self.HVPoint, "efficiency")
                analyzer.loadConfig(cfg, cfg_x, cfg_y)
                analyzer.setVerbose(1)
                
                analyzer.set1DAnalyzers(muonWindowMean_x, muonWindowSigma_x, muonWindowMean_y, muonWindowSigma_y)
                analyzer.efficiency()
                analyzer.stripProfile2D()
                self.cluster_collection_trx, self.cluster_time_collection_trx, self.cluster_barycenter_collection_trx, self.cluster_barycenter_err_collection_trx = analyzer.clusterEvents("x") # contains a list of clusters, for each event

                self.cluster_collection_try, self.cluster_time_collection_try, self.cluster_barycenter_collection_try, self.cluster_barycenter_err_collection_try = analyzer.clusterEvents("y") # contains a list of clusters, for each event

                analyzer.write()
                
                
                
                clusters = copy.deepcopy(self.cluster_collection_trx)
                clusters_time = copy.deepcopy(self.cluster_time_collection_trx)
                barycenters = copy.deepcopy(self.cluster_barycenter_collection_trx)
                barycenters_err = copy.deepcopy(self.cluster_barycenter_err_collection_trx)


                self.analyzers.append(analyzer)
                self.cfgs.append(cfg)
                
                analyzer_tr = analyzer

                
            else:
            
                # get the time windows, assume those have been calculated before, otherwise -1
                jsname = "%s/output.json" % (saveDir)

                # print(jsname)
                if os.path.isfile(jsname):
                
                    with open(jsname) as f_in: analyzerResults = json.load(f_in)
                    analyzerResults = analyzerResults['output_parameters']
                    muonWindowMean = analyzerResults["muonWindowMean"]
                    muonWindowSigma = analyzerResults["muonWindowSigma"]
            
                else:
                
                    muonWindowMean = -1
                    muonWindowSigma = -1
            
                cfg = getattr(self.config, chamberName)
                analyzer = an.Analyzer(self.basedir, saveDir, self.scanid, self.HVPoint, "efficiency")
                analyzer.loadConfig(cfg)
                analyzer.setVerbose(1)
                analyzer.timeProfile(muonWindowMean, muonWindowSigma)
                analyzer.efficiency()
                analyzer.stripProfile(plotNoSpill = False)
                analyzer.timeStripProfile2D()
                analyzer.clusterization("muon")
                analyzer.write()
                
                clusters, clusters_time, barycenters, barycenters_err = analyzer.clusterEvents() # contains a list of clusters, for each event
                
                self.analyzers.append(analyzer)
                self.cfgs.append(cfg)
   
            cluster_collection.append(clusters)
            cluster_time_collection.append(clusters_time)
            cluster_barycenter_collection.append(barycenters)
            cluster_barycenter_err_collection.append(barycenters_err)


            self.nEvents = len(clusters) # depends on TDC config!
                

        # re-map the collections, to have first index on the event number, second index chamber ID, 3th index clusters
        # basically swap the iEv and chamber indices
        for iEv in range(0, self.nEvents):
        
        
            self.cluster_collection.append([])
            self.cluster_time_collection.append([])
            self.cluster_barycenter_collection.append([])
            self.cluster_barycenter_err_collection.append([])
 
            for chamberId in range(0, len(self.chambers)):
            
                self.cluster_collection[iEv].append(cluster_collection[chamberId][iEv])
                self.cluster_time_collection[iEv].append(cluster_time_collection[chamberId][iEv])
                self.cluster_barycenter_collection[iEv].append(cluster_barycenter_collection[chamberId][iEv])
                self.cluster_barycenter_err_collection[iEv].append(cluster_barycenter_err_collection[chamberId][iEv])    


   
    def createTracks(self): # creation of perpendicular tracks = 1D

        self.track_collection = [] # offsets of the barycenters. The track is orthogonal to it
        self.track_collection_xMin = []
        self.track_collection_xMax = []
        
        # loop over all events
        for iEv in range(0, self.nEvents): 
        
            self.iEv = iEv
            self.track_collection.append([]) # append array for track collection for this event
            self.track_collection_xMin.append([])
            self.track_collection_xMax.append([])
            
            startSeeds = self.cluster_barycenter_collection[self.iEv][0] # seeds based on tag chamber (idx=0)
            for i,xi in enumerate(startSeeds): # loop over all seeds and create perpendicular tracks
            
                self.track_collection[iEv].append(xi) # store offsets w.r.t. reference
               
                cluster = self.cluster_collection[iEv][0][i]
                xc_max, xl_max, xr_max = self.analyzers[0].getStripPos("y", max(cluster)) # strip coordinates of right cluster strip
                xc_min, xl_min, xr_min = self.analyzers[0].getStripPos("y", min(cluster)) # strip coordinates of left cluster strip
                
                self.track_collection_xMin[iEv].append(xl_min)
                self.track_collection_xMax[iEv].append(xr_max)
   
    
    def exportTrackingClusters(self):
    
        return self.cluster_collection_trx, self.cluster_time_collection_trx, self.cluster_barycenter_collection_trx, self.cluster_collection_try, self.cluster_time_collection_try, self.cluster_barycenter_collection_try
    
    def exportProbeClusters(self):
    
        return self.cluster_collection, self.cluster_time_collection, self.cluster_barycenter_collection
    
    def mergeClusters(self, clusters):
    
        ret = []
        for c in clusters: ret += c
        return ret
    
    def eventDisplay(self):
    
        outputdir = "%s/eventDisplay/" % (self.outputdir)
        #if os.path.exists(outputdir): shutil.rmtree(outputdir) # delete output dir, if exists
        if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir

        # event display settings
        canvas_margin = 0.05 # 10% margin for borders
        box_margin = 0.05
        
        self.geo_nLayers = len(self.chambers)
        

        z_sf = (1. - 2*canvas_margin - 2.*(1. - 2*canvas_margin)*box_margin) / (self.geo_layer_height*(self.geo_nLayers-1)) # z scale factor to fit in box
        z_ref = canvas_margin + (1. - 2*canvas_margin)*box_margin # reference bottom

        x_ref = z_ref
        x_ref_strips = 0.6
        x_sf = (1. - 2*canvas_margin - 2.*(1. - 2*canvas_margin)*box_margin) / self.geo_layer_width # z scale factor to fit in box
        
     
        # helper functions
        def getZLayer(iLayer):
        
            return (z_ref + (self.geo_nLayers - iLayer)*self.geo_layer_height*z_sf)
            

        # event display
        c = ROOT.TCanvas("c1", "c1", 1000, 1000)
        c.SetLeftMargin(0.12)
        c.SetRightMargin(0.05)
        c.SetTopMargin(0.05)
        c.SetBottomMargin(0.1)


        for iEv in range(0, self.nEvents):
        
            doPlot = True
            if iEv > 50: break
        
            # make rectangle as contours
            box = ROOT.TBox(canvas_margin, canvas_margin, 1-canvas_margin, 1-canvas_margin)
            box.SetFillStyle(0)
            box.SetLineColor(ROOT.kBlack)
            box.SetLineWidth(2)
            box.Draw("SAME")  
            
            # aux plots    
            textLeft = ROOT.TLatex()
            textLeft.SetTextFont(42)
            textLeft.SetTextSize(0.04)
            textLeft.SetNDC()
            textLeft.DrawLatex(canvas_margin, 1-canvas_margin+0.01, self.textHeader)
                
            textRight = ROOT.TLatex()
            textRight.SetNDC()
            textRight.SetTextFont(42)
            textRight.SetTextSize(0.04)
            textRight.SetTextAlign(31)
            textRight.DrawLatex(1.0-canvas_margin, 1-canvas_margin+0.01, "S%d/HV%d/EV%d" % (self.scanid, self.HVPoint, iEv))
           

            # draw layers
            lines = []
            for chamberId, chamberCfg in enumerate(self.chambers):
            
                chamberName = chamberCfg['chamberId']
                if chamberId == 0: nStrips, stripPitch, stripArea, xPos, zPos = self.analyzers[chamberId].getGeometry("y")
                else: nStrips, stripPitch, stripArea, xPos, zPos = self.analyzers[chamberId].getGeometry()
            
                z = getZLayer(zPos)
                line = ROOT.TLine(x_ref, z, 1.-x_ref, z)
                line.SetLineColor(ROOT.kBlack)
                line.SetLineWidth(1)
                line.Draw("SAME")        
                lines.append(line)

                latex = ROOT.TLatex()
                latex.SetNDC()
                latex.SetTextSize(0.02)
                latex.SetTextColor(ROOT.kBlack)
                latex.SetTextAlign(11)
                latex.DrawLatex(x_ref, z+0.005, self.analyzers[chamberId].chamberName)
                
                
            # draw strips
            strips = {}
            points = {}
            for chamberId, chamberCfg in enumerate(self.chambers):
            
                chamberName = chamberCfg['chamberId']
                if chamberId == 0: nStrips, stripPitch, stripArea, xPos, zPos = self.analyzers[chamberId].getGeometry("y")
                else: nStrips, stripPitch, stripArea, xPos, zPos = self.analyzers[chamberId].getGeometry()
           
            
                strips[chamberName] = []
                points[chamberName] = []
                
                z = getZLayer(zPos)
                stripWidth = 0.8*stripPitch
                
                clusters = self.cluster_collection[iEv][chamberId]
                cluster_barycenters = self.cluster_barycenter_collection[iEv][chamberId]
                mergedClusters = self.mergeClusters(clusters)
                
                # highlight the strips
                for nStrip in range(1, nStrips+1):
                
                    tmp = stripPitch*(nStrip-1)
                    x0 = x_ref_strips + x_sf*(xPos + tmp)
                    x1 = x_ref_strips + x_sf*(xPos + tmp + stripWidth)
                    strip = ROOT.TLine(x0, z, x1, z)
                    strip.SetLineColor(ROOT.kBlue)
                    if nStrip in mergedClusters: strip.SetLineColor(ROOT.kRed)
                    strip.SetLineWidth(4)
                    strip.Draw("SAME")
                    strips[chamberName].append(strip)
                
                
                # plot the barycenters (cross check)
                if chamberId == 0 and len(cluster_barycenters) == 0:  doPlot = False
                for bary in cluster_barycenters:
                
                    point = ROOT.TMarker(x_ref_strips + x_sf*bary, z, 20)
                    point.Draw("SAME")
                    points[chamberName].append(point)
                    

            for k,track in enumerate(self.track_collection[iEv]):
            
                z0 = 0 # bottom layer
                z1 = (self.geo_layer_height*(self.geo_nLayers-1)) # top layer
                
                x0 = track
                x1 = track

                line = ROOT.TLine(x_ref_strips + x_sf*x0, z_ref+z_sf*z0, x_ref_strips + x_sf*x1, z_ref+z_sf*z1)
                line.SetLineColor(ROOT.kRed)
                line.SetLineWidth(3)
                line.Draw("SAME")        
                lines.append(line)
            
                params = ROOT.TLatex()
                params.SetTextFont(42)
                params.SetTextSize(0.03)
                params.SetNDC()

     

            if doPlot: c.SaveAs("%s/event_%d.png" % (outputdir, iEv))
            c.Clear()
         
         
    def efficiency(self, stripClusterTolerance = 1):
        '''
        Calculate efficiency of all test chambers
        '''
        
        # book histograms for residuals (units in cm)
        h_res = []
        for chamberId, chamberName in enumerate(self.chambers):
            h = ROOT.TH1D(chamberName, chamberName, 100, -10, 10)
            h_res.append(h)
        
        self.stripClusterTolerance = stripClusterTolerance
        
        nTrig = 0
        nHits = [] # number of hits for each test chamber
        nHits_muon = [] # raw number of hits, no tracking requirement
        for chamberId, chamberCfg in enumerate(self.chambers):

            nHits.append(0)
            nHits_muon.append(0)
        
        for iEv in range(0, self.nEvents):
        
 
            if len(self.track_collection[iEv]) == 0: continue
            if len(self.track_collection[iEv]) != 1: continue # require one candidate track/hit in tagging chamber
            if len(self.cluster_collection[iEv][0][0]) > 4: continue # MAX cls 4 for tracking chambers

            
            track = self.track_collection[iEv][0] # in this case it is just an offset

            nTrig += 1
            
            # loop over all probe chambers
            for chamberId, chamberName in enumerate(self.chambers):
            
                if chamberId == 0: nStrips, stripPitch, stripArea, xPos, zPos = self.analyzers[chamberId].getGeometry("y")
                else: nStrips, stripPitch, stripArea, xPos, zPos = self.analyzers[chamberId].getGeometry()
        
                
                # extrapolated hit
                x_tag = track
                
                # look for hits on the plane
                clusters = self.cluster_collection[iEv][chamberId]
                
                if len(clusters) > 0: nHits_muon[chamberId] += 1 # raw efficiency means all hits on the plane

                hitFound = False
                res = -1
                for icl, cluster in enumerate(clusters):
                
                    if chamberId == 0:
                        xc_max, xl_max, xr_max = self.analyzers[chamberId].getStripPos("y", max(cluster)+stripClusterTolerance) # strip coordinates of right cluster strip
                        xc_min, xl_min, xr_min = self.analyzers[chamberId].getStripPos("y", min(cluster)-stripClusterTolerance) # strip coordinates of left cluster strip
                    else:
                        xc_max, xl_max, xr_max = self.analyzers[chamberId].getStripPos(max(cluster)+stripClusterTolerance) # strip coordinates of right cluster strip
                        xc_min, xl_min, xr_min = self.analyzers[chamberId].getStripPos(min(cluster)-stripClusterTolerance) # strip coordinates of left cluster strip
                    
                    
                    
                    if (xl_min < self.track_collection_xMax[iEv][0] and xr_max > self.track_collection_xMin[iEv][0]):
                    #if x_tag > xl_min and x_tag < xr_max:
                        hitFound = True
                        res = x_tag - self.cluster_barycenter_collection[iEv][chamberId][icl]
                        h_res[chamberId].Fill(res)
                        # calculate residuals from barycenters
                        break
             

                if hitFound: nHits[chamberId] += 1
                #else: print("NO HIT", iEv)
                
                if not hitFound:
                
                    for icl, cluster in enumerate(clusters):
                    
                        if chamberId == 0:
                            xc_max, xl_max, xr_max = self.analyzers[chamberId].getStripPos("y", max(cluster)+stripClusterTolerance) # strip coordinates of right cluster strip
                            xc_min, xl_min, xr_min = self.analyzers[chamberId].getStripPos("y", min(cluster)-stripClusterTolerance) # strip coordinates of left cluster strip
                        else:
                            xc_max, xl_max, xr_max = self.analyzers[chamberId].getStripPos(max(cluster)+stripClusterTolerance) # strip coordinates of right cluster strip
                            xc_min, xl_min, xr_min = self.analyzers[chamberId].getStripPos(min(cluster)-stripClusterTolerance) # strip coordinates of left cluster strip
                        
                        #if chamberId == 1:
                        
                        #    print(iEv,xl_min, xr_max, x_tag, self.track_collection_xMin[iEv][0], self.track_collection_xMax[iEv][0])
                
                


        c1 = ROOT.TCanvas("c1_residuals", "c1_residuals", 800, 800)
        c1.SetLeftMargin(0.12)
        c1.SetRightMargin(0.05)
        c1.SetTopMargin(0.05)
        c1.SetBottomMargin(0.1)
        
        for chamberId, chamberCfg in enumerate(self.chambers):
            #if chamberCfg['type'] != "test": continue
            
            efficiency_muon = 1.*nHits_muon[chamberId]/nTrig
            efficiency_tracking = 1.*nHits[chamberId]/nTrig
            
            efficiency_muon_err = math.sqrt(efficiency_muon*(1.0-efficiency_muon)/nTrig)
            efficiency_tracking_err = math.sqrt(efficiency_tracking*(1.0-efficiency_tracking)/nTrig)
            
            print("Chamber %s" % chamberName)
            print(" - muon efficiency      %.2f %%" % (100.*efficiency_muon))
            print(" - tracking efficiency  %.2f %%" % (100.*efficiency_tracking))
            
            

            self.param_output[chamberName] = {}
            self.param_output[chamberName]['efficiency_muon'] = efficiency_muon
            self.param_output[chamberName]['efficiency_tracking'] = efficiency_tracking
            self.param_output[chamberName]['efficiency_muon_err'] = efficiency_muon_err
            self.param_output[chamberName]['efficiency_tracking_err'] = efficiency_tracking_err
            
            # plot residuals
            c1.cd()
            c1.Clear()

            #if(h_res[chamberId].Integral() > 0): h_res[chamberId].Scale(1./h_res[chamberId].Integral())
            h_res[chamberId].GetYaxis().SetNoExponent()
            h_res[chamberId].SetLineColor(ROOT.kBlue)
            h_res[chamberId].SetLineWidth(2)
            h_res[chamberId].Draw("HIST")
        
            h_res[chamberId].GetYaxis().SetRangeUser(0, 1.3*h_res[chamberId].GetMaximum())
            h_res[chamberId].GetXaxis().SetTitle("Hit-Track residual (cm)")
            h_res[chamberId].GetXaxis().SetTitleOffset(1.2)
            h_res[chamberId].GetXaxis().SetLabelOffset(0.005)
            h_res[chamberId].GetXaxis().SetLabelSize(0.04)

            h_res[chamberId].GetYaxis().SetTitle("Events")   
            h_res[chamberId].GetYaxis().SetTitleOffset(1.8)
            h_res[chamberId].GetYaxis().SetLabelOffset(0.005)
            
            resFit = ROOT.TF1("resFit", "gaus", -10, 10)
            resFit.SetParameters(h_res[chamberId].Integral(), 0, h_res[chamberId].GetRMS())
            h_res[chamberId].Fit("resFit", "WR", "", -10, 10) # W: ignore empty bins
            
            resFit.SetLineColor(ROOT.kRed)
            resFit.GetXaxis().SetRangeUser(-10, 10)
            resFit.SetLineWidth(2)
            resFit.Draw("L SAME")
        
            tLatex = ROOT.TLatex()
            tLatex.SetTextFont(42)
            tLatex.SetTextSize(0.03)
            tLatex.SetNDC()
            tLatex.DrawLatex(0.16, 0.9, "#bf{%s}" % self.cfgs[chamberId]['chamberName'])
            tLatex.DrawLatex(0.16, 0.85, "Residual mean/RMS: %.2f/%.2f" % (h_res[chamberId].GetMean(), h_res[chamberId].GetRMS()))
            tLatex.DrawLatex(0.16, 0.80, "Fit mean/#sigma: %.2f/%.2f" % (resFit.GetParameter(1), resFit.GetParameter(2)))
            
            self.param_output[chamberName]['residual_mean'] = h_res[chamberId].GetMean()
            self.param_output[chamberName]['residual_rms'] = h_res[chamberId].GetRMS()
            self.param_output[chamberName]['residual_mean_fit'] = resFit.GetParameter(1)
            self.param_output[chamberName]['residual_sigma_fit'] = resFit.GetParameter(2)

            # aux plots    
            textLeft = ROOT.TLatex()
            textLeft.SetTextFont(42)
            textLeft.SetTextSize(0.04)
            textLeft.SetNDC()
            textLeft.DrawLatex(c1.GetLeftMargin(), 0.96, self.textHeader)
                
            textRight = ROOT.TLatex()
            textRight.SetNDC()
            textRight.SetTextFont(42)
            textRight.SetTextSize(0.04)
            textRight.SetTextAlign(31)
            textRight.DrawLatex(1.0-c1.GetRightMargin(), 0.96, "S%d/HV%d" % (self.scanid, self.HVPoint))

            c1.RedrawAxis()
            c1.Modify()
            c1.SaveAs("%s/%s_residual.png" % (self.outputdir, chamberName))
            c1.SaveAs("%s/%s_residual.pdf" % (self.outputdir, chamberName))
   
                
    def generateBackground(self, bkg_poiss_mean):
    
        self.generateRandom = True
        self.bkg_poiss_mean = bkg_poiss_mean
        

    def calculateBackground(self):
    
        nHits_bkg = [] # 
        for chamberId, chamberName in enumerate(self.chambers): nHits_bkg.append(0)
        
        for iEv in range(0, self.nEvents):
       
            for chamberId, chamberCfg in enumerate(self.chambers):
                chamberName = chamberCfg['chamberId']
            
                clusters = self.cluster_collection_bkg[iEv][chamberId]
                nHits_bkg[chamberId] += len(clusters) # each cluster is a single hiy
                #if len(clusters) > 0: 
                #    print(iEv, chamberId, clusters)
    
        print("##############################################")  
        print("Background simulation statistics")    
        print("Total number of triggers %d" % self.nEvents)
        for chamberId, chamberCfg in enumerate(self.chambers):
            chamberName = chamberCfg['chamberId']
        
            print("Chamber %s   %d hits" % (chamberName, nHits_bkg[chamberId]))
                
    
    def write(self):
    
        
        out = {}
        
        param_input = {
        
            "dR"                            : self.dR,
            "stripClusterTolerance"         : self.stripClusterTolerance,
            "cluster_barycenter_algo"       : self.cluster_barycenter_algo,
            "bkg_poiss_mean"                : self.bkg_poiss_mean,
            
            
            "scanid"                        : self.scanid,
            "HVPoint"                       : self.HVPoint,
        }
        
        data = {
        
            "input_parameters"          :  param_input, 
            "output_parameters"         :  self.param_output, 
        }
    
        with open("%s/output.json" % (self.outputdir), 'w') as fp: json.dump(data, fp, indent=4)
        
    
        
    
    
    
if __name__ == "__main__":

    doCalculate = True
    tagChamber = config.KODEL_TRACKING
    probeChambers = [config.KODELC]

    scanid = int(sys.argv[1])
    tag = "KODEL_TRACKING_1D"
    basedir = "/var/webdcs/HVSCAN/%06d/" % scanid
    
    textHeader = "#bf{GIF++} #scale[0.75]{ #it{Work in progress}}"
    
    ROOT.gErrorIgnoreLevel = ROOT.kWarning # suppress info messages
    
    
    CAEN_files = glob.glob("%s/Scan%06d_HV*_CAEN.root" % (basedir, scanid))
    if len(CAEN_files) == 0: sys.exit("No CAEN ROOT files in directory") 
    CAEN_files.sort(key=functions.natural_keys) # sort on file name, i.e. according to HV points

    outputdir = "%s/ANALYSIS/%s/" % (basedir, tag)
    #if os.path.exists(outputdir): shutil.rmtree(outputdir) # delete output dir, if exists
    if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir
    

    # prepare TGraphs
    graphs = {}
    HVeff = {}
    out = {}
    for chamberId, chamberCfg in enumerate(probeChambers):
        
        ch = chamberCfg['chamberId']
        HVeff[ch] = []
        graphs['g_ntracks_'+ch] = ROOT.TGraph()
        graphs['g_eff_muon_'+ch] = ROOT.TGraphErrors()
        graphs['g_eff_tracking_'+ch] = ROOT.TGraphErrors()
        out[chamberCfg['chamberId']] = {}
    
    for gr in graphs:
        graphs[gr].SetLineWidth(2)
        graphs[gr].SetLineColor(ROOT.kBlue)
        graphs[gr].SetMarkerStyle(20)
        graphs[gr].SetMarkerColor(ROOT.kBlue)


    # get all ROOT files in the dir
    j = 0
    for i,CAENFile in enumerate(CAEN_files):
        
        
        HVPoint_ = int(os.path.basename(CAENFile).split("_")[1][2:])
        print("Analyze HV point %d " % HVPoint_)
   
        #if HVPoint_ != 6: continue

        saveDir = outputdir + "HV%d/" % HVPoint_
        if not os.path.exists(saveDir): os.makedirs(saveDir)

        if doCalculate:
        
            if not os.path.exists("%s/HV%d/output.json" % (outputdir, HVPoint_)) or True:
                tr = RPCTracking1D(basedir, saveDir, scanid, HVPoint_, config, textHeader)
                tr.setTagChamber(tagChamber) # first the tagging chamber!
                for chamber in probeChambers: tr.addProbeChamber(chamber)
                tr.collectClusters()
                tr.createTracks()
                tr.eventDisplay()
                tr.efficiency(1) # infinite tolerance
                tr.write()
                del tr
    
        
        # load analyzer results
        with open("%s/HV%d/output.json" % (outputdir, HVPoint_)) as f_in: analyzerResults = json.load(f_in)
        analyzerResults = analyzerResults['output_parameters']
        
        CAEN = ROOT.TFile(CAENFile)
        for chamberId, chamberCfg in enumerate(probeChambers):
            
            ch = chamberCfg['chamberId']
            out[ch]["HV%d" % HVPoint_] = {}
            
            # load CAEN for HV
            HVeff_ = -999 # SG mode: HV can be low, so search for the max HV
            for k,gap in enumerate(chamberCfg['gapIds']):
            
                imon = CAEN.Get("Imon_%s" % gap).GetMean()
                imon_err = CAEN.Get("Imon_%s" % gap).GetStdDev()
                hv_ = CAEN.Get("HVeff_%s" % gap).GetMean()
                if hv_ > HVeff_: HVeff_ = hv_
                
                out[ch]["HV%d" % HVPoint_]["imon_%s" % gap] = imon
                out[ch]["HV%d" % HVPoint_]["imon_err_%s" % gap] = imon_err
                out[ch]["HV%d" % HVPoint_]["hveff_%s" % gap] = hv_
                
                

            HVeff[ch].append(HVeff_)            
            
            graphs['g_eff_muon_'+ch].SetPoint(j, HVeff_, 100.*analyzerResults[ch]['efficiency_muon'])
            graphs['g_eff_tracking_'+ch].SetPoint(j, HVeff_, 100.*analyzerResults[ch]['efficiency_tracking'])
            
            graphs['g_eff_muon_'+ch].SetPointError(j, 0, 100.*analyzerResults[ch]['efficiency_muon_err'])
            graphs['g_eff_tracking_'+ch].SetPointError(j, 0, 100.*analyzerResults[ch]['efficiency_tracking_err'])
            
            out[ch]["HV%d" % HVPoint_]['efficiencyMuon'] = 100.*analyzerResults[ch]['efficiency_muon']
            out[ch]["HV%d" % HVPoint_]['efficiencyTracking'] = 100.*analyzerResults[ch]['efficiency_tracking']
            out[ch]["HV%d" % HVPoint_]['efficiencyMuon_err'] = 100.*analyzerResults[ch]['efficiency_muon_err']
            out[ch]["HV%d" % HVPoint_]['efficiencyTracking_err'] = 100.*analyzerResults[ch]['efficiency_tracking_err']
        
        CAEN.Close()  
        
        j += 1

    c = ROOT.TCanvas("c1", "c1", 800, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.1)
        
    params = ROOT.TLatex()
    params.SetTextFont(42)
    params.SetTextSize(0.03)
    params.SetNDC()

    
   

    for chamberId, chamberCfg in enumerate(probeChambers):
            
        ch = chamberCfg['chamberId']
    
        xMin_ = min(HVeff[ch])
        xMax_ = max(HVeff[ch])
        
        ############################
        # tracking efficiency + fit
        ############################  
        c.Clear()
        g = graphs['g_eff_tracking_'+ch]
        dummy = functions.dummyHist("HV_{eff} (V)", "Tracking efficiency (%)", xMin_, xMax_, 0, 100)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        fitted_tracking, emax_tracking, lam_tracking, hv50_tracking, WP_tracking, emax_err_tracking, lam_err_tracking, hv50_err_tracking, WP_err_tracking = functions.sigmoidFit(chamberCfg, g)
        
        out[ch]["emax_tracking"] = emax_tracking
        out[ch]["lam_tracking"] = lam_tracking
        out[ch]["hv50_tracking"] = hv50_tracking
        out[ch]["WP_tracking"] = WP_tracking
        out[ch]["emax_err_tracking"] = emax_err_tracking
        out[ch]["lam_err_tracking"] = lam_err_tracking
        out[ch]["hv50_err_tracking"] = hv50_err_tracking
        out[ch]["WP_err_tracking"] = WP_err_tracking
        out[ch]["eff_WP_tracking"] = fitted_tracking.Eval(WP_tracking)

        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.035)
        latex.SetTextColor(1)
        latex.SetTextAlign(13)
        latex.DrawLatex(0.6, 0.5, "#epsilon_{max} = %.1f %%" % (emax_tracking))
        latex.DrawLatex(0.6, 0.45, "#lambda = %.3f" % lam_tracking)
        latex.DrawLatex(0.6, 0.4, "HV_{50%%} = %.1f V" % hv50_tracking)
        latex.DrawLatex(0.6, 0.35, "WP = %.1f V" % WP_tracking)
        latex.DrawLatex(0.6, 0.3, "eff(WP) = %.1f %%" % (fitted_tracking.Eval(WP_tracking)))
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % chamberCfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Tracking efficiency")
        functions.drawAux(c, textHeader, "S%d" % (scanid))
        c.SaveAs("%s/%s_efficiency_tracking.png" % (outputdir, ch))
        c.SaveAs("%s/%s_efficiency_tracking.pdf" % (outputdir, ch))
        
        
        
    
        ############################
        # muon efficiency + fit
        ############################    
        c.Clear()
        g = graphs['g_eff_muon_'+ch]
        dummy = functions.dummyHist("HV_{eff} (V)", "Muon efficiency (%)", xMin_, xMax_, 0, 100)
        dummy.Draw("HIST")
        g.Draw("SAME LP")
        
        fitted_muon, emax_muon, lam_muon, hv50_muon, WP_muon, emax_err_muon, lam_err_muon, hv50_err_muon, WP_err_muon = functions.sigmoidFit(chamberCfg, g)

        out[ch]["emax_muon"] = emax_muon
        out[ch]["lam_muon"] = lam_muon
        out[ch]["hv50_muon"] = hv50_muon
        out[ch]["WP_muon"] = WP_muon
        out[ch]["emax_err_muon"] = emax_err_muon
        out[ch]["lam_err_muon"] = lam_err_muon
        out[ch]["hv50_err_muon"] = hv50_err_muon
        out[ch]["WP_err_muon"] = WP_err_muon
        out[ch]["eff_WP_muon"] = fitted_muon.Eval(WP_muon)
        
        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.035)
        latex.SetTextColor(1)
        latex.SetTextAlign(13)
        latex.DrawLatex(0.6, 0.5, "#epsilon_{max} = %.1f %%" % (emax_muon))
        latex.DrawLatex(0.6, 0.45, "#lambda = %.3f" % lam_muon)
        latex.DrawLatex(0.6, 0.4, "HV_{50%%} = %.1f V" % hv50_muon)
        latex.DrawLatex(0.6, 0.35, "WP = %.1f V" % WP_muon)
        latex.DrawLatex(0.6, 0.3, "eff(WP) = %.1f %%" % (fitted_muon.Eval(WP_muon)))
        
        params.DrawLatex(0.16, 0.9, "#bf{%s}" % chamberCfg['chamberName'])
        params.DrawLatex(0.16, 0.85, "Muon efficiency")
        functions.drawAux(c, textHeader, "S%d" % (scanid))
        c.SaveAs("%s/%s_efficiency_muon.png" % (outputdir, ch))
        c.SaveAs("%s/%s_efficiency_muon.pdf" % (outputdir, ch))
        
        
        # write results to file
        with open("%s/output_%s.json" % (outputdir, ch), 'w') as fp: json.dump(out[ch], fp, indent=4)
        
        
        
  