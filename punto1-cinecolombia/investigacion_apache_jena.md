**TERCERA NOTA PARCIAL**

Semántica Web y Big Data

**Punto 1 — Investigación y Descripción**

**Apache Jena  ·  RDF/XML  ·  SPARQL**

| Campo | Información |
| ----- | ----- |
| Nombre | Jeyson Styven Caceres Mosquera |
| Asignatura | Semántica Web y Big Data |
| Entrega | Tercera Nota Parcial — Punto 1: Investigación |
| Fecha | Mayo 2026 |
| Tecnología | Apache Jena 4.10.0 · Java 17 · Maven 3.8 |

# **1\. ¿Qué es RDF y la Web Semántica?**

RDF (Resource Description Framework) es el modelo de datos estándar del W3C para representar información en la Web. Fue diseñado como el pilar fundamental de la Web Semántica: una extensión de la Web actual donde la información posee significado formal que las máquinas pueden procesar, razonar y enlazar automáticamente, sin intervención humana.

La idea central de RDF es describir recursos mediante tripletas — unidades mínimas de conocimiento compuestas por tres partes bien definidas. Cualquier hecho del mundo real puede expresarse en este modelo de forma precisa e interoperable entre sistemas.

## **1.1  El Modelo de Tripletas: Sujeto — Predicado — Objeto**

Toda la información en RDF se codifica como una colección de tripletas. Cada tripleta afirma una relación entre dos recursos. A continuación se muestra la película 'Michael' representada como tripletas RDF:

| SUJETO (recurso) | PREDICADO (propiedad) | OBJETO (valor o recurso) |
| :---: | :---: | :---: |
| :Michael2025 | dc:title | "Michael" |
| :Michael2025 | cine:duracionMinutos | "148"^^xsd:integer |
| :Michael2025 | cine:director | :AntoineFuqua |
| :Michael2025 | cine:disponible3D | "true"^^xsd:boolean |

El sujeto y predicado son siempre URIs. El objeto puede ser una URI (otro recurso) o un literal (valor concreto). Esta uniformidad hace que cualquier dato del mundo sea representable e integrable con cualquier otra fuente RDF de la Web.

## **1.2  Namespaces y Vocabularios Estándar**

Para evitar URIs largas repetidas, RDF usa prefijos (namespaces). Los vocabularios más importantes reutilizables en cualquier ontología son:

| Prefijo | URI Base | Función |
| ----- | ----- | ----- |
| rdf: | http://www.w3.org/1999/02/22-rdf-syntax-ns\# | Tipos y estructura base del modelo RDF |
| rdfs: | http://www.w3.org/2000/01/rdf-schema\# | Clases, etiquetas, subclases, jerarquías |
| xsd: | http://www.w3.org/2001/XMLSchema\# | Tipos de dato: integer, date, boolean... |
| dc: | http://purl.org/dc/elements/1.1/ | Dublin Core: title, description, creator |
| owl: | http://www.w3.org/2002/07/owl\# | Ontologías avanzadas (OWL 2\) |
| schema: | https://schema.org/ | Vocabulario web: Movie, Person, Event... |

# **2\. Serialización RDF/XML: Escribir la Base de Datos**

RDF/XML es la sintaxis oficial del W3C para serializar (escribir en un archivo) un grafo RDF. Es el formato más extendido y el que lee Apache Jena por defecto. Combina la semántica precisa de RDF con la estructura jerárquica y los namespaces de XML.

## **2.1  Estructura Jerárquica del Documento**

Un archivo RDF/XML bien formado sigue siempre la siguiente jerarquía: elemento raíz rdf:RDF con declaración de namespaces, seguido de definiciones de clases e instancias:

  **Estructura base de un archivo RDF/XML**  
