package lager;

import java.util.*;

/** Kleiner JSON-Leser und -Schreiber, damit das Spiel ohne fremde Bibliothek auskommt. */
final class Json {
    private final String s;
    private int i;

    private Json(String s) { this.s = s; }

    static Object parse(String s) { return new Json(s).value(); }

    private void ws() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }

    private Object value() {
        ws();
        char c = s.charAt(i);
        if (c == '{') {
            Map<String, Object> m = new LinkedHashMap<>();
            i++; ws();
            if (s.charAt(i) == '}') { i++; return m; }
            while (true) {
                ws(); String k = string(); ws(); i++;
                m.put(k, value()); ws();
                if (s.charAt(i++) == '}') return m;
            }
        }
        if (c == '[') {
            List<Object> l = new ArrayList<>();
            i++; ws();
            if (s.charAt(i) == ']') { i++; return l; }
            while (true) {
                l.add(value()); ws();
                if (s.charAt(i++) == ']') return l;
            }
        }
        if (c == '"') return string();
        if (s.startsWith("true", i)) { i += 4; return Boolean.TRUE; }
        if (s.startsWith("false", i)) { i += 5; return Boolean.FALSE; }
        if (s.startsWith("null", i)) { i += 4; return null; }
        int a = i;
        while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
        return Double.valueOf(s.substring(a, i));
    }

    private String string() {
        StringBuilder sb = new StringBuilder();
        i++;
        while (s.charAt(i) != '"') {
            char c = s.charAt(i++);
            if (c != '\\') { sb.append(c); continue; }
            char e = s.charAt(i++);
            switch (e) {
                case 'n': sb.append('\n'); break;
                case 't': sb.append('\t'); break;
                case 'r': sb.append('\r'); break;
                case 'b': sb.append('\b'); break;
                case 'f': sb.append('\f'); break;
                case 'u': sb.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; break;
                default: sb.append(e);
            }
        }
        i++;
        return sb.toString();
    }

    static String str(Object o) { StringBuilder sb = new StringBuilder(); write(sb, o); return sb.toString(); }

    private static void write(StringBuilder sb, Object o) {
        if (o == null) sb.append("null");
        else if (o instanceof String) {
            sb.append('"');
            for (char c : ((String) o).toCharArray()) {
                if (c == '"' || c == '\\') sb.append('\\').append(c);
                else if (c == '\n') sb.append("\\n");
                else if (c < 32) sb.append(String.format("\\u%04x", (int) c));
                else sb.append(c);
            }
            sb.append('"');
        } else if (o instanceof Map) {
            sb.append('{'); boolean first = true;
            for (Map.Entry<?, ?> e : ((Map<?, ?>) o).entrySet()) {
                if (!first) sb.append(','); first = false;
                write(sb, String.valueOf(e.getKey())); sb.append(':'); write(sb, e.getValue());
            }
            sb.append('}');
        } else if (o instanceof Collection) {
            sb.append('['); boolean first = true;
            for (Object x : (Collection<?>) o) { if (!first) sb.append(','); first = false; write(sb, x); }
            sb.append(']');
        } else if (o instanceof int[]) {
            List<Object> l = new ArrayList<>(); for (int x : (int[]) o) l.add(x); write(sb, l);
        } else if (o instanceof Double && ((Double) o) == Math.rint((Double) o)) sb.append(((Double) o).longValue());
        else sb.append(o);
    }

    static int num(Object o) { return ((Number) o).intValue(); }

    @SuppressWarnings("unchecked") static Map<String, Object> map(Object o) { return o == null ? new LinkedHashMap<>() : (Map<String, Object>) o; }

    @SuppressWarnings("unchecked") static List<Object> list(Object o) { return o == null ? new ArrayList<>() : (List<Object>) o; }

    static int[] ints(Object o) { List<Object> l = list(o); int[] r = new int[l.size()]; for (int k = 0; k < r.length; k++) r[k] = num(l.get(k)); return r; }
}
