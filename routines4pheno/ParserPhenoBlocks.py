#!/usr/bin/python3
'''Parser for the main building blocks of the phenopacket schema, that are
Phenopacket, Family, Cohort and Interpretation'''
import json

import datetime
import logging

from google.protobuf.json_format import Parse, MessageToJson
from google.protobuf import message
from google.protobuf.timestamp_pb2 import Timestamp

from base_pb2 import MetaData,Individual,Disease,Biosample,Pedigree,Gene,PhenotypicFeature, \
     Variant,HtsFile,OntologyClass,Age,Evidence,ExternalReference

from phenopackets_pb2 import Phenopacket,Family,Cohort
from interpretation_pb2 import Interpretation,Diagnosis,GenomicInterpretation

from typing import List
import copy

def ParsePheno(jsonpheno:json)->Phenopacket:
    phenopacket_input={}
    ##first required fields
    #id
    phenopacket_input['id']=jsonpheno['id']
    #metadata
    phenopacket_input['meta_data']=ParseMeta(jsonpheno['meta_data'])
    ##optional and recommended fields
    #subject
    if 'subject' in jsonpheno:
        phenopacket_input['subject']= ParseSubject(jsonpheno['subject'])
    #diseases
    if 'diseases' in jsonpheno:
        phenopacket_input['diseases']=ParseDiseases(jsonpheno['diseases'])
    #biosamples
    if 'biosamples' in jsonpheno:
        phenopacket_input['biosamples']=ParseBiosamples(jsonpheno['biosamples'])
    #genes
    if 'genes' in jsonpheno:
        phenopacket_input['genes']=ParseGenes(jsonpheno['genes'])
    #phenotypic_features
    if 'phenotypic_features' in jsonpheno:
        phenopacket_input['phenotypic_features']=ParsePhenotypic(jsonpheno['phenotypic_features'])
    #variants
    if 'variants' in jsonpheno:
        phenopacket_input['variants']=ParseVariants(jsonpheno['variants'])
    #hts_files
    if 'hts_files' in jsonpheno:
        phenopacket_input['hts_files']= Parsehts(jsonpheno['hts_files'])
    return Phenopacket(**phenopacket_input)


def ParseFamily(jsonfamily:json)->Family:
    family_input={}
    ##first required fields
    #id
    family_input['id']=jsonfamily['id']
    #proband
    family_input['proband']=ParsePheno(jsonfamily['proband'])
    #pedigree
    family_input['pedigree']=ParsePedigree(jsonfamily['pedigree'])
    #metadata
    family_input['meta_data']= ParseMeta(jsonfamily['meta_data'])
    ##optional and recommended fields
    #relatives
    if 'relatives' in jsonfamily:
        family_input['relatives']=ParseRelatives(jsonfamily['relatives'])
    #hts_files
    if 'hts_files' in jsonfamily:
        family_input['hts_files']= Parsehts(jsonfamily['hts_files'])
    return Family(**family_input)


def ParseCohort(jsoncohort:json)->Cohort:
    cohort_input={}
    ##first required fields
    #id
    cohort_input['id']=jsoncohort['id']
    #members
    cohort_input['members']=ParseRelatives(jsoncohort['members'])
    #metadata
    cohort_input['meta_data']=ParseMeta(jsoncohort['meta_data'])
    ##optional and recommended fields
    #description
    if 'description' in jsoncohort:
        cohort_input['description']=jsoncohort['description']
    #hts_files
    if 'hts_files' in jsoncohort:
        cohort_input['hts_files']=Parsehts(jsoncohort['hts_files'])

    return Cohort(**cohort_input)

