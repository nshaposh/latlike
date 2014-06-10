import pyfits
import subprocess as sp
import threading
import time
import string
#from psfcor import arfcreate
from GtApp import *

evbin = GtApp('gtbin')
gtrsp = GtApp('gtrspgen')
gtpsf = GtApp('gtpsf')
gtcube = GtApp('gtltcube')
gtexp =  GtApp('gtexposure')
gtselect = GtApp('gtselect')
mktime = GtApp('gtmktime')


class like_thread():

    def __init__(self,evfile,scfile,sra,sdec,rad,bra,bdec,brad,
            cube,tbin = 86400,irfs = "P7REP_SOURCE_V15",
            tstart="INDEF",tstop="INDEF",emin=100.0,
            emax=300000.0,enbin=20,outfile='like.xml',
            dcostheta=0.05,thetamax=60.0,binsz=1.0,zmax=100.0,
            logfile="latlike.log",logqueue = None):
        self.srad = rad
        self.brad = brad

        self.logqueue = logqueue


        self.thread = threading.Thread(target=self.run,args=(
                evfile,scfile,sra,sdec,rad,bra,bdec,brad,
                cube,tbin,irfs,tstart,tstop,emin,
                emax,enbin,outfile,
                dcostheta,thetamax,binsz,zmax,
                logfile))

        self.state = "not_run_yet"


    
    def start(self):
        """Starts the likelihood"""
        
        self.thread.start()
        self.state = "running"


    def putlog(self,s):


        if not self.logqueue == None:
#            print s
            self.logqueue.put("Likelihood ("+time.ctime()+"):\n"+s)
            


    def stop(self):
        """Stops likelihood calculation"""
        self.state = "stop"


    def run(self,evfile,scfile,sra,sdec,rad,bra,bdec,brad,
            cube,tbin,irfs,tstart,tstop,emin,
            emax,enbin,outfile,
            dcostheta,thetamax,binsz,zmax,
            pl_index,index_free,logfile):
        
        
        ''' Given the LAT dat event file (evfile), source and background regions,
        Generates a full flux curve using xspec fits for every interval. 
        

        Parameters:
        
        evfile  - observation event file, create with gtmktime
        scfile  - observation house keeping file
        outfile [like.xml] - output lightcurve FITS file
        tbin [86400]    - final flux curve time binnig (sec).
        tstart [INDEF]  - start time (MET sec). If INDEF the value is taken from the evfile.
        tstop  [INDEF] - start time (MET sec). If INDEF the value is taken from the evfile.
        emin [100.0]   - lower energy limit of the energy interval (MeV). 
        emin [300000.0]   - upper energy of the energy interval (MeV). 
        enbin [20]   - number of the energy bins to use in xspec fits.
        cube    - the galactic cube file. If not given or does not exist - it will be 
        calculated (takes a long time!!!). 
        binsz [1.0], zmax [100.0]   - corresponding gtltcube parameters if a cube is to be calculated. 
        thetamax [60.0],dcostheta [0.05] - corresponding parameters for psf and response calculations.
        See gtpsf,gtrspgen help for details.
        
        ''' 
   
        logf  = open(logfile,"w")
        res_str = ""
        
# Nothing here yet

        logf.close()
        
        if self.state == "running": self.state = "done"
        if self.state == "stop": self.state = "stopped"

#    End of run() for likelihood thread
#    End of the likelihood thread


# start of the cmap thread


class cmap3d_thread():

    def __init__(self,evfile,scfile,ra,dec,
            tstart,tstop,emin=100.0,
            emax=300000.0,enbin=20,outfile='like.xml',
            dcostheta=0.05,thetamax=60.0,binsz=0.2,zmax=100.0,
            logqueue = None):
        self.srad = rad
        self.brad = brad

        self.logqueue = logqueue


        self.thread = threading.Thread(target=self.run,args=(
                evfile,scfile,ra,dec,rad,
                tstart,tstop,emin,
                emax,enbin,outfile,
                dcostheta,thetamax,binsz,zmax,
                logfile))

        self.state = "not_run_yet"


    
    def start(self):
        """Starts the likelihood"""
        
        self.thread.start()
        self.state = "running"


    def putlog(self,s):


        if not self.logqueue == None:
