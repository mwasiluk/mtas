package mtas.parser;

import static org.junit.Assert.*;

import java.io.BufferedReader;
import java.io.StringReader;

import mtas.parser.cql.MtasCQLParser;
import mtas.parser.cql.ParseException;
import mtas.parser.cql.util.MtasCQLParserWordPositionQuery;
import mtas.parser.cql.util.MtasCQLParserWordQuery;
import mtas.search.spans.MtasSpanAndQuery;
import mtas.search.spans.MtasSpanNotQuery;
import mtas.search.spans.MtasSpanOrQuery;
import mtas.search.spans.util.MtasSpanQuery;

public class MtasCQLParserTestWord {

  @org.junit.Test
  public void test() {
    try {
      basicTests();
      basicNotTests();
    } catch (ParseException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }    
  }
  
  private void testCQLParse(String field, String defaultPrefix, String cql, MtasSpanQuery q) {    
    MtasCQLParser p = new MtasCQLParser(new BufferedReader(new StringReader(cql)));
    try {
      assertEquals(p.parse(field, defaultPrefix, null, null, null) ,q);
      //System.out.println("Tested CQL parsing:\t"+cql);
    } catch (ParseException e) {
      //System.out.println("Error CQL parsing:\t"+cql);
      e.printStackTrace();
    }
  }
  
  private void testCQLEquivalent(String field, String defaultPrefix, String cql1, String cql2) {    
    MtasCQLParser p1 = new MtasCQLParser(new BufferedReader(new StringReader(cql1)));   
    MtasCQLParser p2 = new MtasCQLParser(new BufferedReader(new StringReader(cql2)));   
    try {
      assertEquals(p1.parse(field, defaultPrefix,null, null, null) ,p2.parse(field, defaultPrefix, null, null, null));
      //System.out.println("Tested CQL equivalent:\t"+cql1+" and "+cql2);
    } catch (ParseException e) {
      //System.out.println("Error CQL equivalent:\t"+cql1+" and "+cql2);
      e.printStackTrace();
    }
  }
  
  private void basicNotTests() throws ParseException {
    basicNotTest1();
    basicNotTest2();
    basicNotTest3();
    basicNotTest4();
    basicNotTest5();
  }
  
  private void basicTests() throws ParseException {
    basicTest1();
    basicTest2();
    basicTest3();
    basicTest4();
    basicTest5();
    basicTest6();
    basicTest7();
    basicTest8();
    basicTest9();
    basicTest10(); 
    basicTest11(); 
    basicTest12(); 
    basicTest13(); 
  }
  
