#
#
#   History -----
#   
#  11.02.2014 ---- 
#  Starting a new project : LatLike
#  
#  
#  20.11.2013
#
#  Improving logging by using queues
#
#
#

import Tkinter as tk
#import ttk
import tkFileDialog
import os
import tkFont
import time
from fgltools import get_brightest_sources
import subprocess
import threading
import Queue
from math import sqrt



class LatLikeApp(tk.Frame):

    """ Latlike GUI class. Handles graphics for Latlike tool."""
        
    def __init__(self, master=None,analysis=None):
        
        self.analysis = analysis
        self.master = master
        master.protocol("WM_DELETE_WINDOW",self.quit_handler)
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.logQueue = Queue.Queue()
        self.logerrQueue = Queue.Queue()
        self.logblueQueue = Queue.Queue()
        self.logThread = threading.Thread(target = self.logger,args=())
        self.logLock = threading.Lock()
        self.logThread.deamon = True
        self.stop = False
#        self.norm_flux = 1e-9
#        self.all_flux = 1e-8
#        self.norm_deg = self.analysis.obs_pars['roi']
#        self.all_deg = self.analysis.obs_pars['roi']*0.5
        self.createWidgets()

#  logging stuff


        self.logThread.start()

    def quit_handler(self):

        self.quit_gui()
        

    def logger(self):
        
        import time
        while not self.stop:
            self.logLock.acquire()

            if not self.logQueue.empty():
                logtext = self.logQueue.get()
                self.logit_to_text(logtext)
                self.hline()

            if not self.logerrQueue.empty():

                logtext = self.logerrQueue.get()
                self.logerr_to_text(logtext)
                self.hline()

            if not self.logblueQueue.empty():
                logtext = self.logblueQueue.get()                
                self.logblue_to_text(logtext)
                self.hline()                

            self.logLock.release()
            time.sleep(0.1)


            

    def logit(self,s):


        self.logQueue.put(s)


    def logerr(self,s):


        self.logerrQueue.put(s)


    def logblue(self,s):


        self.logblueQueue.put(s)

         

    def createWidgets(self):
    
        from ScrolledText import ScrolledText

        top=self.winfo_toplevel()                
        top.rowconfigure(0, weight=1)            
        top.columnconfigure(0, weight=1)         
        self.rowconfigure(0, weight=1)           
        self.columnconfigure(0, weight=1)        


# ****** Define threads


        self.skipch = False
        self.basename_entry = tk.StringVar()
        self.date_extracted = tk.StringVar()
        self.tmin_entry = tk.StringVar()
        self.tmax_entry = tk.StringVar()
        self.ltcube_file= tk.StringVar()
        self.emin_entry = tk.StringVar()
        self.emax_entry = tk.StringVar()
#        self.emax = self.analysis.obs_pars["emax"]
#        self.emin = self.analysis.obs_pars["emin"]
        self.lc_emin_entry = tk.StringVar()
        self.lc_emax_entry = tk.StringVar()
        self.lc_pl_index = tk.StringVar()
        self.par_fixed = tk.IntVar()
        self.lc_emax = self.analysis.emax
        self.lc_emin = self.analysis.emin
        self.zmax_entry = tk.StringVar()
        self.binsz_entry = tk.StringVar()
        self.dcostheta_entry = tk.StringVar()
        self.thetacut_entry = tk.StringVar()
        self.src_spc = tk.StringVar()
        self.cat_source = tk.StringVar()
        self.source_model = tk.StringVar()
        self.flux_entry = tk.StringVar()
        self.nchan_entry = tk.StringVar()
        self.rootname_entry = tk.StringVar()
        self.modelvar = tk.StringVar()
        self.filtered_events = tk.StringVar()
        self.image_file = tk.StringVar()
        self.ccube_file = tk.StringVar()        
        self.expcube_file = tk.StringVar()        
        self.srcmap_file = tk.StringVar()
        self.irfs = tk.StringVar()
#        self.lc_bin.set("month")
#        self.lc_tres = 30*86400
#        self.lc_file.set("lc.fits")
#        self.lc_pl_index.set("2.5")
        self.par_fixed.set(1)


        self.rad_entry = tk.StringVar()
        self.norm_deg_entry = tk.StringVar()
        self.all_deg_entry = tk.StringVar()
#        self.src_rad_entry = tk.StringVar()
#        self.bkg_rad_entry = tk.StringVar()

        
# ***** Analysis Frame *********

        self.AnalysisFrame = tk.Frame(self,padx=0,pady=0)
        self.AnalysisFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.AnalysisFrame.grid_columnconfigure(0,weight=1)
        self.AnalysisFrame.grid_rowconfigure(0,weight=1)

# ***** Navigation Frame *********

        self.NavFrame = tk.Frame(self,padx=0,pady=0)
        self.NavFrame.grid(column=0,row=1,sticky=tk.N+tk.S+tk.E+tk.W)
        self.NavFrame.grid_columnconfigure(0,weight=1)
        self.NavFrame.grid_columnconfigure(1,weight=1)
        self.NavFrame.grid_columnconfigure(2,weight=1)
        self.NavFrame.grid_columnconfigure(3,weight=1)

# ******* Log Frame *******
        self.logfont = tkFont.Font(family="Courier New", size=11)
        self.LogFrame = tk.LabelFrame(self,text="Log",padx=5,pady=5,labelanchor=tk.N)
        self.LogFrame.grid(column=0,row=2,sticky=tk.N+tk.S+tk.E+tk.W)
        self.LogText = ScrolledText(self.LogFrame,bg='white',font=self.logfont)
        self.LogText.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.Y)

        self.logit("Welcome to LATlike, likelihood analysis of FERMI LAT data.")
        if self.analysis.haveCatalog:
            self.logit("Using 2FGL catalog: "+self.analysis.catalog)
        else:
            self.logit("2FGL catalog (and related functionality) is not available.")

        if self.analysis.havedata:
            self.log_data_info()

# *** Bottom Panel

        self.BottomFrame = tk.LabelFrame(self,padx=5,pady=5)
        self.BottomFrame.grid(column=0,row=3,sticky=tk.N+tk.S+tk.E+tk.W)
        self.BottomFrame.grid_columnconfigure(0,weight=1)
        self.BottomFrame.grid_columnconfigure(1,weight=1)
        self.BottomFrame.grid_columnconfigure(2,weight=1)
        self.BottomFrame.grid_columnconfigure(3,weight=1)


        self.SaveLogButton = tk.Button(self.BottomFrame,text="Save Log",
                                   command=self.save_log)
        self.SaveLogButton.grid(column=0,row=0,sticky='EWNS')
        self.ClearLogButton = tk.Button(self.BottomFrame,text="Clear Log",
                                    command=self.clear_log)
        self.ClearLogButton.grid(column=1,row=0,sticky='EWNS')
        self.QuitButton = tk.Button(self.BottomFrame,text="Quit",
                                command=self.quit_gui)
        self.QuitButton["text"] = "Quit"
        self.QuitButton["command"] =  self.quit_gui
        self.QuitButton.grid(column=3,row=0,sticky='EWNS')
        
        self.HelpButton = tk.Button(self.BottomFrame,text="Help",command=self.open_help)
        self.HelpButton.grid(column=2,row=0,sticky='EWNS')


        self.populate_cat_source_menu()
#        self.set_spectrum_panel()
        self.set_filter_panel()
        self.set_like_panel()


# **** Analysis Panels pack into Analysis (top) frame ***


# ****** Settings Panel

        self.SettingsFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
                                       relief=tk.GROOVE,labelanchor=tk.N,
                                       text="Settings",pady=5)

        
        self.DataFr = tk.LabelFrame(self.SettingsFrame,bd=1,relief=tk.GROOVE,
                                text="Data")

    
        self.DataDirButton = tk.Button(self.DataFr,text="...",
                                   command=self.askdirectory,
                                   relief=tk.GROOVE)
        self.DataDirButton.grid(column=0,row=0,sticky='EW',pady=2,padx=2)
        self.DataShowButton = tk.Button(self.DataFr,text="Data Info",
                                    command=self.log_data_info,
                                    relief=tk.GROOVE)
        self.DataShowButton.grid(column=1,row=0,sticky='EW',pady=2,padx=2)
        self.DataDirLabel = tk.Label(self.SettingsFrame)
#        self.DataDirLabel.grid(column=0,row=0,sticky='EW')

        self.DataFr.grid(column=0,row=0,sticky='EWNS',pady=3,padx=3)
        self.DataFr.grid_columnconfigure(0,weight=1)
        self.DataFr.grid_columnconfigure(1,weight=1)


        self.CatalogFr = tk.LabelFrame(self.SettingsFrame,bd=1,
                                   relief=tk.GROOVE,
                                   text="Catalog")
        self.CatButton = tk.Button(self.CatalogFr,text="...",
                               command=self.askfile,relief=tk.GROOVE)
#        self.CatLabel = tk.Label(self.SettingsFrame,text=self.analysis.catalog)
#        self.CatLabel.grid(column=1,row=1,columnspan=4,sticky='W')
        self.CatButton.grid(column=0,row=0,sticky='EW',pady=2,padx=2)
        self.CatFluxLabel = tk.Label(self.CatalogFr,text="Flux Threshold")
        self.CatFluxEntry = tk.Entry(self.CatalogFr,
                                 textvariable=self.flux_entry)
        
        self.CatFluxLabel.grid(column=1,row=0,sticky='EW',pady=2,padx=2)
        self.CatFluxEntry.grid(column=2,row=0,sticky='EW',pady=2,padx=2)
        self.CatFluxEntry.bind("<Return>",self.flux_tres_rtrn)
        self.flux_entry.set(self.analysis.fluxTres)

        self.CatalogFr.grid(column=0,row=1,sticky='EWNS',pady=3,padx=3)
        self.CatalogFr.grid_columnconfigure(0,weight=1)
        self.CatalogFr.grid_columnconfigure(1,weight=2)
        self.CatalogFr.grid_columnconfigure(2,weight=2)


        self.ParsFr = tk.LabelFrame(self.SettingsFrame,bd=1,
                                relief=tk.GROOVE,
                                text="Parameters")
    

        self.BinszLabel = tk.Label(self.ParsFr,text='binsz:')
        binsz_isok_command = self.register(self.binsz_isok)
        self.BinszEntry = tk.Entry(self.ParsFr,
                               textvariable=self.binsz_entry,validate='all',
                               validatecommand=(binsz_isok_command,'%i','%s','%P'))
    
        self.BinszLabel.grid(column=0,row=0,sticky='E',pady=2,padx=2)
        self.BinszEntry.grid(column=1,row=0,sticky='EW',pady=2,padx=2)

        self.ZmaxLabel = tk.Label(self.ParsFr,text='zmax:')
        zmax_isok_command = self.register(self.zmax_isok)
        self.FilterZmaxEntry = tk.Entry(self.ParsFr,
                                    textvariable=self.zmax_entry,validate='all',
                                    validatecommand=(zmax_isok_command,'%i','%s','%P'))
        self.ZmaxLabel.grid(column=0,row=1,sticky='E',pady=2,padx=2)
        self.FilterZmaxEntry.grid(column=1,row=1,sticky='EW',pady=2,padx=2)


        self.DcosthetaLabel = tk.Label(self.ParsFr,text='dcostheta:')
        dcostheta_isok_command = self.register(self.dcostheta_isok)
        self.DcosthetaEntry = tk.Entry(self.ParsFr,
                          textvariable=self.dcostheta_entry,
                          validate='all',
                          validatecommand=(dcostheta_isok_command,'%i','%s','%P'))
        self.DcosthetaLabel.grid(column=0,row=2,sticky='E',pady=2,padx=2)
        self.DcosthetaEntry.grid(column=1,row=2,sticky='EW',pady=2,padx=2)

        self.ThetacutLabel = tk.Label(self.ParsFr,text='thetacut:')
        thetacut_isok_command = self.register(self.thetacut_isok)
        self.ThetacutEntry = tk.Entry(self.ParsFr,
                         textvariable=self.thetacut_entry,validate='all',
                         validatecommand=(thetacut_isok_command,'%i','%s','%P'))
        self.ThetacutLabel.grid(column=0,row=3,sticky='E',pady=2,padx=2)
        self.ThetacutEntry.grid(column=1,row=3,sticky='EW',pady=2,padx=2)

#        self.irfs.trace("w",self.cat_source_change)
        self.IrfsLabel = tk.Label(self.ParsFr,text='IRFS:')
        self.IrfsLabel.grid(column=0,row=4,sticky='E',pady=2,padx=2)
        self.irfs.trace("w",self.irfs_change)
        self.IrfsMenu = tk.OptionMenu(self.ParsFr,self.irfs,"")
        self.IrfsMenu.config(width=15)
        self.IrfsMenu.grid(column=1,row=4,sticky='EWNS')


        self.ParsFr.grid(column=1,row=0,rowspan=3,sticky='EWNS',pady=3,padx=3)
        self.ParsFr.grid_columnconfigure(0,weight=1)
        self.ParsFr.grid_columnconfigure(1,weight=1)
        self.ParsFr.grid_rowconfigure(0,weight=1)
        self.ParsFr.grid_rowconfigure(1,weight=1)
        self.ParsFr.grid_rowconfigure(2,weight=1)
        self.ParsFr.grid_rowconfigure(3,weight=1)
        self.ParsFr.grid_rowconfigure(4,weight=1)

        self.BasenameFr = tk.LabelFrame(self.SettingsFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Basename")
        self.DataBasenameEntry = tk.Entry(self.BasenameFr,
                                      textvariable=self.basename_entry)
        self.DataBasenameEntry.bind("<Return>",self.basename_return)
        self.DataBasenameEntry.grid(column=0,row=0,sticky='EW',pady=2,padx=2)
        self.basename_entry.set(self.analysis.basename)

        self.BasenameFr.grid(column=0,row=2,sticky='EWNS',pady=3,padx=3)
        self.BasenameFr.grid_columnconfigure(0,weight=1)


        self.SettingsFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.SettingsFrame.grid_columnconfigure(0,weight=1)
        self.SettingsFrame.grid_columnconfigure(1,weight=1)
        self.SettingsFrame.grid_rowconfigure(0,weight=1)
        self.SettingsFrame.grid_rowconfigure(1,weight=1)
        self.SettingsFrame.grid_rowconfigure(2,weight=2)


        self.set_settings_panel()

# ***** Prerequisites (Filter) Panel *************

        self.FilterFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
                                         relief=tk.GROOVE,labelanchor='n',
                                         padx=5,pady=5,text="Prerequisites")
        self.FilterFrame.grid_columnconfigure(0,weight=3)
        self.FilterFrame.grid_columnconfigure(1,weight=1)
        self.FilterFrame.grid_rowconfigure(0,weight=1)
        self.FilterFrame.grid_rowconfigure(1,weight=1)
        self.FilterFrame.grid_rowconfigure(2,weight=2)
        self.FilterFrame.grid_rowconfigure(3,weight=1)

        self.DataFr = tk.LabelFrame(self.FilterFrame,bd=1,text="Events")
        self.DataFr.grid_columnconfigure(0,weight=1)
        self.DataFr.grid_columnconfigure(1,weight=1)
        self.DataFr.grid(column=0,row=0,sticky='EW')

        self.DataFilterButton = tk.Button(self.DataFr,
                                      text="Filter Events",relief=tk.GROOVE,
                                      command=self.filterevents)

        self.DataFilterFileLabel = tk.Label(self.DataFr,
                                        textvariable=self.filtered_events)
        self.DataFilterButton.grid(column=1,row=0,sticky='EW')
