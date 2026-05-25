package co.cinecolombia;

import org.apache.jena.rdf.model.Model;

public class Main {

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════════════╗");
        System.out.println("║   BASE DE DATOS RDF — CARTELERA CINE COLOMBIA        ║");
        System.out.println("║   Semántica Web y Big Data · Apache Jena 4.10.0      ║");
        System.out.println("╚══════════════════════════════════════════════════════╝\n");

        Model model = ModelLoader.loadModel("peliculas_cine_colombia.rdf");
        System.out.printf("✔ Modelo cargado exitosamente. Tripletas totales: %d%n%n", model.size());

        new SparqlQueries(model).executeAll();

        model.close();
        System.out.println("\n╔══════════════════════════════════════════════════════╗");
        System.out.println("║  Ejecución completada. Modelo cerrado correctamente. ║");
        System.out.println("╚══════════════════════════════════════════════════════╝");
    }
}
