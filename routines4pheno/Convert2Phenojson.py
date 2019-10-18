#!/usr/bin/python3
'''convert from an interpretation template composition or a cohort template composition
read from a json file to a pheno-like json which is easier to read with written
routines'''
import json
import logging
import sys

def convert2phenojson(filename:str)->json:
#    print (filename)
    with open(filename,'r') as f:
        jsoncomp = json.load(f)
        myjson={}
        if 'interpretation_report' in jsoncomp:
            myjson['Interpretation']=convert_interpretation_report(jsoncomp['interpretation_report'])
        elif 'cohort_report' in jsoncomp:
            myjson['Cohort']=convert_cohort_report(jsoncomp['cohort_report'])
        else:
            print(f'{filename} is not an interpretation nor a cohort composition')
            logging.error(f'{filename} is not an interpretation nor a cohort composition')
    return myjson



def convert_interpretation_report(jsoncomp:json)->json:
    myjson={}
    jsonint=jsoncomp['interpretation'][0]
    #id
    myjson['id']=jsonint['id'][0]['|id']
    #resolution_status
    myjson['resolution_status']=jsonint['resolution_status'][0]['|value']
    #phenopacket or family
    if 'phenopacket' in jsonint:
        myjson['phenopacket']=convertPheno(jsonint['phenopacket'][0])
    elif 'family' in jsonint:
        myjson['family']=convertFamily(jsonint['family'][0])
    else:
        logging.error('one between phenopacket or family is required in interpretation composition')
        exit(1)
    #diagnosis
    myjson['diagnosis']=convertDiagnosis(jsonint['diagnosis'][0])
    #metadata
    myjson['meta_data']=convertMeta(jsonint['metadata'][0])
    return myjson

def convert_cohort_report(jsoncomp:json)->json:
    myjson={}
    return myjson


def convertPheno(jsonint:json)->json:
    jp={}
    #id
    jp['id']=jsonint['id'][0]['|id']
    #subject
    subject={}
    subject['id']=jsonint['subject'][0]
    jp['subject']=subject
    #phenotypic_features
    if 'phenotypic_feature' in jsonint:
        jp['phenotypic_features']=convertPhenotypic_features(jsonint['phenotypic_feature'])
    #biosamples
    if 'biosample' in jsonint:
        jp['biosamples']=convertBiosamples(jsonint['biosample'])
    #genes
    if 'gene' in jsonint:
        jp['genes']=convertGenes(jsonint['gene'])
    #variants
    if 'variant' in jsonint:
        jp['variants']=convertVariants(jsonint['variant'])
    #diseases
    if 'disease' in jsonint:
        jp['diseases']=convertDiseases(jsonint['disease'])
    #hts_files
    if 'htsfile' in jsonint:
        jp['hts_files']=convertHts_Files(jsonint['htsfile'])
    #metadata
    jp['meta_data']=convertMeta(jsonint['metadata'][0])
    return jp

def convertFamily(jsonint:json)->json:
    jf={}
    jf['id']=jsonint['id'][0]['|id']
    #proband
    jf['proband']=convertPheno(jsonint['proband'][0])
    #relatives
    if 'relative' in jsonint:
        relatives=[]
        for rel in jsonint['relative']:
            relative.append(convertPheno(rel[0]))
        jf['relatives']=relatives
    #pedigree
    jf['pedigree']=convertPedigree(jsonint['pedigree'])
    #hts_files
    if 'htsfile' in jsonint:
        jf['hts_files']=convertHts_Files(jsonint['htsfile'])
    #metadata
    jf['meta_data']=convertMeta(jsonint['metadata'][0])
    return jf



