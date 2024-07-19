import numpy

# from borepy.gmodel._stock import Stock

class Production():

    headersSIM = ["Wells","Date","Days","oil","water","gas","Wi",]

    headersOPT = ["WELL","DATE","DAYS","OPTYPE","ROIL","RWATER","RGAS","TOIL","TWATER","TGAS",]
    
    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

    def get_wellnames(self):

        pass

    def fill_missing_daily_production(timeO,rateO,timeStart=None,timeEnd=None):

        timeStart = datetime(datetime.today().year,1,1) if timeStart is None else timeStart

        timeEnd = datetime.today() if timeEnd is None else timeEnd

        delta = timeEnd-timeStart

        timeaxis = np.array([timeStart+timedelta(days=i) for i in range(delta.days)],dtype=np.datetime64)

        nonzeroproduction = np.where(timeaxis==timeO.reshape((-1,1)))[1]

        rateEdited = np.zeros(delta.days)

        rateEdited[nonzeroproduction] = rateO

        return rateEdited

    def op_process(self):

        warnDNEOM = "{:%d %b %Y} {} date is not the last day of month."
        warnADGDM = "{:%d %b %Y} {} active days is greater than the days in the month."
        warnOPHNE = "{:%d %b %Y} {} oil production has negative entry."
        warnWPHNE = "{:%d %b %Y} {} water production has negative entry."
        warnGPHNE = "{:%d %b %Y} {} gas production has negative entry."
        warnWIHNE = "{:%d %b %Y} {} water injection has negative entry."
        warnHZPAI = "{:%d %b %Y} {} has zero production and injection."
        warnHBPAI = "{:%d %b %Y} {} has both production and injection data."

        path = os.path.join(self.workdir,self.filename_op+"0")

        prod = frame(filepath=path,skiplines=1)

        prod.texttocolumn(0,deliminator="\t",maxsplit=7)
        prod.get_columns(headers=self.headers_opraw,inplace=True)
        prod.sort(header_indices=[1],inplace=True)

        prod.astype(header=self.headers_opraw[1],datestring=True)
        prod.astype(header=self.headers_opraw[2],dtype=np.int64)
        prod.astype(header=self.headers_opraw[3],dtype=np.float64)
        prod.astype(header=self.headers_opraw[4],dtype=np.float64)
        prod.astype(header=self.headers_opraw[5],dtype=np.float64)
        prod.astype(header=self.headers_opraw[6],dtype=np.float64)

        vdate1 = np.vectorize(lambda x: x.day!=calendar.monthrange(x.year,x.month)[1])

        if any(vdate1(prod.running[1])):
            for index in np.where(vdate1(prod.running[1]))[0]:
                well = prod.running[0][index]
                date = prod.running[1][index]
                warnings.warn(warnDNEOM.format(date,well))

        vdate2 = np.vectorize(lambda x,y: x.day<y)

        if any(vdate2(prod.running[1],prod.running[2])):
            for index in np.where(vdate2(prod.running[1],prod.running[2]))[0]:
                well = prod.running[0][index]
                date = prod.running[1][index]
                warnings.warn(warnADGDM.format(date,well))

        if any(prod.running[3]<0):
            for index in np.where(prod.running[3]<0)[0]:
                well = prod.running[0][index]
                date = prod.running[1][index]
                warnings.warn(warnOPHNE.format(date,well))

        if any(prod.running[4]<0):
            for index in np.where(prod.running[4]<0)[0]:
                well = prod.running[0][index]
                date = prod.running[1][index]
                warnings.warn(warnWPHNE.format(date,well))

        if any(prod.running[5]<0):
            for index in np.where(prod.running[5]<0)[0]:
                well = prod.running[0][index]
                date = prod.running[1][index]
                warnings.warn(warnGPHNE.format(date,well))

        if any(prod.running[6]<0):
            for index in np.where(prod.running[6]<0)[0]:
                well = prod.running[0][index]
                date = prod.running[1][index]
                warnings.warn(warnWIHNE.format(date,well))

        roil = prod.running[3]
        rwater = prod.running[4]+prod.running[6]
        rgas = prod.running[5]

        rprod = prod.running[3]+prod.running[4]+prod.running[5]
        rinj = prod.running[6]

        rtot = rprod+rinj

        optype = np.empty(prod.running[2].shape,dtype=object)

        optype[rprod>0] = "production"
        optype[rinj>0] = "injection"

        if any(rtot==0):
            for index in np.where(rtot==0)[0]:
                well = prod.running[0][index]
                date = prod.running[1][index]
                warnings.warn(warnHZPAI.format(date,well))

        if any(np.logical_and(rprod!=0,rinj!=0)):
            for index in np.where(np.logical_and(rprod!=0,rinj!=0))[0]:
                well = prod.running[0][index]
                date = prod.running[1][index]
                warnings.warn(warnHBPAI.format(date,well))

        if self.wnamefstr is not None:
            vname = np.vectorize(lambda x: self.wnamefstr.format(re.sub("[^0-9]","",str(x)).zfill(3)))
            prod.set_column(vname(prod.running[0]),header_index=0)

        def shifting(x):
            date = x+relativedelta(months=-1)
            days = calendar.monthrange(date.year,date.month)[1]
            return datetime(date.year,date.month,days)

        vdate3 = np.vectorize(lambda x: shifting(x))

        prod.set_column(vdate3(prod.running[1]),header_index=1)

        path = os.path.join(self.workdir,self.filename_op+"1")

        fstring = "{:6s}\t{:%Y-%m-%d}\t{:2d}\t{:.1f}\t{:.1f}\t{:.1f}\t{:.1f}\n"

        prod.write(filepath=path,fstring=fstring)

        prod.set_column(roil,header_new="ROIL")
        prod.set_column(rwater,header_new="RWATER")
        prod.set_column(rgas,header_new="RGAS")

        prod.set_column(optype,header_new="OPTYPE")

        prod.set_header(0,self.headers_op[0])
        prod.set_header(1,self.headers_op[1])
        prod.set_header(2,self.headers_op[2])

        prod.get_columns(headers=self.headers_op[:7],inplace=True)
        
        path = os.path.join(self.workdir,self.filename_op+"2")

        fstring = "{:6s}\t{:%Y-%m-%d}\t{:2d}\t{:10s}\t{:.1f}\t{:.1f}\t{:.1f}\n"

        prod.write(filepath=path,fstring=fstring)

    def op_get(self,filending=None,wellname=None):

        for filename in os.listdir(self.workdir):

            if filename[:len("operation")]=="operation":

                path = os.path.join(self.workdir,filename)

                ending = filename[len("operation"):]

                if filename[:2]+ending in self.attrnames:
                    continue

                if filending is not None:
                    if filending!=ending:
                        continue

                try:
                    index = int(ending)
                except ValueError:
                    index = None

                attrname = filename[:2]+ending

                attrvals = frame(filepath=path,skiplines=1)

                setattr(self,attrname,attrvals)

                getattr(self,attrname).texttocolumn(0,deliminator="\t")

                if index < 2:
                    getattr(self,attrname).astype(header=self.headers_opraw[1],datestring=True)
                    getattr(self,attrname).astype(header=self.headers_opraw[2],dtype=int)
                    getattr(self,attrname).astype(header=self.headers_opraw[3],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_opraw[4],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_opraw[5],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_opraw[6],dtype=np.float64)         
                elif index < 3:
                    getattr(self,attrname).astype(header=self.headers_op[1],datestring=True)
                    getattr(self,attrname).astype(header=self.headers_op[2],dtype=int)
                    getattr(self,attrname).astype(header=self.headers_op[4],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_op[5],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_op[6],dtype=np.float64)
                elif index == 3:
                    getattr(self,attrname).astype(header=self.headers_op[1],datestring=True)
                    getattr(self,attrname).astype(header=self.headers_op[2],dtype=int)
                    getattr(self,attrname).astype(header=self.headers_op[4],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_op[5],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_op[6],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_op[7],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_op[8],dtype=np.float64)
                    getattr(self,attrname).astype(header=self.headers_op[9],dtype=np.float64)

                self.attrnames.append(attrname)

                if wellname is not None:
                    getattr(self,attrname).filter(0,keywords=[wellname],inplace=False)