#        self.DataFilterButton.grid(column=0,row=4,sticky='E')
        self.DataFilterFileLabel.grid(column=0,row=0,sticky='EW')


        self.CubeFr = tk.LabelFrame(self.FilterFrame,bd=1,
                                relief=tk.GROOVE,
                                text="Ltcube")
        self.CubeFr.grid_columnconfigure(0,weight=1)
        self.CubeFr.grid_columnconfigure(1,weight=1)
        self.CubeFr.grid_columnconfigure(2,weight=1)

        self.SourceLtcubeButton = tk.Button(self.CubeFr,text="Run GTLTcube",
                                        command=self.getCube,relief=tk.GROOVE)
        self.SourceLtcubeFileLabel = tk.Label(self.CubeFr,
                                          textvariable=self.ltcube_file)
        self.SourceLtcubeButton.grid(column=2,row=0,sticky='EW',pady=2,padx=2)
        self.ltcube_file.set(self.analysis.ltcube)
        self.LtcubeChooseBtn = tk.Button(self.CubeFr,text="Load Cube",
                                         relief=tk.GROOVE,
                                         command=self.ask_cube)
        self.LtcubeChooseBtn.grid(column=1,row=0,sticky='EW')
        self.SourceLtcubeFileLabel.grid(column=0,row=0,sticky='EW')
#        self.rootname_entry.trace("w",self.set_spectrum_panel)        
        
        self.CubeFr.grid(column=0,row=1,sticky='EWNS')


# Frame for 3D cube (gtbin)

        self.CcubeFrame = tk.LabelFrame(self.FilterFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="3D Map")

        self.CcubeFrame.grid_columnconfigure(0,weight=1)
        self.CcubeFrame.grid_columnconfigure(1,weight=1)
        self.CcubeFrame.grid_columnconfigure(2,weight=1)

        self.CcubeCreateButton = tk.Button(self.CcubeFrame,
                                       text="Extract Ccube",relief=tk.GROOVE,
                                       command=self.ccube_thread)
        self.CcubeCreateButton.grid(column=1,row=0,sticky='EWNS')

        self.CcubeLabel = tk.Label(self.CcubeFrame,textvariable=self.ccube_file)
        self.CcubeLabel.grid(column=0,row=0,sticky='EWNS')

        self.CcubeFrame.grid(column=0,row=2,sticky=tk.N+tk.S+tk.E+tk.W)

# Frame for exposure map (gtexpcube2)

        self.ExpcubeFrame = tk.LabelFrame(self.FilterFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Exposure Map")

        self.ExpcubeFrame.grid_columnconfigure(0,weight=1)
        self.ExpcubeFrame.grid_columnconfigure(1,weight=1)
        self.ExpcubeFrame.grid_columnconfigure(2,weight=1)

        self.ExpcubeCreateButton = tk.Button(self.ExpcubeFrame,
                                       text="Calculate Exposure Map",relief=tk.GROOVE,
                                       command=self.expcube_thread)
        self.ExpcubeCreateButton.grid(column=1,row=0,sticky='EWNS')

        self.ExpcubeLabel = tk.Label(self.ExpcubeFrame,textvariable=self.expcube_file)
        self.ExpcubeLabel.grid(column=0,row=0,sticky='EWNS')

        self.ExpcubeFrame.grid(column=0,row=3,sticky=tk.N+tk.S+tk.E+tk.W)



        self.set_filter_panel()


# ****** Model Frame ********

        self.ModelFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
                                 relief=tk.GROOVE,padx=5,pady=5,
                                 text="Model",labelanchor='n')

        self.ModelFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.ModelFrame.grid_columnconfigure(0,weight=2)
        self.ModelFrame.grid_columnconfigure(1,weight=1)
        self.ModelFrame.grid_rowconfigure(0,weight=1)
        self.ModelFrame.grid_rowconfigure(1,weight=6)



# ****** Image Frame (now a part of the Model Panel) *******

        self.ImageFrame = tk.LabelFrame(self.ModelFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Image")

        self.ImageFrame.grid_columnconfigure(0,weight=1)
        self.ImageFrame.grid_columnconfigure(1,weight=1)
        self.ImageFrame.grid_columnconfigure(2,weight=1)

        self.ImageCreateButton = tk.Button(self.ImageFrame,
                                       text="Extract Image",relief=tk.GROOVE,
                                       command=self.image_thread)
        self.ImageCreateButton.grid(column=1,row=0,sticky='EWNS')

        self.ImageLabel = tk.Label(self.ImageFrame,textvariable=self.image_file)
        self.ImageLabel.grid(column=0,row=0,sticky='EWNS')

        self.ImageFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)


        self.ImageDS9Button = tk.Button(self.ImageFrame,
                                        text="Run ds9",
                                        command=self.run_ds9,
                                            relief=tk.GROOVE)
        self.ImageDS9Button.grid(column=2,row=0,sticky='EW')


#        self.src_spc.set("")
#        self.ImageSrcSpcLabel = tk.Label(self.ImageFrame,textvariable=self.src_spc)
#        self.ImageSrcSpcLabel.grid(column=2,row=1)

# *************** Source Frame **************************************