def convertMeta(jsonmeta:json)->json:
    metadata={}
    metadata['created']=jsonmeta['created'][0]
    metadata['created_by']=jsonmeta['created_by'][0]
    resources=[]
    for res in jsonmeta['resource']:
        resource={}
        resource['id']=res['id'][0]['|id']
        resource['name']=res['name'][0]
        resource['url']=res['url'][0]
        resource['version']=res['version'][0]
        resource['namespace_prefix']=res['namespace_prefix'][0]
        resource['iri_prefix']=res['iri-prefix'][0]
        resources.append(resource)
    metadata['resources']=resources
    if 'external_reference' in jsonmeta:
        external_references=[]
        for ext in jsonmeta['external_reference']:
            external_ref={}
            external_ref['id']=ext['id'][0]['|id']
            if 'description' in ext:
                external_ref['description']=ext['description'][0]
            external_references.append(external_ref)
        metadata['external_references']=external_references
    if 'update' in jsonmeta:
        updates=[]
        for upd in jsonmeta['update']:
            update={}
            update['timestamp']=upd['timestamp'][0]
            update['comment']=upd['comment'][0]
            if 'updated_by' in upd:
                update['updated_by']=upd['updated_by'][0]
            updates.append(update)
        metadata['updates']=updates
    if 'submitted_by' in jsonmeta:
        metadata['submitted_by']=jsonmeta['submitted_by'][0]
    if 'phenopacket_schema_version' in jsonmeta:
        metadata['phenopacket_schema_version']=jsonmeta['phenopacket_schema_version'][0]
    return metadata

def convertPhenotypic_features(jsonphenot:list)->list:
    phenotypic_features=[]
    for phen in jsonphenot:
        phenotypic_feature={}
        ptype={}
        ptype['id']=phen['type'][0]['|terminology']+':'+ \
                    phen['type'][0]['|code']
        ptype['label']=phen['type'][0]['|value']
        phenotypic_feature['type']=ptype
        if 'description' in phen:
            phenotypic_feature['description']=phen['description'][0]
        if 'negated' in phen:
            phenotypic_feature['negated']=phen['negated'][0]
        if 'severity' in phen:
            pf={}
            pf['id']=phen['severity'][0]['|terminology']+':'+ \
                     phen['severity'][0]['|code']
            pf['label']=phen['severity'][0]['|value']
            phenotypic_feature['severity']=pf
        if 'modifier' in phen:
            modifiers=[]
            for modi in phen['modifier']:
                modifier={}
                modifier['id']=modi['|terminology']+':'+ \
                               modi['|code']
                modifier['label']=modi['|value']
                modifiers.append(modifier)
            phenotypic_feature['modifiers']=modifiers
        if 'onset' in phen:
            onset={}
            onset['id']=phen['onset'][0]['|terminology']+':'+ \
                                        phen['onset'][0]['|code']
            onset['label']=phen['onset'][0]['|value']
            phenotypic_feature['onset']=onset
        if 'evidence' in phen:
            evidences=[]
            for evid in phen['evidence']:
                evidence={}
                ev={}
                ev['id']=evid['evidence_code'][0]['|terminology']+':'+ \
                         evid['evidence_code'][0]['|code']
                ev['label']=evid['evidence_code'][0]['|value']
                evidence['evidence_code']=ev

                if 'external_reference' in evid:
                    ref={}
                    ref['id']=evid['external_reference'][0]['id'][0]['|id']
                    if 'description' in evid['external_reference'][0]:
                        ref['description']=evid['external_reference'][0]['description'][0]
                    evidence['reference']=ref
                evidences.append(evidence)
            phenotypic_feature['evidence']=evidences
        phenotypic_features.append(phenotypic_feature)
    return phenotypic_features