def ParseInterpretation(jsoninterpretation:json)->Interpretation:
    interpretation_input={}
    ##first required fields
    #id
    interpretation_input['id']=jsoninterpretation['id']
    #resolution_status
    interpretation_input['resolution_status']=jsoninterpretation['resolution_status']
    #phenopacket or family
    if 'phenopacket' in jsoninterpretation:
        interpretation_input['phenopacket']=ParsePheno(jsoninterpretation['phenopacket'])
    if 'family' in jsoninterpretation:
        interpretation_input['family']=ParseFamily(jsoninterpretation['family'])
    #metadata
    interpretation_input['meta_data']=ParseMeta(jsoninterpretation['meta_data'])
    #diagnosis
    if 'diagnosis' in jsoninterpretation:
        interpretation_input['diagnosis']=ParseDiagnosis(jsoninterpretation['diagnosis'])
    return Interpretation(**interpretation_input)


def ToOnto(jsononto:json)->OntologyClass:
#    print (jsononto)
    return OntologyClass(id=jsononto['id'],label=jsononto['label'])


def ParseMeta(meta_data:json)->MetaData:
    ts=Timestamp()
    oldvalue=meta_data['created']
    dt= datetime.datetime.strptime(oldvalue,'%Y-%m-%dT%H:%M:%S.%fZ')
    ts.FromDatetime(dt)
    meta_data['created']=ts
    if ('updates' in meta_data):
        for up in meta_data['updates']:
            oldvalue=up['timestamp']
            dt= datetime.datetime.strptime(oldvalue,'%Y-%m-%dT%H:%M:%S.%fZ')
            ts.FromDatetime(dt)
            up['timestamp']=ts
 #   for res in meta_data['resources']:
 #       print("llllllllllllllllll")
 #       print(res)
 #       oldvalue=res['version']
 #       oldvalue='2019-10-10'
 #       res['version']=oldvalue
#        dt=datetime.datetime.strptime(oldvalue,'%Y-%m-%d')
#        ts.FromDatetime(dt)
#        res['version']=ts
#        del res['version']
        # timestamp = Timestamp(seconds=1570695783)
        # res['version']=timestamp
    return MetaData(**meta_data)

def Parsehts(jsonhts:json)->List[HtsFile]:
    hts=[]
    for ht in jsonhts:
        if ht['hts_format']=='at0010':
            ht['hts_format']='VCF'
        hts.append(HtsFile(**ht))
    return hts

def ParseSubject(subjectP:json)->Individual:
    ts=Timestamp()
    if ('date_of_birth' in subjectP):
        oldvalue=subjectP['date_of_birth']
        dt= datetime.datetime.strptime(oldvalue,'%Y-%m-%dT%H:%M:%SZ')
        ts.FromDatetime(dt)
        subjectP['date_of_birth']=ts
    return Individual(**subjectP)

def ParseDiseases(jsondis:list)->List[Disease]:
    diseases=[]
    for dis in jsondis:
        dis['term']=ToOnto(dis['term'])
        if 'tumor_stage' in dis:
            for tum in dis['tumor_stage']:
                tum=ToOnto(tum)
        if 'onset' in dis:
            dis['age_of_onset']=Age(age=dis.pop('onset'))
        diseases.append(Disease(**dis))
    return diseases

def ParseBiosamples(jsonbio:json)->List[Biosample]:
    biosamples=[]
    for bio in jsonbio:
        bio['sampled_tissue']=ToOnto(bio['sampled_tissue'])
        if 'individual_age_at_collection' in bio:
            bio['age_of_individual_at_collection']=Age(age=bio.pop('individual_age_at_collection'))
        if 'taxonomy' in bio:
            bio['taxonomy']=ToOnto(bio['taxonomy'])
        if 'histological_diagnosis' in bio:
            bio['histological_diagnosis']=ToOnto(bio['histological_diagnosis'])
        if 'tumor_progression' in bio:
            bio['tumor_progression']=ToOnto(bio['tumor_progression'])
        if 'tumor_grade' in bio:
            bio['tumor_grade']=ToOnto(bio['tumor_grade'])
        if 'diagnostic_markers' in bio:
            for dm in bio['diagnostic_markers']:
                dm=ToOnto(dm)
        biosamples.append(Biosample(**bio))
    return biosamples

