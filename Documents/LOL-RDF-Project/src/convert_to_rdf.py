import json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD, URIRef
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_path = os.path.join(base_dir, "data", "champion.json")

LOL = Namespace("http://example.org/lol#")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)["data"]

g = Graph()
g.bind("lol", LOL)

for champ_name, champ in data.items():

    champ_uri = LOL[champ_name.replace(" ", "_")]
    g.add((champ_uri, RDF.type, LOL.Champion))

    # Roles (tags)
    for role in champ["tags"]:
        role_uri = LOL[role]
        g.add((role_uri, RDF.type, LOL.Role))
        g.add((champ_uri, LOL.hasRole, role_uri))

    # Melee / Ranged
    if champ["stats"]["attackrange"] <= 200:
        g.add((champ_uri, LOL.isMelee, Literal(True, datatype=XSD.boolean)))
    else:
        g.add((champ_uri, LOL.isRanged, Literal(True, datatype=XSD.boolean)))

    # Stats
    for stat_name, stat_value in champ["stats"].items():
        stat_uri = URIRef(f"{LOL}{champ_name}_{stat_name}")
        g.add((stat_uri, RDF.type, LOL.Stat))
        g.add((stat_uri, LOL.statName, Literal(stat_name)))
        g.add((stat_uri, LOL.statValue, Literal(float(stat_value))))

        g.add((champ_uri, LOL.hasStat, stat_uri))

g.serialize("output/champions.ttl", format="turtle")
print("Archivo generado: output/champions.ttl")
