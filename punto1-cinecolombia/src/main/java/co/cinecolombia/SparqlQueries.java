package co.cinecolombia;

import org.apache.jena.query.QueryExecution;
import org.apache.jena.query.QueryExecutionFactory;
import org.apache.jena.query.QuerySolution;
import org.apache.jena.query.ResultSet;
import org.apache.jena.query.ResultSetFormatter;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Resource;

public class SparqlQueries {

    private static final String NS_CINE   = "http://cinecolombia.com/ontologia#";
    private static final String NS_DC     = "http://purl.org/dc/elements/1.1/";
    private static final String NS_RDFS   = "http://www.w3.org/2000/01/rdf-schema#";
    private static final String NS_SCHEMA = "https://schema.org/";

    private static final String PREFIXES =
        "PREFIX cine:   <" + NS_CINE   + "> \n" +
        "PREFIX dc:     <" + NS_DC     + "> \n" +
        "PREFIX rdfs:   <" + NS_RDFS   + "> \n" +
        "PREFIX schema: <" + NS_SCHEMA + "> \n";

    private final Model model;

    public SparqlQueries(Model model) {
        this.model = model;
    }

    public void executeAll() {
        query1_ListadoCompleto();
        query2_PeliculasMayores12();
        query3_PeliculasCon3D();
        query4_OrdenadoPorDuracion();
        query5_AskExisteMortalKombat();
        query6_InfoDirectores();
        query7_PeliculasPorGenero();
        query8_PromedioDuracionPorGenero();
        query9_Peliculas3DOLargas();
        query10_ConstructPeliculas3D();
    }