def ParseGenes(jsongenes:json)->List[Gene]:
    genes=[]
    for gen in jsongenes:
        genes.append(Gene(**gen))
    return genes

def ParsePhenotypic(jsonpheno:json)->List[PhenotypicFeature]:
    phefe=[]
    for phe in jsonpheno:
        phe['type']=ToOnto(phe['type'])
        if 'severity' in phe:
            phe['severity']=ToOnto(phe['severity'])
        if 'modifiers' in phe:
            for modi in phe['modifiers']:
                modi=ToOnto(modi)
        if 'onset' in phe:
            phe['class_of_onset']=ToOnto(phe.pop('onset'))
        if 'evidence' in phe:
            for evid in phe['evidence']:
                evid['evidence_code']=ToOnto(evid['evidence_code'])
                if 'reference' in evid:
                    evid['reference']=ExternalReference(**evid['reference'])
        phefe.append(PhenotypicFeature(**phe))
    return phefe

def ParseVariants(jsonvar:json)->List[Variant]:
    variants=[]
    for vari in jsonvar:
        print('bbbb')
        print (vari)
        variants.append(Variant(**vari))
    return variants

def ParsePedigree(jsonped:json)->Pedigree:
    return Pedigree(**jsonped)

def ParseRelatives(jsonrel:json)->List[Phenopacket]:
    relatives=[]
    for rel in jsonrel:
        relatives.append(ParsePheno(rel))
    return relatives

def ParseDiagnosis2(dia:json)->Diagnosis:
    print ('start ParseDiagnosis')
    print (dia)
    dia['disease']=ParseDiseases([dia['disease']])[0]
    if 'gene' in dia['genomic_interpretations']:
        dia['genomic_interpretations']['gene']=Gene(**dia['genomic_interpretations']['gene'][0])
    if 'variant' in dia['genomic_interpretations']:
        variants=[]
        for vari in dia['genomic_interpretations']['variant']:
            variants.append(Variant(**vari))
#        del dia['genomic_interpretations']['variant']
        dia['genomic_interpretations']['variant']=variants[0] #scelgo la prima
#        dia['genomic_interpretations']['variants']=Variant(**dia['genomic_interpretations']['variant'])
    dia['genomic_interpretations']=[GenomicInterpretation(**dia['genomic_interpretations'])]
    print (dia)
    print ('aaaaaaaaaaaaaaaaaaaaaaaaaaa')
    for d in dia:
        print (d)
        print (dia[d])
        print ()
    return Diagnosis(**dia)

def ParseDiagnosis(dia:json)->Diagnosis:
#si aspetta solo una tra Variant e Gene
#per ogni Variant si aspetta solo un allele
#quindi moltiplico le genomic_interpretations
#per contenere tutti i dati
    print (dia)
    dia['disease']=ParseDiseases([dia['disease']])[0]
    genomic_interpretations=[]
    ngi=0
    if 'gene' in dia['genomic_interpretations']:
        genes=ParseGenes(dia['genomic_interpretations']['gene'])
        for gene in genes:
            genomic_interpretation={}
            genomic_interpretation['status']=dia['genomic_interpretations']['status']
            genomic_interpretation['gene']=gene
            genomic_interpretations.append(GenomicInterpretation(**genomic_interpretation))

    if 'variant' in dia['genomic_interpretations']:
        variants=ParseVariants(dia['genomic_interpretations']['variant'])
        for vari in variants:
            genomic_interpretation={}
            genomic_interpretation['status']=dia['genomic_interpretations']['status']
            genomic_interpretation['variant']=vari
            genomic_interpretations.append(GenomicInterpretation(**genomic_interpretation))
    dia['genomic_interpretations']=genomic_interpretations
    return [Diagnosis(**dia)]