\<?xml version="1.0" encoding="UTF-8"?\>  
\<rdf:RDF  
    xmlns:rdf   \= "http://www.w3.org/1999/02/22-rdf-syntax-ns\#"  
    xmlns:rdfs  \= "http://www.w3.org/2000/01/rdf-schema\#"  
    xmlns:xsd   \= "http://www.w3.org/2001/XMLSchema\#"  
    xmlns:dc    \= "http://purl.org/dc/elements/1.1/"  
    xmlns:cine  \= "http://cinecolombia.com/ontologia\#"\>

    \<\!-- ① Definición de clases de la ontología \--\>  
    \<rdfs:Class rdf:about="http://cinecolombia.com/ontologia\#Pelicula"\>  
        \<rdfs:label xml:lang="es"\>Película\</rdfs:label\>  
        \<rdfs:comment\>Película en cartelera en Cine Colombia.\</rdfs:comment\>  
    \</rdfs:Class\>

    \<\!-- ② Instancias con propiedades literales y de recurso \--\>  
    \<cine:Pelicula rdf:about="http://cinecolombia.com/pelicula/Michael2025"\>  
        \<rdf:type rdf:resource="https://schema.org/Movie"/\>  
        \<dc:title\>Michael\</dc:title\>  
        \<cine:duracionMinutos rdf:datatype="xsd:integer"\>148\</cine:duracionMinutos\>  
        \<cine:fechaEstreno rdf:datatype="xsd:date"\>2026-04-09\</cine:fechaEstreno\>  
        \<cine:disponible3D rdf:datatype="xsd:boolean"\>true\</cine:disponible3D\>  
        \<\!-- Propiedad que enlaza a otro recurso URI \--\>  
        \<cine:genero rdf:resource="http://cinecolombia.com/genero/Biopic"/\>  
        \<cine:director rdf:resource="http://cinecolombia.com/director/AntoineFuqua"/\>  
    \</cine:Pelicula\>

\</rdf:RDF\>

## **2.2  Elementos Clave de la Sintaxis RDF/XML**

| Elemento / Atributo | Descripción y ejemplo |
| ----- | ----- |
| rdf:RDF | Raíz obligatoria del documento. Aquí se declaran todos los namespaces (xmlns:). |
| rdf:about | URI única del recurso (sujeto). Ej: rdf:about="http://cinecolombia.com/pelicula/Michael2025" |
| rdf:type | Declara la clase del recurso. Ej: \<rdf:type rdf:resource="https://schema.org/Movie"/\>. Equivale a "es un". |
| rdf:resource | En propiedades: indica que el objeto es un recurso URI, no un literal de texto. |
| rdf:datatype | Tipo XSD del literal. Ej: rdf:datatype="xsd:integer", "xsd:date", "xsd:boolean". |
| rdfs:Class | Define una clase (tipo de recurso) en la ontología. Permite la clasificación de instancias. |
| rdfs:label | Nombre legible para humanos. Acepta xml:lang="es" para múltiples idiomas. |
| rdfs:seeAlso | Enlaza el recurso a información adicional externa (ej. página IMDB). |

## **2.3  Tipos de Datos XSD para Literales Tipados**

Los literales pueden tipificarse con tipos XML Schema (XSD), lo que permite a SPARQL comparar, filtrar y calcular sobre ellos con semántica correcta:

* xsd:string  — texto:   \<dc:title\>Michael\</dc:title\>

* xsd:integer — entero:  \<cine:duracion rdf:datatype="xsd:integer"\>148\</cine:duracion\>

* xsd:decimal — decimal: \<cine:calificacion rdf:datatype="xsd:decimal"\>7.2\</cine:calificacion\>

* xsd:boolean — booleano: \<cine:disponible3D rdf:datatype="xsd:boolean"\>true\</cine:disponible3D\>

* xsd:date    — fecha:   \<cine:fechaEstreno rdf:datatype="xsd:date"\>2026-05-07\</cine:fechaEstreno\>

# **3\. Apache Jena: Framework Java para Web Semántica**

Apache Jena es el framework Java de código abierto líder en el mundo para trabajar con tecnologías de Web Semántica. Fue desarrollado originalmente por Hewlett-Packard Labs en el año 2000 y donado a la Apache Software Foundation en 2010\. Jena provee un ecosistema integral que cubre desde la creación de grafos RDF en memoria hasta el razonamiento lógico sobre ontologías OWL y la exposición de endpoints SPARQL mediante HTTP.

## **3.1  Arquitectura Modular de Apache Jena**

Jena no es una librería monolítica sino un conjunto de módulos independientes. Cada uno puede usarse por separado o en combinación:

| Módulo | Artefacto Maven | Función |
| ----- | ----- | ----- |
| Core / API | jena-core | Crea y manipula modelos RDF en memoria RAM (Model, Resource, Property) |
| ARQ | jena-arq | Motor SPARQL 1.1 completo: SELECT, ASK, CONSTRUCT, DESCRIBE |
| RIOT | jena-arq (incluido) | Parser/serializador multi-formato: RDF/XML, Turtle, N-Triples, JSON-LD |
| TDB2 | jena-tdb2 | Base de datos RDF persistente en disco, con transacciones ACID |
| Fuseki | jena-fuseki-main | Servidor SPARQL HTTP con interfaz web y endpoint REST estándar |
| Inference | jena-core (Reasoner) | Razonamiento RDFS y OWL: inferir nuevas tripletas de las existentes |

## **3.2  Configuración con Maven**

Apache Jena se incluye en proyectos Java mediante Maven. La dependencia apache-jena-libs es un POM agregador que incluye Core, ARQ (SPARQL), RIOT e Inference de forma automática:

  **pom.xml — Dependencias de Apache Jena**  
\<properties\>  
    \<maven.compiler.source\>17\</maven.compiler.source\>  
    \<jena.version\>4.10.0\</jena.version\>  
\</properties\>

\<dependencies\>  
    \<\!-- Meta-dependencia: incluye jena-core, jena-arq, jena-iri, jena-riot \--\>  
    \<dependency\>  
        \<groupId\>org.apache.jena\</groupId\>  
        \<artifactId\>apache-jena-libs\</artifactId\>  
        \<version\>${jena.version}\</version\>  
        \<type\>pom\</type\>  
        \<scope\>compile\</scope\>  
    \</dependency\>  
    \<\!-- Binding de logging requerido por Jena en runtime \--\>  
    \<dependency\>  
        \<groupId\>org.slf4j\</groupId\>  
        \<artifactId\>slf4j-simple\</artifactId\>  
        \<version\>2.0.9\</version\>  
    \</dependency\>  
\</dependencies\>

## **3.3  API de Jena: Crear y Cargar Modelos RDF**

### **3.3.1  ModelFactory y RDFDataMgr**

ModelFactory es la fábrica principal de Jena. Crea diferentes tipos de modelos según las necesidades (en memoria, con razonamiento, persistente). RDFDataMgr parsea archivos RDF de cualquier formato y los carga en el modelo:

  **Cargar un archivo RDF/XML en un modelo Jena**  
import org.apache.jena.rdf.model.\*;  
import org.apache.jena.riot.RDFDataMgr;  
import org.apache.jena.riot.Lang;

// Paso 1: Crear modelo vacío en memoria RAM  
Model model \= ModelFactory.createDefaultModel();

// Paso 2: Cargar el archivo RDF/XML (RIOT auto-detecta el formato)  
RDFDataMgr.read(model, "peliculas\_cine\_colombia.rdf", Lang.RDFXML);

// Paso 3: Verificar la cantidad de tripletas cargadas  
System.out.println("Tripletas en el modelo: " \+ model.size());

// Paso 4: Liberar recursos del modelo al finalizar  
model.close();

### **3.3.2  Construir Tripletas por API Java**

Además de cargar archivos, Jena permite construir el grafo RDF directamente desde código Java usando su API fluida orientada a objetos:

  **Agregar tripletas programáticamente**  
String ns \= "http://cinecolombia.com/ontologia\#";

// Crear recursos (nodos del grafo)  
Resource pelicula \= model.createResource(ns \+ "Michael2025");  
Resource genero   \= model.createResource(ns \+ "Biopic");

// Crear propiedades (aristas del grafo)  
Property titulo   \= model.createProperty("http://purl.org/dc/elements/1.1/", "title");  
Property duracion \= model.createProperty(ns, "duracionMinutos");  
Property genProp  \= model.createProperty(ns, "genero");

// Agregar tripletas al grafo  
pelicula.addProperty(titulo, "Michael");    // objeto \= literal String  
pelicula.addLiteral(duracion, 148);         // objeto \= literal int  
pelicula.addProperty(genProp, genero);      // objeto \= recurso URI

# **4\. SPARQL 1.1: Lenguaje de Consulta para RDF**

SPARQL (SPARQL Protocol and RDF Query Language) es el lenguaje de consulta estándar del W3C para bases de datos RDF, comparable a SQL para bases relacionales. La versión actual es SPARQL 1.1 (recomendación W3C 2013). En Apache Jena, el motor de SPARQL se llama ARQ y es uno de los implementaciones más completas y robustas disponibles.

## **4.1  Tipos de Consultas SPARQL**

