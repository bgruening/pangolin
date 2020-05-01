import imp
import argparse
from collections import defaultdict
import pandas as pd
import csv
import report_classes as classes


parser = argparse.ArgumentParser(description="Results generator script")

parser.add_argument("-p", required=True, help="pangolin output")
parser.add_argument("-b", required=True, help="background data csv")
parser.add_argument("-o", required=True, help="output")


args = parser.parse_args()

pangolin_output =  str(args.p)
background = str(args.b)

def get_lineages_present(pangolin_output):

    lineages_present = set()
    with open(pangolin_output,newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lineages_present.add(row["lineage"])

    return lineages_present

def make_objects(background_data, lineages_present):

    lineage_objects = []
    taxa = []
    lineages_to_taxa = defaultdict(list)
    lin_obj_dict = {}

    with open(background_data,newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            gisaid_id=row["GISAID ID"]
            lin_string = row["lineage"]
            date = row["sample date"]
            country = row["country"]
            
            tax_name = f"{name}|{gisaid_id}|{country}|{date}"

            if lin_string in lineages_present:
                new_taxon = classes.taxon(tax_name, lin_string)
                taxa.append(new_taxon)
                
                lineages_to_taxa[lin_string].append(new_taxon)


    for lin, taxa in lineages_to_taxa.items():
        l_o = classes.lineage(lin, taxa)

        lin_obj_dict[lin] = l_o

    return lin_obj_dict


def make_dataframe(pangolin_output, background_data):

    lineages_present = get_lineages_present(pangolin_output)
    lin_obj_dict = make_objects(background_data, lineages_present)

    dataframe_dict = defaultdict(list)

    for i in lin_obj_dict.values():
        
        dataframe_dict["Lineage name"].append(i.id)
        dataframe_dict["Most common countries"].append(i.main_locs)
        dataframe_dict["Date range"].append((i.pretty_oldest,i.pretty_mrd))
        dataframe_dict["Number of taxa"].append(len(i.taxa))
        dataframe_dict["Days since last sampling"].append(i.last_sampled)

    dataframe = pd.DataFrame(dataframe_dict)

    dataframe.set_index("Lineage name", inplace=True)
    
    new_countries_list = []
    for i in dataframe["Most common countries"]:
        new_countries = str(i).strip("[").strip("]").replace("'","")
        new_countries_list.append(new_countries)
    dataframe["Most common countries"] = new_countries_list

    new_dates = []
    for i in dataframe["Date range"]:
        new_date = str(i).strip("(").strip(")").replace("'","")
        new_dates.append(new_date)
    dataframe["Date range"] = new_dates


    return dataframe


dataframe = make_dataframe(pangolin_output, background)

dataframe.to_csv(str(args.o))

