from rdflib import RDF, RDFS, Graph, Namespace

EX = Namespace("http://narc.org/agri_knowledge#")

g = Graph()

g.parse("./narc_graph.ttl", format="turtle")

print("Loading Ontology...")
g.parse("./ontology/agri_onto_protege.ttl", format="turtle")

print("Reasoning: Classifying High Altitude Zones...")

for zone in g.subjects(RDF.type, EX.Zone):
    max_alt_val = g.value(zone, EX.maxAltitude)
    if max_alt_val:
        try:
            if int(max_alt_val) > 2000:
                g.add((zone, RDF.type, EX.HighAltitudeZone))
                print(f"   -> Tagged {g.value(zone, RDFS.label)} as High Altitude Zone")
        except ValueError:
            print(
                f"   -> Skipping {g.value(zone, RDFS.label)} (Altitude is not a number)"
            )

print("Reasoning: Classifying High Altitude Crops...")

for crop in g.subjects(RDF.type, EX.Crop):
    crop_label = g.value(crop, RDFS.label)

    for zone in g.objects(crop, EX.suitableIn):
        if (zone, RDF.type, EX.HighAltitudeZone) in g:
            g.add((crop, RDF.type, EX.HighAltitudeCrop))
            print(f"   -> Classified {crop_label} as High Altitude Crop")
            break

print("\n ---- Querying the Smart Graph ----")

query = """
PREFIX ex: <http://narc.org/agri_knowledge#>
SELECT ?cropLabel
WHERE {
    ?crop a ex:HighAltitudeCrop ;
          rdfs:label ?cropLabel .
}
"""

results = g.query(query)

if results:
    print("The following crops were identified as High Altitude Crops:")
    for row in results:
        print(f"  ✅ {row.cropLabel}")
else:
    print("No high altitude crops found.")

g.serialize("narc_final_reasoned_graph.ttl", format="turtle")
print("\nFinal reasoned graph saved.")