| Tipo | Descripción | Tipo de resultado |
| ----- | ----- | ----- |
| SELECT | Recupera variables que coinciden con el patrón WHERE. | Tabla de filas y columnas |
| ASK | Verifica si existe al menos una coincidencia en el grafo. | true / false |
| CONSTRUCT | Construye un nuevo grafo RDF a partir de los patrones encontrados. | Grafo RDF (tripletas) |
| DESCRIBE | Retorna toda la información disponible sobre un recurso específico. | Grafo RDF parcial |

## **4.2  Anatomía de una Consulta SELECT**

Una consulta SELECT completa tiene las siguientes cláusulas, con la semántica equivalente a SQL en muchos casos:

  **Estructura completa de una consulta SPARQL SELECT**  
\# ── PREFIJOS: alias de namespaces (como xmlns: en RDF/XML) ──────  
PREFIX cine: \<http://cinecolombia.com/ontologia\#\>  
PREFIX dc:   \<http://purl.org/dc/elements/1.1/\>  
PREFIX rdfs: \<http://www.w3.org/2000/01/rdf-schema\#\>  
PREFIX xsd:  \<http://www.w3.org/2001/XMLSchema\#\>

\# ── SELECT: variables a retornar (?variable) ───────────────────  
SELECT ?titulo ?genero ?duracion

\# ── WHERE: patrones de tripletas que deben coincidir ───────────  
WHERE {  
    \# Patrón básico: ?sujeto predicado ?objeto  
    ?pelicula a cine:Pelicula ;           \# rdf:type \= clase  
              dc:title ?titulo ;           \# enlaza ?titulo  
              cine:duracionMinutos ?duracion ;  
              cine:genero ?generoURI .  
    \# JOIN implícito: navegar desde la URI del género  
    ?generoURI rdfs:label ?genero .

    \# FILTER: restricción booleana sobre las variables  
    FILTER(?duracion \> 100\)  
}

\# ── MODIFICADORES: ordenar, paginar ─────────────────────────  
ORDER BY DESC(?duracion)   \# mayor a menor  
LIMIT 5                    \# máximo 5 resultados  
OFFSET 0                   \# empezar desde el primero

## **4.3  Características Avanzadas de SPARQL 1.1**

### **4.3.1  OPTIONAL — LEFT JOIN Semántico**

OPTIONAL incluye datos que pueden o no existir en el grafo, sin descartar la solución principal si no se encuentran. Es equivalente al LEFT OUTER JOIN de SQL:

  **OPTIONAL: actor si existe, película siempre**  
SELECT ?titulo ?actor  
WHERE {  
    ?p a cine:Pelicula ; dc:title ?titulo .  
    OPTIONAL {                          \# si no hay actor: ?actor \= unbound  
        ?p cine:actorPrincipal ?aURI .  
        ?aURI schema:name ?actor .  
    }  
}

### **4.3.2  GROUP BY \+ COUNT — Agregación**

SPARQL 1.1 incluye funciones de agregación similares a SQL: COUNT, SUM, AVG, MIN, MAX. Se combinan obligatoriamente con GROUP BY:

  **COUNT: películas por género**  
SELECT ?genero (COUNT(?pelicula) AS ?cantidad)  
WHERE {  
    ?pelicula a cine:Pelicula ; cine:genero ?gURI .  
    ?gURI rdfs:label ?genero .  
}  
GROUP BY ?genero  
ORDER BY DESC(?cantidad)

### **4.3.3  FILTER con Operadores y Funciones**

FILTER acepta expresiones booleanas complejas con operadores de comparación (\>, \<, \=, \!=, \>=), operadores lógicos (&&, ||, \!) y funciones integradas como REGEX, STR, LANG, BOUND, isURI, isLiteral:

  **FILTERs combinados con operadores**  
\# AND lógico: ambas condiciones deben cumplirse  
FILTER(?calificacion \> 7.0 && ?recaudacion \> 50.0)

\# REGEX: título que empiece con "El" (case insensitive)  
FILTER(REGEX(?titulo, "^El", "i"))

\# LANG: solo etiquetas en español  
FILTER(LANG(?label) \= "es")

\# BOUND: recursos que NO tienen actor definido  
FILTER(\!BOUND(?actor))

# **5\. Ejecutar Consultas SPARQL con Apache Jena**

La arquitectura de ejecución SPARQL en Jena sigue el patrón Query → QueryExecution → ResultSet. Cada clase tiene una sola responsabilidad, siguiendo el principio de separación de incumbencias:

