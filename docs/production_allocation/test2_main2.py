import numpy

import pandas

FT = pandas.read_csv('test2_formation_tops.txt',delimiter='\t')
UT = pandas.read_csv('test2_flow_unit_tops.txt',delimiter='\t')
PR = pandas.read_csv('test2_perforations.txt',delimiter='\t')
FP = pandas.read_csv('test2_production_horizon_based.txt',delimiter='\t')

FT['Top'] = FT['Top'].astype('float64',copy=True)
FT['Bottom'] = FT['Bottom'].astype('float64',copy=True)

UT['Top'] = UT['Top'].astype('float64',copy=True)
UT['Bottom'] = UT['Bottom'].astype('float64',copy=True)

PR['Date'] = PR['Date'].astype('datetime64',copy=True)
PR['Top'] = PR['Top'].astype('float64',copy=True)
PR['Bottom'] = PR['Bottom'].astype('float64',copy=True)

FP['Date'] = FP['Date'].astype('datetime64',copy=True)
FP['OilRate'] = FP['OilRate'].astype('float64',copy=True)

UTwells = UT['WellName'].to_numpy().astype(str)
PRwells = PR['WellName'].to_numpy().astype(str)

with open('perforations_flow_unit_based.txt','w') as file:

    file.write("{}\t{}\t{}\t{}\n".format("WellName","Date","FlowUnit","OilRate"))

    for index,formation in enumerate(FP['Horizon']):
        
        WN = FP['WellName'][index]
        DT = FP['Date'][index]
        HZ = FP['Horizon'][index]
        OR = FP['OilRate'][index]

        PRsub = PR[PRwells==WN]

        boolarr = DT<PRsub['Date'].to_numpy()

        try:
            pindex = numpy.where(boolarr)[0][0]
        except IndexError:
            pindex = boolarr.size

        pindex = pindex if pindex==0 else pindex-1
        
        TOP = PRsub['Top'].to_numpy()[pindex]
        BOT = PRsub['Bottom'].to_numpy()[pindex]

        UTsub = UT[UTwells==WN]

        TOTAL_FORMATION_PRODUCTION_THICKNESS = BOT-TOP

        UNIT_PRODUCTION_THICKNESS = []

        CTOP = []
        CBOT = []

        for J,flowunit in enumerate(UTsub['FlowUnit']):

            top = UTsub['Top'].to_numpy()[J]
            bot = UTsub['Bottom'].to_numpy()[J]
            
            if TOP<bot and BOT>top:

                TOP_temp = TOP if TOP>top else top
                BOT_temp = BOT if BOT<bot else bot

                unit_prod_thickness = BOT_temp-TOP_temp

                CTOP.append(TOP_temp)
                CBOT.append(BOT_temp)

                UNIT_PRODUCTION_THICKNESS.append(unit_prod_thickness)

            else:

                CTOP.append(None)
                CBOT.append(None)

                UNIT_PRODUCTION_THICKNESS.append(0)

        DISTRIBUTED_THICKNESS = numpy.array(UNIT_PRODUCTION_THICKNESS)

        TOTAL_UNIT_PRODUCTION_THICKNESS = numpy.sum(DISTRIBUTED_THICKNESS)

        if TOTAL_UNIT_PRODUCTION_THICKNESS==0:
            # print("{}\t{}\t{}\t{}\n".format(WN,DT,HZ,"PRODUCTION FROM SHALE WARNING"))
            file.write("{}\t{}\t{}\t{}\t{}\n".format(WN,DT,HZ,"","PRODUCTION FROM SHALE WARNING"))
            continue

        for J,flowunit in enumerate(UTsub['FlowUnit']):

            DOR = OR*DISTRIBUTED_THICKNESS[J]/TOTAL_UNIT_PRODUCTION_THICKNESS
            
            if DOR>0:
                # print("{}\t{}\t{}\t{}\n".format(WN,DT,flowunit,DOR))
                file.write("{}\t{}\t{}\t{}\t{}\n".format(WN,DT,flowunit,CTOP[J],CBOT[J]))