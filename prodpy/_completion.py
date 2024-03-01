import numpy

from borepy.gmodel._stock import Stock

class Completion():

    headersRAW = ["Wells","Horizont","Top","Bottom","start","stoped",]

    headersOPT = ["WELL","DATE","EVENT","TOP","BOTTOM","DIAM",]

    headersUNI = ["WELL","DATE","COUNT",]
    
    def __init__(self):

        pass

    def get_wellnames(self):

        pass

    def comp_call(self,wellname=None):

        warnWELLNAME = "{} has name conflict in completion directory."
        warnFORMNAME = "{} does not have proper layer name in completion directory."
        warnUPPDEPTH = "{} top level depths must be positive in completion directory."
        warnBTMDEPTH = "{} bottom level depths must be positive in completion directory."
        warnUPBOTTOM = "{} top level must be smaller than bottom levels in completion directory."
        warnSTRTDATE = "{} start date is not set properly in completion directory."
        warnSTOPDATE = "{} stop date is not set properly in completion directory."
        warnSTARTEND = "{} start date is after or equal to stop date in completion directory."

        compraw = frame(headers=self.headers_compraw)

        for wname in self.itemnames:

            print("{} gathering completion data ...".format(wname))

            wellindex = int(re.sub("[^0-9]","",wname))

            folder1 = "GD-{}".format(str(wellindex).zfill(3))

            filename = "GD-{}.xlsx".format(str(wellindex).zfill(3))

            filepath = os.path.join(self.comprawdir,folder1,filename)
            
            comp = frame(filepath=filepath,sheetname=folder1,headerline=1,skiplines=2,min_row=2,min_col=2)

            comp.get_columns(headers=self.headers_compraw,inplace=True)

            comp.astype(header=self.headers_compraw[2],dtype=np.float64)
            comp.astype(header=self.headers_compraw[3],dtype=np.float64)

            if np.any(comp.running[0]!=wname):
                warnings.warn(warnWELLNAME.format(wname))

            if np.any(comp.running[1]==None) or np.any(np.char.strip(comp.running[1].astype(str))==""):
                warnings.warn(warnFORMNAME.format(wname))

            if np.any(comp.running[2]<0):
                warnings.warn(warnUPPDEPTH.format(wname))

            if np.any(comp.running[3]<0):
                warnings.warn(warnBTMDEPTH.format(wname))

            if np.any(comp.running[2]-comp.running[3]>0):
                warnings.warn(warnUPBOTTOM.format(wname))

            if any([not isinstance(value,datetime) for value in comp.running[4].tolist()]):
                warnings.warn(warnSTRTDATE.format(wname))

            indices = [not isinstance(value,datetime) for value in comp.running[5].tolist()]

            if any(indices) and np.any(comp.running[5][indices]!="ACTIVE"):
                warnings.warn(warnSTOPDATE.format(wname))

            comp.running[5][indices] = datetime.now()

            if any([(s2-s1).days<0 for s1,s2 in zip(comp.running[4].tolist(),comp.running[5].tolist())]):
                warnings.warn(warnSTARTEND.format(wname))

            compraw.set_rows(comp.get_rows())

        path = os.path.join(self.workdir,self.filename_comp+"0")

        fstring = "{:6s}\t{}\t{:.1f}\t{:.1f}\t{:%Y-%m-%d}\t{:%Y-%m-%d}\n"

        compraw.write(filepath=path,fstring=fstring)

    def comp_process(self):

        path = os.path.join(self.workdir,self.filename_comp+"0")

        comp1 = frame(filepath=path,skiplines=1)
        comp2 = frame(filepath=path,skiplines=1)

        comp1.texttocolumn(0,deliminator="\t")
        comp2.texttocolumn(0,deliminator="\t")

        headers_compraw1 = self.headers_compraw[:4]+(self.headers_compraw[4],)
        headers_compraw2 = self.headers_compraw[:4]+(self.headers_compraw[5],)

        comp1.get_columns(headers=headers_compraw1,inplace=True)
        comp2.get_columns(headers=headers_compraw2,inplace=True)

        comp1.astype(header=headers_compraw1[2],dtype=np.float64)
        comp1.astype(header=headers_compraw1[3],dtype=np.float64)
        comp1.astype(header=headers_compraw1[4],datestring=True)

        comp2.astype(header=headers_compraw2[2],dtype=np.float64)
        comp2.astype(header=headers_compraw2[3],dtype=np.float64)
        comp2.astype(header=headers_compraw2[4],datestring=True)

        col_perf = np.empty(comp1.running[0].size,dtype=object)
        col_perf[:] = "PERF"

        col_diam = np.empty(comp1.running[0].size,dtype=object)
        col_diam[:] = "0.14"

        comp1.set_column(col_perf,header_new="EVENT")
        comp1.set_column(col_diam,header_new="DIAM")

        col_plug = np.empty(comp2.running[0].size,dtype=object)
        col_plug[:] = "PLUG"

        col_none = np.empty(comp2.running[0].size,dtype=object)
        col_none[:] = ""

        comp2.set_column(col_plug,header_new="EVENT")
        comp2.set_column(col_none,header_new="DIAM")

        comp1.set_rows(comp2.get_rows())

        comp1.set_header(0,self.headers_comp[0])
        comp1.set_header(2,self.headers_comp[3])
        comp1.set_header(3,self.headers_comp[4])
        comp1.set_header(4,self.headers_comp[1])

        comp1.get_columns(headers=self.headers_comp,inplace=True)

        comp1.sort(header_indices=[1],inplace=True)

        path = os.path.join(self.workdir,self.filename_comp+"1")

        fstring = "{:6s}\t{:%Y-%m-%d}\t{:4s}\t{:.1f}\t{:.1f}\t{:4s}\n"

        comp1.write(filepath=path,fstring=fstring)

        compuni = frame(headers=self.headers_compuni)

        for wname in self.itemnames:

            comp1.filter(0,keywords=[wname],inplace=False)

            update_dates = np.unique(comp1.running[1])
            update_wells = np.empty(update_dates.size,dtype=object)
            update_counts = np.zeros(update_dates.size,dtype=int)

            update_wells[:] = wname

            update_indices = np.insert(
                np.cumsum(np.sum(comp1.running[1]==update_dates.reshape((-1,1)),axis=1)),0,0)

            open_intervals = np.empty((0,2))

            for index,date in enumerate(update_dates):

                compevents = comp1.running[2][update_indices[index]:update_indices[index+1]]
                compuppers = comp1.running[3][update_indices[index]:update_indices[index+1]]
                complowers = comp1.running[4][update_indices[index]:update_indices[index+1]]

                perfevents = compevents=="PERF"

                perfintervals = np.array([compuppers[perfevents],complowers[perfevents]]).T

                open_intervals = np.concatenate((open_intervals,perfintervals),axis=0)

                plugevents = compevents=="PLUG"

                pluguppermatch = np.any(open_intervals[:,0]==compuppers[plugevents].reshape((-1,1)),axis=0)
                pluglowermatch = np.any(open_intervals[:,1]==complowers[plugevents].reshape((-1,1)),axis=0)

                plugmatch = np.where(np.logical_and(pluguppermatch,pluglowermatch))[0]

                open_intervals = np.delete(open_intervals,plugmatch,0)

                update_counts[index] = open_intervals.shape[0]

            rows = np.array([update_wells,update_dates,update_counts]).T.tolist()

            compuni.set_rows(rows)

        compuni.astype(header_index=2,dtype=int)

        compuni.sort(header_indices=[1],inplace=True)

        path = os.path.join(self.workdir,self.filename_comp+"uni")

        fstring = "{:6s}\t{:%Y-%m-%d}\t{:d}\n"

        compuni.write(filepath=path,fstring=fstring)

    def comp_get(self,filending=None,wellname=None):

        for filename in os.listdir(self.workdir):

            if filename[:len("completion")]=="completion":

                path = os.path.join(self.workdir,filename)

                ending = filename[len("completion"):]

                if filename[:4]+ending in self.attrnames:
                    continue

                if filending is not None:
                    if filending!=ending:
                        continue

                try:
                    index = int(ending)
                except ValueError:
                    index = None

                attrname = filename[:4]+ending

                attrvals = frame(filepath=path,skiplines=1)

                setattr(self,attrname,attrvals)

                if index is not None:

                    if index==0:
                        getattr(self,attrname).texttocolumn(0,deliminator="\t")
                        getattr(self,attrname).astype(header=self.headers_compraw[2],dtype=np.float64)
                        getattr(self,attrname).astype(header=self.headers_compraw[3],dtype=np.float64)
                        getattr(self,attrname).astype(header=self.headers_compraw[4],datestring=True)
                        getattr(self,attrname).astype(header=self.headers_compraw[5],datestring=True)
                    else:
                        getattr(self,attrname).texttocolumn(0,deliminator="\t",maxsplit=6)
                        getattr(self,attrname).astype(header=self.headers_comp[1],datestring=True)
                        getattr(self,attrname).astype(header=self.headers_comp[3],dtype=np.float64)
                        getattr(self,attrname).astype(header=self.headers_comp[4],dtype=np.float64)

                else:

                    if ending == "uni":
                        getattr(self,attrname).texttocolumn(0,deliminator="\t")
                        getattr(self,attrname).astype(header=self.headers_compuni[1],datestring=True)
                        getattr(self,attrname).astype(header=self.headers_compuni[2],dtype=int)

                self.attrnames.append(attrname)

                if wellname is not None:
                    getattr(self,attrname).filter(0,keywords=[wellname],inplace=False)