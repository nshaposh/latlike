#!/usr/bin/env python

""" 

       Fermi LAT Likelihood GUI (version 0.1.1)

The Latlike is a graphical interactive analysis tool designed for
likelihood analysis of the Fermi/LAT (http://fermi.gsfc.nasa.gov/ssc).
The tool is integrated with Fermi Science Tools, FTOOLS, Xspec and 
DS9 imaging tool (hea-www.harvard.edu/RD/ds9) to provide
fast and convenient analysis steps from LAT server data to 
likelihood analysis.


> latlike

To get help on parameters:

> latlike -h

"""

__author__ = 'Nikolai Shaposhnikov'
__version__ = '1.0'

import sys
import os
from numpy import sort,array,floor,log10
from coorconv import sdist


class LatLike:


    """This is the base class for Latspec application. It is 
    created and passed into LatSpecApp class, which runs GUI.

    will create an object called latSpec with the <basename> of
    'latspec' and will read in all of the options from the resource
    file. Reads the data in the current directory and initialises
    oll variables decribing the data. Then it is passed to 
    LatspecApp.
    """

    def __init__(self,basename='latlike',
                 tmin = "INDEF",
                 tmax = "INDEF",
                 zmax = 100.0,
#                 irfs = "P7REP_SOURCE_V15",
                 irfs = "P7SOURCE_V6",
                 flux_tres = 5.0e-9,
                 verbosity = 4,
                 catalog = '',
                 datapath=''):
        
        
        self.havedata = False
        self.basename = basename
        self.tmin = tmin
        self.tmax = tmax
        self.emin = 100.0
        self.emax = 300000.0
        self.zmax = zmax
        self.binsz = 0.2
        self.fluxTres = flux_tres
        self.dist_tres = 0.5
        self.irfs = irfs
        self.catalog = catalog
        self.haveCatalog = False
        self.thetacut = 60.0
        self.eventclass = int(2)
        self.dcostheta = 0.05
        self.chatter = verbosity
        self.ltcube = "None"
        self.cmap = "None"
        self.expcube = "None"
        self.srcmap = "None"
        self.model_file =  self.basename+'_model.xml'
        self.datapath = os.getcwd()
        self.datapath = datapath
        self.nchans = int(30)
        self.templates_path = ""
        self.SourceList = {}
        

        self.ds9 = False

#    Check if we have a 2FGL catalog
        conffile = os.environ['HOME']+'/.latlike'
        if os.path.exists(conffile):
            cf = open(conffile,'r')
#            print cf
            lll = cf.readlines()
#            print lll
            for line in lll:
#                print line.find('LAT_DATA_PATH=')

                if line.find('LAT_DATA_PATH=') == 0:
                    
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
#                    print pt
                    if os.path.isdir(pt):
