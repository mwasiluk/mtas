package mtas.solr.handler.stat;

import org.apache.commons.lang3.StringUtils;
import org.apache.solr.common.params.ModifiableSolrParams;

public class MtasGroupQueryHandler {
    int countLimit = 1000;
    int displLimit = 10;
    int occurLimit = 1;
    String sortOrder = null;
    String groupby;
    String leftGroupby, rightGroupby;
    int maxCount = 0;
    private String simpleQueryText;
    private String groupText;

    public boolean handleGroups(int groupIndex, String queryText, String mtasField, ModifiableSolrParams params) {

        this.simpleQueryText = queryText;
        if (!hasGroupQueryCOmponent(queryText)) {
            return false;
        }

        String groupByString = " group by ";
        int ind = queryText.indexOf(groupByString);
        if (ind < 0) {
            return false;
        }
        this.groupText = queryText.substring(ind + groupByString.length());
        this.simpleQueryText = queryText.substring(0, ind);

        if (groupIndex < 0) {
            return false;
        }

        try {

            groupby = stripModifiers(groupText);
            params.set("mtas.group", true);
            params.set("mtas.group."+groupIndex+".query.type", "cql");
            params.set("mtas.group."+groupIndex+".number", displLimit);
            params.set("rows", 0);
            params.set("mtas.group."+groupIndex+".query.value", simpleQueryText);

            params.set("mtas.group."+groupIndex+".field", mtasField);

            int i = groupby.indexOf(';');
            if (i != -1) {
                leftGroupby = groupby.substring(0, i).trim();
                rightGroupby = groupby.substring(i+1).trim();
                //TODO advanced collocations
            } else {
                leftGroupby = groupby;
                rightGroupby = "";


                String[] split = groupby.split(" *, *");
                for (int gi = 0; gi < split.length; gi++) {

                    String[] h = split[gi].split("\\.");


                    int segno;
                    String type;

                    if (h.length == 2) {
                        segno = Math.max(0, Util.safeParseInt(h[0], 1) - 1);

                        type = h[1];
                    } else if (h.length == 1) {
                        segno = 0;
                        type = h[0];
                    }else{
                        continue;
                    }

                    params.set("mtas.group."+groupIndex+".grouping.hit.insideLeft."+gi+".position", segno);
                    params.set("mtas.group."+groupIndex+".grouping.hit.insideLeft."+gi+".prefixes", type);


                }

            }

        } catch (StatQueryException e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    public static boolean hasGroupQueryCOmponent(String query) {
        return StringUtils.isNotBlank(query) && query.toLowerCase().contains(" group by ");
    }




    private int modifierEndPosition(String groupby, int start)
            throws StatQueryException
    {
        boolean checkNumber = false, checkAll = false;
        int offset = -1;
        int len = groupby.length();

        if (groupby.regionMatches(start, " display ", 0, 9)) {
            checkNumber = true;
            offset = 9;
        } else if (groupby.regionMatches(start, " min ", 0, 5)) {
            checkNumber = true;
            offset = 5;
        } else if (groupby.regionMatches(start, " count ", 0, 7)) {
            checkNumber = true;
            checkAll = true;
            offset = 7;
        } else if (groupby.regionMatches(start, " sort ", 0, 6)) {
            offset = 6;
        } else {
            throw new StatQueryException();
        } // failed to parse

        offset += start;
        if (checkNumber) {
            if (checkAll && groupby.regionMatches(offset, "all", 0, 3)) {
                return offset + 3;
            }
            while (offset < len && Character.isDigit(groupby.charAt(offset))) {
                offset++;
            }
            return offset;
        }
        // sort modifier, check possible cases
        if (groupby.regionMatches(offset, "a fronte", 0, 8)) {
            return offset + 8;
        }
        if (groupby.regionMatches(offset, "a tergo", 0, 7)) {
            return offset + 7;
        }
        if (groupby.regionMatches(offset, "by ", 0, 3)) {
            offset += 3;
            if (groupby.regionMatches(offset, "freq", 0, 4)) {
                return offset + 4;
            }
            if (groupby.regionMatches(offset, "maxcp", 0, 5)) {
                return offset + 5;
            }
            if (groupby.regionMatches(offset, "dice", 0, 4)) {
                return offset + 4;
            }
            if (groupby.regionMatches(offset, "cp", 0, 2)) {
                return offset + 2;
            }
            if (groupby.regionMatches(offset, "scp bias ", 0, 9)) {
                offset += 9;
                while (offset < len && groupby.charAt(offset) != ' ') {
                    offset++;
                }
                return offset;
            }
            if (groupby.regionMatches(offset, "scp", 0, 3)) {
                return offset + 3;
            }
        }
        throw new StatQueryException();
    }


    String stripModifiers(String groupby) throws StatQueryException {
        int i, end;

        i = groupby.indexOf(" display ");
        if (i != -1) {
            end = modifierEndPosition(groupby, i);
            displLimit = Util.safeParseInt(groupby.substring(i + 9, end), displLimit);
            groupby = groupby.substring(0, i) + groupby.substring(end);
        }

        i = groupby.indexOf(" count ");
        if (i != -1) {
            end = modifierEndPosition(groupby, i);
            countLimit = Util.safeParseInt(groupby.substring(i + 7, end), countLimit);
            groupby = groupby.substring(0, i) + groupby.substring(end);
        }

        i = groupby.indexOf(" min ");
        if (i != -1) {
            end = modifierEndPosition(groupby, i);
            occurLimit = Util.safeParseInt(groupby.substring(i + 5, end), occurLimit);
            groupby = groupby.substring(0, i) + groupby.substring(end);
        }

        i = groupby.indexOf(" sort ");
        if (i != -1) {
            end = modifierEndPosition(groupby, i);
            sortOrder = (groupby.substring(i + 6, end));
            groupby = groupby.substring(0, i) + groupby.substring(end);
        }

        return groupby;
    }

    public int getCountLimit() {
        return countLimit;
    }

    public void setCountLimit(int countLimit) {
        this.countLimit = countLimit;
    }

    public int getDisplLimit() {
        return displLimit;
    }

    public void setDisplLimit(int displLimit) {
        this.displLimit = displLimit;
    }

    public int getOccurLimit() {
        return occurLimit;
    }

    public void setOccurLimit(int occurLimit) {
        this.occurLimit = occurLimit;
    }

    public String getSortOrder() {
        return sortOrder;
    }

    public void setSortOrder(String sortOrder) {
        this.sortOrder = sortOrder;
    }

    public String getGroupby() {
        return groupby;
    }

    public void setGroupby(String groupby) {
        this.groupby = groupby;
    }

    public String getLeftGroupby() {
        return leftGroupby;
    }

    public void setLeftGroupby(String leftGroupby) {
        this.leftGroupby = leftGroupby;
    }

    public String getRightGroupby() {
        return rightGroupby;
    }

    public void setRightGroupby(String rightGroupby) {
        this.rightGroupby = rightGroupby;
    }

    public int getMaxCount() {
        return maxCount;
    }

    public void setMaxCount(int maxCount) {
        this.maxCount = maxCount;
    }

    public String getSimpleQueryText() {
        return simpleQueryText;
    }

    public void setSimpleQueryText(String simpleQueryText) {
        this.simpleQueryText = simpleQueryText;
    }

    public String getGroupText() {
        return groupText;
    }

    public void setGroupText(String groupText) {
        this.groupText = groupText;
    }
}
