#!/usr/bin/python3
'''Parse a pheno-like json, creates the Phenopacket messages and serialize them.
Optionally check that the serialization has gone well'''
import json
from json_tools import diff

import copy
import collections

from .ChangeDictNamingConvention import change_dict_naming_convention,convertcase
from .ParserPhenoBlocks import ParsePheno,ParseFamily,ParseInterpretation, \
    ParseCohort

from google.protobuf import message
from google.protobuf.json_format import Parse, MessageToJson

from typing import Any,Callable

import logging

def parsejsonpacketlike(outputfile:str,jsoninput:json,check:bool=False)->None:
    logging.info("json file has got:")
    for j in jsoninput:
        logging.info(j)
    logging.info('\n')

    if 'Phenopacket' in jsoninput:
        jsonpheno=jsoninput['Phenopacket']
        originaljson=copy.deepcopy(jsonpheno)
 #       print (originaljson)
        pheno=ParsePheno(jsonpheno)
        printmessage('phenotype.json',pheno)
        printmessage(outputfile,pheno)
        #reread from the disk and compare the two json
#        firstjson=ordered(MessageToJson(pheno))
#        secondjson=ordered(MessageToJson(readmessage('phenotype.json',Phenopacket())))
        with open('phenotype.json','r') as f:
            newjson = json.load(f)
        otherjson=change_dict_naming_convention(newjson,convertcase)
        one=flatten(originaljson)
        two=flatten(otherjson)
        logging.info("Phenopacket: diff between original json and serialized one")
        logging.info(json.dumps((diff(one,two)),indent=4))

#
    if 'Family' in jsoninput:
        jsonfamily=jsoninput['Family']
        originaljson=copy.deepcopy(jsonfamily)
        fam=ParseFamily(jsonfamily)
        printmessage('family.json',fam)
        printmessage(outputfile,fam)
        #reread from the disk and compare the two json
        with open('family.json','r') as f:
            newjson = json.load(f)
        otherjson=change_dict_naming_convention(newjson,convertcase)
        one=flatten(originaljson)
        two=flatten(otherjson)
        logging.info("Family: diff between original json and serialized one")
        logging.info(json.dumps((diff(one,two)),indent=4))

    if 'Cohort' in jsoninput:
        jsoncohort=jsoninput['Cohort']
        originaljson=copy.deepcopy(jsoncohort)
        coh=ParseCohort(jsoncohort)
        printmessage('cohort.json',coh)
        printmessage(outputfile,coh)
        with open('cohort.json','r') as f:
            newjson = json.load(f)
        otherjson=change_dict_naming_convention(newjson,convertcase)
        one=flatten(originaljson)
        two=flatten(otherjson)
        logging.info("Cohort: diff between original json and serialized one")
        logging.info(json.dumps((diff(one,two)),indent=4))

    if "Interpretation" in jsoninput:
        jsoninter=jsoninput['Interpretation']
        originaljson=copy.deepcopy(jsoninter)
        inter=ParseInterpretation(jsoninter)
        printmessage('interpretation.json',inter)
        printmessage(outputfile,inter)
        with open('interpretation.json','r') as f:
            newjson = json.load(f)
        otherjson=change_dict_naming_convention(newjson,convertcase)
        one=flatten(originaljson)
        two=flatten(otherjson)
        logging.info("Interpretation: diff between original json and serialized one")
        logging.info(json.dumps((diff(one,two)),indent=4))

# try:
#     os.remove(test_json_file)
# except OSError as e:
#     print("Error: %s - %s." % (e.filename, e.strerror))


def flatten(d:dict, parent_key:str='', sep:str='_')->dict:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def printmessage(string:str,message:message)->None:
    with open(string, 'w') as jsfile:
        json = MessageToJson(message)
        jsfile.write(json)

def readmessage(string:str,type:message)->message:
    with open(string, 'r') as jsfile:
        round_trip = Parse(message=type, text=jsfile.read())
        return round_trip


def ordered(obj:Any)->Any:
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj





