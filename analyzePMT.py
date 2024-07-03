
import sys, os, glob, shutil, json, math, re, random
import ROOT
import analyzerPMT as an
import config 

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)',text) ]





if __name__ == "__main__":

    scanid = int(sys.argv[1])
    chamber = sys.argv[2]

    ## tag: all the plots and results will be saved in a directory with its tagname
    tag = sys.argv[2]
    
    try:
        cfg = getattr(config, tag)
    except:
        sys.exit("Tag %s not found in config file" % tag)
    
    
    ## dir: ROOT directory of all raw data files 
    dir = "/var/webdcs/HVSCAN/%06d/" % scanid
    

    
    
    ##############################################################################################
    outputdir = "%s/ANALYSIS/%s/" % (dir, tag)
    #if os.path.exists(outputdir): shutil.rmtree(outputdir) # delete output dir, if exists
    if not os.path.exists(outputdir):os.makedirs(outputdir) # make output dir
    

    

    
    # get the scan ID from the ROOT file
    files = glob.glob("%s/*CAEN.root" % dir)
    if len(files) == 0: sys.exit("No ROOT files in directory") 
    scanid = int(re.findall(r'\d+', files[0])[0])
    
    # get all ROOT files in the dir
    files.sort(key=natural_keys) # sort on file name, i.e. according to HV points
    for i,CAENFile in enumerate(files):
        
        HVPoint = int(os.path.basename(CAENFile).split("_")[1][2:])
        print("Analyze HV point %d " % HVPoint)
        
        
        saveDir = outputdir + "HV%d/" % HVPoint
        if not os.path.exists(saveDir): os.makedirs(saveDir)

        
        analyzer = an.Analyzer(dir, saveDir, scanid, HVPoint, "efficiency")
        analyzer.loadConfig(cfg)
        analyzer.setVerbose(1)
        #analyzer.timeProfile(370, 10)
        analyzer.timeProfile() # w/o arguments the peakMean/peakWidth are determined by Gaussian fit
        analyzer.timeStripProfile2D()
        analyzer.stripProfile()
        #analyzer.eventDisplay(50) # args: amount of events to be plotted (randomly). -1: all events
        analyzer.write() # write all results to JSON file
        
        