    private void query1_ListadoCompleto() {
        printHeader("CONSULTA 1 · Listado completo de la cartelera");

        String sparql = PREFIXES +
            "SELECT ?titulo ?duracion ?distribuidora ?fechaEstreno \n" +
            "WHERE { \n" +
            "    ?pelicula a cine:Pelicula ; \n" +
            "              dc:title ?titulo ; \n" +
            "              cine:duracionMinutos ?duracion ; \n" +
            "              cine:distribuidora ?distribuidora ; \n" +
            "              cine:fechaEstreno ?fechaEstreno . \n" +
            "} \n" +
            "ORDER BY ?titulo";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            ResultSet rs = qe.execSelect();
            System.out.printf("%-40s %-8s %-30s %-12s%n", "TÍTULO", "MIN", "DISTRIBUIDORA", "ESTRENO");
            System.out.println("─".repeat(96));
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                System.out.printf("%-40s %-8s %-30s %-12s%n",
                    sol.getLiteral("titulo").getString(),
                    sol.getLiteral("duracion").getInt(),
                    sol.getLiteral("distribuidora").getString(),
                    sol.getLiteral("fechaEstreno").getString());
            }
        }
    }

    private void query2_PeliculasMayores12() {
        printHeader("CONSULTA 2 · Películas aptas para mayores de 12 años (FILTER)");

        String sparql = PREFIXES +
            "SELECT ?titulo ?generoLabel ?duracion \n" +
            "WHERE { \n" +
            "    ?pelicula a cine:Pelicula ; \n" +
            "              dc:title ?titulo ; \n" +
            "              cine:duracionMinutos ?duracion ; \n" +
            "              cine:clasificacion ?clasi ; \n" +
            "              cine:genero ?genero . \n" +
            "    ?clasi cine:edadMinima ?edad . \n" +
            "    ?genero rdfs:label ?generoLabel . \n" +
            "    FILTER (?edad <= 12) \n" +
            "} \n" +
            "ORDER BY DESC(?duracion)";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            ResultSet rs = qe.execSelect();
            System.out.printf("%-40s %-25s %-6s%n", "TÍTULO", "GÉNERO", "MIN");
            System.out.println("─".repeat(73));
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                System.out.printf("%-40s %-25s %-6d%n",
                    sol.getLiteral("titulo").getString(),
                    sol.getLiteral("generoLabel").getString(),
                    sol.getLiteral("duracion").getInt());
            }
        }
    }

    private void query3_PeliculasCon3D() {
        printHeader("CONSULTA 3 · Películas disponibles en 3D");

        String sparql = PREFIXES +
            "SELECT ?titulo ?distribuidora \n" +
            "WHERE { \n" +
            "    ?pelicula a cine:Pelicula ; \n" +
            "              dc:title ?titulo ; \n" +
            "              cine:distribuidora ?distribuidora ; \n" +
            "              cine:disponible3D true . \n" +
            "}";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            ResultSet rs = qe.execSelect();
            System.out.printf("%-40s %-30s%n", "TÍTULO", "DISTRIBUIDORA");
            System.out.println("─".repeat(72));
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                System.out.printf("%-40s %-30s%n",
                    sol.getLiteral("titulo").getString(),
                    sol.getLiteral("distribuidora").getString());
            }
        }
    }

    private void query4_OrdenadoPorDuracion() {
        printHeader("CONSULTA 4 · Películas ordenadas por duración + promedio (AVG)");

        String sparqlLista = PREFIXES +
            "SELECT ?titulo ?duracion \n" +
            "WHERE { \n" +
            "    ?p a cine:Pelicula ; \n" +
            "       dc:title ?titulo ; \n" +
            "       cine:duracionMinutos ?duracion . \n" +
            "} \n" +
            "ORDER BY DESC(?duracion)";

        try (QueryExecution qe = QueryExecutionFactory.create(sparqlLista, model)) {
            ResultSet rs = qe.execSelect();
            System.out.printf("%-40s %-6s%n", "TÍTULO", "MIN");
            System.out.println("─".repeat(48));
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                System.out.printf("%-40s %-6d%n",
                    sol.getLiteral("titulo").getString(),
                    sol.getLiteral("duracion").getInt());
            }
        }

        String sparqlAvg = PREFIXES +
            "SELECT (AVG(?duracion) AS ?promedio) (COUNT(?p) AS ?total) \n" +
            "WHERE { \n" +
            "    ?p a cine:Pelicula ; \n" +
            "       cine:duracionMinutos ?duracion . \n" +
            "}";

        try (QueryExecution qe = QueryExecutionFactory.create(sparqlAvg, model)) {
            ResultSet rs = qe.execSelect();
            if (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                System.out.printf("%nTotal películas   : %d%n", sol.getLiteral("total").getInt());
                System.out.printf("Duración promedio: %.1f minutos%n", sol.getLiteral("promedio").getDouble());
            }
        }
    }

    private void query5_AskExisteMortalKombat() {
        printHeader("CONSULTA 5 · ¿Está 'Mortal Kombat II' en cartelera? (ASK)");

        String sparql = PREFIXES +
            "ASK { \n" +
            "    ?p a cine:Pelicula ; \n" +
            "       dc:title \"Mortal Kombat II\" . \n" +
            "}";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            boolean resultado = qe.execAsk();
            System.out.println("Resultado ASK → " + (resultado ? "true ✔ Sí está en cartelera" : "false ✘ No está en cartelera"));
        }
    }

    private void query6_InfoDirectores() {
        printHeader("CONSULTA 6 · Películas con su director (JOIN sobre recursos)");

        String sparql = PREFIXES +
            "SELECT ?titulo ?nombreDirector ?nacionalidad \n" +
            "WHERE { \n" +
            "    ?p a cine:Pelicula ; \n" +
            "       dc:title ?titulo ; \n" +
            "       cine:director ?dir . \n" +
            "    ?dir schema:name ?nombreDirector . \n" +
            "    OPTIONAL { ?dir schema:nationality ?nacionalidad } \n" +
            "} \n" +
            "ORDER BY ?nombreDirector";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            ResultSet rs = qe.execSelect();
            System.out.printf("%-38s %-22s %-16s%n", "TÍTULO", "DIRECTOR", "NACIONALIDAD");
            System.out.println("─".repeat(78));
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                String nac = sol.contains("nacionalidad") ? sol.getLiteral("nacionalidad").getString() : "(no registrada)";
                System.out.printf("%-38s %-22s %-16s%n",
                    sol.getLiteral("titulo").getString(),
                    sol.getLiteral("nombreDirector").getString(),
                    nac);
            }
        }
    }

    private void query7_PeliculasPorGenero() {
        printHeader("CONSULTA 7 · Películas agrupadas por género (GROUP BY + COUNT)");

        String sparql = PREFIXES +
            "SELECT ?generoLabel (COUNT(?p) AS ?cantidad) \n" +
            "WHERE { \n" +
            "    ?p a cine:Pelicula ; \n" +
            "       cine:genero ?g . \n" +
            "    ?g rdfs:label ?generoLabel . \n" +
            "} \n" +
            "GROUP BY ?generoLabel \n" +
            "ORDER BY DESC(?cantidad)";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            ResultSet rs = qe.execSelect();
            System.out.printf("%-30s %-8s%n", "GÉNERO", "PELÍCULAS");
            System.out.println("─".repeat(40));
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                System.out.printf("%-30s %-8d%n",
                    sol.getLiteral("generoLabel").getString(),
                    sol.getLiteral("cantidad").getInt());
            }
        }
    }

    private void query8_PromedioDuracionPorGenero() {
        printHeader("CONSULTA 8 · Géneros con duración promedio alta (GROUP BY + HAVING)");

        String sparql = PREFIXES +
            "SELECT ?generoLabel (AVG(?duracion) AS ?promedio) (COUNT(?p) AS ?cantidad) \n" +
            "WHERE { \n" +
            "    ?p a cine:Pelicula ; \n" +
            "       cine:genero ?g ; \n" +
            "       cine:duracionMinutos ?duracion . \n" +
            "    ?g rdfs:label ?generoLabel . \n" +
            "} \n" +
            "GROUP BY ?generoLabel \n" +
            "HAVING (AVG(?duracion) > 110) \n" +
            "ORDER BY DESC(?promedio)";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            ResultSet rs = qe.execSelect();
            System.out.printf("%-30s %-12s %-8s%n", "GÉNERO", "PROMEDIO", "CANT.");
            System.out.println("─".repeat(53));
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                System.out.printf("%-30s %-12.1f %-8d%n",
                    sol.getLiteral("generoLabel").getString(),
                    sol.getLiteral("promedio").getDouble(),
                    sol.getLiteral("cantidad").getInt());
            }
        }
    }

    private void query9_Peliculas3DOLargas() {
        printHeader("CONSULTA 9 · Películas 3D o muy largas (UNION + DISTINCT)");

        String sparql = PREFIXES +
            "SELECT DISTINCT ?titulo ?duracion ?en3D \n" +
            "WHERE { \n" +
            "    { \n" +
            "        ?p a cine:Pelicula ; \n" +
            "           dc:title ?titulo ; \n" +
            "           cine:duracionMinutos ?duracion ; \n" +
            "           cine:disponible3D true . \n" +
            "        BIND(true AS ?en3D) \n" +
            "    } \n" +
            "    UNION \n" +
            "    { \n" +
            "        ?p a cine:Pelicula ; \n" +
            "           dc:title ?titulo ; \n" +
            "           cine:duracionMinutos ?duracion . \n" +
            "        FILTER(?duracion > 120) \n" +
            "        BIND(false AS ?en3D) \n" +
            "    } \n" +
            "} \n" +
            "ORDER BY DESC(?duracion)";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            ResultSet rs = qe.execSelect();
            System.out.printf("%-40s %-6s %-4s%n", "TÍTULO", "MIN", "3D");
            System.out.println("─".repeat(52));
            while (rs.hasNext()) {
                QuerySolution sol = rs.nextSolution();
                System.out.printf("%-40s %-6d %-4s%n",
                    sol.getLiteral("titulo").getString(),
                    sol.getLiteral("duracion").getInt(),
                    sol.getLiteral("en3D").getBoolean() ? "Sí" : "No");
            }
        }
    }

    private void query10_ConstructPeliculas3D() {
        printHeader("CONSULTA 10 · Subgrafo CONSTRUCT de películas en 3D");

        String sparql = PREFIXES +
            "CONSTRUCT { \n" +
            "    ?p a cine:Pelicula ; \n" +
            "       dc:title ?titulo ; \n" +
            "       cine:distribuidora ?distribuidora . \n" +
            "} \n" +
            "WHERE { \n" +
            "    ?p a cine:Pelicula ; \n" +
            "       dc:title ?titulo ; \n" +
            "       cine:disponible3D true ; \n" +
            "       cine:distribuidora ?distribuidora . \n" +
            "}";

        try (QueryExecution qe = QueryExecutionFactory.create(sparql, model)) {
            Model constructed = qe.execConstruct();
            System.out.printf("Subgrafo CONSTRUCT generado con %d tripletas.%n", constructed.size());
            constructed.write(System.out, "TURTLE");
            constructed.close();
        }
    }

    private void printHeader(String title) {
        System.out.println();
        System.out.println("┌─────────────────────────────────────────────────────");
        System.out.println("│  " + title);
        System.out.println("└─────────────────────────────────────────────────────");
    }
}