#        fff = tkFont.Font(family='Helvetica',size=8)
#        fff.configure(size=8)
        self.SourceFrame = tk.LabelFrame(self.ModelFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Source")
        self.SourceFrame.grid(column=0,row=1,sticky="EWNS")
        self.SourceFrame.grid_columnconfigure(0,weight=1)
        self.SourceFrame.grid_columnconfigure(1,weight=2)
        self.SourceFrame.grid_columnconfigure(2,weight=1)
        self.SourceFrame.grid_columnconfigure(3,weight=2)
        self.SourceFrame.grid_columnconfigure(4,weight=1)
        self.SourceFrame.grid_columnconfigure(5,weight=2)



        self.CatSourceLabel = tk.Label(self.SourceFrame,text="Source:")
        self.CatSourceLabel.grid(column=0,row=0,sticky='EW',padx=1,pady=1)
        self.cat_source.trace("w",self.cat_source_change)
        self.CatSourceMenu = tk.OptionMenu(self.SourceFrame,self.cat_source,"")
        self.CatSourceMenu.config(width=12)
        self.CatSourceMenu.grid(column=1,row=0,sticky='EWNS',padx=1,pady=1)



        self.source_type = tk.StringVar()        
        self.SourceTypeLabel = tk.Label(self.SourceFrame,text="Type:")
        self.SourceTypeLabel.grid(column=2,row=0,sticky='EW',padx=1,pady=1)
        self.source_type.trace("w",self.source_type_change)
        self.SourceTypeMenu = tk.OptionMenu(self.SourceFrame,self.source_type,"")
        self.SourceTypeMenu.config(width=12)
        self.SourceTypeMenu.grid(column=3,row=0,sticky='EWNS',padx=1,pady=1)

        self.source_template = tk.StringVar()        
        self.SourceTemplateLabel = tk.Label(self.SourceFrame,text="Template:")
        self.SourceTemplateLabel.grid(column=4,row=1,sticky='EW',padx=1,pady=1)
        self.source_template.trace("w",self.source_template_change)
        self.SourceTemplateMenu = tk.OptionMenu(self.SourceFrame,self.source_template,"")
        self.SourceTemplateMenu.config(width=12)
        self.SourceTemplateMenu.grid(column=5,row=1,sticky='EWNS',padx=1,pady=1)


        self.SourceModelLabel = tk.Label(self.SourceFrame,text="Model:")
        self.SourceModelLabel.grid(column=4,row=0,sticky='EW',padx=1,pady=1)
        self.source_model.trace("w",self.source_model_change)
        self.SourceModelMenu = tk.OptionMenu(self.SourceFrame,
                                             self.source_model,"")
        self.SourceModelMenu.config(width=12)
        self.SourceModelMenu.grid(column=5,row=0,sticky='EWNS',padx=1,pady=1)
        
        self.model_parameter = tk.StringVar()
        self.ParamLabel = tk.Label(self.SourceFrame,text="Param:")
        self.ParamLabel.grid(column=0,row=1,sticky="EWNS",padx=1,pady=1)
        self.ModParMenu = tk.OptionMenu(self.SourceFrame,self.model_parameter,"")
        self.ModParMenu.config(width=12)
        self.ModParMenu.grid(column=1,row=1,sticky='EWNS',padx=1,pady=1)
        self.model_parameter.trace("w",self.model_par_change)

        self.model_par_value = tk.StringVar()
        self.ModParLabel = tk.Label(self.SourceFrame,text="Value:")
        self.ModParLabel.grid(column=0,row=2,sticky="EWNS",padx=1,pady=1)
        self.ModParEnt = tk.Entry(self.SourceFrame,
                                  textvariable=self.model_par_value,width=7)
        self.ModParEnt.grid(column=1,row=2,sticky="EWNS",padx=1,pady=1)

        self.model_par_scale = tk.StringVar()
        self.ParScaleLabel = tk.Label(self.SourceFrame,text="Scale:")
        self.ParScaleLabel.grid(column=0,row=3,sticky="EWNS",padx=1,pady=1)
        self.ParScaleEnt = tk.Entry(self.SourceFrame,textvariable=self.model_par_scale,width=7)
        self.ParScaleEnt.grid(column=1,row=3,sticky="EWNS",padx=1,pady=1)

        self.par_max_value = tk.StringVar()
        self.ParMaxLabel = tk.Label(self.SourceFrame,text="Max:")
        self.ParMaxLabel.grid(column=2,row=2,sticky="EWNS",padx=1,pady=1)
        self.ParMaxEnt = tk.Entry(self.SourceFrame,textvariable=self.par_max_value,width=7)
        self.ParMaxEnt.grid(column=3,row=2,sticky="EWNS",padx=1,pady=1)

        self.par_min_value = tk.StringVar()
        self.ParMinLabel = tk.Label(self.SourceFrame,text="Min:")
        self.ParMinLabel.grid(column=2,row=3,sticky="EWNS",padx=1,pady=1)
        self.ParMinEnt = tk.Entry(self.SourceFrame,textvariable=self.par_min_value,width=7)
        self.ParMinEnt.grid(column=3,row=3,sticky="EWNS",padx=1,pady=1)


        self.ParFixCB = tk.Checkbutton(self.SourceFrame,text="free",variable=self.par_fixed)
        self.ParFixCB.grid(column=2,row=1,columnspan=2,sticky='EWN',pady=1)
        self.par_fixed.trace("w",self.par_fixed_change)

        self.set_source_frame()


#******** Limits Frame *****************


        self.LimitsFrame = tk.LabelFrame(self.ModelFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Limits")

        self.LimitsFrame.grid_rowconfigure(0,weight=1)
        self.LimitsFrame.grid_rowconfigure(1,weight=1)
        self.LimitsFrame.grid_rowconfigure(2,weight=5)
        self.LimitsFrame.grid_rowconfigure(3,weight=1)
#        self.LimitsFrame.grid_rowconfigure(4,weight=1)
        self.LimitsFrame.grid_columnconfigure(0,weight=1)
        self.LimitsFrame.grid_columnconfigure(1,weight=1)
        self.LimitsFrame.grid_columnconfigure(2,weight=1)



        self.ApplyRegionsButton = tk.Button(self.LimitsFrame,
                                        text="Apply",
                                        command=self.apply_reg,
                                            relief=tk.GROOVE)
        self.ApplyRegionsButton.grid(column=0,row=3,columnspan=3,sticky='EW')


        self.NoneLbl = tk.Label(self.LimitsFrame,text="None")
#        self.DegLbl = tk.Label(self.LimitsFrame,text="Degrees")
        self.NormLbl =  tk.Label(self.LimitsFrame,text="Prefactor")
        self.AllLbl =  tk.Label(self.LimitsFrame,text="All")
        self.FreeLbl =  tk.Label(self.LimitsFrame,text="Free Pars")

#        norm_flux_isok_command = self.register(self.norm_flux_isok)
#        all_flux_isok_command =  self.register(self.all_flux_isok)
#        src_rad_isok_command =  self.register(self.src_rad_isok)


        entryw = 6

#        self.NormFluxEntry = tk.Entry(self.LimitsFrame,width=entryw,
#                                   textvariable=self.norm_flux_entry,validate='key',
#                         validatecommand=(norm_flux_isok_command,'%d','%s','%P'))
#        self.AllFluxEntry = tk.Entry(self.LimitsFrame,width=entryw,
#                                   textvariable=self.all_flux_entry,validate='key',
#                         validatecommand=(all_flux_isok_command,'%d','%s','%P'))
#        self.SrcRADEntry = tk.Entry(self.RegionsFrame,width=entryw,
#                           textvariable=self.src_rad_entry,validate='key',
#                         validatecommand=(src_rad_isok_command,'%d','%s','%P'))
        self.NoneLbl.grid(column=2,row=1,sticky="EWNS")
        self.NormLbl.grid(column=1,row=1,sticky="EWNS")
        self.AllLbl.grid(column=0,row=1,sticky="EWNS")
        self.FreeLbl.grid(column=0,row=0,columnspan=3,sticky="EWNS")
#        self.SrcRADEntry.grid(column=1,row=3,sticky="EWNS",pady=8)



        norm_deg_isok_command  =  self.register(self.norm_deg_isok)
        all_deg_isok_command =  self.register(self.all_deg_isok)
        rad_isok_command =  self.register(self.rad_isok)

        if self.analysis.havedata:
            upper = self.analysis.obs_pars['roi']*1.5
        else:
            upper = 0.0
            
        self.none_scale = tk.DoubleVar()


        self.NoneScale = tk.Scale(self.LimitsFrame,from_=upper,to=0.0,
                                  command=self.update_ds9)
        self.NoneScale.grid(column=2,row=2,sticky='EWNS')

        self.AllScale = tk.Scale(self.LimitsFrame,from_=upper,to=0.0,
                                 command=self.update_ds9)
        self.AllScale.grid(column=0,row=2,sticky='EWNS')

        self.NormScale = tk.Scale(self.LimitsFrame,from_=upper,to=0.0,
                                  command=self.update_ds9)
        self.NormScale.grid(column=1,row=2,sticky='EWNS')

        self.set_scales()

#        self.NoneDegEntry = tk.Entry(self.LimitsFrame,width=entryw,
#                          textvariable=self.rad_entry,validate='key',
#                          validatecommand=(rad_isok_command,'%d','%s','%P'))
#        self.NormDegEntry = tk.Entry(self.LimitsFrame,width=entryw,
#                          textvariable=self.norm_deg_entry,validate='key',
#                          validatecommand=(norm_deg_isok_command,'%d','%s','%P'))
#        self.AllDegEntry = tk.Entry(self.LimitsFrame,width=entryw,
#                           textvariable=self.all_deg_entry,validate='key',
#                           validatecommand=(all_deg_isok_command,'%d','%s','%P'))

 #       print self.analysis.all_deg,self.analysis.norm_deg,self.analysis.rad            
 #       self.norm_deg_entry.set(str(self.analysis.norm_deg)) 
 #       self.all_deg_entry.set(str(self.analysis.all_deg))        
 #       self.rad_entry.set(str(self.analysis.rad))        
 #       print self.analysis.all_deg,self.analysis.norm_deg,self.analysis.rad

#        self.norm_deg_entry.trace("w",self.set_norm_deg)        
#        self.all_deg_entry.trace("w",self.set_all_deg)        
#        self.rad_entry.trace("w",self.set_rad)

 #       self.DegLbl.grid(column=1,row=0,sticky="EWNS")

 #       self.NoneDegEntry.grid(column=1,row=1,sticky="EWNS",pady=8)
 #       self.NormDegEntry.grid(column=1,row=2,sticky="EWNS",pady=8)
 #       self.AllDegEntry.grid(column=1,row=3,sticky="EWNS",pady=8)



        self.LimitsFrame.grid(column=2,row=0,rowspan=2,sticky=tk.N+tk.S+tk.E+tk.W)


        self.populate_cat_source_menu()
        self.populate_source_model_menu()
        self.populate_source_type_menu()
        self.populate_source_template_menu()
        


# ****** Likelihood Frame *******

        self.LikeFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
                                 relief=tk.GROOVE,padx=5,pady=5,
                                 text="Likelihood",labelanchor='n')

        self.LikeFrame.grid_columnconfigure(0,weight=1)
        self.LikeFrame.grid_columnconfigure(1,weight=1)
        self.LikeFrame.grid_columnconfigure(2,weight=1)
        self.LikeFrame.grid_rowconfigure(0,weight=1)
        self.LikeFrame.grid_rowconfigure(1,weight=1)

        self.LikeFrame1 = tk.LabelFrame(self.LikeFrame,bd=1,
                                    relief=tk.GROOVE)
        self.LikeFrame1.grid_columnconfigure(0,weight=1)
        self.LikeFrame1.grid_columnconfigure(1,weight=1)
        self.LikeFrame1.grid_columnconfigure(2,weight=1)
        self.LikeFrame1.grid_columnconfigure(3,weight=1)
        self.LikeFrame1.grid_columnconfigure(4,weight=1)
        self.LikeFrame1.grid_rowconfigure(0,weight=1)
        self.LikeFrame1.grid_rowconfigure(1,weight=1)
        self.LikeFrame1.grid_rowconfigure(2,weight=1)

        self.LikeFrame1.grid(column=0,row=0,columnspan=3,sticky="EWNS")

#        self.LikeScale = tk.Scale(self.LikeFrame1,from_=0,to=10)
#        self.LikeScale.grid(column=0,row=1,sticky='EWNS')

        self.LikeRootnameLabel = tk.Label(self.LikeFrame1,bd=1,
                                                 text="Product directory:")

        self.LikeRootnameLabel.grid(column=0,row=0,sticky='EWNS')



        self.LikeRootnameEntry = tk.Entry(self.LikeFrame1,relief=tk.FLAT,
                                        textvariable=self.rootname_entry,
                                          disabledforeground="black")

        self.LikeRootnameEntry.grid(column=1,row=0,columnspan=3,sticky='EWNS',pady=2)
#        self.LcBinLabel = tk.Label(self.LcFrame1,text="Likelihood")
#        self.LcBinLabel.grid(column=0,row=2,sticky='EWNS',pady=2)
#        self.LcFileLabel = tk.Label(self.LcFrame1,text="Output File:")
#        self.LcFileLabel.grid(column=0,row=1,sticky='EWNS',pady=2)

#        self.LcFileEntry = tk.Entry(self.LcFrame1,textvariable=self.lc_file)
#        self.LcFileEntry.grid(column=1,row=1,columnspan=3,sticky='EWNS',pady=2)
#        self.lc_bin.trace("w",self.lc_bin_change)
#        self.LcBinMenu = tk.OptionMenu(self.LcFrame1,self.lc_bin,"")
#        self.LcBinMenu.config(width=15)
#        self.LcBinMenu.grid(column=1,row=2,columnspan=3,sticky='EWNS',pady=2)
#        self.LcBinMenu["menu"].delete(0, tk.END)
#        self.lc_bin.set("binned")
#        for s in ["binned","week","day"]: 
#            self.LcBinMenu["menu"].add_command(label=s, 
#                                           command=lambda temp = s: 
#                                           self.LcBinMenu.setvar(self.LcBinMenu.cget("textvariable"),
#                                             value = temp))
#        self.LcShowBtn = tk.Button(self.LcFrame,text="Show Lightcurve",
#                                   relief=tk.GROOVE,command=self.plot_lc)
#        self.LcShowBtn.grid(column=1,row=1,sticky='EWNS')




# Frame for exposure map (gtexpcube2)

        self.SrcmapFrame = tk.LabelFrame(self.LikeFrame,bd=1,
                                    relief=tk.GROOVE,
                                    text="Source Map")

        self.SrcmapFrame.grid_columnconfigure(0,weight=1)
        self.SrcmapFrame.grid_columnconfigure(1,weight=1)
        self.SrcmapFrame.grid_columnconfigure(2,weight=1)

        self.SrcmapCreateButton = tk.Button(self.SrcmapFrame,
                                       text="Calculate Source Map",relief=tk.GROOVE,
                                       command=self.srcmap_thread)
        self.SrcmapCreateButton.grid(column=1,row=0,sticky='EWNS')

        self.SrcmapLabel = tk.Label(self.SrcmapFrame,textvariable=self.srcmap_file)
        self.SrcmapLabel.grid(column=0,row=0,sticky='EWNS')

        self.SrcmapFrame.grid(column=0,row=3,sticky=tk.N+tk.S+tk.E+tk.W)



        self.LikeRunBtn = tk.Button(self.LikeFrame,
                                  text="Run Likelihood",
                                  relief=tk.GROOVE,
                                  command=self.run_likelihood)
#        self.SaveLcBtn = tk.Button(self.LcFrame,
#                                   text="Save lightcurve",
#                                   command=self.save_lightcurve,height=1,
#                                   relief=tk.GROOVE)


        self.LikeRunBtn.grid(column=0,row=1,sticky='EWNS')
#        self.SaveLcBtn.grid(column=2,row=1,sticky='EWNS')


#        emin_isok_command = self.register(self.emin_isok)
#        emax_isok_command = self.register(self.emax_isok)
        

#        self.LcEnergyRangeLabel = tk.Label(self.LcFrame1,text='Energy Range:')
#        self.LcELabel = tk.Label(self.LcFrame1,text='-')
#        self.LcEunitLabel = tk.Label(self.LcFrame1,text='MeV')
#        self.LcEminEntry = tk.Entry(self.LcFrame1,textvariable=self.lc_emin_entry,
#                                validate='all',
#                                validatecommand=(emin_isok_command,'%P'))
#        self.LcEmaxEntry = tk.Entry(self.LcFrame1,
#                                textvariable=self.lc_emax_entry,validate='all',
#                                validatecommand=(emax_isok_command,'%P'))


#        self.LcEnergyRangeLabel.grid(column=0,row=3,sticky='EWNS',pady=2)
#        self.LcEminEntry.grid(column=1,row=3,sticky='EWNS',pady=2)
#        self.LcELabel.grid(column=2,row=3,sticky='EWNS',pady=2)
#        self.LcEmaxEntry.grid(column=3,row=3,sticky='EWNS',pady=2)
#        self.LcEunitLabel.grid(column=4,row=3,sticky='EWNS',pady=2)
    
#        self.lc_emin_entry.set(str(self.analysis.emin))
#        self.lc_emax_entry.set(str(self.analysis.emax))
    
#        self.LcEmaxEntry.bind("<Return>",self.lc_emax_enter)
#        self.LcEminEntry.bind("<Return>",self.lc_emin_enter)
#        self.LcPLindLabel = tk.Label(self.LcFrame1,text="Powerlaw Index:")
#        self.LcPLindEntry = tk.Entry(self.LcFrame1,textvariable=self.lc_pl_index,width=5)
#        self.LcPLindLabel.grid(column=0,row=4,sticky='EWNS',pady=8)
#        self.LcPLindEntry.grid(column=1,row=4,sticky='EWNS',pady=8)
#        self.LcIndFixCB = tk.Checkbutton(self.LcFrame1,text="fixed",variable=self.lc_index_fixed)
#        self.LcIndFixCB.grid(column=2,row=4,columnspan=2,sticky='EWN',pady=12)
        

        
# ****** Spectrum Frame *******
        
#        self.SpectrumFrame = tk.LabelFrame(self.AnalysisFrame,bd=2,
#                                       relief=tk.GROOVE,padx=5,pady=5,
#                                       text="Spectrum",labelanchor='n')

#        self.SpectrumFrame.grid_columnconfigure(0,weight=1)
#        self.SpectrumFrame.grid_columnconfigure(1,weight=1)
#        self.SpectrumFrame.grid_columnconfigure(2,weight=1)
#        self.SpectrumFrame.grid_columnconfigure(3,weight=1)
#        self.SpectrumFrame.grid_columnconfigure(4,weight=1)
#        self.SpectrumFrame.grid_rowconfigure(0,weight=2)
#        self.SpectrumFrame.grid_rowconfigure(1,weight=1)
#        self.SpectrumFrame.grid_rowconfigure(2,weight=2)
        

#        self.SpFrame = tk.LabelFrame(self.SpectrumFrame,bd=1,
#                                    relief=tk.GROOVE)
#

#        self.SpFrame.grid(column=0,row=0,columnspan=3,sticky="EWNS")

#        self.SpFrame.grid_columnconfigure(0,weight=3)
#        self.SpFrame.grid_columnconfigure(1,weight=10)
#        self.SpFrame.grid_columnconfigure(2,weight=1)
#        self.SpFrame.grid_columnconfigure(3,weight=10)
#        self.SpFrame.grid_columnconfigure(4,weight=2)

#        self.SourceRootnameLabel = tk.Label(self.SpFrame,bd=1,
#                                                 text="Product directory:")
#
#        self.SourceRootnameLabel.grid(column=0,row=0,sticky='EWNS')



#        self.SourceRootnameEntry = tk.Entry(self.SpFrame,relief=tk.FLAT,
#                                        textvariable=self.rootname_entry,
#                                            disabledforeground="black")
#        self.rootname_entry.set(self.analysis.name)
#        self.rootname_entry.trace("w",self.rootname_change)
#        self.SourceRootnameEntry.grid(column=1,row=0,columnspan=4,sticky='EW')
#        self.SourceRootnameEntry["state"] = tk.DISABLED
    
#        self.SourceCountsButton = tk.Button(self.SpectrumFrame,
#                                            text="Plot spectrum/background",
#                                        command=self.show_spectra,height=1,
#                                            relief=tk.GROOVE)
#        self.SourceGetspcButton = tk.Button(self.SpectrumFrame,
#                                        text="Extract spectrum",
#                                        command=self.get_spectra_thr,height=1,
#                                            relief=tk.GROOVE)
#        self.SaveSpecBtn = tk.Button(self.SpectrumFrame,
#                                        text="Save spectrum",
#                                        command=self.save_spectrum,height=1,
#                                            relief=tk.GROOVE)
        
#        self.SourceCountsButton.grid(column=1,row=1,sticky='EWNS')
#        self.SourceGetspcButton.grid(column=0,row=1,sticky='EWNS')
#        self.SaveSpecBtn.grid(column=2,row=1,sticky='EWNS')
#        self.SourceChannelsLabel = tk.Label(self.SpFrame,text="Channels:")
#        self.SourceChannelsEntry = tk.Entry(self.SpFrame,textvariable=self.nchan_entry,width=3)
#        self.SourceChannelsLabel.grid(column=0,row=2,sticky='E')
#        self.SourceChannelsEntry.grid(column=1,row=2,sticky='W')
#        self.nchan_entry.set(self.analysis.nchan)


#        self.TimeRangeLabel = tk.Label(self.SpFrame,text='Time Range:')
#        tmin_isok_command = self.register(self.tmin_isok)
#        tmax_isok_command = self.register(self.tmax_isok)
#        self.FilterTminEntry = tk.Entry(self.SpFrame,
#                                    textvariable=self.tmin_entry,validate='all',
#                                    validatecommand=(tmin_isok_command,'%i','%s','%P'))

#        self.FilterTmaxEntry = tk.Entry(self.SpFrame,
#                                    textvariable=self.tmax_entry,validate='all',
#                                    validatecommand=(tmax_isok_command,'%i','%s','%P'))

#        self.TimeRangeLabel.grid(column=0,row=1,sticky='EWNS')

#        self.FilterTLabel = tk.Label(self.SpFrame,text='-')
#        self.FilterTunitLabel = tk.Label(self.SpFrame,text='MET,s')
#        self.FilterTLabel.grid(column=2,row=1,sticky='EW')
#        self.FilterTminEntry.grid(column=1,row=1,sticky='EW')
#        self.FilterTmaxEntry.grid(column=3,row=1,sticky='EW')
#        self.FilterTunitLabel.grid(column=4,row=1,sticky='EW')


#        self.set_spectrum_panel()

# ****** Xspec Frame ( now part of the Spectrum panel)******
        
#        self.XspecFrame = tk.LabelFrame(self.SpectrumFrame,bd=1,
#                                    relief=tk.GROOVE,text="Xspec")

#        self.XspecFrame.grid_columnconfigure(0,weight=1)
#        self.XspecFrame.grid_columnconfigure(1,weight=1)
#        self.XspecFrame.grid_columnconfigure(2,weight=1)
#        self.XspecFrame.grid_columnconfigure(3,weight=1)

#        self.XspecModelLabel = tk.Label(self.XspecFrame,text="Model")
#        list = ('','PowerLaw','LogParabola','PLExpCutoff')
#        self.modelvar.trace("w",self.model_change)
#        self.modelvar.set(self.analysis.spectrum_type)
#        self.XspecModelMenu = tk.OptionMenu(self.XspecFrame,self.modelvar,*list)
#        self.XspecModelLabel.grid(column=2,row=0,sticky='EW')
#        self.XspecModelMenu.grid(column=3,row=0,columnspan=2,sticky='EW')
#        self.XspecRunButton = tk.Button(self.XspecFrame,
#                                        relief=tk.GROOVE,
#                                        text = "Start Xspec")
#        self.XspecRunButton["command"] = self.analyse
#        self.XspecRunButton.grid(column=0,row=0,sticky='EW')
#        self.XspecRunButton["state"] = tk.DISABLED

#        self.XspecPromptLabel = tk.Label(self.XspecFrame,text="xspec>")
#        self.XspecPromptLabel.grid(column=0,row=2,sticky='E')
#        self.xspec_prompt = tk.StringVar()
#        self.XspecPromptEntry = tk.Entry(self.XspecFrame,textvariable=self.xspec_prompt)
#        self.xspec_prompt.set("")
#        self.XspecPromptEntry.grid(column=1,row=2,columnspan=4,sticky='EW')
#        self.XspecPromptEntry["bg"] = 'white'
#        self.XspecPromptEntry.bind("<Return>",self.xspec_prompt_return)        
#        self.XspecPromptEntry["state"]=tk.DISABLED


#        self.FilterEnergyRangeLabel = tk.Label(self.XspecFrame,text='Fit Energy Range:')


 
#        self.FilterELabel = tk.Label(self.XspecFrame,text='-')

#        self.FilterEunitLabel = tk.Label(self.XspecFrame,text='MeV')
#        self.FilterEminEntry = tk.Entry(self.XspecFrame,textvariable=self.emin_entry,
#                                    validate='all',
#                                    validatecommand=(emin_isok_command,'%P'))
#        self.FilterEmaxEntry = tk.Entry(self.XspecFrame,#
#                                    textvariable=self.emax_entry,validate='all',
#                                    validatecommand=(emax_isok_command,'%P'))

#        self.FilterEnergyRangeLabel.grid(column=0,row=1,sticky='E')
#        self.FilterEminEntry.grid(column=1,row=1,sticky='EW')
#        self.FilterELabel.grid(column=2,row=1,sticky='EW')
#        self.FilterEmaxEntry.grid(column=3,row=1,sticky='EW')

#        self.FilterEunitLabel.grid(column=4,row=1,sticky='EW')
        
#        self.FilterEmaxEntry.bind("<Return>",self.emax_enter)
#        self.FilterEminEntry.bind("<Return>",self.emin_enter)

#        self.XspecFrame.grid(column=0,row=4,columnspan=5,sticky='EW')

#   End of Spectrum frame definition


        self.FilterFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.LikeFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
#        self.SpectrumFrame.grid(column=0,row=0,sticky=tk.N+tk.S+tk.E+tk.W)
        self.SettingsFrame.lift()

#  Navigation Buttons

        self.NavSettingsBtn = tk.Button(self.NavFrame,text="Settings",
                                        command=self.nav_settings_btn)
        self.NavPrerequisitesBtn = tk.Button(self.NavFrame,text="Prerequisites",
                                        command=self.nav_prerequisites_btn)
        self.NavLikelihoodBtn = tk.Button(self.NavFrame,text="Likelihood",
                                        command=self.nav_likelihood_btn)
        self.NavModelBtn = tk.Button(self.NavFrame,text="Spectrum",
                                        command=self.nav_model_btn)

        
        self.NavSettingsBtn.grid(column=0,row=0,sticky='EWNS')
        self.NavPrerequisitesBtn.grid(column=1,row=0,sticky='EWNS')
        self.NavLikelihoodBtn.grid(column=3,row=0,sticky='EWNS')
        self.NavModelBtn.grid(column=2,row=0,sticky='EWNS')

        self.nav_settings_btn()
        print self.analysis.all_deg,self.analysis.norm_deg,self.analysis.rad
        

    def open_help(self):
        
        from latlike_help import help_thread

        self.HelpButton["state"] = tk.DISABLED

        self.helpthrd = help_thread()
        self.helpthrd.start()
            
        helpwait = threading.Thread(target=self.help_wait,args=())
        helpwait.start()

    def help_wait(self):
            
        import time

        while self.helpthrd.state == "on":
            time.sleep(1.0)
                
        try:

            self.HelpButton["state"] = tk.NORMAL
        
        except:
            pass


#
# Navigation button commands



    def nav_settings_btn(self):
       
        self.NavSettingsBtn["text"] = ">>Settings<<"
        self.SettingsFrame.lift()
        self.NavModelBtn["text"] = "Model"
        self.NavPrerequisitesBtn["text"] = "Prerequisites"
        self.NavLikelihoodBtn["text"] = "Likelihood"
#        self.NavSpectrumBtn["text"] = "Spectrum"


    def nav_prerequisites_btn(self):
       
        self.FilterFrame.lift()
        self.NavModelBtn["text"] = "Model"
        self.NavPrerequisitesBtn["text"] = ">>Prerequisites<<"
        self.NavLikelihoodBtn["text"] = "Likelihood"
        self.NavSettingsBtn["text"] = "Settings"


    def update_ds9(self,*args):
        

        a = min(self.AllScale.get(),self.NormScale.get())
        n = max(self.NormScale.get(),self.NoneScale.get())
        norm = max(self.AllScale.get(),min(n,self.NormScale.get()))

        self.analysis.none_deg = n
        self.analysis.all_deg = a
        self.analysis.norm_deg = norm
        self.AllScale.set(a)
        self.NormScale.set(norm)
        self.NoneScale.set(n)

        self.show_cat_sources()


    def nav_model_btn(self):
       
        self.ModelFrame.lift()
        self.NavPrerequisitesBtn["text"] = "Prerequisites"
        self.NavLikelihoodBtn["text"] = "Likelihood"
        self.NavModelBtn["text"] = ">>Model<<"
        self.NavSettingsBtn["text"] = "Settings"

        
    def nav_likelihood_btn(self):
       
        self.LikeFrame.lift()
        self.NavLikelihoodBtn["text"] = ">>Likelihood<<"
        self.NavModelBtn["text"] = "Model"
        self.NavPrerequisitesBtn["text"] = "Prerequisites"
#        self.NavSpectrumBtn["text"] = "Spectrum"
        self.NavSettingsBtn["text"] = "Settings"


#    def nav_spectrum_btn(self):
       
#        self.SpectrumFrame.lift()
#        self.NavSpectrumBtn["text"] = ">>Spectrum<<"
#        self.NavLightcurveBtn["text"] = "Lightcurve"
#        self.NavSettingsBtn["text"] = "Settings"
#        self.NavPrerequisitesBtn["text"] = "Prerequisites"

        
#  ***** End of the create_widgets *****


    def set_source_frame(self):
        
        if self.analysis.havedata and len(self.analysis.SourceList):
            selsrc = self.analysis.SourceList[self.analysis.selected_source]

            self.logit(selsrc.name)
            nm = selsrc.name
            if selsrc.assoc_name != "": 
                nm = selsrc.assoc_name
            self.cat_source.set(nm)
            self.source_model.set(selsrc.model)
            self.source_type.set(selsrc.type)
            self.model_parameter.set(selsrc.pars.keys()[0])

            if selsrc.type != "SkyDirFunction":
                self.SourceTemplateMenu["state"] = tk.NORMAL
                self.source_template.set(selsrc.template)
            else:
                self.source_template.set('')
                self.SourceTemplateMenu["state"] = tk.DISABLED

                
#            for s in [self.analysis.SourceList[self.analysis.selected_source]:
#            self.logit(self.analysis.selected_source)
            for p in self.analysis.SourceList[self.analysis.selected_source].pars: 
                self.logit("Par: %s = %s %i"%(self.analysis.SourceList[self.analysis.selected_source].pars[p].name,
                                              self.analysis.SourceList[self.analysis.selected_source].pars[p].value,
                                              self.analysis.SourceList[self.analysis.selected_source].pars[p].fixed))
                    
                

#            self.populate_model_pars_menu()
#            self.set_par()


    def set_par(self):

        if self.analysis.havedata and len(self.analysis.SourceList):
            selsrc = self.analysis.SourceList[self.analysis.selected_source]
            par = self.model_parameter.get()
#            self.logit("%s %s %s"%(par,self.analysis.selected_source,selsrc.name))
            self.model_par_value.set(str(selsrc.pars[par].value))
            self.model_par_scale.set(str(selsrc.pars[par].scale))
            self.par_min_value.set(str(selsrc.pars[par].min))
            self.par_max_value.set(str(selsrc.pars[par].max))
            self.par_fixed.set(selsrc.pars[par].fixed)
#            if self.analysis.selected_source.pars[par].fixed == 1: self.par_fixed.set(0)      
#            if self.analysis.selected_source.pars[par].fixed == 0: self.par_fixed.set(1)
#            for p in self.analysis.selected_source.pars:
#                pa = self.analysis.selected_source.pars[p]
#                self.logit("%s %i"%(p,pa.fixed))


    def set_settings_panel(self):

        self.zmax_entry.set(str(self.analysis.zmax)) 
        self.binsz_entry.set(str(self.analysis.binsz))
        self.dcostheta_entry.set(str(self.analysis.dcostheta))
        self.thetacut_entry.set(str(self.analysis.thetacut))
        self.populate_irfs_menu()

        pass

    def log_data_info(self):

        import pyfits
        import string
        try:

            if self.analysis.havedata:
                
                logstring = ""

                logstring += "Data info:\n"
                logstring += "Data path: "+self.analysis.datapath+"\n"
                
                scf = pyfits.open(self.analysis.scfile)
                logstring += "Extracted:          "+scf[1].header['DATE']+"\n"
                logstring += "Start:              "+scf[1].header['DATE-OBS']+"\n"
                logstring += "Start:              "+scf[1].header['DATE-END']+"\n"
                scf.close()

                logstring += "Time Range:         "+\
                    str(self.analysis.obs_pars["tmin"])+\
                    " - "+str(self.analysis.obs_pars["tmax"])+" MET, sec\n"
                logstring += "Extraction Region:  Circle(RA="+str(self.analysis.obs_pars["RA"])+\
                    ",DEC="+str(self.analysis.obs_pars["DEC"])+",ROI="+\
                    str(self.analysis.obs_pars["roi"])+" deg)\n"
                logstring += "Energy Range:       "+str(self.analysis.obs_pars["emin"])+\
                    " - "+str(self.analysis.obs_pars["emax"])+" MeV"
            else:

                logstring = "No LAT data found."

            self.logit(logstring)



            logstring = "Photon event file(s):\n"
            ff = open('efiles.list','r')
            for li in ff:
                logstring += "    "+string.join(li.split(),'')+"\n"
       
            
            logstring += "Spacecraft data file:\n"
            logstring += "    "+self.analysis.scfile
             
            self.logit(logstring)
            ff.close()


        except:
            pass


        

    def set_filter_panel(self):

        self.ltcube_file.set(self.analysis.ltcube)
        self.filtered_events.set(self.analysis.evfile)
        self.image_file.set(self.analysis.image)
        self.ccube_file.set(self.analysis.ccube)
        self.expcube_file.set(self.analysis.expcube)


    def set_model_panel(self):

        self.set_limits_entry()

    def set_limits_entry(self):
        
        self.rad_entry.set("{:.3f}".format(self.analysis.rad))
        self.norm_deg_entry.set("{:.3f}".format(self.analysis.norm_deg))
        self.all_deg_entry.set("{:.3f}".format(self.analysis.all_deg))
    
    def set_like_panel(self,*arg):

        self.srcmap_file.set(self.analysis.srcmap)
        
        pass


#    def set_spectrum_panel(self,*arg):
#        try:
#            if not self.analysis.havedata:
#                self.tmin_entry.set("")
#                self.tmax_entry.set("")
#                return
#            else:
#                self.rootname_entry.set(self.analysis.name)
#                self.tmin_entry.set(str(self.analysis.obs_pars["tmin"]))
#                self.tmax_entry.set(str(self.analysis.obs_pars["tmax"]))
#                self.emin_entry.set(str(self.analysis.emin))
#                self.emax_entry.set(str(self.analysis.emax))
                
#                self.XspecPromptEntry["state"] = tk.DISABLED
#        except:
#            pass
        

    def logit_to_text(self,s):
        
        self.LogText["state"] = tk.NORMAL

        spl = s.split("\n")
        for l in spl:

            self.LogText.insert(tk.END,l+"\n")
        
            self.LogText.see(tk.END)
        self.LogText["state"] = tk.DISABLED



#    def set_rad(self):
#        self.analysis.rad = float(self.rad_entry.get())

#    def set_norm_deg(self):
#        self.norm_deg = float(self.norm_deg_entry.get())

#    def set_all_deg(self):
#        self.all_deg = float(self.all_deg_entry.get())


    def logerr_to_text(self,s):
        
        self.LogText["state"] = tk.NORMAL

        spl = s.split("\n")
        for l in spl:

            self.LogText.insert(tk.END,l+'\n')
            self.LogText.update()
            self.LogText.tag_add('err',"%s-2l"%tk.END,"%s-1l"%tk.END)
        
        self.LogText.tag_config('err',foreground="red")
        self.LogText.see(tk.END)
        self.LogText["state"] = tk.DISABLED


    def logblue_to_text(self,s):
        
        self.LogText["state"] = tk.NORMAL
        spl = s.split("\n")
        for l in spl:

            
            self.LogText.insert(tk.END,l+'\n')
            self.LogText.update()
            self.LogText.tag_add('blue',"%s-2l-0c"%tk.END,"%s-1l-0c"%tk.END)
        
        self.LogText.tag_config('blue',foreground="blue")
        self.LogText.see(tk.END)
        self.LogText["state"] = tk.DISABLED
        self.LogText.update()

    def tmin_isok(self,why,vbefore,vafter):
        
        try:
            xxx= float(vafter)
         
        except:
            self.tmin_entry.set(vbefore)
            return False

        if xxx < self.analysis.obs_pars["tmin"]:

            self.logit("TMIN should not be less than start time of the obseration!")
            self.tmin_entry.set(vbefore)
            return False
        return True

    def zmax_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.zmax_entry.set(vbefore)
            return False

        if xxx > 180.0 or xxx < 0.0:

            self.logit("Zmax should be in the [0:180] range.")
            self.zmax_entry.set(vbefore)
            return False
        return True

    def binsz_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.binsz_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logit("Binsz can take only positive values.")
            self.binsz_entry.set(vbefore)
            return False

        self.analysis.binsz = xxx
        return True


    def src_ra_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.src_ra_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logit("Invalid RA value {0}."%xxx)
            self.src_ra_entry.set(vbefore)
            return False
        self.analysis.ra = float(xxx)
        self.catsourceid()
        if int(why) >= 0:
            self.show_cat_sources()
        return True



    def norm_flux_isok(self,why,vbefore,vafter):    

        try:
            xxx = float(vafter)
            
        except:
            self.norm_flux_entry.set(vbefore)
            return False

        if xxx < -0.0:

            self.logerr("Flux limit can not be negative."%vafter)
            self.norm_flux_entry.set(vbefore)
            return False
        self.norm_flux = float(xxx)
#        self.catsourceid()
#        if int(why)>=0: 
#            self.show_cat_sources()
        return True

    def rad_isok(self,why,vbefore,vafter):    

        try:
            xxx = float(vafter)
            
        except:
            self.rad_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logerr("Radius can not be negative.")
            self.rad_entry.set(vbefore)
            return False
        self.analysis.rad = float(xxx)
        if int(why)>=0: self.show_cat_sources()
        return True

    def norm_deg_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.norm_deg_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logerr("Radius can not be negative.")
            self.norm_deg_entry.set(vbefore)
            return False
        self.analysis.norm_deg = float(xxx)
        if int(why)>=0: self.show_cat_sources()
        return True

    def all_deg_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.all_deg_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logerr("Radius can not be negative.")
            self.all_deg_entry.set(vbefore)
            return False
        self.analysis.all_deg = float(xxx)
        if int(why)>=0: self.show_cat_sources()
        return True


    def dcostheta_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.dcostheta_entry.set(vbefore)
            return False

        if xxx < 0.0:

            self.logit("Dcostheta can take only positive values.")
            self.dcostheta_entry.set(vbefore)
            return False
        self.analysis.dcostheta = xxx
        return True

    def thetacut_isok(self,why,vbefore,vafter):    
        try:
            xxx = float(vafter)
            
        except:
            self.thetacut_entry.set(vbefore)
            return False

        if xxx < 0.0 or xxx > 90.0:

            self.logit("Thetacut can take only values betweeen 0 and 90.0.")
            self.thetacut_entry.set(vbefore)
            return False
        self.analysis.thetacut = xxx

        return True


    def tmax_isok(self,why,vbefore,vafter):
        
        try:
            xxx= float(vafter)
         
        except:
            self.tmax_entry.set(vbefore)
            return False

        if xxx > self.analysis.obs_pars["tmax"]:

            self.logit("TMAX should not be greater than start time of the obseration!")
            self.tmax_entry.set(vbefore)
            return False
        return True


    def emin_isok(self,vafter):
        

        try:
            xxx= float(vafter)
         
        except:

            return False
        return True

    def emin_enter(self,*arg):

        txt = self.emin_entry.get()
        xxx= float(txt)

        if xxx < self.analysis.obs_pars["emin"] or xxx < 100.0:

            self.logerr("EMIN should not be less than 100 MeV or the minimum energy ("+
                        str(self.analysis.obs_pars["emin"])+" MeV) of the data.")
            self.emin_entry.set(str(max(100.0,self.analysis.emin)))
        
        return

    def lc_emin_enter(self,*arg):

        txt = self.lc_emin_entry.get()
        xxx= float(txt)

        if xxx < self.analysis.obs_pars["emin"]:

            self.logerr("EMIN should not be less than 100 MeV or the minimum energy ("+
                        str(self.analysis.obs_pars["emin"])+" MeV) of the data!")
            self.lc_emin_entry.set(str(self.analysis.emin))

        return

    def emax_isok(self,vafter):

        try:
            xxx= float(vafter)         
        except:
            return False

        return True

    def emax_enter(self,*arg):

        txt = self.emax_entry.get()
        xxx= float(txt)
         
        if xxx > self.analysis.obs_pars["emax"]:

            self.logerr("EMAX should not be greater than maximum energy ("+
                        str(self.analysis.obs_pars["emax"])+
                        " MeV) of the data!")
            self.emax_entry.set(str(self.analysis.emax))

            return
        self.analysis.emax = xxx
        return

    def lc_emax_enter(self,*arg):

        txt = self.lc_emax_entry.get()
        xxx= float(txt)

        if xxx < self.analysis.obs_pars["emin"]:

            self.logerr("EMAX should not be greater than maximum energy("+
                        str(self.analysis.obs_pars["emax"])+" MeV) of the data!")
            self.lc_emax_entry.set(str(self.analysis.emin))

        return


    def populate_cat_source_menu(self):

        if not self.analysis.havedata: return

        try:
            self.CatSourceMenu["menu"].delete(0, tk.END)

            for s in self.analysis.SourceList:
                src = self.analysis.SourceList[s]
                n = src.name
                if src.assoc_name != "": n = src.assoc_name
                self.CatSourceMenu["menu"].add_command(label=n, 
                                        command=lambda temp = n: 
                                        self.CatSourceMenu.setvar(self.CatSourceMenu.cget("textvariable"), value = temp))
#            self.cat_source.set(self.analysis.fgl_source)
        except:
            pass

    def populate_source_model_menu(self):

        if not self.analysis.havedata: return

        try:
            self.SourceModelMenu["menu"].delete(0, tk.END)


            models = ["PowerLaw","LogParabola","PLExpCutoff"]
            for m in models: 
                self.SourceModelMenu["menu"].add_command(label=m, 
                                        command=lambda temp = m: 
                                        self.SourceModelMenu.setvar(self.SourceModelMenu.cget("textvariable"), value = temp))

        except:
            pass



    def populate_source_template_menu(self):

        if not self.analysis.havedata: return

        try:
            self.SourceTemplateMenu["menu"].delete(0, tk.END)


            temps = self.analysis.templates
            for m in temps: 
                self.SourceTemplateMenu["menu"].add_command(label=m, 
                                        command=lambda temp = m: 
                                        self.SourceTemplateMenu.setvar(self.SourceTemplateMenu.cget("textvariable"), value = temp))

        except:
            pass

    def populate_model_pars_menu(self):

        self.ModParMenu["menu"].delete(0, tk.END)
        if not self.analysis.havedata or len(self.analysis.SourceList) == 0:
            return

        for p in self.analysis.SourceList[self.analysis.selected_source].pars:
            self.ModParMenu["menu"].add_command(label=p,
                         command=lambda temp = p: 
                         self.ModParMenu.setvar(self.ModParMenu.cget("textvariable"),
                                    value = temp))
        
        self.model_parameter.set(p)
        


    def populate_irfs_menu(self):

        irf = subprocess.Popen(["gtirfs"],stdout=subprocess.PIPE).communicate()[0]
#        irf = fff.readlines()
#        print irf
        
       
        for s in str(irf).split("\n"):
            self.IrfsMenu["menu"].add_command(label=s, 
                                        command=lambda temp = s: 
                                        self.IrfsMenu.setvar(self.IrfsMenu.cget("textvariable"),
                                                                  value = temp))
#            if s[0:self.analysis.irfs.__len__()] == self.analysis.irfs:
            if s.split(" ")[0] == self.analysis.irfs:
                self.irfs.set(s)

    def populate_source_type_menu(self):

        if not self.analysis.havedata: return
        self.SourceTypeMenu["menu"].delete(0, tk.END)


        for s in ["SkyDirFunction","SpatialMap","MapCubeFunction","ConstantValue"]:
            self.SourceTypeMenu["menu"].add_command(label=s,command=lambda temp = s: 
                                        self.SourceTypeMenu.setvar(self.SourceTypeMenu.cget("textvariable"),
                                                                  value = temp))
#            if s[0:self.analysis.irfs.__len__()] == self.analysis.irfs:
#            if s.split(" ")[0] == self.analysis.irfs:
#                self.irfs.set(s)
 

    def set_scales(self):

        self.NoneScale.set(self.analysis.none_deg)
        self.AllScale.set(self.analysis.all_deg)
        self.NormScale.set(self.analysis.norm_deg)
        
    def irfs_change(self,*arg):

        st = self.irfs.get()
        s = st.split(" ")
        self.analysis.irfs = s[0]
#        print self.analysis.irfs


    def source_template_change(self,*args):
        
        self.analysis.SourceList[self.analysis.selected_source].template = self.source_template.get()

        pass

    def source_model_change(self,*arg):
        
        model = self.source_model.get()
#        selsrc = self.analysis.SourceList[self.analysis.selected_source]
        if not self.analysis.SourceList[self.analysis.selected_source].model == model:
            self.analysis.SourceList[self.analysis.selected_source].model = model
#            print "model change"
            self.analysis.SourceList[self.analysis.selected_source].pars = self.analysis.default_pars(model)

#        pset = False
#        if ('Prefactor' in self.analysis.SourceList[self.analysis.selected_source].pars):
        self.model_parameter.set(self.analysis.SourceList[self.analysis.selected_source].pars.keys()[0])
#            pset = True
#        elif ('index' in self.analysis.SourceList[self.analysis.selected_source].pars) and not pset:
#            self.model_parameter.set('index')
#            pset = True
#        elif ('alpha' in self.analysis.SourceList[self.analysis.selected_source].pars) and not pset:
#            self.model_parameter.set('alpha')
        self.populate_model_pars_menu()
#        self.set_par()


    def model_par_change(self,*arg):
        
        self.set_par()
        

    def source_type_change(self,*arg):
        

        selsrc = self.analysis.SourceList[self.analysis.selected_source]
        selsrc.type = self.source_type.get()   

        if selsrc.type in ["SpatialMap","MapCubeFunction","ConstantValue"]:
            self.SourceTemplateMenu["state"] = tk.NORMAL
            self.source_template.set(selsrc.template)
        else:
            self.source_template.set('')
            self.SourceTemplateMenu["state"] = tk.DISABLED    


    def par_fixed_change(self,*arg):
        
        self.analysis.SourceList[self.analysis.selected_source].pars[self.model_parameter.get()].fixed = self.par_fixed.get()

    def cat_source_change(self,*arg):

#        from coorconv import loffset,eq2gal,gal2eq,dist
#        from fgltools import get_fgl_source_coords

        if self.skipch: return

        sname = self.cat_source.get()

        for s in self.analysis.SourceList:
            src = self.analysis.SourceList[s]
            if src.name == sname or src.assoc_name == sname:
                self.analysis.selected_source = s
#        print sname,self.analysis.selected_source.name,self.analysis.selected_source.assoc_name
        self.analysis.selected_ra = self.analysis.SourceList[self.analysis.selected_source].ra
        self.analysis.selected_dec = self.analysis.SourceList[self.analysis.selected_source].dec
        
        self.analysis.set_names()

        try:
            self.rootname_entry.set(self.analysis.name)
            self.modelvar.set(self.analysis.spectrum_type)
        except:
            pass
        
        self.show_cat_sources()
        self.set_source_frame()


        return

    def show_cat_sources(self):

        try:       
            ds9_poll = self.analysis.ds9.poll()            
        except:
            pass
        else:
            if ds9_poll == None:
                self.analysis.write_regions()
                lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,"regions","delete","all"])
                lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,
                                        "regions","file",self.analysis.basename+'.reg'])




    def dist_isok(self,why,vbefore,vafter):
        
        try:
            xxx= float(vafter)
         
        except:
            self.dist_tres.set(vbefore)
            return False

        if xxx < 0.0 :

            self.logit("Source distance threshold should not be less than zero!")
            self.dist_tres.set(vbefore)
            return False

        self.analysis.dist_tres = xxx
        self.analysis.set_names()
        self.cat_source.set(self.analysis.assoc_source)
        self.rootname_entry.set(self.analysis.name)
        return True


