/**
 *
 */
package mtas.analysis.parser;

import mtas.analysis.util.MtasConfigException;
import mtas.analysis.util.MtasConfiguration;

/**
 * The Class MtasTEIParser.
 */
final public class MtasXcesParser extends MtasXMLParser {

  /**
   * Instantiates a new mtas TEI parser.
   *
   * @param config the config
   */
  public MtasXcesParser(MtasConfiguration config) {
    super(config);
  }

  /*
   * (non-Javadoc)
   *
   * @see mtas.analysis.parser.MtasXMLParser#initParser()
   */
  @Override
  protected void initParser() throws MtasConfigException {
    rootTag = "cesAna";
    contentTag = "chunkList";
    allowNonContent = true;
    super.initParser();
  }

}
