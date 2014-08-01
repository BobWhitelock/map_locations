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

    private static StanfordCoreNLP corenlpPipeline;

    public CoreNlpServlet() {
        // set up the corenlp pipeline used to process all requests
        Properties corenlpProps = new Properties();
        corenlpProps.put("annotators", "tokenize, ssplit, pos, lemma, ner");
        corenlpPipeline = new StanfordCoreNLP(corenlpProps);
    }

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        
        // get text sent
        String text = request.getParameter("text");
        if (text == null) {
            // if no text parameter given assign text to empty string
            text = "";
        }
        
        // tag the text using pipeline
        Annotation document = new Annotation(text);
        corenlpPipeline.annotate(document);

        // response will be xml - TODO add other headers?
        response.addHeader("Content-Type", "text/xml");

        // send xml as the response
        try {
            corenlpPipeline.xmlPrint(document, response.getWriter());
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