#    def xspec_session(self):

#        import time

#        logfile = self.analysis.name+'/'+self.analysis.name+'_xspec.log'
#        os.system('rm -f '+logfile+'\n')
#        filo = open(logfile,'w')
#        self.xs_proc = subprocess.Popen(['xspec'],bufsize=0,stdin=subprocess.PIPE,stdout=filo,stderr=filo)
#        infile =  self.xs_proc.stdin

#        infile.write('query yes\n')
#        infile.write("cd "+self.analysis.name+'\n')
#        infile.write('data '+self.analysis.specfile+'\n')   
#        self.xs_fil = open(logfile,'r')
#        infile.write('ignore **-100000.0 100000000.0-**\n')

#        if self.analysis.haveCatalog and self.analysis.fgl_source != "None": 
#            if self.analysis.spectrum_type == "PowerLaw": 
#                infile.write("model cflux*pow & 100000 -1 0 0 1e10 1e10 & 100000000 -1  0 0 1e10 1e10 & -8.0 0.01 &  {0} 0.01 & 1.0 -1 & \n".format(self.analysis.fgl_powerlaw_index))
#            if self.analysis.spectrum_type == "LogParabola": 
#                infile.write("model cflux*logpar & 100000 -1 0 0 1e10 1e10 & 100000000 -1  0 0 1e10 1e10 & -8.0 0.01 & {0} 0.01 & {1} 0.01 & {2} 0.01 & 1.0 -1 &\n".format(self.analysis.fgl_powerlaw_index,self.analysis.fgl_beta,self.analysis.fgl_pivot_e*1000.0))
#            if self.analysis.spectrum_type == "PLExpCutoff": 
#                infile.write("model cflux*powerlaw*spexpcut & 100000 -1 0 0 1e10 1e10 & 100000000 -1  0 0 1e10 1e10 & -8.0 0.01 & {0} 0.01 & 1.0 -1 & {1} 0.01 0.0 0.0 1.0e10 1.0e10 & -0.3 -0.01 &\n".format(self.analysis.fgl_powerlaw_index,float(self.analysis.fgl_cutoff_e)*1000.0))
 
