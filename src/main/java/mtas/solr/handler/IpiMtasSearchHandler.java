package mtas.solr.handler;


import mtas.solr.handler.stat.MtasGroupQueryHandler;
import org.apache.commons.lang3.StringUtils;
import org.apache.solr.common.params.ModifiableSolrParams;
import org.apache.solr.common.params.SolrParams;
import org.apache.solr.handler.component.SearchHandler;
import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.response.SolrQueryResponse;

public class IpiMtasSearchHandler extends SearchHandler {


    @Override
    public void handleRequestBody(SolrQueryRequest req, SolrQueryResponse rsp) throws Exception {
        transformParams(req);
        super.handleRequestBody(req, rsp);
    }

    private void transformParams(SolrQueryRequest req) {
        SolrParams params = req.getParams();
        ModifiableSolrParams newParams = ModifiableSolrParams.of(params);

        if (!isMtasRequest(params)) {
            return;
        }

        handleGroups(newParams);


        req.setParams(newParams);
    }
    private boolean isMtasRequest(SolrParams params) {
        return Boolean.TRUE.equals(params.getBool("mtas"));
    }

    private void handleGroups(ModifiableSolrParams params) {
        int groupIndex = handleGroupsInListQueries(0, params);

    }


    private int handleGroupsInListQueries(int groupIndex, ModifiableSolrParams params) {
        for(int i=0; i<100 ;i++){
            String queryParamName = "mtas.list."+i+".query.value";
            String queryText = params.get(queryParamName);
            if(StringUtils.isBlank(queryText)){
                return groupIndex;
            }
            if (!MtasGroupQueryHandler.hasGroupQueryCOmponent(queryText)) {
                continue;
            }
            String mtasField = params.get("mtas.list."+i+".field");
            MtasGroupQueryHandler handler = new MtasGroupQueryHandler();
            if(handler.handleGroups(groupIndex, queryText, mtasField, params)){
                groupIndex++;
            }
            params.set(queryParamName, handler.getSimpleQueryText());

        }
        return groupIndex;
    }


}
