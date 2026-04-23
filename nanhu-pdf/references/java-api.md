# Java API Reference

## Core Class: `NanhuprintInterpreter`

`com.hongjinqiu.nanhuprint.NanhuprintInterpreter`

All PDF generation goes through this class. It is stateless — create one instance and reuse it.

## Main Methods

### `interpreterString(String filePath, String metaString, Map<String, Object> env)`

Parse XML + data, write PDF to file.

```java
NanhuprintInterpreter interpreter = new NanhuprintInterpreter();
interpreter.interpreterString("/tmp/output.pdf", xmlString, env);
```

### `interpreterString(String metaString, Map<String, Object> env) → byte[]`

Parse XML + data, return PDF as byte array (useful for HTTP responses).

```java
byte[] pdfBytes = interpreter.interpreterString(xmlString, env);
response.setContentType("application/pdf");
response.getOutputStream().write(pdfBytes);
```

## Typical Usage Pattern

```java
import com.hongjinqiu.nanhuprint.NanhuprintInterpreter;
import net.sf.json.JSONObject;
import org.apache.commons.io.IOUtils;

// 1. Load XML template
String xmlTemplate = IOUtils.toString(
    getClass().getResourceAsStream("/templates/invoice.xml"), "UTF-8");

// 2. Build env from JSON business data
Map<String, Object> env = JSONObject.fromObject(jsonDataString);

// 3. Generate PDF
NanhuprintInterpreter interpreter = new NanhuprintInterpreter();
byte[] pdf = interpreter.interpreterString(xmlTemplate, env);
```

## Optional env Parameters

These keys in `env` control number formatting:

| Key | Default | Description |
|-----|---------|-------------|
| `amountPrecision` | `"2"` | Decimal places for `format="amt"` |
| `numberPrecision` | `"0"` | Decimal places for `format="num"` |
| `unitPricePrecision` | `"2"` | Decimal places for `format="unitPrice"` |

Example:
```java
env.put("amountPrecision", "2");
env.put("numberPrecision", "3");
```

## Spring Boot Integration

```java
@RestController
public class PdfController {

    @GetMapping(value = "/invoice/{id}", produces = "application/pdf")
    public ResponseEntity<byte[]> generateInvoice(@PathVariable String id) throws Exception {
        // Load template
        String xml = IOUtils.toString(
            getClass().getResourceAsStream("/templates/invoice.xml"), "UTF-8");

        // Build business data
        Map<String, Object> env = new HashMap<>();
        env.put("order", orderService.findById(id));

        // Generate
        NanhuprintInterpreter interpreter = new NanhuprintInterpreter();
        byte[] pdf = interpreter.interpreterString(xml, env);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentDispositionFormData("attachment", "invoice-" + id + ".pdf");
        return ResponseEntity.ok().headers(headers).body(pdf);
    }
}
```

## Lower-Level Methods

For advanced use cases where you need to separate dynamic-tag evaluation from PDF rendering:

```java
// Step 1: Evaluate dynamic tags (if/forEach/set) → resolved XML string
String resolvedXml = interpreter.unmarshallerAndRunDynamicElement(xmlTemplate, env);

// Step 2: Render resolved XML → PDF bytes
byte[] pdf = interpreter.unmarshallerAndRunToPdf(resolvedXml, env);
```

## Exception Handling

The framework throws `NanhuprintException` (unchecked) on errors. Wrap calls in try-catch for production:

```java
try {
    byte[] pdf = interpreter.interpreterString(xml, env);
} catch (NanhuprintException e) {
    log.error("PDF generation failed", e);
    throw new RuntimeException("PDF generation failed", e);
}
```

## Docker Demo (for testing)

```bash
docker pull hjq20021984/nanhu-print-java-demo:1.0.6
docker run -d -p 8891:8891 --name nanhu-demo hjq20021984/nanhu-print-java-demo:1.0.6
# Visit http://localhost:8891
```