#        else:
#            infile.write('model cflux*pow & 100000 -1 0 0 1e10 1e10 & 100000000 -1  0 0 1e10 1e10 & -8.0 0.01 &  2.0 0.01 & 10.0 0.1 & \n')
#            print "Here"
#        infile.write("renorm\n")
#        infile.write("fit\n")
#        infile.write("cpd /xw\n")
#        infile.write("setplot energy\n")
#        infile.write("plot ldata del\n")
#        infile.write("iplot\n")
#        infile.write("label T \"{0}\"\n".format(self.analysis.assoc_source))
#        infile.write("time off\n")
#        infile.write("p\n")
#        infile.write("q\n")
#        time.sleep(0.5)
#        self.logit(self.xs_fil.read())
        

#    def save_xcm(self):
#        try:
#            self.xs_proc.stdin.write("save all "+self.analysis.name+".xcm\n")
#        except:
#            self.logerr("Error saving Xspec session. Try \"Start Xspec\".")
#        else:
#           self.logit("Xspec session is saved to "+self.analysis.name+".xcm.") 

#    def analyse(self):

#        import sys
#        import time

#        try:
#            p = self.xs_proc.poll()

#        except:
            
#            if not os.path.exists(self.analysis.name+'/'+self.analysis.specfile) \
#               and not os.path.exists(self.analysis.name+'/'+self.analysis.bkgfile) \
#               and not os.path.exists(self.analysis.name+'/'+self.analysis.rspfile)  \
#               and not os.path.exists(self.analysis.name+'/'+self.analysis.arffile) :
            
#                self.logerr("There is no spectrum yet. Use \"Extract  Spectrum\" button first!")
#                return
#            else:

#                self.XspecRunButton["text"] = "Quit Xspec"
#                self.XspecPromptEntry["state"]=tk.NORMAL      
#                self.xspec_session()
#                time.sleep(0.2)

#        else:

#            if p == None:

 #               self.xs_proc.terminate()
  #              self.xs_proc.kill()
  #              self.XspecRunButton["text"] = "Start Xspec"
  #              self.XspecPromptEntry["state"]=tk.DISABLED

 #           else:
#                self.XspecRunButton["text"] = "Quit Xspec"
#                self.xspec_session()
#                self.XspecPromptEntry["state"]=tk.NORMAL



#    def rootname_change(self,*args):
        
#        xxx = self.rootname_entry.get()
#        self.analysis.specfile = xxx+'_src.pha'
#        self.analysis.bkgfile = xxx+'_bkg.pha'
#        self.analysis.rspfile = xxx+'.rsp'
#        self.analysis.arffile = xxx+'.arf'
        

#    def model_change(self,*args):

#        xxx = self.modelvar.get()
#        if self.analysis.spectrum_type != xxx:
            
#            self.analysis.spectrum_type = xxx
#            if self.analysis.spectrum_type == "LogParabola":
#                if self.analysis.fgl_beta == "INDEF": self.analysis.fgl_beta = 0.5
#                if self.analysis.fgl_beta == "INDEF": self.fgl_pivot_e = 200.0
#            if self.analysis.spectrum_type == "PLExpCutoff":
#                if self.analysis.fgl_cutoff_e == "INDEF": self.analysis.fgl_cutoff_e = 500000.0

    def getCube(self):

        """Generates a livetime cube"""


        self.ltcube_stop = False

        run = 0
        try:

            ltcube_poll = self.ltcube_proc.poll()

        except:
            
            run = 1

        else:

