import os

import pandas as pd
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDFS, XSD

EX = Namespace("http://narc.org/agri_knowledge#")
AGROVOC = Namespace("https://aims.fao.org/aos/agrivoc/c_")

g = Graph()
g.bind("ex", EX)
g.bind("rdfs", RDFS)


def get_uri(prefix, name):
    final_name = name.replace(" ", "_").replace("/", "_")
    return URIRef(prefix + final_name)


zone_uris = {}
crop_uris = {}
disease_uris = {}
solution_uris = {}


## Adding Zones
df_zones = pd.read_csv("data_new/nepal_zone.csv")
df_zones.columns = df_zones.columns.str.strip()

for index, row in df_zones.iterrows():
    zone_uri = get_uri(EX, f"Zone_{row['Zone_ID']}")
    zone_uris[row["Zone_ID"]] = zone_uri

    g.add((zone_uri, RDF.type, EX.Zone))
    g.add((zone_uri, RDFS.label, Literal(row["Zone_Name"])))
    g.add((zone_uri, EX.altitudeRange, Literal(row["Altitude_Range_Meters"])))
    g.add((zone_uri, EX.climateType, Literal(row["Climate_Type"])))
    g.add((zone_uri, EX.typicalSoil, Literal(row["Typical_Soil"])))

## Adding Crops

df_crops = pd.read_csv("data_new/crops_nepal.csv")
df_crops.columns = df_crops.columns.str.strip()

for index, row in df_crops.iterrows():
    crop_uri = get_uri(EX, f"Crop_{row['Crop_ID']}")
    crop_uris[row["Crop_ID"]] = crop_uri

    g.add((crop_uri, RDF.type, EX.Crop))
    g.add((crop_uri, RDFS.label, Literal(row["Crop_Name"])))
    g.add((crop_uri, EX.scientificName, Literal(row["Scientific_Name"])))

## Adding Suitability

df_suitability = pd.read_csv("data_new/crop_suitability.csv")
df_suitability.colums = df_suitability.columns.str.strip()

for index, row in df_suitability.iterrows():
    crop_uri = crop_uris.get(row["Crop_ID"])
    zone_uri = zone_uris.get(row["Zone_ID"])

    if crop_uri and zone_uri:
        g.add((crop_uri, EX.suitableIn, zone_uri))
        g.add((crop_uri, EX.season, Literal(row["Season"])))
    else:
        print(f"Could not link {row['Crop_ID']} to {row['Zone_ID']}")

## Pathology addition

df_pathology = pd.read_csv("data_new/narc_pathology.csv")
df_pathology.columns = df_pathology.columns.str.strip()

for index, row in df_pathology.iterrows():
    disease_uri = get_uri(EX, f"Disease{row['Disease_ID']}")
    disease_uris[row["Disease_ID"]] = disease_uri

    g.add((disease_uri, RDF.type, EX.Disease))
    g.add((disease_uri, RDFS.label, Literal(row["Disease_Name"])))
    g.add((disease_uri, EX.pathogenName, Literal(row["Pathogen_Name"])))
    g.add((disease_uri, EX.severity, Literal(row["Severity"])))
    g.add((disease_uri, EX.notes, Literal(row["Notes"])))

    parent_crop_uri = crop_uris.get(row["Crop_ID"])

    if parent_crop_uri:
        g.add((parent_crop_uri, EX.succeptibleTo, disease_uri))

## Solution addition
df_solution = pd.read_csv("data_new/narc_solution.csv")
df_solution.columns = df_solution.columns.str.strip()

for index, row in df_solution.iterrows():
    solution_uri = get_uri(EX, f"Solution{row['Solution_ID']}")
    solution_uris[row["Solution_ID"]] = solution_uri

    g.add((solution_uri, RDF.type, EX.Solution))
    g.add((solution_uri, RDFS.label, Literal(row["Agent_Name"])))
    g.add((solution_uri, EX.dosage, Literal(row["Dosage"])))
    g.add((solution_uri, EX.method, Literal(row["Method"])))
    g.add((solution_uri, EX.Description, Literal((row["Description"]))))

    target_id = row["Target_Disease_ID"]
    parent_disease_uri = disease_uris.get(target_id)

    if parent_disease_uri:
        g.add((parent_disease_uri, EX.hasSolution, solution_uri))
    else:
        print(f"could not find disease {target_id} for solution {row['Solution_ID']}")


output_file = "narc_graph.ttl"
g.serialize(output_file, format="turtle")
print(f"A rdf structure of {len(g)} triples was created.")
