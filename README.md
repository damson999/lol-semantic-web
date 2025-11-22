# LOL RDF Project

Este proyecto convierte los datos de los campeones de **League of Legends** en un grafo RDF y carga los datos a un servidor **Fuseki**.

## **Requisitos**

- **Python 3.6+**
- **Dependencias**:
  - `rdflib`
  - `requests`

Archivos del Proyecto

data/champions.json: Datos de los campeones en formato JSON.

output/champions.ttl: Archivo de salida con los datos ordenados.

queries/: Carpeta que contiene las consultas SPARQL utilizadas para interactuar con el servidor Fuseki.

src/convert_to_rdf.py: Script que convierte los datos a formato rdf y genera champions.ttl.
