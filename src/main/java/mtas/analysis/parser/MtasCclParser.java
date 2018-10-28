/**
 *
 */
package mtas.analysis.parser;

import mtas.analysis.util.MtasConfigException;
import mtas.analysis.util.MtasConfiguration;

/**
 * The Class MtasCclParser.
 */
final public class MtasCclParser extends MtasXMLParser {

  /**
   * Instantiates a new mtas CCl parser.
   *
   * @param config the config
   */
  public MtasCclParser(MtasConfiguration config) {
    super(config);
  }

  /*
   * (non-Javadoc)
   *
   * @see mtas.analysis.parser.MtasXMLParser#initParser()
   */
  @Override
  protected void initParser() throws MtasConfigException {
    rootTag = "chunkList";
    contentTag = "chunkList";
    allowNonContent = true;
    super.initParser();
  }

}
