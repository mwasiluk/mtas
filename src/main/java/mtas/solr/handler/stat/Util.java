package mtas.solr.handler.stat;

public class Util {
   static public int safeParseInt(String c, int def) {
      if (c.equals("all"))
         return -1;
      else
         try {
            return Integer.parseInt(c);
         } catch (NumberFormatException e) {
            System.err.println("safeParseInt(): could not parse <"+c+">");
            return def;
         }
   }

   static public float safeParseFloat(String c) {
      try {
         return Float.parseFloat(c);
      } catch (NumberFormatException e) {
         System.err.println("safeParseFloat(): could not parse <"+c+">");
         return 0;
      }
   }
}
