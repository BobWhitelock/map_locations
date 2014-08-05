import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import java.io.IOException;
import java.util.Properties;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 *
 * @author bob
 */
@WebServlet("/core-nlp-servlet")
public class CoreNlpServlet extends HttpServlet {

    private static StanfordCoreNLP nerPipeline;
    private static StanfordCoreNLP tokenizePipeline;

    public CoreNlpServlet() {
        // set up corenlp pipelines
        Properties nerProps = new Properties();
        nerProps.put("annotators", "tokenize, ssplit, pos, lemma, ner");
        nerPipeline = new StanfordCoreNLP(nerProps);
        
        Properties tokenizeProps = new Properties();
        tokenizeProps.put("annotators", "tokenize, ssplit");
        tokenizePipeline = new StanfordCoreNLP(tokenizeProps);
    }

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        System.out.println(request);
        // get text sent
        String text = request.getParameter("text");
        if (text == null) {
            // if no text parameter given assign text to empty string
            text = "";
        }
        
        // tag text according to pipeline requested with 'pipeline' parameter
        Annotation document = new Annotation(text);
        String pipeline = request.getParameter("pipeline");
        switch (pipeline) {
            case "tokenize":
                tokenizePipeline.annotate(document);
                break;
            case "ner":
            default:
                // by default tag with fuller pipeline
                nerPipeline.annotate(document);
                break;
        }
                
        // response will be xml - TODO add other headers?
        response.addHeader("Content-Type", "text/xml");

        // send xml as the response
        try {
            nerPipeline.xmlPrint(document, response.getWriter());
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
