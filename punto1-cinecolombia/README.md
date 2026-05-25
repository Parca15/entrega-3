# Cartelera Cine Colombia — Base de Datos RDF/XML con Apache Jena

**Asignatura:** Semántica Web y Big Data  
**Entrega:** Tercera Nota Parcial  
**Tecnología:** Apache Jena 4.10.0 · Java 17 · Maven 3.8 · SPARQL 1.1  
**Fecha de cartelera:** 14 de mayo de 2026

---

## Descripción

Base de datos RDF/XML que modela la cartelera actual de **Cine Colombia**
usando la ontología `http://cinecolombia.com/ontologia#`. El proyecto incluye:

- Archivo RDF/XML con 126 tripletas (5 películas, directores, géneros, clasificaciones)
- Código Java con Apache Jena que carga el modelo y ejecuta 10 consultas SPARQL 1.1 usando clases separadas

## Estructura del proyecto

```
cinecolombia/
├── pom.xml                                    ← Dependencias Maven (Jena 4.10.0)
├── README.md                                  ← Este archivo
├── src/
    ├── main/
    │   ├── java/co/cinecolombia/
    │   │   ├── Main.java                      ← Punto de entrada Java
    │   │   ├── ModelLoader.java               ← Carga del modelo RDF/XML
    │   │   └── SparqlQueries.java             ← Ejecución de 10 consultas SPARQL
    │   └── resources/
    │       └── peliculas_cine_colombia.rdf    ← Base de datos RDF/XML
    └── test/
        └── java/co/cinecolombia/             ← (carpeta reservada para tests)
```

## Ejecución

### Con Java + Maven
```bash
cd cinecolombia
mvn package
java -jar target/cartelera-rdf-1.0.0.jar
```

## Consultas SPARQL implementadas

| # | Tipo | Característica |
|---|------|---------------|
| 01 | SELECT | Patrón básico de tripletas |
| 02 | SELECT | FILTER numérico |
| 03 | SELECT | FILTER booleano + BIND/IF |
| 04 | SELECT | OPTIONAL anidado |
| 05 | SELECT | ORDER BY DESC + LIMIT |
| 06 | ASK | Verificación de existencia |
| 07 | SELECT | COUNT · AVG · MIN · MAX · SUM |
| 08 | SELECT | GROUP BY + HAVING |
| 09 | SELECT | UNION + DISTINCT |
| 10 | CONSTRUCT | Generación de subgrafo RDF |