#            print s
            self.logqueue.put("Likelihood ("+time.ctime()+"):\n"+s)
            


    def stop(self):
        """Stops likelihood calculation"""
        self.state = "stop"


    def run(self,evfile,scfile,ra,dec,rad,
            tstart,tstop,emin,
            emax,enbin,outfile,
            dcostheta,thetamax,binsz,zmax,
            pl_index,index_free):
        
        
        ''' Given the LAT dat event file (evfile), source and background regions,
        Generates a full flux curve using xspec fits for every interval. 
        

        Parameters:
        
        evfile  - observation event file, create with gtmktime
        scfile  - observation house keeping file
        outfile [like.xml] - output lightcurve FITS file
        tbin [86400]    - final flux curve time binnig (sec).
        tstart [INDEF]  - start time (MET sec). If INDEF the value is taken from the evfile.
        tstop  [INDEF] - start time (MET sec). If INDEF the value is taken from the evfile.
        emin [100.0]   - lower energy limit of the energy interval (MeV). 
        emin [300000.0]   - upper energy of the energy interval (MeV). 
        enbin [20]   - number of the energy bins to use in xspec fits.
        cube    - the galactic cube file. If not given or does not exist - it will be 
        calculated (takes a long time!!!). 
        binsz [1.0], zmax [100.0]   - corresponding gtltcube parameters if a cube is to be calculated. 
        thetamax [60.0],dcostheta [0.05] - corresponding parameters for psf and response calculations.
        See gtpsf,gtrspgen help for details.
        
        ''' 
   
        logf  = open(logfile,"w")
        res_str = ""
        npics = int(rad/binzs)
        process = subprocess.Popen(["gtbin","algorithm=CCUBE","ebinalg=LOG",
                                    "scfile=NONE",
                                    "evfile="+evfile,
                                    "outfile="+outfile,
                                    "tstart="+str(tstart),
                                    "tstop="+str(tstop),
                                    "emin="+str(emin),
                                    "emax="+str(emax),
                                    "nxpix="+str(npics),"nypix="+str(npics),
                                    "binsz="+str(binsz),"xref="+str(ra),
                                    "yref="+str(dec),"axisrot=0.0",
                                    "proj=SGT","coordsys=CEL",
                                    "chatter="+str(chatter)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    

#       except:
        catchError = "at the top level:"
        for line in process.stdout:
            self.putlog("CCUBE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        for line in process.stderr:
            self.putlog("CCUBE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        
        if (gtbinerr):
            self.putlog("ERROR DURING GTBIN EXECUTION!!!!")
            self.analysis.image = "None"
        

        
# Nothing here yet

        logf.close()
        
        if self.state == "running": self.state = "done"
        if self.state == "stop": self.state = "stopped"

#    End of run() for likelihood thread
#    End of the likelihood thread


# start of the cmap thread


class filter_thread():

    def __init__(self,flist,scfile,outfile,obj_ra,obj_dec,roi_deg,tmin,tmax,emin,emax,zmax,
            logqueue = None):

        self.logqueue = logqueue

        self.thread = threading.Thread(target=self.run,args=(flist,scfile,outfile,
                                             obj_ra,obj_dec,roi_deg,tmin,tmax,emin,emax,zmax))

        self.state = "not_run_yet"
        self.out = ""

    
    def start(self):
        """Starts filtering """
        
        self.thread.start()
        self.state = "running"


    def putlog(self,s):


        if not self.logqueue == None:
#            print s
            self.logqueue.put("Filtering: ("+time.ctime()+"):\n"+s)


    def stop(self):
        """Stops filtering """
        import time
        self.state = "stop"
        self.out += "Filter thread: stop requested!\n"

        try:
            self.proc.terminate()
            time.sleep(0.5)
            proc_poll = self.proc.poll()
            while proc_poll == None:
#                time.sleep(0.5)
                os.kill(self.proc.pid(),0)
                proc_poll = self.proc.poll()
        
#                self.putlog("killing filter"+proc_poll)
        except:
            pass
        else:
            self.state = "stopped"


    def run(self,flist,scfile,outfile,obj_ra,obj_dec,roi_deg,tmin,tmax,emin,emax,zmax):
        import time

        pid = str(os.getpid())
        try:
            os.system('rm -f '+outfile)
            os.system('rm -f '+pid+'_filtered.fits')
        except:
            pass
        
        if self.state != "stop":

#            self.putlog("****Runnig GTSELECT****:")
            self.putlog(string.join(["gtselect",'infile=@'+flist,
                                          "outfile="+pid+"_filtered.fits",
                                          "ra="+str(obj_ra),"dec="+str(obj_dec),
                                          "rad="+str(roi_deg),
                                          "tmax="+str(tmax),"tmin="+str(tmin),
                                          "emax="+str(emax),"emin="+str(emin),
                                          "zmax="+str(zmax)," chatter=4"]," "))
            catchError = "at the top level:"
            gterr = False
            self.proc = subprocess.Popen(["gtselect","evclass=2",'infile=@'+flist,
                                          "outfile="+pid+"_filtered.fits",
                                          "ra="+str(obj_ra),"dec="+str(obj_dec),
                                          "rad="+str(roi_deg),
                                          "tmax="+str(tmax),"tmin="+str(tmin),
                                          "emax="+str(emax),"emin="+str(emin),
                                          "zmax="+str(zmax),"chatter=4"],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
            for line in self.proc.stdout:
                self.putlog("GTSELECT: "+line)
                if line.find(catchError) != -1:
                    gterr = True

            for line in self.proc.stderr:
                self.putlog("GTSELECT: "+line)
                if line.find(catchError) != -1:
                    gterr = True

        if gterr:

            self.putlog("Filter: GTSELECT error! Exiting...")
            self.out += "Filter: GTSELECT error!"
            self.state = "stop"

        if self.state != "stop":

            filter_string = "DATA_QUAL==1&&LAT_CONFIG==1&&ABS(ROCK_ANGLE)<52"                                    

            mktime["scfile"]=scfile
            mktime["filter"] = filter_string
            mktime["evfile"] = pid+'_filtered.fits'
            mktime["outfile"] = outfile
            mktime["chatter"] = 4

            self.putlog(string.join(["gtmktime","scfile="+scfile,
                                          "filter="+filter_string,
                                          "evfile="+pid+'_filtered.fits',
                                          "outfile="+outfile,"chatter=4"]," "))
            mktimeerr = False
            self.proc = subprocess.Popen(["gtmktime","scfile="+scfile,
                                          "filter="+filter_string,
                                          "roicut=yes",
                                          "evfile="+pid+'_filtered.fits',
                                          "outfile="+outfile,"chatter=4"],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            for line in self.proc.stdout:
                self.putlog("GTMKTIME: "+line)
                if line.find(catchError) != -1:
                    mktimeerr = True            

            for line in self.proc.stderr:
                self.putlog("GTMKTIME: "+line)
                if line.find(catchError) != -1:
                    mktimeerr = True            


            if mktimeerr:
                
                self.putlog("Filter: GTMKTIME error! Exiting...")
                self.out += "Filter: GTMKTIME error!"
                self.state = "stop"



        if self.state == "stop":

            self.state = "stopped"
            self.putlog("Stopped.")
            return
        
        if self.state == "running":

            self.state = "done"
            self.putlog("Done")
#            self.out += "Filter thread: Done." 
            return


