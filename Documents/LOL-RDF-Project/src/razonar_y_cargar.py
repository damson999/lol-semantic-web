import json
from rdflib import Graph, Literal, Namespace, RDF
from owlrl import DeductiveClosure, OWLRL_Semantics
import requests
import sys
import unicodedata

# -----------------------------------------------------------
# CONFIGURACIÓN DEL USUARIO
# -----------------------------------------------------------
ONTOLOGY_FILE = "ontology/lol.ttl"   # Ontología
CHAMPIONS_JSON_FILE = "C:/Users/ignac/Documents/LOL-RDF-Project/data/champion.json"  # Datos de los campeones en JSON
OUTPUT_FILE = "output/final.ttl"  # Archivo de salida con inferencias

# URL del dataset en Fuseki (UPDATE endpoint)
FUSEKI_DATA_URL = "http://localhost:3030/lol/data"  # Cambia si tu dataset tiene otro nombre

# -----------------------------------------------------------
# 1. CARGAR ONTOLOGÍA + DATOS
# -----------------------------------------------------------
print("Cargando ontología y datos...")

# Crear un grafo RDF
g = Graph()

# Cargar ontología desde el archivo lol.txt
try:
    g.parse(ONTOLOGY_FILE, format="ttl")  # Asumiendo que la ontología está en formato TTL
    print(f"Ontología cargada. Triples: {len(g)}")
except Exception as e:
    print(f"Error al cargar la ontología: {e}")
    sys.exit(1)

# Cargar datos de campeones desde el archivo JSON
try:
    with open(CHAMPIONS_JSON_FILE, 'r', encoding="utf-8") as f:
        champions_data = json.load(f)
    
    # Definir el espacio de nombres (namespace)
    LOL = Namespace("http://example.org/lol#")
    
    # Convertir los datos de campeones a triples RDF
    for champ_name, champ_info in champions_data['data'].items():
        champ_uri = LOL[champ_name.replace(" ", "_")]
        
        # Crear los triples básicos para cada campeón
        g.add((champ_uri, RDF.type, LOL.Champion))
        
        for role in champ_info['tags']:
            role_uri = LOL[role]
            g.add((champ_uri, LOL.hasRole, role_uri))

        # Agregar estadísticas (como daño)
        attack_range = champ_info['stats'].get('attackrange', None)
        if attack_range is not None:
            g.add((champ_uri, LOL.hasAttackRange, Literal(attack_range)))

        attack_damage = champ_info['stats'].get('attackdamage', None)
        if attack_damage is not None:
            g.add((champ_uri, LOL.hasAttackDamage, Literal(attack_damage)))
    
    print(f"Datos de campeones cargados. Triples: {len(g)}")

except Exception as e:
    print(f"Error al cargar los datos de campeones: {e}")
    sys.exit(1)


def contains_invalid_chars(text):
    """Verifica si el texto contiene caracteres no válidos."""
    return any(ord(c) > 127 for c in text)

# Verificar cada nombre de campeón y los tags
for champ_name, champ_info in champions_data['data'].items():
    if contains_invalid_chars(champ_name):
        print(f"Nombre de campeón con caracteres no válidos: {champ_name}")
    
    for role in champ_info['tags']:
        if contains_invalid_chars(role):
            print(f"Tag con caracteres no válidos: {role}")


# -----------------------------------------------------------
# 2. EJECUTAR RAZONAMIENTO OWL RL
# -----------------------------------------------------------
print("Ejecutando razonamiento (OWL RL)...")
try:
    DeductiveClosure(OWLRL_Semantics).expand(g)
    print(f"Triples totales después de razonamiento: {len(g)}")
except Exception as e:
    print(f"Error al ejecutar razonamiento OWL RL: {e}")
    sys.exit(1)

# -----------------------------------------------------------
# 3. FUNCION DE LIMPIEZA DE CARACTERES NO VÁLIDOS
# -----------------------------------------------------------
def clean_string(s):
    """Reemplaza caracteres no válidos por un signo de interrogación."""
    return ''.join(c if ord(c) < 128 else '?' for c in s)  # Solo caracteres ASCII válidos

# -----------------------------------------------------------
# 4. GUARDAR ARCHIVO TTL INFERIDO (Limpieza previa)
# -----------------------------------------------------------
print(f"Guardando resultado en {OUTPUT_FILE} ...")

# Serializar el grafo y decodificar a cadena de texto (UTF-8)
serialized_graph = g.serialize(format="turtle", encoding="utf-8").decode('utf-8')

# Limpiar el grafo (si contiene caracteres problemáticos)
cleaned_data = clean_string(serialized_graph)

# Guardar el archivo limpio
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(cleaned_data)

print("Archivo guardado.\n")


def clean_start_of_file(content):
    """Elimina cualquier carácter no imprimible o extraño al inicio del archivo."""
    # Eliminar caracteres hasta encontrar un carácter imprimible
    i = 0
    while i < len(content) and ord(content[i]) > 127:
        i += 1
    return content[i:]

# Limpiar el contenido antes de guardar
cleaned_content = clean_start_of_file(serialized_graph)

# Guardar el archivo limpio
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(cleaned_content)

# -----------------------------------------------------------
# 5. SUBIR AL SERVIDOR FUSEKI
# -----------------------------------------------------------
print("Subiendo a Fuseki...")
try:
    with open(OUTPUT_FILE, "rb") as f:
        headers = {"Content-Type": "text/turtle"}
        
        # Realizamos la solicitud POST para cargar los datos inferidos
        response = requests.post(
            FUSEKI_DATA_URL,
            data=f,
            headers=headers
        )

        if response.status_code in (200, 201, 204):
            print("✔ Datos cargados exitosamente en Fuseki.")
        else:
            print("❌ Error al cargar en Fuseki:", response.status_code)
            print(response.text)
            sys.exit(1)
except Exception as e:
    print(f"Error al subir los datos a Fuseki: {e}")
    sys.exit(1)


print("\nProceso completado.")

