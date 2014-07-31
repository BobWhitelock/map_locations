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
        Properties corenlpProps = new Properties();

//        corenlpProps.put("pos.model", "/usr/java/packages/lib/ext/stanford-corenlp-full-2014-06-16/"
//                + "stanford-corenlp-3.4-models/edu/stanford/nlp/models/pos-tagger/"
//                + "english-left3words/english-left3words-distsim.tagger");
//        corenlpProps.put("ner.model", "/usr/java/packages/lib/ext/stanford-corenlp-full-2014-06-16"
//                + "/stanford-corenlp-3.4-models/edu/stanford/nlp/models/ner"
//                + "/english.all.3class.distsim.crf.ser.gz");

        corenlpProps.put("annotators", "tokenize, ssplit, pos, lemma, ner");

        corenlpPipeline = new StanfordCoreNLP(corenlpProps);
    }

    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        String text = request.getParameter("text");
        Annotation document = new Annotation(text);
        corenlpPipeline.annotate(document);

        response.addHeader("Content-Type", "text/xml");

        try {
            corenlpPipeline.xmlPrint(document, response.getWriter());
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}