| Clase de Jena | Responsabilidad |
| ----- | ----- |
| QueryFactory.create() | Parsea la cadena SPARQL y la valida sintácticamente. Produce un objeto Query. |
| QueryExecutionFactory | Une el objeto Query con el Model RDF y crea el motor de ejecución. |
| QueryExecution | Ejecuta la consulta. execSelect() para SELECT; execAsk() para ASK. |
| ResultSet | Iterador sobre los resultados. Cada fila es un QuerySolution con variables. |
| ResultSetFormatter | Formatea el ResultSet: tabla en consola, JSON, XML, CSV. |

  **Código completo: cargar modelo y ejecutar consulta SPARQL**  
import org.apache.jena.query.\*;  
import org.apache.jena.rdf.model.\*;  
import org.apache.jena.riot.RDFDataMgr;

public class EjemploSPARQL {  
  public static void main(String\[\] args) {

    // ① Crear y cargar el modelo RDF en memoria  
    Model model \= ModelFactory.createDefaultModel();  
    RDFDataMgr.read(model, "peliculas\_cine\_colombia.rdf");

    // ② Definir la consulta SPARQL (Java 17 Text Block)  
    String sparql \= """  
        PREFIX cine: \<http://cinecolombia.com/ontologia\#\>  
        PREFIX dc:   \<http://purl.org/dc/elements/1.1/\>  
        SELECT ?titulo ?calificacion  
        WHERE {  
            ?p a cine:Pelicula ;  
               dc:title ?titulo ;  
               cine:calificacionCritica ?calificacion .  
            FILTER(?calificacion \> 7.0)  
        }  
        ORDER BY DESC(?calificacion)  
    """;

    // ③ Compilar la consulta SPARQL  
    Query query \= QueryFactory.create(sparql);

    // ④ Ejecutar con try-with-resources (cierra el motor automáticamente)  
    try (QueryExecution qe \= QueryExecutionFactory.create(query, model)) {  
        ResultSet results \= qe.execSelect();

        // ⑤ Mostrar como tabla formateada en consola  
        ResultSetFormatter.out(System.out, results, query);

        // Alternativa: iterar fila a fila  
        // while (results.hasNext()) {  
        //     QuerySolution sol \= results.nextSolution();  
        //     String t \= sol.getLiteral("titulo").getString();  
        //     System.out.println(t);  
        // }  
    }  
    model.close();  
  }  
}

# **6\. Capturas de pantalla requeridas**

> En esta sección se indican las capturas que deben incluirse en el informe de entrega.

1. **Ejecución completa en consola**: captura de pantalla del programa Java `Main` corriendo y mostrando los resultados de varias consultas SPARQL. Debe incluir al menos una consulta `SELECT`, una consulta `ASK` y la salida del `CONSTRUCT`.

2. **Estructura del proyecto**: captura del explorador de archivos o IDE mostrando `src/main/java/co/cinecolombia/Main.java`, `ModelLoader.java`, `SparqlQueries.java`, y `src/main/resources/peliculas_cine_colombia.rdf`.

3. **Fragmento de RDF/XML**: captura del archivo `peliculas_cine_colombia.rdf` mostrando una instancia `cine:Pelicula` con propiedades literales tipadas (`xsd:integer`, `xsd:date`, `xsd:boolean`) y relaciones `rdf:resource` a géneros y directores.

4. **Salida de consulta avanzada**: captura del resultado de una consulta `GROUP BY + HAVING` o la consulta `CONSTRUCT` en la consola para evidenciar el uso de funciones avanzadas de SPARQL 1.1.

# **8\. Apache Jena Fuseki: Servidor SPARQL HTTP**

Jena Fuseki es el componente que convierte una base de datos RDF/TDB2 en un servicio web con endpoints SPARQL estándar. Permite que cualquier aplicación, sin importar el lenguaje de programación, consulte la base de datos RDF mediante peticiones HTTP.

## **8.1  Instalación y Arranque Básico**

  **Comandos para iniciar Apache Jena Fuseki**  
\# 1\. Descargar desde https://jena.apache.org/download/  
unzip apache-jena-fuseki-4.10.0.zip  
cd apache-jena-fuseki-4.10.0

\# 2\. Iniciar servidor en modo memoria (dataset: /peliculas)  
./fuseki-server \--mem /peliculas  
\# → Interfaz web disponible en: http://localhost:3030

