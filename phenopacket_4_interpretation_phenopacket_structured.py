#!/usr/bin/python3
'''Read from "input" file the path where the compositions are located.
Then creates a json suitable to be handled by the rest of the program
which is phenopacket_heather_whole_phenopacket_schema.py'''
import json

import logging
import argparse


from routines4pheno.FindCompositions import find_compositions
from routines4pheno.ParseJsonPacketlike import parsejsonpacketlike
from routines4pheno.Convert2Phenojson import convert2phenojson

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel',help='the logging level:DEBUG,INFO,WARNING,ERROR or CRITICAL',default='WARNING')
    parser.add_argument('--pathfile',help='the file with the paths to the compositions',type=str)
    parser.add_argument('--check',help='4 debuggin: check the phenopacket file against the converted json')
    args=parser.parse_args()

    loglevel=getattr(logging, args.loglevel.upper(),logging.WARNING)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(filename='./phenopacket_4_interpretation_phenopacket_structured.log',filemode='w',level=loglevel)

    inputfile="input"
    if args.pathfile:
        inputfile=args.pathfile

    print(inputfile)
#    print (args.check)
    if args.check:
        check=True
        print ('Check is set to true')


    #read input file with path where compositions are located
    try:
        with open(inputfile,'r') as f:
            paths=f.readlines()
            paths=[x.strip() for x in paths]

            print ('paths read:')
            for path in paths:
                print(path)
    except:
        print(f"problem with input file {inputfile}")
        exit(1)


    #find a list of all the compositions
    list_of_compositions={}
    for path in paths:
        newlist=find_compositions(path)
        list_of_compositions.update(newlist)
    print("compositions found:")
    for listc in list_of_compositions:
        for file in list_of_compositions[listc]:
            print (listc+"/"+file)


    #Convert each composition into a phenopacket-like json and serialize
    #Phenopacket obtained
    for listc in list_of_compositions:
        for file in list_of_compositions[listc]:
            filename=listc+"/"+file
            jsonconverted=convert2phenojson(filename)
            logging.debug(json.dumps(jsonconverted,sort_keys=True,indent=4))
#            outputfile=listc+"/PHENO_FROM_"+file
            outputfile='./PHENO_FROM'+file
            print (f'New pheno file created: {outputfile}')
#        with open('../phenowholeinput.json','r') as f:
#            jsoninput = json.load(f)
#        jsonconverted=jsoninput
            print (f'check is {check}')
            parsejsonpacketlike(outputfile,jsonconverted,check)


if __name__ == '__main__':
    main()