#            print "Mark1 ",ltcube_poll
            if ltcube_poll == None:
                
                self.logit("Stopping GTLTcube calculation.")
                self.ltcube_proc.kill()
                self.SourceLtcubeButton["text"] = "Run CTLTcube"


            else:

               run = 1
                
        if run:

            if not os.path.exists(self.analysis.evfile):
                self.logerr("CTLTcube extractor:\nEvent file is not available. Can't calculate cube without it.")
                self.logblue("Hint: Click on \"Filter events\" button.")
                return

            logstring  = "*** Running GTLTCUBE with parameters:\n"
            self.SourceLtcubeButton["text"] = "Stop GTLTcube"


            outfile = self.analysis.basename+'_ltcube.fits'
            evfile = self.analysis.evfile
            scfile = self.analysis.scfile
            dcostheta = self.analysis.dcostheta
            binsz = self.analysis.binsz
            zmax = self.analysis.zmax
            res_str = ""

            logstring += "    evfile  = "+evfile+"\n"
            logstring += "    scfile  = "+scfile+"\n"
            logstring += "    outfile = "+outfile+"\n"
            logstring += "    dcostheta  = "+str(dcostheta)+"\n"
            logstring += "    binsz  = "+str(binsz)+"\n"
            logstring += "    zmax  = "+str(zmax)
            
            self.logit(logstring)

            if os.path.exists(outfile):

                oldfile = "old"+str(os.getpid())+"_"+outfile
                self.logit("The file "+outfile+" exists. Move it to "+oldfile+".")
                os.system("mv -f "+outfile+" "+oldfile)

            self.ltcube_proc = subprocess.Popen(["gtltcube",evfile,scfile,outfile,
                                             str(dcostheta),str(binsz),"zmax="+str(zmax)],
                                            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            ltcube_thread = threading.Thread(target=self.ltcube_wait,args=())
            ltcube_thread.start()

            self.ltcube_file.set("calculating...")
            self.SourceLtcubeFileLabel.update()

        return

    def ltcube_wait(self):

        import time
        
        while not self.ltcube_stop:

            time.sleep(1.0)

            try:       

                cube_poll = self.ltcube_proc.poll()


            except:        

                # this should not happen
                break

#
            else:
                if cube_poll == None:  
                    continue
                else:
                    break


        self.logblue("GTLTCUBE finished.\nGalactic cube is saved to "+self.analysis.basename+"_ltcube.fits")
        self.SourceLtcubeButton["text"] = "Run GTLTcube"

        if self.ltcube_proc.returncode:
            self.analysis.ltcube = 'None'

        else:
            self.analysis.ltcube = self.analysis.basename+'_ltcube.fits'

        self.ltcube_file.set(self.analysis.ltcube)            
        return 
            
#    def get_spectra_thr(self):
        
#        from llthreads import spectrum_thread

#        if not self.analysis.havedata:
#            self.nodata()
#            return -1

#        run = int(0)

#        try:
#            state = self.specthread.state
#        except Exception as e:
#            print "1",e
#            run = int(1)
#        else:
 #           print "2 ",state
#            if state != "running":
#                run = int(1)
#            else:
#                self.specthread.stop()


 #       eemin = max(float(self.analysis.obs_pars["emin"]),100.0)
 #       if (float(self.analysis.obs_pars["emin"]) < 100.0):
 #           self.logit("Warning: Minimum energy for spectrum extraction is set to 100.0 MeV. ")

#        if run:

#            self.logblue("Starting spectrum calculation.")

#            try:
#                subprocess.Popen(["mkdir",self.analysis.name],
#                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#            except:
#                pass

#            self.specthread = spectrum_thread(self.analysis.evfile,self.analysis.scfile,
#                                      self.analysis.ra,self.analysis.dec,self.analysis.rad,
#                                      self.analysis.bkg_ra,self.analysis.bkg_dec,self.analysis.bkg_rad,
#                                      tmin=float(self.tmin_entry.get()),tmax=float(self.tmax_entry.get()),
#                                      emin=eemin,
#                                      emax=float(self.analysis.obs_pars["emax"]),
#                                      enbin=self.nchan_entry.get(),
#                                      irfs=self.analysis.irfs,
#                                      cube=self.analysis.ltcube,outroot=self.analysis.name,
#                                      dcostheta=float(self.dcostheta_entry.get()),
#                                      thetamax=float(self.thetacut_entry.get()),
#                                      binsz=float(self.binsz_entry.get()),
#                                      zmax=float(self.zmax_entry.get()),
#                                      logqueue = self.logQueue)

#            self.specthread.start()
#            specthread_wait = threading.Thread(target = self.spectrum_wait,args=())
#            specthread_wait.start() 
#            self.SourceGetspcButton["text"] = "Stop extracting spectrum"


#    def spectrum_wait(self):
        
#        import time
        
#        while self.specthread.state != "stopped" and self.specthread.state != "done" :

#            time.sleep(0.5)


#        if self.specthread.state == "done":

#            lcf = self.lc_file.get()
#            os.system("mv "+self.analysis.name+"_src.pha "+" "+self.analysis.name+'/'+self.analysis.name+"_src.pha")
#            os.system("mv "+self.analysis.name+"_bkg.pha "+" "+self.analysis.name+'/'+self.analysis.name+"_bkg.pha")
#            os.system("mv "+self.analysis.name+".rsp "+" "+self.analysis.name+'/'+self.analysis.name+".rsp")
#            os.system("mv "+self.analysis.name+".arf "+" "+self.analysis.name+'/'+self.analysis.name+".arf")
#            self.logblue("Finished extracting spectrum.\n"+\
#            "     Spectrum:  "+self.analysis.name+'/'+self.analysis.name+"_src.pha\n"+\
#            "     Background:"+self.analysis.name+'/'+self.analysis.name+"_bkg.pha\n"+\
#            "     Response:  "+self.analysis.name+'/'+self.analysis.name+".rsp\n"+\
#            "     Arf:       "+self.analysis.name+'/'+self.analysis.name+".arf")
            
#            self.logblue("To see the plot of source and background spectra versus channels,\npress \"Plot spectrum/background\". Press \"Save spectrum\" to save files in different location. To analyse spectrum in Xspec press \"Start Xspec\".")

#        if self.specthread.state == "stopped":

#            self.logerr("Spectrum extraction aborted.") 

#        self.SourceGetspcButton["text"] = "Extract spectrum"
    

#    def save_spectrum(self):
#        import string
#        from tkMessageBox import askquestion

#        spcf = self.analysis.name+'/'+self.analysis.name+"_src.pha"
#        bkgf = self.analysis.name+'/'+self.analysis.name+"_bkg.pha"
#        rspf = self.analysis.name+'/'+self.analysis.name+".rsp"
#        arff = self.analysis.name+'/'+self.analysis.name+".arf"

#        if ( not os.path.exists(spcf) or not os.path.exists(bkgf) or \
#                 not os.path.exists(rspf) or not os.path.exists(arff)):
#            self.logerr("Warning: one or more spectral products are not found.")
        
#        fopt = options = {}
#        options['defaultextension'] = ''
#        options['filetypes'] = [('PHA files','*.pha')]
#        if (self.analysis.fgl_source != "None"):
#            initname = string.join(string.split(self.analysis.fgl_source," "),"")
#        else:
#            initname = "ra%.2f_dec%.2f_r%.2f"%(self.analysis.ra,self.analysis.dec,
#                                               self.analysis.rad)
#        initname = self.analysis.name+'_src'
#        options['initialfile'] = initname
#        options['parent'] = root
#        options['title'] = 'Save spectrum'
#        fname = tkFileDialog.asksaveasfilename(**fopt)
#        if (fname == ""): return
        
#        print fname
#        bfname = os.path.basename(fname)
#        if (os.path.exists(fname+"_src.pha") or os.path.exists(fname+"_bkg.pha") or \
#                os.path.exists(fname+".rsp") or os.path.exists(fname+".arf")):
#            ans = askquestion("Files exist","One or more files "+os.path.basename(fname)+"* exist in this location. Replace?")
#            if (ans): 
#                os.system("rm -f "+fname+"_src.pha "+fname+".rsp "+fname+"_bkg.pha "+fname+".arf ")
#            else:
#                return


#        try:
#            os.system("cp "+spcf+" "+fname+"_src.pha")
#            os.system("cp "+bkgf+" "+fname+"_bkg.pha")
#            os.system("cp "+rspf+" "+fname+".rsp")
#            os.system("cp "+arff+" "+fname+".arf")

#            os.system("fparkey "+bfname+"_bkg.pha "+fname+"_src.pha BACKFILE")
#            os.system("fparkey "+bfname+".rsp "+fname+"_src.pha RESPFILE")
#            os.system("fparkey "+bfname+".arf "+fname+"_src.pha BACKFILE")

#        except:
#            self.logerr("Error occured when saving spectrum. Check you results.")
#            return

#        else:
#            self.logblue("Spectrum sucessfully saved to\n"+\
#            "Source spectrum:     "+fname+"_src.pha\n"+\
#            "Background spectrum: "+fname+"_bkg.pha\n"+\
#            "Response:            "+fname+".rsp\n"+\
#            "Ancillary response:  "+fname+".arf")
           

#    def show_spectra(self):

#        if not os.path.exists(self.analysis.name+'/'+self.analysis.specfile):
            
#            self.logerr("There is no spectrum yet. Use \"Extract  Spectrum\" button first!")
#            return

#        try:
#            pr = self.xspec_proc.poll()
#        except:
          
#            self.xspec_proc = subprocess.Popen(['xspec'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
#            fil = self.xspec_proc.stdin 
#            fil.write("cd "+self.analysis.name+'\n')
#            fil.write('data 1 '+self.analysis.specfile+'\n')
#            fil.write('backgrnd 1 none\n')
#            fil.write('data 2 '+self.analysis.bkgfile+'\n')
#            fil.write('backgrnd 1 none\n')
#            fil.write("cpd \/xw\n")
#            fil.write("setplot ch\n")
#            fil.write('plot ldata\n')
            
#            fil.write("iplot\n")
#            fil.write("LAB T RED - BACKGROUND \n")
#            fil.write("LAB OT BLACK - SOURCE - BLACK \n")
#            fil.write("plot\n")
    
            

 #           self.SourceCountsButton["text"] = "Hide spectrum/background" 

#        else:
#            if pr == None:
#                try:
#                    self.xspec_proc.terminate()
#                    self.xspec_proc.kill()
#                except:
#                    pass
#                self.SourceCountsButton["text"] = "Plot spectrum/background" 
                
#            else:

#                self.xspec_proc = subprocess.Popen(['xspec'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
#                fil = self.xspec_proc.stdin 
#                fil.write("cd "+self.analysis.name+'\n')
#                fil.write('data 1 '+self.analysis.specfile+'\n')
#                fil.write('data 2 '+self.analysis.bkgfile+'\n')
#                fil.write("cpd \/xw\n")
#                fil.write("setplot ch\n")
#                fil.write('plot ldata\n')
#                self.SourceCountsButton["text"] = "Hide counts spectrum/background" 


    def run_likelihood(self):
        
        from llthreads import like_thread

        if not self.analysis.havedata:
            self.nodata()
            return -1

        run = int(0)

        try:
            state = self.lsthread.state
        except Exception as e:
#            print "1",e
            run = int(1)
        else:
 #           print "2 ",state
            if state != "running":
                run = int(1)
            else:
                self.lsthread.state = "stopped"


        if run:

            self.analysis.write_xml_model()
            self.logblue("Starting likelihood calculation.")

#            lcf = self.lc_file.get()
#             lcf = self.analysis.name+'_'+self.lc_bin.get()+'.lc'

            pl_free = True
            if self.lc_index_fixed.get(): pl_free = False

#        res = latspeclc(self.analysis.evfile,self.analysis.scfile,

            try:
                subprocess.Popen(["mkdir",self.analysis.name],
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            except:
                pass

            self.likethread = like_thread(self.analysis.evfile,self.analysis.scfile,
                                      self.analysis.ra,self.analysis.dec,
                                      self.analysis.rad,
                                      self.analysis.bkg_ra,self.analysis.bkg_dec,self.analysis.bkg_rad,
                                      emin=float(self.lc_emin_entry.get()),
                                      emax=float(self.lc_emax_entry.get()),
                                      irfs=self.analysis.irfs,
                                      pl_index=float(self.lc_pl_index.get()), index_free = pl_free,
                                      cube=self.analysis.ltcube,outfile=self.analysis.name+'/'+lcf,
                                      tbin=self.lc_tres,dcostheta=float(self.dcostheta_entry.get()),
                                      logqueue = self.logQueue)

            self.likethread.start()
            likethread_wait = threading.Thread(target = self.like_wait,args=())
            likethread_wait.start() 
            self.LikeRunBtn["text"]= "Stop Likelihood"
            
    def ls_wait(self):
        
        import time
        

        while self.lsthread.state != "stopped" and self.lsthread.state != "done" :

            time.sleep(0.5)


        if self.lsthread.state == "done":

#            lcf = self.lc_file.get()
            lcf = self.analysis.name+'_'+self.lc_bin.get()+'.lc'
            self.lc_file.set(lcf)
            self.logblue("Finished producing lightcurve.\n" + \
            "Lightcurve file is saved to "+self.analysis.name+'/'+lcf+".  Press \"Show lightcurve\" to see the lightcurve. Press \"Save lightcurve\" to save the file in different location.")


        if self.lsthread.state == "stopped":

            self.logerr("Lightcurve extraction aborted.") 

        self.LcExtBtn["text"]= "Extract Lightcurve"


    def plot_lc(self):
        
        try:
            fplot_poll = ""
            fplot_poll = self.lcplot_proc.poll()
        except:
            pass
              
        if fplot_poll == None:
            self.lcplot_proc.stdin.write("quit\n")
            self.LcShowBtn["text"] = "Show Lightcurve"
        else:

            lcf = self.analysis.name+'/'+self.analysis.name+'_'+self.lc_bin.get()+'.lc'
            if not os.path.exists(lcf):
                self.logerr("Lightcurve file is not available.")
                self.logblue("Create lightcurve by pressing \"Extract lightcurve\" button.")
                return
# If index is free then show flux and index, otherwise just flux
            ystr = "FLUX[ERROR] INDEX[INDEXERR]"
            if self.lc_index_fixed.get(): ystr = "FLUX[ERROR]"
            
            if os.path.exists(lcf):
                self.lcplot_proc = subprocess.Popen(["fplot",lcf,
                                                     "TIME",ystr,"-",
                                                     "/xw","line step;plot;"],
                                                    stdout=subprocess.PIPE,
                                                    stdin=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
                self.LcShowBtn["text"] = "Hide Lightcurve"
        return



    def save_lightcurve(self):
#        from tkMessageBox import askquestion
        
        lcf = self.analysis.name+'/'+self.analysis.name+'_'+self.lc_bin.get()+'.lc'
        if ( not os.path.exists(lcf)):
#            self.logerr("Error saving lightcurve: file not found.")
            self.logerr("Lightcurve file is not available.")
            self.logblue("Create lightcurve by pressing \"Extract lightcurve\" button.")
            return;
        
        fopt = options = {}
        options['defaultextension'] = '.fits'
        options['filetypes'] = [('All files','*.*'),('LC files','*.lc'),('FITS files','*.fits')]
        options['initialfile'] = self.analysis.name+'_'+self.lc_bin.get()+'.lc'
#        options['parent'] = root
        options['title'] = 'Save lightcurve'
        fname = tkFileDialog.asksaveasfilename(**fopt)
        if fname == "": return;
#        print fname
        bfname = os.path.basename(fname)
#        if (os.path.exists(fname)):
#            ans = askquestion("File exists","File:"+os.path.basename(fname)+" exists\nin this location.Replace?")
#            if (ans): 
#                os.system("rm -f "+fname)
#            else:
#                return
        try:
            os.system("cp "+lcf+" "+fname)

        except:
            self.logerr("Error occured when saving lightcurve. Check you results.")

        else:
            self.logblue("Lightcurve sucessfully saved to "+fname)


    def flux_tres_rtrn(self,event):
#        import subprocess
        xxx = self.flux_entry.get()
        try:
            yyy = float(xxx)
        except:
            self.flux_entry.set(self.analysis.fluxTres)
        else:

            self.analysis.fluxTres = float(xxx)
            self.flux_entry.set(self.analysis.fluxTres)
            self.populate_cat_source_menu()
            try:       
                ds9_poll = self.analysis.ds9.poll()
            except:
                pass
            else:
                if ds9_poll == None:
                    self.analysis.write_regions()
                    lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,"regions","delete","all"])
                    lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,
                                            "regions","file",self.analysis.basename+'.reg'])

        return

            

    def basename_return(self,event):

        li = self.basename_entry.get()
        xxx = li.split()
        if len(xxx)>1: 
            self.logit("Basename should not contain spaces!!!")
            self.basename_entry.set(self.analysis.basename)
            return
        
        xxx = li.split("/")
        if len(xxx)>1: 
            self.logit("Basename should not contain slashes!!!")
            self.basename_entry.set(self.analysis.basename)
            return
        if li == "":
            self.logit("Basename can not be empty string.")
            self.basename_entry.set(self.analysis.basename)
            return
        
        self.analysis.basename = li
        self.analysis.ltcube = li+'_ltcube.fits'
        self.analysis.set_names()
        self.set_filter_panel()
