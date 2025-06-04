import numpy

import pandas

FT = pandas.read_csv('formation_tops.txt',delimiter='\t')
UT = pandas.read_csv('flow_unit_tops.txt',delimiter='\t')
PR = pandas.read_csv('perforations.txt',delimiter='\t')
FP = pandas.read_csv('production_horizon_based.txt',delimiter='\t')

FT['Top'] = FT['Top'].astype('float64',copy=True)
FT['Bottom'] = FT['Bottom'].astype('float64',copy=True)

UT['Top'] = UT['Top'].astype('float64',copy=True)
UT['Bottom'] = UT['Bottom'].astype('float64',copy=True)

##PR['Date'] = PR['Date'].astype('datetime64',copy=True)
PR['Top'] = PR['Top'].astype('float64',copy=True)
PR['Bottom'] = PR['Bottom'].astype('float64',copy=True)

##FP['Date'] = FP['Date'].astype('datetime64',copy=True)
FP['OilRate'] = FP['OilRate'].astype('float64',copy=True)

UTwells = UT['WellName'].to_numpy().astype(str)

with open('production_flow_unit_based.txt','w') as file:

    file.write("{}\t{}\t{}\t{}\n".format("WellName","Date","FlowUnit","OilRate"))

    for index,formation in enumerate(FP['Horizon']):
        
        WN = FP['WellName'][index]
        DT = FP['Date'][index]
        HZ = FP['Horizon'][index]
        OR = FP['OilRate'][index]
        
        TOP = PR['Top'][index]
        BOT = PR['Bottom'][index]

        UTsub = UT[UTwells==WN]

        TOTAL_FORMATION_PRODUCTION_THICKNESS = BOT - TOP

        UNIT_PRODUCTION_THICKNESS = []

        for J,flowunit in enumerate(UTsub['FlowUnit']):
            
            if TOP<UTsub['Bottom'].to_numpy()[J] and BOT>UTsub['Top'].to_numpy()[J]:

                TOP_temp = TOP if TOP>UTsub['Top'].to_numpy()[J] else UTsub['Top'].to_numpy()[J]
                BOT_temp = BOT if BOT<UTsub['Bottom'].to_numpy()[J] else UTsub['Bottom'].to_numpy()[J]

                unit_prod_thickness = BOT_temp-TOP_temp

                UNIT_PRODUCTION_THICKNESS.append(unit_prod_thickness)

            else:

                UNIT_PRODUCTION_THICKNESS.append(0)

        DISTRIBUTED_THICKNESS = numpy.array(UNIT_PRODUCTION_THICKNESS)

        TOTAL_UNIT_PRODUCTION_THICKNESS = numpy.sum(DISTRIBUTED_THICKNESS)

        if TOTAL_UNIT_PRODUCTION_THICKNESS==0:
            file.write("{}\t{}\t{}\t{}\n".format(WN,DT,HZ,"PRODUCTION FROM SHALE WARNING"))
            continue

        for J,flowunit in enumerate(UTsub['FlowUnit']):

            DOR = OR*DISTRIBUTED_THICKNESS[J]/TOTAL_UNIT_PRODUCTION_THICKNESS
            
            if DOR>0:
                file.write("{}\t{}\t{}\t{}\n".format(WN,DT,flowunit,DOR))

        

    
        

    