def convertBiosamples(jsonbio:list)->list:
    biosamples=[]
    for bio in jsonbio:
        biosample={}
        biosample['id']=bio['id'][0]['|id']
        if 'individual_id' in bio:
            biosample['individual_id']=bio['individual_id'][0]['|id']
        if 'description' in bio:
            biosample['description']=bio['description'][0]
        sampled_tissue={}
        sampled_tissue['id']=bio['sampled_tissue'][0]['|terminology']+':'+ \
                             bio['sampled_tissue'][0]['|code']
        sampled_tissue['label']=bio['sampled_tissue'][0]['|value']
        biosample['sampled_tissue']=sampled_tissue
        if 'phenotypic_feature' in bio:
            biosample['phenotypic_features']=convertPhenotypic_features(bio['phenotypic_feature'])
        if 'taxonomy' in bio:
            taxonomy={}
            taxonomy['id']=bio['taxonomy'][0]['|terminology']+':'+ \
                           bio['taxonomy'][0]['|code']
            taxonomy['label']=bio['taxonomy'][0]['|value']
            biosample['taxonomy']=taxonomy
        if 'individual_age_at_collection' in bio:
            biosample['individual_age_at_collection']=bio['individual_age_at_collection'][0]['duration_value'][0]
        if 'histological_diagnosis' in bio:
            histo={}
            histo['id']=bio['histological_diagnosis'][0]['|terminology']+':'+ \
                           bio['histological_diagnosis'][0]['|code']
            histo['label']=bio['histological_diagnosis'][0]['|value']
            biosample['histological_diagnosis']=histo
        if 'tumor_progression' in bio:
            tumor={}
            tumor['id']=bio['tumor_progression'][0]['|terminology']+':'+ \
                           bio['tumor_progression'][0]['|code']
            tumor['label']=bio['tumor_progression'][0]['|value']
            biosample['tumor_progression']=tumor
        if 'tumor_grade' in bio:
            grade={}
            grade['id']=bio['tumor_grade'][0]['|terminology']+':'+ \
                           bio['tumor_grade'][0]['|code']
            grade['label']=bio['tumor_grade'][0]['|value']
            biosample['tumor_grade']=grade
        if 'diagnostic_markers' in bio:
            diamarks=[]
            for dm in bio['diagnostic_markers']:
                diamark={}
                diamark['id']=dm['|terminology']+':'+ \
                              dm['|code']
                diamark['label']=dm['|value']
                diamarks.append(diamark)
            biosample['diagnostic_markers']=diamarks
        if 'procedure' in bio:
            procedure={}
            code={}
            code['id']=bio['procedure'][0]['code'][0]['|terminology']+':'+ \
                       bio['procedure'][0]['code'][0]['|code']
            code['label']=bio['procedure'][0]['code'][0]['|value']
            procedure['code']=code
            if 'body_site' in bio['procedure'][0]:
                body_site={}
                body_site['id']=bio['procedure'][0]['body_site'][0]['|terminology']+':'+ \
                                bio['procedure'][0]['body_site'][0]['|code']
                body_site['label']=bio['procedure'][0]['body_site'][0]['|value']
                procedure['body_site']=body_site
            biosample['procedure']=procedure
        if 'htsfile' in bio:
            hts_files=convertHts_Files(bio['htsfile'])
            biosample['hts_files']=hts_files
        if 'variant' in bio:
            variants=convertVariants(bio['variant'])
            biosample['variants']=variants
        if 'is_control_sample' in bio:
            biosample['is_control_sample']=bio['is_control_sample'][0]
        biosamples.append(biosample)
    return biosamples


def convertHts_Files(jsonhts:list)->list:
    hts_files=[]
    for hts in jsonhts:
        htsfile={}
        htsfile['uri']=hts['uri'][0]
        htsfile['hts_format']=hts['hts_format'][0]['|code']
        htsfile['genome_assembly']=hts['genome_assembly'][0]
        if 'description' in hts:
            htsfile['description']=hts['description'][0]
        if 'individual_identifier' in hts:
            htsfile['individual_to_sample_identifiers']={hts['individual_identifier'][0]['|id']: \
                                                        hts['sample_identifier'][0]['|id']}
        hts_files.append(htsfile)
    return hts_files