#        self.ImageLself.analysis.image
        self.rootname_entry.set(self.analysis.name)
#        self.set_ltcube_ckbtn()
#        self.XspecRunButton["state"] = tk.DISABLED
#        self.clear_model()
        try:
            self.analysis.ds9.terminate()
            self.xs_proc.kill()
            self.xs_fil.close()
            self.XspecPromptEntry["state"] = tk.DISABLED
            self.XspecRunButton["state"] = tk.NORMAL
        except:
            pass


    def run_ds9(self):

        """
        Invokes ds9 and predefines regions.
        If catalog is available, puts 2FGL sources, which are brighter
        than <flux_tres> parameter.

        """

        import time

        if not self.analysis.havedata:
            self.nodata()
            return

        if not os.path.exists(self.analysis.image):
            self.logerr("You need to extact image first! Use \"Extract\" button.")
            return

        try:       
            ds9_poll = self.analysis.ds9.poll()

        except:

            self.analysis.ds9 = self.analysis.runds9()
            self.ds9_thread = threading.Thread(target = self.ds9wait,args=())
            self.ds9_thread.start()
            self.ImageDS9Button["text"] = "Stop ds9"
            self.logblue("Opening ds9 session to edit/verify regions.The source region is shown in green,\nbackground region is red. DO NOT ADD or DELETE regions!")

            if self.analysis.haveCatalog:
                self.logblue("Hint: you can place the source region over a Catalog source by choosing \nthe source name in the \"2FGL source\" menu.")

        else:

            if ds9_poll == None:

                lget = subprocess.call(["xpaset","-p",self.analysis.ds9id,"exit"])

                self.logit("DS9 session finished.")
            else:

                self.analysis.ds9 = self.analysis.runds9()
                self.ds9_thread = threading.Thread(target = self.ds9wait,args=())
                self.ds9_thread.start()
                self.ImageDS9Button["text"] = "Stop ds9"
                self.logblue("Opening ds9 session to edit/verify regions.The source region is shown in green,\nbackground region is red. DO NOT ADD or DELETE regions!")
                if self.analysis.haveCatalog:
                    self.logblue("Hint: you can jump to a Catalog source by using \"2FGL source\" menu.")

        return


    def ds9wait(self):
        
        
        import time
        xpa_response = "no"
        nwait = 0
        while xpa_response.strip() != "yes" and nwait < 30:
            time.sleep(0.2)
            xpa_response = subprocess.Popen(['xpaaccess','-c',self.analysis.ds9id],
                                            stdout=subprocess.PIPE).communicate()[0]
            nwait += 1
#            print xpa_response.strip(),nwait,'here'


            
#        time.sleep(5.0)

        tol = 1.0e-4
        lra = self.analysis.obs_pars['RA']
        ldec = self.analysis.obs_pars['DEC']
        selra = self.analysis.selected_ra
        seldec = self.analysis.selected_dec

#        lrad = float(self.src_rad_entry.get())
#        lbra = float(self.bkg_ra_entry.get())
#        lbdec = float(self.bkg_dec_entry.get())
#        lbrad = float(self.bkg_rad_entry.get())

        while 1:

            time.sleep(1.0)

            try:       

                ds9_poll = self.analysis.ds9.poll()

            except:

                try:
                    self.ImageDS9Button["text"] = "Run ds9"
                except:
                    pass
                return

            else:
                
                if ds9_poll != None:

                    try:
                        self.ImageDS9Button["text"] = "Run ds9"
                    except:
                        pass
                
                    return

                self.analysis.getregions()
                sd = 100.0
                sn = ""
                chk = False
                if ( abs(self.analysis.ra - lra)>tol):
                    chk = True
#                    self.src_ra_entry.set("{:.3f}".format(self.analysis.ra))
                    lra = self.analysis.ra
#                    sn,sd,sassn,res = get_closest_fgl_asssource(self.analysis.ra,
#                                      self.analysis.dec,self.analysis.catalog)

                if ( abs(self.analysis.dec - ldec)>tol): 
                    chk = True
                    ldec = self.analysis.dec
#                    self.src_dec_entry.set("{:.3f}".format(ldec))
#                    sn,sd,sassn,res = get_closest_fgl_asssource(self.analysis.ra,
#                                      self.analysis.dec,self.analysis.catalog)
                if ( abs(self.analysis.selected_ra - selra)>tol):
                    chk = True
                    selra = self.analysis.selected_ra
                    seldec = self.analysis.selected_dec
#                    self.src_rad_entry.set("{:.3f}".format(lrad))
#                    sn,sd,sassn,res = get_closest_fgl_asssource(self.analysis.ra,
#                                      self.analysis.dec,self.analysis.catalog)

                if  ( abs(self.analysis.selected_dec - seldec)>tol):
                    chk = True
                    seldec = self.analysis.selected_dec
                    selra = self.analysis.selected_ra
#                if ( abs(self.analysis.bkg_dec - lbdec)>tol): 
#                    lbdec = self.analysis.bkg_dec
#                    self.bkg_dec_entry.set("{:.3f}".format(lbdec))
#                if ( abs(self.analysis.bkg_rad - lbrad)>tol):
#                    lbrad = self.analysis.bkg_rad
#                    self.bkg_rad_entry.set("{:.3f}".format(lbrad))

#                self.analysis.set_names()
#                self.rootname_entry.set(self.analysis.name)
                if chk:
                    print "Check"
                    self.catsourceid()
                    self.set_scales()

#                    print self.cat_source.get()
        self.analysis.set_names()
        self.set_spectrum_panel()
                

    def catsourceid(self):

        from fgltools import sdist
#        from string import split,join

        distance = self.analysis.rad
        for s in self.analysis.SourceList:
            src = self.analysis.SourceList[s]
#            d = sdist(s.ra,s.dec,self.analysis.selected_ra,
#                     self.analysis.selected_dec)
#            d = sdist(s.ra,s.dec,self.analysis.selected_ra,
#                     self.analysis.selected_dec)
            d = abs(src.ra-self.analysis.selected_ra)+\
                      +abs(self.analysis.selected_dec-src.dec)
            if d < distance and d < self.analysis.dist_tres:
                self.analysis.selected_source = s
                distance = d

#        print d,self.analysis.selected_source.name
        self.skipch = True
        self.set_source_frame()
        self.skipch = False



    def apply_reg(self):
        
        self.analysis.initsources()
        self.show_cat_sources()
        self.populate_cat_source_menu()
        self.set_par()
        self.logit("N Sources %i"%len(self.analysis.SourceList))

    def get_regions(self):
        
        if not self.analysis.havedata:
            self.nodata()
            return


        try:       
            ds9_poll = self.analysis.ds9.poll()
        except:

            self.logerr("You need to start ds9 first! Use \"Run sd9\" button.")
            return


        else:

            if ds9_poll == None:
                self.analysis.getregions()
#                print self.analysis.ra,self.analysis.dec
                self.analysis.write_regions()
                self.analysis.set_names()
                self.rootname_entry.set(self.analysis.name)
                if self.analysis.assoc_source != "":
                    self.cat_source.set(self.analysis.assoc_source)
#                    print self.cat_source.get()
                else:
                    self.cat_source.set(self.analysis.fgl_source)
#                    print self.cat_source.get()                    
#            self.src_spc.set("")
                self.modelvar.set(self.analysis.spectrum_type)
#                self.XspecRunButton["state"] = tk.DISABLED
                self.logit("New regions set:\n"+\
                "Source: Circle(RA= %.2f, DEC= %.2f, Radius=%.2f deg)\n"%(self.analysis.ra,self.analysis.dec,self.analysis.rad)+\
                "Background: Circle(RA= %.2f, DEC= %.2f, Radius=%.2f deg)"%(self.analysis.bkg_ra,self.analysis.bkg_dec,self.analysis.bkg_rad))
#            else:
#                self.analysis.ds9 = self.analysis.runds9()
           
                
    def nodata(self):
        self.logerr("No LAT data in the current directory. " +\
                        "Specify data directory using \"...\" \n button in \"Data\"" +\
                    "section of the \"Settings\" panel.")


    def filterevents(self):

        from lsthreads import filter_thread

        if not self.analysis.havedata:
            self.nodata()
            return
        
        run = int(0)

        try:
            state = self.filt_thread.state
#            print state

        except:            
            run = int(1)

        else:
            if state == "running":
                self.filt_thread.stop()

            if state == "done" or state == "stopped":
                run = int(1)


        if run:
            
#            self.logblue("Start filtering thread.")
            self.filt_thread = filter_thread('efiles.list',
                                             self.analysis.scfile,
                                             self.analysis.basename+"_filtered_gti.fits",
                                             self.analysis.obs_pars["RA"],
                                             self.analysis.obs_pars["DEC"],
                                             self.analysis.obs_pars["roi"],
                                             self.analysis.obs_pars["tmin"],
                                             self.analysis.obs_pars["tmax"],
                                             self.analysis.obs_pars["emin"],
                                             self.analysis.obs_pars["emax"],
                                             self.analysis.zmax,
                                             logqueue = self.logQueue)
            self.filt_thread.start()

            wait_thread = threading.Thread(target=self.filter_wait,args=())
            wait_thread.start()

            self.DataFilterButton["text"] = "Stop Flitering"
#        self.DataFilterButton["command"] = self.filter_events_thread._Thread_stop

            self.filtered_events.set("calculating...")
            self.DataFilterFileLabel.update()


    def filter_wait(self):
        
        import time

        while self.filt_thread.state != "stopped" and self.filt_thread.state != "done":

            time.sleep(0.5)


        if  self.filt_thread.state == "stopped":
            
            self.analysis.evfile = "None"
            self.filtered_events.set(self.analysis.evfile)           
            self.logerr("Event file production aborted!")
 
        if  self.filt_thread.state == "done":
            
            ef = self.analysis.basename+"_filtered_gti.fits"
            if (os.path.exists(ef)):
                self.analysis.evfile = \
                    self.analysis.basename+"_filtered_gti.fits"
                self.filtered_events.set(self.analysis.evfile)           
                self.logblue("Finished filtering events! Now you can create galctic cube\nby pressing \"Run GTLTcube\" and the region image by pressing \"Extract Image\".")
                
            else:
                self.logerr("Something wrong. Event file was not created!!!")
                self.analysis.evfile = "None"
                self.filtered_events.set(self.analysis.evfile)           

#                pass

#        if self.filt_thread.state == "error":
#            self.logit(self.filt_thread.out)
            

        self.logit(self.filt_thread.out)
        self.DataFilterButton["text"] = "Filter Events"            
                        

    def image_thread(self):
        
        """Defines and starts image extraction thread."""
        
        self.im_thread = threading.Thread(target=self.createimage,args=())
        self.im_thread.start()
        
    def createimage(self):
        
        from string import join
        
        """Performs image extraction. Called from image thread."""

        if not self.analysis.havedata:
            self.nodata()
            return -1 


        if not os.path.exists(self.analysis.evfile):
            self.logerr("Event file is not available. Use \"Filter Events\" to create one.")
            return

        self.ImageCreateButton["state"] = tk.DISABLED
        self.logit("****RUNNING GTBIN TO CREATE REGION IMAGE ******")
        binsz = float(self.binsz_entry.get())
        npics = int(self.analysis.obs_pars['roi']*2/binsz)
        self.logit(join(["    Parameters:","    algorithm=CMAP","    ebinalg=LOG",
                                    "    scfile="+self.analysis.scfile,
                                    "    evfile="+self.analysis.evfile,
                                    "    outfile="+self.analysis.basename+'_image.fits',
                                    "    tstart="+str(self.analysis.tmin),
                                    "    tstop="+str(self.analysis.tmax),
                                    "    emin="+str(self.analysis.emin),
                                    "    emax="+str(self.analysis.emax),
                                    "    nxpix="+str(npics),"    nypix="+str(npics),
                                    "    binsz="+str(binsz),"    xref="+str(self.analysis.ra),
                                    "    yref="+str(self.analysis.dec),"    axisrot=0.0",
                                    "    proj=AIT","    coordsys=CEL",
                                    "    chatter="+str(self.analysis.chatter)],"\n"))
        self.image_file.set("calculating...")
        self.ImageLabel.update()
#        time.sleep(0.05)
#        try:

        self.analysis.ra  = self.analysis.obs_pars["RA"]
        self.analysis.dec = self.analysis.obs_pars["DEC"]

