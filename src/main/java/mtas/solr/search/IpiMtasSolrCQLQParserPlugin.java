package mtas.solr.search;

import mtas.solr.handler.stat.MtasGroupQueryHandler;
import org.apache.solr.common.params.ModifiableSolrParams;
import org.apache.solr.common.params.SolrParams;
import org.apache.solr.common.util.NamedList;
import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.search.QParser;
import org.apache.solr.search.QParserPlugin;

/**
 * The Class MtasSolrCQLQParserPlugin.
 */
public class IpiMtasSolrCQLQParserPlugin extends MtasSolrCQLQParserPlugin {

  @Override
  public QParser createParser(String qstr, SolrParams localParams,
      SolrParams params, SolrQueryRequest req) {

    //Remove grouping from query
    ModifiableSolrParams newLocalParams = ModifiableSolrParams.of(localParams);
    String query = newLocalParams.get("query");
    if (MtasGroupQueryHandler.hasGroupQueryCOmponent(query)) {
      MtasGroupQueryHandler gh = new MtasGroupQueryHandler();
      gh.handleGroups(-1, query, null, null);
      newLocalParams.set("query", gh.getSimpleQueryText());
    }



    return new MtasCQLQParser(qstr, newLocalParams, params, req);
  }

}
