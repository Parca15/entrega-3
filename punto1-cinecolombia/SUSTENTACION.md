# Sustentación del Proyecto: Cartelera Cine Colombia RDF

## Objetivo

El proyecto modela una cartelera de Cine Colombia como una base de datos RDF/XML y demuestra su uso con Apache Jena en Java. El propósito principal es evidenciar:

- la construcción de un grafo RDF con películas, directores, géneros, clasificaciones y fechas de estreno;
- la carga del modelo RDF desde un recurso en `src/main/resources`;
- la ejecución de consultas SPARQL 1.1 con distintos patrones y operaciones.

## Tecnologías usadas

- Java 17
- Apache Maven 3.8
- Apache Jena 4.10.0
- SPARQL 1.1
- RDF/XML como formato de datos semánticos

## Archivos principales y responsabilidades

### `pom.xml`

- Define el proyecto Maven, versión `1.0.0` y `Java 17`.
- Agrega la dependencia `apache-jena-libs` para Jena Core, ARQ y RIOT.
- Incluye `slf4j-simple` para registrar mensajes de Apache Jena en tiempo de ejecución.
- Configura el plugin `maven-shade-plugin` para generar un JAR ejecutable que contiene todas las dependencias.
- Incluye el archivo RDF en el paquete final para que la aplicación pueda cargarlo desde el classpath.

### `src/main/resources/peliculas_cine_colombia.rdf`

- Contiene la base de datos RDF/XML que representa la cartelera.
- Incluye los datos de películas, directores, géneros, distribuidoras y clasificación por edad.
- Es el recurso cargado por la aplicación Java.

### `src/main/java/co/cinecolombia/ModelLoader.java`

- Lee el recurso RDF en formato RDF/XML usando `RDFDataMgr.read`.
- Crea un modelo Jena (`Model`) y lo retorna para uso posterior.
- Maneja errores de carga lanzando una excepción clara si el recurso no existe o falla el parseo.

### `src/main/java/co/cinecolombia/SparqlQueries.java`

- Contiene la lógica para ejecutar las consultas SPARQL sobre el modelo cargado.
- Define prefijos comunes para los espacios de nombres utilizados en el RDF.
- Implementa 10 consultas SPARQL con distintos enfoques:
  - SELECT con listado completo y ordenación.
  - FILTER numérico para clasificación por edad.
  - Búsqueda de películas 3D.
  - ORDER BY y agregados como AVG y COUNT.
  - ASK para verificar existencia de un recurso específico.
  - OPTIONAL para manejar información opcional de directores.
  - GROUP BY y HAVING para análisis por género.
  - CONSTRUCT para generar un subgrafo RDF.
- Cada consulta imprime resultados tabulados en la consola.

### `src/main/java/co/cinecolombia/Main.java`

- Punto de entrada de la aplicación.
- Carga el modelo RDF usando `ModelLoader.loadModel("peliculas_cine_colombia.rdf")`.
- Muestra en consola el número total de tripletas del modelo.
- Ejecuta todas las consultas definidas en `SparqlQueries`.
- Cierra el modelo al terminar para liberar recursos.

## Qué se hizo para sustentar

1. Se modeló una cartelera de cine como un grafo RDF/XML completo y consistente.
2. Se separaron responsabilidades en capas: carga de datos (`ModelLoader`) y consultas (`SparqlQueries`).
3. Se comprobó que el RDF se carga correctamente y se puede consultar con Jena.
4. Se implementaron consultas SPARQL representativas de varios conceptos clave de la materia:
   - patrones básicos de tripleta
   - filtros (`FILTER`)
   - consultas booleanas (`ASK`)
   - agregaciones y estadísticas (`AVG`, `COUNT`)
   - relaciones entre recursos (`OPTIONAL`, `JOIN`)
   - construcción de subgrafos (`CONSTRUCT`)
5. Se empacó la aplicación en un JAR ejecutable para demostrar su funcionamiento independiente.

## Ejecución

Para generar el JAR y correr la aplicación:

```bash
cd "/Users/jeyson/Documents/BigData/entrega 3/punto1-cinecolombia"
mvn package
java -jar target/cartelera-rdf-1.0.0.jar
```

## Resultados esperados

- Carga exitosa del modelo RDF.
- Visualización de la cantidad de tripletas totales.
- Impresión de los resultados de las 10 consultas SPARQL.
- Cierre correcto del modelo al finalizar.

## Conclusión

Este proyecto evidencia el uso práctico de RDF y SPARQL con Apache Jena para representar y consultar información de una cartelera de cine. Permite sustentar que se trabajó con conceptos de Semántica Web y Big Data en un flujo completo de modelado, consulta y ejecución en Java.