#        out = self.analysis.runevtbin(alg="CMAP",
#                                      outfile=self.analysis.basename+'_roi.fits')
        gtbinerr = False
        process = subprocess.Popen(["gtbin","algorithm=CMAP","ebinalg=LOG",
                                    "scfile="+self.analysis.scfile,
                                    "evfile="+self.analysis.evfile,
                                    "outfile="+self.analysis.basename+'_image.fits',
                                    "tstart="+str(self.analysis.tmin),
                                    "tstop="+str(self.analysis.tmax),
                                    "emin="+str(self.analysis.emin),
                                    "emax="+str(self.analysis.emax),
                                    "nxpix="+str(npics),"nypix="+str(npics),
                                    "binsz="+str(binsz),"xref="+str(self.analysis.ra),
                                    "yref="+str(self.analysis.dec),"axisrot=0.0",
                                    "proj=AIT","coordsys=CEL",
                                    "chatter="+str(self.analysis.chatter)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    

#       except:
        catchError = "at the top level:"
        for line in process.stdout:
            self.logit("IMAGE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        for line in process.stderr:
            self.logit("IMAGE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        
        if (gtbinerr):
            self.logerr("ERROR DURING GTBIN EXECUTION!!!!")
            self.analysis.image = "None"
        
        
        if os.path.exists(self.analysis.basename+'_image.fits'):
            self.logit("Image file: "+self.analysis.basename+"_image.fits created.")
            self.logblue("Finished extracting image.")
            self.logblue("Press \"Run ds9\" to explore the image and edit extraction regions.")
            self.analysis.image = self.analysis.basename+'_image.fits'

        self.set_filter_panel()
        
        self.ImageCreateButton["state"] = tk.NORMAL
        return



    def ccube_thread(self):
        
        """Defines and starts 3D count map extraction thread."""
        
        self.cc_thread = threading.Thread(target=self.create_ccube,args=())
        self.cc_thread.start()
        
    def create_ccube(self):
        
        from string import join
        
        """Performs 3D count map extraction. Called from ccube_thread thread."""

        if not self.analysis.havedata:
            self.nodata()
            return -1 


        if not os.path.exists(self.analysis.evfile):
            self.logerr("Event file is not available. Use \"Filter Events\" to create one.")
            return

        self.CcubeCreateButton["state"] = tk.DISABLED
        self.logit("****RUNNING GTBIN TO CREATE CCUBE ******")
        binsz = float(self.binsz_entry.get())
        npics = int(self.analysis.obs_pars['roi']*sqrt(2.0)/binsz)
        self.logit(join(["    Parameters:","    algorithm=CCUBE","    ebinalg=LOG",
                                    "    scfile="+self.analysis.scfile,
                                    "    evfile="+self.analysis.evfile,
                                    "    outfile="+self.analysis.basename+'_ccube.fits',
                                    "    tstart="+str(self.analysis.tmin),
                                    "    tstop="+str(self.analysis.tmax),
                                    "    emin="+str(self.analysis.emin),
                                    "    emax="+str(self.analysis.emax),
                                    "    nxpix="+str(npics),"    nypix="+str(npics),
                                    "    binsz="+str(binsz),"    xref="+str(self.analysis.ra),
                                    "    yref="+str(self.analysis.dec),"    axisrot=0.0",
                                    "    proj=STG","    coordsys=CEL",
                                    "    enumbins="+str(self.analysis.nchans),
                                    "    chatter="+str(self.analysis.chatter)],"\n"))
        self.ccube_file.set("calculating...")
        self.CcubeLabel.update()
#        time.sleep(0.05)
#        try:

        self.analysis.ra  = self.analysis.obs_pars["RA"]
        self.analysis.dec = self.analysis.obs_pars["DEC"]

#        out = self.analysis.runevtbin(alg="CMAP",
#                                      outfile=self.analysis.basename+'_roi.fits')
        gtbinerr = False
        process = subprocess.Popen(["gtbin","algorithm=CCUBE","ebinalg=LOG",
                                    "scfile="+self.analysis.scfile,
                                    "evfile="+self.analysis.evfile,
                                    "outfile="+self.analysis.basename+'_ccube.fits',
                                    "tstart="+str(self.analysis.tmin),
                                    "tstop="+str(self.analysis.tmax),
                                    "emin="+str(self.analysis.emin),
                                    "emax="+str(self.analysis.emax),
                                    "nxpix="+str(npics),"nypix="+str(npics),
                                    "binsz="+str(binsz),"xref="+str(self.analysis.ra),
                                    "yref="+str(self.analysis.dec),"axisrot=0.0",
                                    "proj=STG","coordsys=CEL",
                                    "enumbins="+str(self.analysis.nchans),
                                    "chatter="+str(self.analysis.chatter)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    

#       except:
        catchError = "at the top level:"
        for line in process.stdout:
            self.logit("CCUBE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        for line in process.stderr:
            self.logit("CCUBE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        
        if (gtbinerr):
            self.logerr("ERROR DURING GTBIN EXECUTION!")
            self.analysis.image = "None"
        
        
        if os.path.exists(self.analysis.basename+'_ccube.fits'):
            self.analysis.ccube = self.analysis.basename+'_ccube.fits'
            self.logit("3D count cube file: "+self.analysis.basename+"_ccube.fits created.")
            self.logblue("Finished extracting CCUBE.")
#            self.logblue("Press \"Run ds9\" to explore the image and edit extraction regions.")
#            self.analysis.ccube = self.analysis.basename+'_image.fits'

        self.set_filter_panel()
        
        self.CcubeCreateButton["state"] = tk.NORMAL
        return

    def expcube_thread(self):
        
        """Defines and starts 3D count map extraction thread."""
        
        self.em_thread = threading.Thread(target=self.create_expcube,args=())
        self.em_thread.start()
        
    def create_expcube(self):
        
        from string import join
        
        """Performs 3D count map extraction. Called from ccube_thread thread."""

        if not self.analysis.havedata:
            self.nodata()
            return -1 


        if not os.path.exists(self.analysis.evfile):
            self.logerr("Event file is not available. Use \"Filter Events\" to create one.")
            return

        if not os.path.exists(self.analysis.ltcube):
            self.logerr("Ltcube is not available. Use \"Run GTLTcube\" to create one.")
            return

        self.ExpcubeCreateButton["state"] = tk.DISABLED
        self.logit("****RUNNING GTEXPCUBE2 TO CREATE CCUBE ******")
        binsz = float(self.binsz_entry.get())
        npics = int((self.analysis.obs_pars['roi']+20.0)*sqrt(2.0)/binsz)
        self.logit(join(["    Parameters:",
                         "    infile="+self.analysis.ltcube,
                         "    ebinalg=LOG",
                                    "    outfile="+self.analysis.basename+'_expcube.fits',
                                    "    irfs="+self.analysis.irfs,                                    
                                    "    emin="+str(self.analysis.emin),
                                    "    emax="+str(self.analysis.emax),
                                    "    nxpix="+str(npics),"    nypix="+str(npics),
                                    "    binsz="+str(binsz),"    xref="+str(self.analysis.ra),
                                    "    yref="+str(self.analysis.dec),"    axisrot=0.0",
                                    "    proj=STG","    coordsys=CEL",
                                    "    enumbins="+str(self.analysis.nchans),
                                    "    chatter="+str(self.analysis.chatter)],"\n"))
        self.expcube_file.set("calculating...")
        self.ExpcubeLabel.update()
#        time.sleep(0.05)
#        try:

        self.analysis.ra  = self.analysis.obs_pars["RA"]
        self.analysis.dec = self.analysis.obs_pars["DEC"]

#        out = self.analysis.runevtbin(alg="CMAP",
#                                      outfile=self.analysis.basename+'_roi.fits')
        gtbinerr = False
        process = subprocess.Popen(["gtexpcube2","infile="+self.analysis.ltcube,
                                    "cmap=none",
                                    "outfile="+self.analysis.basename+'_expcube.fits',
                                    "irfs="+self.analysis.irfs, 
                                    "emin="+str(self.analysis.emin),
                                    "emax="+str(self.analysis.emax),
                                    "nxpix="+str(int(360.0/binsz)),"nypix="+str(int(180.0/binsz)),
#                                    "nxpix="+str(npics),"nypix="+str(npics),
                                    "binsz="+str(binsz),"xref="+str(self.analysis.ra),
                                    "yref="+str(self.analysis.dec),"axisrot=0.0",
                                    "proj=STG","coordsys=CEL",
                                    "enumbins="+str(self.analysis.nchans),
                                    "chatter="+str(self.analysis.chatter)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    

#       except:
        catchError = "at the top level:"
        for line in process.stdout:
            self.logit("EXPCUBE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        for line in process.stderr:
            self.logit("EXPCUBE EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        
        if (gtbinerr):
            self.logerr("ERROR DURING GTEXPCUBE2 EXECUTION!")
            self.analysis.image = "None"
        
        
        if os.path.exists(self.analysis.basename+'_expcube.fits'):
            self.analysis.xpcube = self.analysis.basename+'_expcube.fits'
            self.logit("Exposure map file: "+self.analysis.basename+"_expcube.fits created.")
            self.logblue("Finished extracting EXPCUBE.")
#            self.logblue("Press \"Run ds9\" to explore the image and edit extraction regions.")
#            self.analysis.ccube = self.analysis.basename+'_image.fits'

        self.set_filter_panel()
        
        self.ExpcubeCreateButton["state"] = tk.NORMAL
        return

    def srcmap_thread(self):
        
        """Defines and starts 3D count map extraction thread."""
        
        self.sm_thread = threading.Thread(target=self.create_srcmap,args=())
        self.sm_thread.start()
        
    def create_srcmap(self):
        
        from string import join
        
        """Performs 3D count map extraction. Called from srcmap_thread thread."""

        if not self.analysis.havedata:
            self.nodata()
            return -1 


        if not os.path.exists(self.analysis.scfile):
            self.logerr("SC file is not available.")
            return

        if not os.path.exists(self.analysis.ltcube):
            self.logerr("Ltcube is not available. Use \"Run GTLTcube\" to create one.")
            return

        if not os.path.exists(self.analysis.ccube):
            self.logerr("3D map is not available. Use \"Extract 3D Map\" to create one.")
            return

        if not os.path.exists(self.analysis.expcube):
            self.logerr("Expcube is not available. Use \"Extract Exposure Map\" to create one.")
            return

        self.SrcmapCreateButton["state"] = tk.DISABLED
        self.logit("****RUNNING GTSCRMAPS TO CREATE Source Map ******")

        self.logit(join(["    Parameters:",
                                    "    expcube="+self.analysis.ltcube,
                                    "    cmap="+self.analysis.ccube,
                                    "    outfile="+self.analysis.basename+'_srcmap.fits',
                                    "    srcmdl="+self.analysis.model_file,
                                    "    irfs="+self.analysis.irfs,                            
                                    "    bexpmap="+self.analysis.expcube,
                                    "    chatter="+str(self.analysis.chatter)],"\n"))
        self.srcmap_file.set("calculating...")
        self.SrcmapLabel.update()
        self.analysis.write_xml_model()
#        time.sleep(0.05)
#        try:

#                                      outfile=self.analysis.basename+'_roi.fits')
        gtbinerr = False
        process = subprocess.Popen(["gtsrcmaps",
                                    "expcube="+self.analysis.ltcube,
                                    "cmap="+self.analysis.ccube,
                                    "outfile="+self.analysis.basename+'_srcmap.fits',
                                    "irfs="+self.analysis.irfs, 
                                    "srcmdl="+self.analysis.model_file,
                                    "bexpmap="+self.analysis.expcube,
                                    "chatter="+str(self.analysis.chatter)],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    

#       except:
        catchError = "at the top level:"
        for line in process.stdout:
            self.logit("SRCMAP EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        for line in process.stderr:
            self.logit("SRCMAP EXTRACTION:"+line)
            if line.find(catchError) != -1:
                gtbinerr = True
        
        if (gtbinerr):
            self.logerr("ERROR DURING GTEXPCUBE2 EXECUTION!")
            self.analysis.image = "None"
        
        
        if os.path.exists(self.analysis.basename+"_srcmap.fits"):
            self.analysis.srcmap = self.analysis.basename+"_srcmap.fits"
            self.logit("Exposure map file: "+self.analysis.basename+"_srcmap.fit created.")
            self.logblue("Finished extracting EXPCUBE.")
#            self.logblue("Press \"Run ds9\" to explore the image and edit extraction regions.")
#            self.analysis.ccube = self.analysis.basename+'_image.fits'

        self.set_like_panel()
        
        self.ExpcubeCreateButton["state"] = tk.NORMAL
        return


    def askdirectory(self):

        """ Asks for a new LAT data directory"""

        dirname = tkFileDialog.askdirectory()
        if dirname == "": return
#        self.DataDirLabel["text"] = dirname
        os.chdir(dirname)
        self.analysis.datapath = dirname
        self.analysis.prepData()
        self.analysis.set_names()
        self.set_settings_panel()
        self.set_filter_panel()
#        self.set_spectrum_panel()
#        self.set_regions_entry()
#        self.clear_log()
        self.populate_cat_source_menu()
        try:
            self.analysis.ds9.terminate()
            self.xs_proc.kill()
            self.xs_fil.close()
            self.XspecPromptEntry["state"] = tk.DISABLED
            self.XspecRunButton["state"] = tk.NORMAL
        except:
            pass
        if self.analysis.havedata:
            self.logit("Working directory: "+dirname)
#            self.logit("Fermi/LAT data is found.")
            self.log_data_info()
        else:
            self.logit("No LAT data is found in directory.")
        return

    def askfile(self):

        fname = tkFileDialog.askopenfilename()
        if fname == "": return

        try:
            res = os.path.exists(fname)
        except:
            return

        self.analysis.catalog = fname
        self.analysis.verify_cat()
        self.analysis.set_names()
        self.set_filter_panel()
        if self.analysis.haveCatalog:
#            self.CatLabel["text"] = self.analysis.catalog
            self.logit("Using 2FGL catalog: "+self.analysis.catalog)
            self.populate_cat_source_menu()
            self.show_cat_sources()

        else:
            self.logit("2FGL catalog (and related functionality) is not available.")
        return

    def ask_cube(self):

        fname = tkFileDialog.askopenfilename()
        if fname == "": return

        try:
            res = os.path.exists(fname)
        except:
            return


        self.ltcube_file.set(os.path.basename(fname))
        self.analysis.ltcube = self.ltcube_file.get()
        self.logit("Using Galactic cube: "+fname)
        return

    def xspec_prompt_return(self,event):
        import time
        try:
            self.xs_proc.stdin.write(self.xspec_prompt.get()+"\n")
            time.sleep(0.5)
            self.logit(self.xs_fil.read())
        except:
            self.logerr("Error send input to xspec.")
            pass
        self.xspec_prompt.set("")
        return

    def save_log(self):
        text = self.LogText.get(1.0,tk.END)
        logfile = self.analysis.datapath+"/"+self.analysis.basename + '.log'
        fil = open(logfile,"w")
        fil.write(text)
        fil.close()
        self.logit("Log saved to "+logfile)

    def clear_log(self):
        self.logLock.acquire()
        self.LogText["state"] = tk.NORMAL
        self.LogText.delete(0.0,tk.END)
        self.LogText["state"] = tk.DISABLED
        self.logLock.release()

    def hline(self):

        self.LogText["state"] = tk.NORMAL
        self.LogText.insert(tk.END,'---------------------------------------------------------------------------\n')
        self.LogText["state"] = tk.DISABLED

    def quit_gui(self):
        
        self.stop = True
        self.ltcube_stop = True

        try:
            self.filt_thread.stop()
        except:
            pass


        try:
            self.lsthread.stop()
        except:
            pass

        try:
            self.helpthrd.stop()
        except:
            pass

        try:
            self.analysis.ds9.kill()
            
        except:
            pass

        try:
            self.xs_proc.terminate() 
        except:
            pass

        self.analysis.writerc()

        self.quit()