def convertVariants(jsonv:list)->list:
    variants=[]
    for vart in jsonv:
        variant = [{} for i in range(4)]
        number_of_subvariants=0
        already_one=False
        if 'hgvsallele' in vart:
            if not already_one:
                already_one=True
            else:
                number_of_subvariants+=1
            allele={}
            if 'id' in vart['hgvsallele']:
                allele['id']=vart['hgvsallele'][0]['id'][0]['|id']
            allele['hgvs']=vart['hgvsallele'][0]['hgvs'][0]
            variant[number_of_subvariants]['hgvs_allele']=allele
        if 'vcfallele' in vart:
            if not already_one:
                already_one=True
            else:
                number_of_subvariants+=1
            allele={}
            allele['genome_assembly']=vart['vcfallele'][0]['genome_assembly'][0]
            if 'id' in vart['vcfallele'][0]:
                allele['id']=vart['vcfallele'][0]['id'][0]['|id']
            allele['chr']=vart['vcfallele'][0]['chr'][0]
            allele['pos']=vart['vcfallele'][0]['pos'][0]
            allele['ref']=vart['vcfallele'][0]['re'][0]
            allele['alt']=vart['vcfallele'][0]['alt'][0]
            if 'info' in vart['vcfallele'][0]:
                allele['info']=vart['vcfallele'][0]['info'][0]
            variant[number_of_subvariants]['vcf_allele']=allele
        if 'spdiallele' in vart:
            if not already_one:
                already_one=True
            else:
                number_of_subvariants+=1
            allele={}
            if 'id' in vart['spdiallele'][0]:
                allele['id']=vart['spdiallele'][0]['id'][0]['|id']
            allele['seq_id']=vart['spdiallele'][0]['seq_id'][0]['|id']
            allele['position']=vart['spdiallele'][0]['position'][0]
            allele['deleted_sequence']=vart['spdiallele'][0]['deleted_sequence'][0]
            allele['inserted_sequence']=vart['spdiallele'][0]['inserted_sequence'][0]
            variant[number_of_subvariants]['spdi_allele']=allele
        if 'iscnallele' in vart:
            if not already_one:
                already_one=True
            else:
                number_of_subvariants+=1
            allele={}
            if 'id' in vart['iscnallele'][0]:
                allele['id']=vart['iscnallele'][0]['id'][0]['|id']
            allele['iscn']=vart['iscnallele'][0]['iscn'][0]
            variant[number_of_subvariants]['iscn_allele']=allele
        if 'zygosity' in vart:
            zygo={}
            zygo['id']=vart['zygosity'][0]['|terminology']+':'+\
                       vart['zygosity'][0]['|code']
            zygo['label']=vart['zygosity'][0]['|value']
            for i in range(number_of_subvariants):
                variant[i]['zygosity']=zygo
        variants.extend(variant)
    return variants


def convertGenes(jsongenes:list)->list:
    genes=[]
#    print ('jsongenes')
#    print (jsongenes)
    for ge in jsongenes:
        gene={}
        gene['id']=ge['gene_symbol'][0]['|terminology']+':'+\
                   ge['gene_symbol'][0]['|code']
        gene['symbol']=ge['gene_symbol'][0]['|value']
        genes.append(gene)
    return genes

def convertDiseases(jsondiseases:list)->list:
    diseases=[]
    for dis in jsondiseases:
        disease={}
        term={}
        term['id']=dis['term'][0]['|terminology']+':'+\
                   dis['term'][0]['|code']
        term['label']=dis['term'][0]['|value']
        disease['term']=term
        if 'onset' in dis:
            disease['onset']=dis['onset'][0]['duration_value'][0]
        if 'tumor_stage' in dis:
            tumor_stage=[]
            for tum in dis['tumor_stage']:
                tumor={}
                tumor['id']=tum['|terminology']+':'+\
                            tum['|code']
                tumor['label']=tum['|value']
                tumor_stage.append(tumor)
            disease['tumor_stage']=tumor_stage
        diseases.append(disease)
    return diseases

def convertDiagnosis(dia:json)->json:
    diagnosis={}
    diagnosis['disease']=convertDiseases(dia['disease'])[0]
    diagnosis['genomic_interpretations']=convertGenomicInterpretations(dia['genomic_interpretation'][0])
    return diagnosis


def convertGenomicInterpretations(geno:json)->json:
    genints=[]
    if 'gene' in geno:
        for gene in convertGenes(geno['gene']):
#            print (gene)
            genint={}
            genint['status']=geno['genomicinterpretation_status'][0]['|value']
            genint['gene']=gene
            genints.append(genint)
    if 'variant' in geno:
        zygo='Undef'
        if 'zygosity' in geno['variant']:
            zygo=geno['variant']['zygosity']
            del geno['variant']['zygosity']
        for variant in convertVariants(geno['variant']):
            genint={}
            genint['status']=geno['genomicinterpretation_status'][0]['|value']
            genint['variant']=variant
            if zygo != 'Undef':
                genint['variant']['zygosity']=zygo
            genints.append(genint)
    return genints

def convertPedigree(jsonped:json)->json:
    pedigree={}
    persons=[]
    for per in jsonperd['person']:
        person={}
        person['family_id']=per['family_id'][0]['|id']
        person['individual_id']=per['individual_id'][0]['|id']
        person['paternal_id']=per['paternal_id'][0]['|id']
        person['maternal_id']=per['maternal_id'][0]['|id']
        person['sex']=per['sex'][0]['|value']
        person['affected_status']=per['affected_status'][0]['|code']
        persons.append(person)
    pedigree['persons']=persons
    return pedigree