#                        print pt
                        os.chdir(pt)
                        self.datapath = pt

                if line.find('TEMPLATES_PATH=') == 0:
                    
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                    if os.path.isdir(pt):
                        self.templates_path = pt

                if line.find('2FGL_CATALOG_FILE=')==0 and not os.path.exists(self.catalog):
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                    if os.path.exists(pt):
                        self.catalog = pt

                if line.find('IRFS=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    self.irfs = pt
#                    print self.irfs

#                if line.find('FLUX_THRESHOLD=')==0:
#                    aaa = line.split("=")
#                    pt = aaa[-1].strip()
                        
#                    try:
#                        self.fluxTres = float(pt)
#                    except:
#                        pass

                if line.find('BINSZ=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        xxx = float(pt)
                        if xxx < 0.0: xxx = 0.2
                        self.binsz = xxx
                    except:
                        self.binsz = 1.0


                if line.find('BASENAME=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        if pt == "": pt = "latspec"
                        self.basename = pt
                    except:
                        self.binsz = "latspec"


                if line.find('ZMAX=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        xxx = float(pt)
                        if xxx < 0.0: xxx = 100.0
                        self.zmax = xxx
                    except:
                        self.zmax = zmax

                if line.find('DCOSTHETA=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        xxx = float(pt)
                        if xxx < 0.0: xxx = 0.05
                        self.dcostheta = xxx
                    except:
                        self.zmax = zmax

                if line.find('THETACUT=')==0:
                    aaa = line.split("=")
                    pt = aaa[-1].strip()
                        
                    try:
                        xxx = float(pt)
                        if xxx < 0.0: xxx = 60.0
                        self.thetacut = xxx
                    except:
                        self.thetacut = 60.0

            cf.close()

        if self.datapath == '':
            self.datapath = os.getcwd()

        self.verify_cat()

#   Prepare directory and set some variables

        self.prepData()
        self.set_names()

        self.templates = os.listdir(self.templates_path)
 


    def writerc(self):

        """ Writes the resource file ~./latlike. """

        conffile = os.environ['HOME']+'/.latlike'
        cf = open(conffile,"w")
        cf.write("BASENAME="+str(self.basename)+"\n")
        cf.write("LAT_DATA_PATH="+self.datapath+"\n")
        cf.write("TEMPLATES_PATH="+self.templates_path+"\n")
        cf.write("2FGL_CATALOG_FILE="+self.catalog+"\n")
#        cf.write("FLUX_THRESHOLD="+str(self.fluxTres)+"\n")
        cf.write("IRFS="+self.irfs+"\n")
        cf.write("ZMAX="+str(self.zmax)+"\n")
        cf.write("BINSZ="+str(self.binsz)+"\n")
        cf.write("DCOSTHETA="+str(self.dcostheta)+"\n")
        cf.write("THETACUT="+str(self.thetacut)+"\n")

        cf.close()
            

    def set_names(self):

#        from fgltools import get_closest_fgl_source

        """
        Performs some data and variable check and sets some flags. 
        """

        from string import split,join        


        self.ltcube = "None"
        self.ccube = "None"
        self.expcube = "None"
        self.srcmap = "None"
        self.evfile = "None"
        self.image = "None"


        if os.path.exists(self.basename+'_ltcube.fits'): 
            self.ltcube = self.basename+'_ltcube.fits'
        if os.path.exists(self.basename+'_ccube.fits'): 
            self.ccube = self.basename+'_ccube.fits'
        if os.path.exists(self.basename+'_srcmap.fits'): 
            self.srcmap = self.basename+'_srcmap.fits'
        if os.path.exists(self.basename+'_expcube.fits'): 
            self.expcube = self.basename+'_expcube.fits'
        if os.path.exists(self.basename+'_filtered_gti.fits'): 
            self.evfile = self.basename+'_filtered_gti.fits'
        if os.path.exists(self.basename+'_image.fits'): 
            self.image = self.basename+'_image.fits'

            
    def prepData(self):

        """ Prepares LAT data in the current directory for analysis.
        In the datadir writes efiles.list file containing the list of
        event files, i.e. files ending on _PH.fits and 
        identifies the SC file. 
        """


        from coorconv import loffset,eq2gal,gal2eq,dist
        import re
        
        ret = ""
        wd = os.getcwd()
        print self.datapath
        print wd
        files = os.listdir(wd)
        scfile = [ f for f in files if re.search("_SC",f) ]
        print "1"
        if len(scfile) == 0: 
            ret += "No SC files found in the directory.Exit.\n"
            self.havedata = False
            self.scfile = ""
            print "11"
            return 
        if len(scfile) > 1:
            ret += "Warning: More that one SC file is found in the\n"
            ret += "specified directory.\n"
            for f in scfile: print f
            ret += "Using"+scfile[0]+"\n"
        phfiles = [ f for f in files if re.search("_PH",f) ]
        if len(phfiles) == 0: 
            ret += "No event files found.Exit.\n"
            self.havedata = False
            self.scfile = ""
            print "12"
            return
        os.system('echo '+phfiles[0]+' > efiles.list')
        for f in phfiles[1:]:os.system('echo '+f+' >> efiles.list')
        self.havedata = True
#        print "prepdata:"+self.havedata
        self.scfile = scfile[0]
        print "2"

        gotinfo,self.obs_pars = self.getObsInfo('efiles.list')

#        self.tmin = self.obs_pars['tmin']
#        self.tmax = self.obs_pars['tmax']
#        self.emin = self.obs_pars['emin']
#        self.emax = self.obs_pars['emax']
        if self.havedata: 
            self.ra = self.obs_pars['RA']
            self.dec = self.obs_pars['DEC']

            self.none_deg = self.obs_pars['roi']+5.0
            self.norm_deg = self.obs_pars['roi']*0.5
            self.all_deg = self.obs_pars['roi']*0.2


            self.rad = self.obs_pars['roi']


#            self.norm_flux = 1.0e-10
#            self.all_flux = 1.0e-9
#            self.show_flux = 1.0e-9

#            self.selected_source = ""
            self.initsources()

            if len(self.SourceList):
#                self.selected_source = self.SourceList[self.SourceList.keys()[0]]                                    
                self.selected_source = self.SourceList.keys()[0]
                self.selected_ra = self.SourceList[self.selected_source].ra
                self.selected_dec = self.SourceList[self.selected_source].dec

#            self.initsources()


        return ret

    def getObsInfo(self,efile):
        
        
        """ Reads the name of the first file in the efiles.list and
        reads the observation information and returns it in the form
        of the disctionary (ra,dec,rad,tmin,tmax,emin,emax,etc) """

        import pyfits
        import string

        try:
            fil = open(efile,'r')
        except:
#            raise FileNotFound
            return 0,{}
        fname = fil.readline()
        fh = pyfits.open(fname)
        dsval3 = fh[1].header['DSVAL3']
        ds_split = string.split(string.split(dsval3,'(')[1],',')
        ra = float(ds_split[0])
        dec = float(ds_split[1])
        roi = float(ds_split[2][:-1])
        dsval5 = fh[1].header['DSVAL5']
        emn,emx =string.split(dsval5,':')
        emin = float(emn)
        emax = float(emx)
        dsval4 = fh[1].header['DSVAL4']
        tmn,tmx = string.split(dsval4,':')
        tmin = float(tmn)
        tmax = float(tmx)
        dict = {"RA":ra,"DEC":dec,"roi":roi,"emin":emin,"emax":emax,"tmin":tmin,"tmax":tmax}
        return 1,dict

    def verify_cat(self):

        """ Verifies if the 2FGL catalog file exists and perform 
        simple check for the file format and content""" 

        import pyfits
        xxx = self.catalog
        self.haveCatalog = False
        self.catalog = "None"
        if os.path.exists(xxx):
            fname = os.path.abspath(xxx)
            try:
                fh = pyfits.open(fname)
                cols = fh[1].columns.names
                if 'Source_Name' in cols and \
                        'RAJ2000' in cols and \
                        'DEJ2000' in cols:
                    self.haveCatalog = True
                    self.catalog = fname

            except:
                self.haveCatalog = False
                self.catalog = "None"
            else:
                fh.close()
        else:
            self.haveCatalog = False
            self.catalog = "None"
                    


    def initsources(self):
        
        from fgltools import sdist
        import pyfits
        
        
        errors = []
#        self.SourceList[:] = []
        
        if self.haveCatalog == True:

#       Getting list of templates

            templates = []
            for (dirpath, dirnames, filenames) in os.walk(self.templates_path):
                templates.extend(filenames)
#----------------------------------------------------                

            fglf = pyfits.open(self.catalog)
            source = fglf[1].data.field('Source_name')
            assoc1 = fglf[1].data.field('ASSOC1')
            ra = fglf[1].data.field('RAJ2000')
            dec = fglf[1].data.field('DEJ2000')
            model = fglf[1].data.field('SpectrumType')
            flux = fglf[1].data.field('Flux1000')
            pl_index =  fglf[1].data.field('Spectral_Index')
            beta =  fglf[1].data.field('beta')
            cutoff =  fglf[1].data.field('Cutoff')
            eb =  fglf[1].data.field('Pivot_Energy')
            
#            inds = [ i for i in range(len(source)) if \
#                         sdist(ra[i],dec[i],self.ra,self.dec)>0.0 \
#                         and sdist(ra[i],dec[i],self.ra,self.dec)<self.all_deg \
#                         and flux[i]>self.all_flux and flux[i]<1.0]
            inds = [ i for i in range(len(source)) if \
                         sdist(ra[i],dec[i],self.ra,self.dec)<self.none_deg and source[i] not in self.SourceList ]



            ext_sn =  fglf[1].data.field('Extended_Source_Name')
            ext_sn4 =  fglf[4].data.field('Source_Name')
            ext_file  =  fglf[4].data.field('Spatial_Filename')

            for i in inds:
                dist = sdist(ra[i],dec[i],self.ra,self.dec)
                mod = model[i]
                pars = self.default_pars(mod,index=pl_index[i],
                                         eb=eb[i],beta=beta[i],cut=cutoff[i],f=flux[i])
                source_type = "SkyDirFunction"
                sn = source[i]
                if assoc1[i].strip() != "": sn = assoc1[i].strip()
                mfil = "" 
                if ext_sn[i].strip() != "":
                    source_type = "SpatialMap"
                    sn = ext_sn[i]
                    for j in range(len(ext_sn4)):
                        if ext_sn[i] == ext_sn4[j]:
                            mfil = ext_file[j]
                            if mfil not in templates: errors.append("Template file %s is not in templates."%mfil)
                            break
                    
                sss = LatSource(sn,ra[i],dec[i],source_type,mod,pars,
                                mfil,flux[i],assoc1[i])

                self.SourceList[source[i]] = sss
                


            dels = []

# delete source outside outer radius limit (self.none_deg)
            for s in self.SourceList:

                src = self.SourceList[s]
                if sdist(src.ra,src.dec,self.ra,self.dec)>self.none_deg: dels.append(s)

            for s in dels:  del self.SourceList[s]


            for s in self.SourceList:

                src = self.SourceList[s]
                d = sdist(src.ra,src.dec,self.ra,self.dec)                

                for p in src.pars:
                    src.pars[p].fixed = 0

                if (d<self.norm_deg):
                    try:
                        src.pars["Prefactor"].fixed = 1
                    except:
                        pass


                if (d<self.all_deg):

                    for p in src.pars:
                        src.pars[p].fixed = 1
                



            reselect = False

            try:
                if sdist(self.ra,self.dec,
                     self.SourceList[self.selected_source].ra,
                     self.SourceList[self.selected_source].dec)>self.none_deg: reselect = True
            except:
               pass     

#            for i in range(len(source)):

#                d = sdist(ra[i],dec[i],self.ra,self.dec)
                        


            if reselect: 
#                print "reselct"
                self.selected_source = self.SourceList.keys()[0] 
                self.selected_ra = self.SourceList[self.selected_source].ra
                self.selected_dec = self.SourceList[self.selected_source].dec

# adding Galactic Diffuse Emission
            
            xxx = [templates[i] for i in  xrange(len(templates)) if templates[i][:3] == "gll"]
            if len(xxx): 
                gd_template = xxx[0]
            else:
                gd_template = ""
                errors.append("Failed to file template for Galactic Diffusion.")

            pars = self.default_pars("PowerLaw",index=0.0)
            source_type = "MapCubeFunction"
            sss = LatSource('GalacticDiffuse',0.0,0.0,source_type,"PowerLaw",pars,gd_template)
            sss.pars["Prefactor"] = Param("Prefactor",1.0,10.0,1.0,1.0,1,0.0)
            sss.pars["Index"] = Param("Index",0.0,1.0,-1.0,1.0,0,0.0)
            sss.pars["Scale"] = Param("Scale",1.0e2,2.0e2,5.0e1,1.0,0,0.0)
            if sss.name not in self.SourceList: self.SourceList[sss.name] = sss


# adding Extragalactic Diffuse Background Emission
            
            xxx = [templates[i] for i in  xrange(len(templates)) if templates[i][:3] == "iso"]
            if len(xxx): 
                gd_template = xxx[0]
            else:
                gd_template = ""
                errors.append("Failed to file template for ExtraGalactic Diffusion.")

            pars = self.default_pars("FileFunction")
            source_type = "ConstantValue"
            sss = LatSource('ExtragalacticDiffBkg',0.0,0.0,source_type,"FileFunction",pars,gd_template)
            if sss.name not in self.SourceList: self.SourceList[sss.name] = sss

                
    def default_pars(self,model,index=-2.0,eb=300.0,beta=1000.0,cut=1000.0,f=1.0e-10):
                prs = {}
#                print model
                if model == "PowerLaw":
                    fscale=int(floor(log10(f)))
                    prs = {"Prefactor":Param("Prefactor",f/10**fscale,1000.0,0.001,10**fscale,0,0.0),
                           "Index":    Param("Index",    index, 5.0,1.0 ,-1,0,0.0),
                           "Scale":    Param("Scale",  100.0,2000.0,30.0,1,0,0.0)}
                elif model == "LogParabola":
                    fscale=int(floor(log10(f)))
                    prs = {"norm":Param("norm",f/10**fscale,1000.0,0.001,10**fscale,0,0.0),
                           "alpha":Param("alpha",index,5.0,0.5,-1,0,0.0),
                           "Eb":Param("Eb",eb,1.0e4,10.0,1,0,0.0),
                           "beta":Param("beta",beta,10.0,0.0,1,0,0.0)}
                elif model == "ExpCutoff":
                    fscale=int(floor(log10(f)))
                    prs = {"Prefactor":Param("Prefactor",f/10**fscale,1000.0,0.001,
                                             10**fscale,0,0.0),
                            "index":Param("index",index,5.0,1.0,-1,0,0.0),
                            "Ebreak":Param("Ebreak",10.0,1.0,300.0,1,0,0.0),
                            "P1":Param("P1",100.0,0.1,300.0,1,0,0.0),
                            "P2":Param("P2",0.0,-1.0,1.0,1,0,0.0),
                            "P3":Param("P3",0.0,-1.0,1.0,1,0,0.0),
                            }
                elif model == "PLExpCutoff":
                    fscale=int(floor(log10(f)))
                    prs = {"Prefactor":Param("Prefactor",f/10**fscale,1000.0,0.001,
                                             10**fscale,0,0.0),
                            "index":Param("index",index,1.0,5.0,-1,0,0.0),
                            "Ebreak":Param("Ebreak",eb,1.0e4,10.0,1,0,0.0),
                            "Cutoff":Param("P1",cut,0.1,300.0,1,0,0.0),
                            "P2":Param("P2",0.0,0.1,300.0,1,0,0.0),
                            "P3":Param("P3",0.0,0.1,300.0,1,0,0.0),
                            }
                elif model == "FileFunction":

                    prs = { "Normalization":Param("Normalization",1.0,1e5,1e-5,1,0,0.0) }

                return prs
        

    def write_xml_model(self):

        dist = []
        dtp = [('dist',float),('name','S20')]
        for k in self.SourceList:
            s = self.SourceList[k]
            dist.append((sdist(s.ra,s.dec,self.ra,self.dec),k))
        
        darr = array(dist,dtype=dtp)
        sort(darr,order='dist')
        xmlf = open(self.model_file,'w')
	xmlf.write('<?xml version="1.0" ?>\n')
        xmlf.write('<source_library title="source library">\n')
	xmlf.write('\n<!-- Point Sources -->\n')
        diff_src = []
        for s in sort(darr,order='dist'):

            src = self.SourceList[s['name']]
            sn = src.name
            st = src.type

            if st != "SkyDirFunction":
                diff_src.append(s['name'])
                continue

            smodel = src.model
            xmlf.write('<source name="%s" type="PointSource">\n' %(sn))
            xmlf.write('\t<!-- Source is %s degrees away from ROI center -->\n' %s['dist'])
            xmlf.write('\t<spectrum type="%s">\n'%smodel)
            for par in src.pars:
                p = src.pars[par]
                fr = "0"
                if p.fixed: fr = "1"

                xmlf.write('\t\t<parameter free="%s" max="%e" min="%e" name="%s" scale="%d" value="%2.4f"/>\n'%(fr,p.max,p.min,p.name,p.scale,p.value))

            xmlf.write('\t</spectrum>\n')
            xmlf.write('\t<spatialModel type="SkyDirFunction">\n')
            xmlf.write('\t\t<parameter free="0" max="360.0" min="-360.0" name="RA" scale="1.0" value="%s"/>\n' %src.ra)
            xmlf.write('\t\t<parameter free="0" max="90" min="-90" name="DEC" scale="1.0" value="%s"/>\n' %src.dec)
            xmlf.write('\t</spatialModel>\n')
            xmlf.write('</source>\n')


	xmlf.write('\n<!-- Extended Sources -->\n')
        for n in diff_src:

            src = self.SourceList[n]
            sn = src.name
            st = src.type
            smodel = src.model
            xmlf.write('<source name="%s" type="DiffuseSource">\n' %(sn))
            xmlf.write('\t<!-- Source is %s degrees away from ROI center -->\n' %s['dist'])
            addfile1 = ""
            addfile2 = 'file="%s/%s"'%(self.templates_path,src.template)        
            if smodel == "FileFunction": 
                addfile1 = 'file="%s/%s"'%(self.templates_path,src.template)
                addfile2 = ""
            xmlf.write('\t<spectrum type="%s" %s>\n'%(smodel,addfile1))
            for par in src.pars:
                p = src.pars[par]
                fr = "1"
                if p.fixed: fr = "0"

                xmlf.write('\t\t<parameter free="%s" max="%e" min="%e" name="%s" scale="%d" value="%2.4f"/>\n'%
                           (fr,p.max,p.min,p.name,p.scale,p.value))


            xmlf.write('\t</spectrum>\n')
            xmlf.write('\t<spatialModel %s type="%s">\n'%(addfile2,src.type))
            if src.type == "SpatialMap": 
                xmlf.write('\t\t<parameter free="0" max="1000.0" min="0.001" name="Prefactor" scale="1.0" value="1.0"/>\n' %s)
            if src.type == "MapCubeFunction": 
                xmlf.write('\t\t<parameter free="0" max="1000.0" min="0.001" name="Normalization" scale="1.0" value="1.0"/>\n' %s)
            if src.type == "ConstantValue": 
                xmlf.write('\t\t<parameter free="0" max="10.0" min="0.0" name="Value" scale="1.0" value="1.0"/>\n' %s)
            xmlf.write('\t</spatialModel>\n')
            xmlf.write('</source>\n')
            

        xmlf.write('</source_library>\n')
        
        xmlf.close()

    def write_regions(self,regfile = ''):

        """
        Writes current regions into a region .reg file readable by DS9.
        Uses fgltool.py module to select brightest sources in the field
        and writes them into the file, so they can be loaded to DS9.
        """

#        from fgltools import get_range_sources
        
        if regfile == '': 
            rf = self.basename+'.reg'
        else:
            rf = regfile

        regf = open(rf,'w')
        regf.write('global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n')
        regf.write("fk5\n")
#        print self.all_deg,self.norm_deg,self.rad
        regf.write("circle({0},{1},{2}\") # color=white select=0\n".format(self.ra,
                    self.dec,self.all_deg*3600.0))
        regf.write("circle({0},{1},{2}\") # color=green  select=0\n".format(self.ra,\
                    self.dec,self.norm_deg*3600.0))
        regf.write("circle({0},{1},{2}\") # color=blue  select=0\n".format(self.ra,\
                    self.dec,self.none_deg*3600.0))
        regf.write("circle({0},{1},{2}\") # color=yellow \n".
                   format(self.selected_ra,\
                          self.selected_dec,3600.0))

        print self.selected_ra,\
                          self.selected_dec


        for s in self.SourceList:
#            if s.flux > self.show_flux:
            src = self.SourceList[s]
            n = src.name
            if src.assoc_name != "": n = src.assoc_name
            regf.write("point({0},{1}) # select=0 point=cross text=\"{2}\" color=cyan\n".format(src.ra,src.dec,n))

        regf.close()
        
        
    def runds9(self):
        
        """Invokes ds9. Loads regions to ds9.
        If 2FLG catalog is available, shows catalog sources, which are brighter
        than FLUX_THRESHOLD  parameter on the ds9 image."""

        from string import atof        
        import subprocess

        rf = self.basename+'.reg'
        self.write_regions()
# This is needed to avoid comunication with another ds9 running from ds9
        pid = os.getpid()
        self.ds9id = 'latspec'+str(pid)
        ds9pr = subprocess.Popen(['ds9','-title',self.ds9id,self.image,'-regions',\
                                      rf,'-cmap','b','-sqrt','-zoom','to','fit',\
                                      '-wcs','skyformat','degrees'])
        self.ds9 = ds9pr
        return ds9pr



    def getregions(self):

        """ Reads region information from ds9"""

        from string import atof
        import subprocess

        try:
            lget = subprocess.Popen(["xpaget",self.ds9id,"regions"],stdout=subprocess.PIPE).communicate()[0]
        except:

            print "Failed to get regions from ds9."
            print lget
            return -1
            
        
        lines = lget.split("\n")

        for line in lines:
            if not line: break
            if line[0:6] == "circle":
                spl = line.split()
                spl1 = line[7:].split(")")[0].split(",")
#                print spl1
                if spl[-1] == "color=white":
#                    print spl1
                    self.all_deg = atof(spl1[2][:-1])/3600.0
#                    print self.bkg_ra,self.bkg_dec,self.bkg_rad
                elif spl[-1] == "color=green":
#                    print spl1
                    self.norm_deg = atof(spl1[2][:-1])/3600.0
                elif spl[-1] == "color=blue":
#                    print spl1
                    self.none_deg = atof(spl1[2][:-1])/3600.0
                elif spl[-1] == "color=yellow":
#                    print spl1
                    self.selected_ra = atof(spl1[0])
                    self.selected_dec = atof(spl1[1])

#                    print self.selected_ra,self.selected_dec,self.rad




#    def spc(self):
#    Calculates the source proximity coefficient according
#    to 2FGL fluxes.
#        import pyfits
#        from coorconv import sdist

#        if self.haveCatalog == True:
#            try:
#                fglf = pyfits.open(self.catalog)
#            except():
#                return 0.0, -1, "Failed to open catalog file"
            
#            name,distance,sind,res = \
#                get_closest_fgl_source(self.ra,self.dec,self.catalog)
#            ass_name = fglf[1].data.field('ASSOC1')[sind]
#            print "Assuming that ",name,"(",ass_name,") is the central source."
#            print "The distance to center of the region is ", distance," degrees."
       
#            source = fglf[1].data.field('Source_name')
#            ra = fglf[1].data.field('RAJ2000')
#            dec = fglf[1].data.field('DEJ2000')
#            flux = fglf[1].data.field('Flux1000')
#            flux_err = fglf[1].data.field('Unc_Flux1000')
#            eflux = fglf[1].data.field('Energy_Flux100')
#            eflux_err = fglf[1].data.field('Unc_Energy_Flux100')
#            print "2FGL Flux1000 is ", flux[sind],"+/-",flux_err[sind]," photons/cm**2/s."
            
                
#            spcx = 0.0
#            for i in range(len(source)):
#                dist = sdist(ra[i],dec[i],self.ra,self.dec)
#                if dist < self.obs_pars['roi'] and  i != sind:
#                    spcx += flux[i]/(2.0+dist*dist)
                        
                        
#            spcx = spcx/flux[sind]
#            print "Source proximity coefficient for ",name,":",spcx
#            return spcx, eflux[sind], eflux_err[sind], 1
#            self.spc = spcx
#        else:
#            print "DO NOT HAVE FGL catalog file."
#            print "Specify catalog file with -c option."
#            return -1.0,0.0,0.0,0




    def run_gui(self):
        import Tkinter as tk
        from latlike_gui import LatLikeApp


        root = tk.Tk()
        app = LatLikeApp(master=root,analysis=self)
        app.master.title('LAT Likelihood Analysis')
        app.mainloop()


def printHelp():

    """This function prints out the help for the CLI."""

    cmd = os.path.basename(sys.argv[0])
    print """
                        - LAT Likelihood Analysis - 

The Latlike is a graphical interactive analysis tool designed for
reduction and analysis of the Fermi/LAT (http://fermi.gsfc.nasa.gov/ssc) 
data using Xspec astrophysical spectral fitting package 
(http://heasarc.gsfc.nasa.gov/docs/xanadu/xspec). The tool
is integrated with Fermi Science Tools, FTOOLS, Xspec and 
DS9 imaging tool (hea-www.harvard.edu/RD/ds9) to provide
fast and convenient way from LAT server data to likelihood analysis.
There are three comand line options:


%s (-h|--help) ... This help text.

%s (-b |--basename=)<basename>  <basename> is the file rootname 
    which will be used for all product files. For example, the 
    spectrum will have the name <basename>_src.pha, background 
    - <basename>_bkg.pha, response -<basename>.rsp and so on.
    Default basename is "latspec".  
   

%s (-c|--catalog) The 2FLG catalog file.


To get more detailed help information on how to use the  program 
and peform LAT data analysis, start the program and press "Help"
button at the bottom of the main window.

""" %(cmd,cmd,cmd)

# Command-line interface             
def run_latlike():
    """Reads the command-line options and starts the program. """
    import getopt
    
#    try:
    opts, args = getopt.getopt(sys.argv[1:], 'hb:c:', ['help',
                                                             'basename=',
                                                             'catalog=',
                                                             ])
        #Loop through first and check for the basename
    basename = 'latlike'
    tstart = "INDEF"
    tstop = "INDEF"
    cat = 'gll_psc_v08.fit'
    fltres = 5.0e-9
    gui = True
#    irfs = 'P7SOURCE_V6'
        
    for opt,val in opts:
        if opt in ('-b','--basename'):
            basename = val
#        elif opt in ('-t','--tint'):
#            ttt = string.split(val,',')
#            if len(ttt) != 2:
#                print "Invalid option -t (--tint). The format is <t1,t2>. Exit"
#                return
 #           tstart = ttt[0]
 #           tstop = ttt[1]
#        elif opt in ('-e','--eint'):
#           ttt = string.split(val,',')
#            if len(ttt) != 2:
#                print "Invalid option -e (--eint). The format is <emin,emax>. Exit"
#                return
#            emin = ttt[0]
#            emax = ttt[1]
#        elif opt in ('-o','--offset'):
#            offset = val
#        elif opt in ('-i','--irfs'):
#            irfs = val
        elif opt in ('-c','--catalog'):
            cat = val
#        elif opt in ('-r','--radius'):
#            radius = float(val)
#        elif opt in ('-f','--flux_tres'):
#            fltres = float(val)
#        elif opt in ('-n','--nchan'):
#            nchan = int(val)
#        elif opt in ('--nogui'):
#            gui = False
        elif opt in ('-h','--help'):
            printHelp()
            return
            
#    par_dict = {"rad":radius,"offset:}
    ls = LatLike(basename=basename,
                 tmin=tstart,
                 tmax=tstop,
                 flux_tres = fltres,
                 catalog=cat)
#**** NS: if no gui, run no gui version. Otherwise run gui interface
    if not gui: 
        ls.run()
    else:
        ls.run_gui()

#


class LatSource:


    """Source class."""

    def __init__(self,name,r,d,t,m,prs,f,flux=0.0,assoc=""):
        self.name = "            "
        self.name = name
        self.ra = float(0.0)
        self.ra = r
        self.dec = float(0.0)
        self.dec = d
        self.model = m
        self.type = t
        self.pars = {}

        for p in prs:
            self.pars[p] = prs[p]

        self.template = f
        self.flux = flux
        self.assoc_name = assoc
#        print "%s, %s, %s, %s, %s"%(name,m,t,assoc,f)
  

    def xml(self):
        pass


class Param:

    def __init__(self,name,val,max,min,scale=1.0,fx=0,er = 0.0):
        
        self.name = name
        self.value = val
        self.err = er
        self.max = max
        self.min = min
        self.fixed = fx
        self.scale = scale

        

    
    
if __name__ == '__main__': run_latlike()