  private void basicNotTest1() throws ParseException {
    String field = "testveld";
    String cql = "[pos=\"LID\" & !lemma=\"de\"]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"pos","LID",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"lemma","de",null, null);
    MtasSpanQuery q = new MtasSpanNotQuery(q1,q2);
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicNotTest2() {
    String field = "testveld";
    String cql1 = "[pos=\"LID\" & (!lemma=\"de\")]";
    String cql2 = "[pos=\"LID\" & !(lemma=\"de\")]";
    testCQLEquivalent(field, null, cql1, cql2);    
  }
  
  private void basicNotTest3() throws ParseException {
    String field = "testveld";
    String cql = "[pos=\"LID\" & !(lemma=\"de\" | lemma=\"een\")]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"pos","LID",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"lemma","de",null, null);
    MtasSpanQuery q3 = new MtasCQLParserWordQuery(field,"lemma","een",null, null);
    MtasSpanQuery q4 = new MtasSpanOrQuery(new MtasSpanQuery[]{q2,q3});
    MtasSpanQuery q = new MtasSpanNotQuery(q1,q4);
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicNotTest4() {
    String field = "testveld";
    String cql1 = "[pos=\"LID\" & !(lemma=\"de\" | lemma=\"een\")]";
    String cql2 = "[pos=\"LID\" & (!lemma=\"de\" & !lemma=\"een\")]";
    testCQLEquivalent(field, null, cql1, cql2);    
  }
  
  private void basicNotTest5() {
    String field = "testveld";
    String cql1 = "[pos=\"LID\" & !(lemma=\"de\" | lemma=\"een\")]";
    String cql2 = "[pos=\"LID\" & !lemma=\"de\" & !lemma=\"een\"]";
    testCQLEquivalent(field, null, cql1, cql2);      
  }
  
  private void basicTest1() throws ParseException {
    String field = "testveld";
    String cql = "[lemma=\"koe\"]";
    MtasSpanQuery q = new MtasCQLParserWordQuery(field, "lemma", "koe",null, null);
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest2() throws ParseException {
    String field = "testveld";
    String cql = "[lemma=\"koe\" & pos=\"N\"]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"lemma","koe",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"pos","N",null, null);
    MtasSpanQuery q = new MtasSpanAndQuery(new MtasSpanQuery[]{q1,q2});
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest3() throws ParseException {
    String field = "testveld";
    String cql = "[lemma=\"koe\" | lemma=\"paard\"]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"lemma","koe",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"lemma","paard",null, null);
    MtasSpanQuery q = new MtasSpanOrQuery(new MtasSpanQuery[]{q1,q2});
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest4() {
    String field = "testveld";
    String cql1 = "[lemma=\"koe\" | lemma=\"paard\"]";
    String cql2 = "[(lemma=\"koe\" | lemma=\"paard\")]";
    testCQLEquivalent(field, null, cql1, cql2);    
  }
  
  private void basicTest5() throws ParseException {
    String field = "testveld";
    String cql = "[(lemma=\"koe\" | lemma=\"paard\") & pos=\"N\"]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"lemma","koe",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"lemma","paard",null, null);
    MtasSpanQuery q3 = new MtasSpanOrQuery(new MtasSpanQuery[]{q1,q2});
    MtasSpanQuery q4 = new MtasCQLParserWordQuery(field,"pos","N",null, null);
    MtasSpanQuery q = new MtasSpanAndQuery(new MtasSpanQuery[]{q3,q4});
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest6() throws ParseException {
    String field = "testveld";
    String cql = "[pos=\"N\" & (lemma=\"koe\" | lemma=\"paard\")]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"pos","N",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"lemma","koe",null, null);
    MtasSpanQuery q3 = new MtasCQLParserWordQuery(field,"lemma","paard",null, null);
    MtasSpanQuery q4 = new MtasSpanOrQuery(new MtasSpanQuery[]{q2,q3});
    MtasSpanQuery q = new MtasSpanAndQuery(new MtasSpanQuery[]{q1,q4});
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest7() throws ParseException {
    String field = "testveld";
    String cql = "[pos=\"LID\" | (lemma=\"koe\" & pos=\"N\")]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"pos","LID",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"lemma","koe",null, null);
    MtasSpanQuery q3 = new MtasCQLParserWordQuery(field,"pos","N",null, null);
    MtasSpanQuery q4 = new MtasSpanAndQuery(new MtasSpanQuery[]{q2,q3});
    MtasSpanQuery q = new MtasSpanOrQuery(new MtasSpanQuery[]{q1,q4});
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest8() throws ParseException {
    String field = "testveld";
    String cql = "[(lemma=\"de\" & pos=\"LID\") | (lemma=\"koe\" & pos=\"N\")]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"lemma","de",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"pos","LID",null, null);
    MtasSpanQuery q3 = new MtasCQLParserWordQuery(field,"lemma","koe",null, null);
    MtasSpanQuery q4 = new MtasCQLParserWordQuery(field,"pos","N",null, null);
    MtasSpanQuery q5 = new MtasSpanAndQuery(new MtasSpanQuery[]{q1,q2});
    MtasSpanQuery q6 = new MtasSpanAndQuery(new MtasSpanQuery[]{q3,q4});
    MtasSpanQuery q = new MtasSpanOrQuery(new MtasSpanQuery[]{q5,q6});
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest9() throws ParseException {
    String field = "testveld";
    String cql = "[((lemma=\"de\"|lemma=\"het\") & pos=\"LID\") | (lemma=\"koe\" & pos=\"N\")]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"lemma","de",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"lemma","het",null, null);
    MtasSpanQuery q3 = new MtasCQLParserWordQuery(field,"pos","LID",null, null);
    MtasSpanQuery q4 = new MtasCQLParserWordQuery(field,"lemma","koe",null, null);
    MtasSpanQuery q5 = new MtasCQLParserWordQuery(field,"pos","N",null, null);
    MtasSpanQuery q6 = new MtasSpanOrQuery(new MtasSpanQuery[]{q1,q2});    
    MtasSpanQuery q7 = new MtasSpanAndQuery(new MtasSpanQuery[]{q6,q3});
    MtasSpanQuery q8 = new MtasSpanAndQuery(new MtasSpanQuery[]{q4,q5});
    MtasSpanQuery q = new MtasSpanOrQuery(new MtasSpanQuery[]{q7,q8});
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest10() throws ParseException {
    String field = "testveld";
    String cql = "[((lemma=\"de\"|lemma=\"het\") & pos=\"LID\") | ((lemma=\"koe\"|lemma=\"paard\") & pos=\"N\")]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"lemma","de",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"lemma","het",null, null);
    MtasSpanQuery q3 = new MtasCQLParserWordQuery(field,"pos","LID",null, null);
    MtasSpanQuery q4 = new MtasCQLParserWordQuery(field,"lemma","koe",null, null);
    MtasSpanQuery q5 = new MtasCQLParserWordQuery(field,"lemma","paard",null, null);
    MtasSpanQuery q6 = new MtasCQLParserWordQuery(field,"pos","N",null, null);
    MtasSpanQuery q7 = new MtasSpanOrQuery(new MtasSpanQuery[]{q1,q2});    
    MtasSpanQuery q8 = new MtasSpanAndQuery(new MtasSpanQuery[]{q7,q3});
    MtasSpanQuery q9 = new MtasSpanOrQuery(new MtasSpanQuery[]{q4,q5});    
    MtasSpanQuery q10 = new MtasSpanAndQuery(new MtasSpanQuery[]{q9,q6});
    MtasSpanQuery q = new MtasSpanOrQuery(new MtasSpanQuery[]{q8,q10});
    testCQLParse(field, null, cql, q);    
  }
  
  private void basicTest11() {
    String field = "testveld";
    String cql1 = "[#300]";
    MtasSpanQuery q1 = new MtasCQLParserWordPositionQuery(field, 300);
    testCQLParse(field, null, cql1, q1); 
    String cql2 = "[#100-110]";
    MtasSpanQuery q2 = new MtasCQLParserWordPositionQuery(field, 100, 110);
    testCQLParse(field, null, cql2, q2);
    String cql3 = "[#100-105 | #110]";
    MtasSpanQuery q3a = new MtasCQLParserWordPositionQuery(field, 100, 105);
    MtasSpanQuery q3b = new MtasCQLParserWordPositionQuery(field, 110);
    MtasSpanQuery q3 = new MtasSpanOrQuery(q3a, q3b);
    testCQLParse(field, null, cql3, q3);
  }  
  
  private void basicTest12() throws ParseException {
    String field = "testveld";
    String cql = "[(t_lc=\"de\"|t_lc=\"het\"|t_lc=\"paard\")]";
    MtasSpanQuery q1 = new MtasCQLParserWordQuery(field,"t_lc","de",null, null);
    MtasSpanQuery q2 = new MtasCQLParserWordQuery(field,"t_lc","het",null, null);
    MtasSpanQuery q3 = new MtasCQLParserWordQuery(field,"t_lc","paard",null, null);
    MtasSpanQuery q = new MtasSpanOrQuery(new MtasSpanQuery[]{q1,q2,q3});
    testCQLParse(field, null, cql, q);   
  }
  
  private void basicTest13() throws ParseException {
    String field = "testveld";
    String cql = "\"de\"";
    MtasSpanQuery q = new MtasCQLParserWordQuery(field,"t_lc","de",null, null);
    testCQLParse(field, "t_lc", cql, q);   
  }
}