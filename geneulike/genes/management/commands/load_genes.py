# Generated by Django 2.0.13 on 2019-10-08 08:31

from django.db import migrations

import sys
import os
import tempfile
import shutil
from urllib.request import urlopen
from zipfile import ZipFile
import gzip
from time import gmtime, strftime
from geneulike.genes.models import Gene
from geneulike.species.models import Species

from django.core.management.base import BaseCommand, CommandError

def download_datafiles():

    dirpath = '/app/loading_data/genes/'
    urls = [
        "ftp://ftp.ncbi.nih.gov/gene/DATA/gene_info.gz",
        "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2refseq.gz",
        "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_history.gz"
        "ftp://ftp.ncbi.nih.gov/gene/DATA/gene2ensembl.gz",
    ]
    for url in urls :
        if not check_file(dirpath, url):
            file_name = url.split('/')[-1]
            u = urlopen(url)
            f = open(os.path.join(dirpath,file_name), 'wb')
            meta = u.info()
            file_size = int(meta.get("Content-Length")[0])
            print("Downloading: %s"% (file_name))

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)

            f.close()
            if ".gz" in file_name :
                with gzip.open(os.path.join(dirpath,file_name), 'rb') as f_in:
                    with open(os.path.join(dirpath,file_name.replace('.gz','')), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

    return dirpath

def concat_files(dirpath, species_list):

    gene2ensembl = os.path.join(dirpath,'gene2ensembl')
    gene_info = os.path.join(dirpath,'gene_info')
    gene2refseq = os.path.join(dirpath,'gene2refseq')
    gene_history = os.path.join(dirpath,'gene_history')

    dData_organized = {}
    # Init dico with gene_info file
    print("INDEX gene_info")
    try :
        print(gene_info)
        fGene_info = open(gene_info,'r')
        for gene_ligne in fGene_info.readlines():
            if gene_ligne[0] != '#':
                line_split = gene_ligne.split('\t')
                tax_id = line_split[0]
                GeneID = line_split[1]
                symbol = line_split[2]
                synonyms = line_split[4]
                if tax_id in species_list :
                    if GeneID not in dData_organized :
                        dData_organized[GeneID] = {'tax_id':tax_id,'symbol':symbol,'synonyms':synonyms, "gene_id": GeneID,
                            'discontinued_gene_ids': [], 'ensembl_rna': [], 'ensembl_protein': [], 'accession_rna': [], 'accession_protein':[]
                        }
        fGene_info.close()
    except Exception as e:
        print("args: ", e.args)
        print("errno: ", e.errno)
        print("strerror: ", e.strerror)

    #Add Ensembl ID informations
    print("INDEX gene2ensembl")
    try :
        fgene2ensembl = open(gene2ensembl,'r')
        for geneensemble_ligne in fgene2ensembl.readlines():
            if geneensemble_ligne[0] != '#':
                line_split = geneensemble_ligne.split('\t')
                GeneID = line_split[1]
                ensemblID = line_split[2]
                ensembl_rna = line_split[4]
                ensembl_protein = line_split[6]
                if GeneID in dData_organized :
                    dData_organized[GeneID]['ensembl_id'] = ensemblID
                    if not ensembl_rna == "-":
                        dData_organized[GeneID]['ensembl_rna'].append(ensembl_rna)
                        if not [ensembl_rna] == ensembl_rna.split("."):
                            dData_organized[GeneID]['ensembl_rna'].append(ensembl_rna.split(".")[0])
                    if not ensembl_protein == "-":
                        dData_organized[GeneID]['ensembl_protein'].append(ensembl_protein)
                        if not [ensembl_protein] == ensembl_protein.split("."):
                            dData_organized[GeneID]['ensembl_protein'].append(ensembl_protein.split(".")[0])
        fgene2ensembl.close()
    except IOError as e:
        print("args: ", e.args)
        print("errno: ", e.errno)
        print("filename: ", e.filename)
        print("strerror: ", e.strerror)

    print("INDEX gene2refseq")
    try :
        fgene2refseq = open(gene2refseq,'r')
        for line in fgene2refseq.readlines():
            if line[0] != '#':
                line_split = line.split('\t')
                accession_rna = line_split[3]
                accession_protein = line_split[5]
                if GeneID in dData_organized :
                    # Store both versioned and non-versioned id
                    if not accession_rna == "-":
                        dData_organized[GeneID]['accession_rna'].append(accession_rna)
                        if not [accession_rna] == accession_rna.split("."):
                            dData_organized[GeneID]['accession_rna'].append(accession_rna.split(".")[0])
                    if not accession_protein == "-":
                        dData_organized[GeneID]['accession_protein'].append(accession_protein)
                        if not [accession_protein] == accession_protein.split("."):
                            dData_organized[GeneID]['accession_protein'].append(accession_protein.split(".")[0])
        fgene2refseq.close()
    except IOError as e:
        print("args: ", e.args)
        print("errno: ", e.errno)
        print("filename: ", e.filename)
        print("strerror: ", e.strerror)

    print("INDEX gene_history")
    try :
        file = open(gene_history,'r')
        for line in file.readlines():
            if line[0] != '#':
                line_split = line.split('\t')
                GeneID = line_split[1]
                discontinued_gene_id = line_split[2]
                if not GeneID == "-" and GeneID in dData_organized :
                    dData_organized[GeneID]['discontinued_gene_ids'].append(discontinued_gene_id)
        file.close()
    except IOError as e:
        print("args: ", e.args)
        print("errno: ", e.errno)
        print("filename: ", e.filename)
        print("strerror: ", e.strerror)

    return dData_organized


def insertCollections(gene_dict):
    print('CreateCollection - create GeneULike_geneDB collection')
    gene_list = []
    for key, value in gene_dict.items():
        gene_list.append(Gene(**value))
    Gene.objects.bulk_create(gene_list, batch_size=1000)

def check_file(path, url):
        file_name = url.split('/')[-1]
        if ".gz" in file_name :
            file_name = file_name.replace('.gz','')

        return os.path.exists(os.path.join(path, file_name))

def populate_genes():
        species = Species.objects.all()
        if species.count == 0:
            print("No species found : skipping")
            return
        species_names = [specie.name for specie in species]
        species_ids = [specie.species_id for specie in species]
        print("Processing species {}".format(", ".join(species_names)))

        dirpath = download_datafiles()
        data = concat_files(dirpath, species_ids)
        insertCollections(data)

class Command(BaseCommand):

    help = 'Populate genes'

    def handle(self, *args, **options):
        populate_genes()
