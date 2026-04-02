import pandas as pd
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDFS, SKOS, XSD

EX = Namespace("http://agrinep.org/nepal-agri#")
AGROVOC = Namespace("http://aims.fao.org/aos/agrovoc/c_")

g = Graph()
g.bind("ex", EX)
g.bind("agrovoc", AGROVOC)
g.bind("rdfs", RDFS)
g.bind("skos", SKOS)


def get_uri(prefix, name) -> URIRef:
    py_name = name.replace(" ", "_").replace("/", "_")
    return URIRef(prefix + py_name)


df_crops = pd.read_csv("data/crops.csv")
df_disease = pd.read_csv("data/crop_disease.csv")
df_treatments = pd.read_csv("data/treatment.csv")
df_regions = pd.read_csv("data/regions.csv")
df_resilience = pd.read_csv("data/crop_resilience.csv")

region_uris = {}

for index, row in df_regions.iterrows():
    region_uri = get_uri(EX, f"Region_{row['Region']}")
    region_uris[row["Region"]] = region_uri

    g.add((region_uri, RDF.type, EX.Region))
    g.add((region_uri, RDFS.label, Literal(row["Region"])))
    g.add((region_uri, EX.climateType, Literal(row["Climate Type"])))
    g.add((region_uri, EX.notes, Literal(row["Notes"])))

crop_uris = {}

for index, row in df_crops.iterrows():
    crop_uri = get_uri(EX, f"Crop_{row['Crop']}")
    crop_uris[row["Crop"]] = crop_uri

    g.add((crop_uri, RDF.type, EX.Crop))
    g.add((crop_uri, RDFS.label, Literal(row["Crop"])))
    g.add((crop_uri, EX.scientificName, Literal(row["Scientific Name"])))
    g.add((crop_uri, EX.regions, Literal(row["Regions"])))
    g.add((crop_uri, EX.climate, Literal(row["Climate"])))
    g.add((crop_uri, EX.soilType, Literal(row["Soil Type"])))


disease_uris = {}

for index, row in df_disease.iterrows():
    disease_uri = get_uri(EX, f"Disease_{row['Disease Name']}")
    disease_uris[row["Disease Name"]] = disease_uri

    g.add((disease_uri, RDF.type, EX.Disease))
    g.add((disease_uri, RDFS.label, Literal(row["Disease Name"])))
    g.add((disease_uri, EX.diseaseType, Literal(row["Disease Type"])))
    g.add((disease_uri, EX.affectedPart, Literal(row["Affected Part"])))
    g.add((disease_uri, EX.severity, Literal(row["Severity"])))
    g.add((disease_uri, EX.notes, Literal(row["Notes"])))


resilience_uris = {}

for index, row in df_resilience.iterrows():
    resilience_uri = get_uri(EX, f"Crop_{row['Crop']}")
    resilience_uris[row["Crop"]] = resilience_uri

    g.add((resilience_uri, EX.droughtTolerance, Literal(row["Drought Tolerance"])))
    g.add((resilience_uri, EX.floodTolerance, Literal(row["Flood Tolerance"])))
    g.add((resilience_uri, EX.inputRequirement, Literal(row["Input Requirement"])))
    g.add((resilience_uri, EX.farmingType, Literal(row["Farming Type"])))


## Link the crops to specific region

for index, row in df_crops.iterrows():
    crop_uri = crop_uris[row["Crop"]]
    region_list = row["Regions"].split(",")

    for region_name in region_list:
        r_name = region_name.strip()
        if r_name in region_uris:
            region_uri = region_uris[r_name]
            g.add((crop_uri, EX.grownIn, region_uri))


## Linking crops to diseases

for index, row in df_disease.iterrows():
    crop_name = row["Crop"]
    disease_name = row["Disease Name"]

    if crop_name in crop_uris and disease_name in disease_uris:
        crop_uri = crop_uris[crop_name]
        disease_uri = disease_uris[disease_name]

        g.add((crop_uri, EX.succeptibleTo, disease_uri))

## Treatment connection to diseases

for index, row in df_treatments.iterrows():
    disease_name = row["Disease Name"]
    treatment_type = row["Treatment Type"]

    if disease_name in disease_uris:
        disease_uri = disease_uris[disease_name]

        treatment_uri = get_uri(EX, f"Treatment_{disease_name}_{treatment_type}")

        g.add((treatment_uri, RDF.type, EX.Treatment))
        g.add((treatment_uri, RDFS.label, Literal("treatment_type")))
        g.add((treatment_uri, EX.methodDescription, Literal(row["Method Description"])))


agri_rdf = "nepal_agri_kg.ttl"
g.serialize(agri_rdf, format="turtle")
print("File successfully saved")
print(f"total {len(g)} triples created ")
