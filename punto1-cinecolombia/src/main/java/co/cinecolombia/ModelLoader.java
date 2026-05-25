package co.cinecolombia;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;

import java.io.InputStream;

public class ModelLoader {

    public static Model loadModel(String resourceName) {
        Model model = ModelFactory.createDefaultModel();

        try (InputStream input = ModelLoader.class.getClassLoader().getResourceAsStream(resourceName)) {
            if (input == null) {
                throw new IllegalArgumentException("No se encontró el recurso RDF: " + resourceName);
            }
            RDFDataMgr.read(model, input, Lang.RDFXML);
        } catch (Exception e) {
            throw new RuntimeException("Error cargando el modelo RDF desde el recurso: " + resourceName, e);
        }

        return model;
    }
}