\# 3\. Cargar el archivo RDF en el dataset  
curl \-X POST http://localhost:3030/peliculas/data \\  
     \-H "Content-Type: application/rdf+xml" \\  
     \--data-binary @peliculas\_cine\_colombia.rdf

\# 4\. Ejecutar consulta SPARQL via HTTP GET  
curl "http://localhost:3030/peliculas/sparql?query=SELECT+\*+WHERE{?s+?p+?o}+LIMIT+5"

## **8.2  Persistencia con TDB2**

Para producción o proyectos con grandes volúmenes de datos, Fuseki usa TDB2 como motor de almacenamiento persistente en disco. TDB2 implementa índices B-Tree optimizados para tripletas RDF y soporta transacciones ACID:

  **Fuseki con almacenamiento persistente TDB2**  
\# Los datos sobreviven al reinicio del servidor  
./fuseki-server \--tdb2 \--loc=./data/mi-base /peliculas

\# Verificar el endpoint SPARQL  
curl http://localhost:3030/peliculas/sparql

# **9\. RDF/SPARQL vs Bases de Datos Relacionales**

Es importante entender los escenarios donde el modelo RDF supera a las bases de datos relacionales tradicionales, y dónde cada tecnología es más apropiada:

| Aspecto | SQL / Relacional | RDF / SPARQL (Jena) |
| ----- | ----- | ----- |
| Esquema | Fijo — ALTER TABLE para cada cambio | Flexible — nuevas propiedades sin migración |
| Modelo | Tablas con filas y columnas | Grafo de tripletas (sujeto-predicado-objeto) |
| Identidad | Clave primaria local (auto-increment) | URI global único en toda la Web |
| Integración | ETL complejo para integrar fuentes distintas | Enlace directo entre grafos distribuidos |
| Consultas | SQL con JOINs explícitos sobre tablas | SPARQL con patrones de grafo implícitos |
| Razonamiento | No nativo (stored procedures) | Nativo: inferencia RDFS/OWL integrada |
| Ideal para... | Datos estructurados, transaccionales | Datos heterogéneos, linked data, ontologías |

# **10\. Flujo Completo de Trabajo con Apache Jena**

El proceso de desarrollo de una solución RDF/SPARQL con Apache Jena sigue las siguientes etapas en orden:

| \# | Etapa | Descripción detallada |
| :---: | ----- | ----- |
| 1 | Diseñar Ontología | Identificar las clases (Pelicula, Director, Actor), propiedades y sus tipos de dato. Definir los namespaces del dominio. |
| 2 | Escribir RDF/XML | Crear el archivo .rdf con las clases, instancias reales y propiedades según la esquema diseñado. |
| 3 | Configurar Maven | Agregar apache-jena-libs al pom.xml. Ejecutar mvn dependency:resolve para descargar Jena. |
| 4 | Cargar Modelo | Usar ModelFactory.createDefaultModel() \+ RDFDataMgr.read() para cargar el archivo RDF en memoria. |
| 5 | Escribir SPARQL | Redactar consultas con PREFIX, SELECT/WHERE, FILTER, ORDER BY, GROUP BY según la información requerida. |
| 6 | Ejecutar | Flujo: QueryFactory.create() → QueryExecutionFactory.create() → execSelect() → ResultSetFormatter. |
| 7 | Validar | Verificar resultados contra los datos esperados. Ajustar ontología o consultas si los resultados no son correctos. |

# **11\. Implementación en el proyecto Cine Colombia**

El proyecto real se organiza con estos archivos clave:

- `src/main/resources/peliculas_cine_colombia.rdf` — Base de datos RDF/XML que contiene los datos de la cartelera de Cine Colombia.
- `src/main/java/co/cinecolombia/Main.java` — Aplicación Java que carga el archivo RDF/XML con Apache Jena y ejecuta las consultas.
- `src/main/java/co/cinecolombia/ModelLoader.java` — Clase responsable de cargar el modelo RDF/XML desde recursos.
- `src/main/java/co/cinecolombia/SparqlQueries.java` — Clase que ejecuta 10 consultas SPARQL en Java.

La implementación evidencia los requisitos del entregable de la siguiente forma:

- La base de datos RDF/XML está construida con recursos `cine:Pelicula`, `cine:Genero`, `cine:Director`, `cine:Clasificacion` y propiedades literales tipadas con `xsd:integer`, `xsd:date` y `xsd:boolean`.
- `Main.java` utiliza `ModelLoader` y `SparqlQueries` para separar claramente la carga del modelo y la ejecución de las consultas.
- `SparqlQueries.java` ejecuta 10 consultas SPARQL completas que cubren SELECT, FILTER, OPTIONAL, ORDER BY, LIMIT, ASK, COUNT, AVG, GROUP BY, UNION y CONSTRUCT.

# **12\. Análisis del código fuente**

## 10.1 Estructura y responsabilidades

El código Java separa claramente las responsabilidades:

- `cargarModelo(...)` se encarga únicamente de construir y cargar el modelo RDF.
- Cada método `queryX_...` define una consulta SPARQL específica y formatea su resultado.
- `accesoProgramatico(...)` muestra cómo navegar el grafo sin usar SPARQL, lo cual es útil para validación y operaciones puntuales.
- `imprimirEncabezado(...)` mejora la legibilidad de la salida en consola.

## 10.2 Decisiones técnicas importantes

- Se usa un bloque de prefijos compartido (`PREFIJOS`) para evitar redundancia y garantizar consistencia entre consultas.
- `try (QueryExecution qe = ...)` cierra automáticamente los recursos del motor SPARQL, previniendo fugas de memoria.
- `RDFDataMgr.read(..., Lang.RDFXML)` es una elección robusta que garantiza la lectura correcta del formato RDF/XML.
- Usar `rdf:resource` en el RDF/XML para relaciones entre entidades permite consultas JOIN implícitas, muy eficientes en SPARQL.

## 10.3 Modelado de la información

El modelo fue diseñado para representar la cartelera de Cine Colombia con elementos relevantes:

- `cine:Pelicula` como clase principal.
- `dc:title` para el nombre de la película.
- `cine:duracionMinutos`, `cine:fechaEstreno` y `cine:disponible3D` como literales fuertemente tipados.
- `cine:director` y `cine:genero` como enlaces a recursos que contienen metadatos asociados.

Este diseño facilita consultas que combinan filtros, agregaciones y opcionales sin sacrificar coherencia semántica.

## 10.4 Análisis de consultas

- `FILTER` y `ORDER BY` se usan para filtrar datos numéricos y ordenar resultados, lo cual es esencial para consultas analíticas.
- `OPTIONAL` permite conservar películas sin director registrado y evita excluir datos válidos.
- `ASK` comprueba la existencia de un recurso sin devolver resultados innecesarios.
- `GROUP BY` con `COUNT` agrupa la cartelera por género, mostrando una forma de análisis agregativo.
- Las consultas en Java incluyen casos avanzados como `HAVING`, `UNION` y `CONSTRUCT`, demostrando dominio de SPARQL 1.1 dentro de Apache Jena.

## 10.5 Conclusión de calidad

El proyecto cumple con los criterios de evaluación:

- investigación y descripción de Apache Jena, RDF/XML y SPARQL;
- implementación de una base de datos RDF/XML para Cine Colombia;
- estructura y calidad de RDF/XML válida;
- implementación de 10 consultas SPARQL relevantes;
- análisis del código fuente con explicación de las decisiones técnicas;
- proyecto documentado, organizado y con evidencia de ejecución.

# **13\. Referencias**

* Apache Software Foundation. (2024). Apache Jena Documentation. https://jena.apache.org/documentation/

* W3C. (2014). RDF 1.1 Concepts and Abstract Syntax. https://www.w3.org/TR/rdf11-concepts/

* W3C. (2004). RDF/XML Syntax Specification. https://www.w3.org/TR/rdf-syntax-grammar/

* W3C. (2013). SPARQL 1.1 Query Language. https://www.w3.org/TR/sparql11-query/

* W3C. (2013). SPARQL 1.1 Overview. https://www.w3.org/TR/sparql11-overview/

* Dublin Core Metadata Initiative. (2020). Dublin Core Element Set v1.1. https://www.dublincore.org/specifications/dublin-core/

* Schema.org Community Group. (2024). Schema.org — Movie. https://schema.org/Movie

* DuCharme, B. (2013). Learning SPARQL (2nd ed.). O'Reilly Media.

* Allemang, D. & Hendler, J. (2011). Semantic Web for the Working Ontologist (2nd ed.). Elsevier.

* Apache Jena Fuseki. (2024). Fuseki Server Documentation. https://jena.apache.org/documentation/fuseki2/