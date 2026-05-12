---
name: nanhu-pdf
description: Generate PDF files using the nanhu-print-java framework. Use this skill when the user wants to create PDF documents with nanhu-print-java, including writing XML templates, preparing JSON business data, calling the Java API (NanhuprintInterpreter), or integrating nanhu-print-java into a Spring Boot service. Triggers on requests like "generate a PDF with nanhu-print-java", "write an XML template for nanhu-print-java", "how do I call NanhuprintInterpreter", or "create a PDF invoice/report using nanhu-print-java".
---

# nanhu-pdf Skill

nanhu-print-java is an XML-to-PDF generation framework for Java. Users write an XML template + prepare JSON business data, then call `NanhuprintInterpreter` to produce a PDF.

Maven dependency:
```xml
<dependency>
    <groupId>io.github.hongjinqiu</groupId>
    <artifactId>nanhu-print-java</artifactId>
    <version>1.0.6</version>
</dependency>
```

## Workflow

1. Write an XML template (see `references/xml-template.md`)
2. Prepare JSON business data
3. Call the Java API (see `references/java-api.md`)

## Quick Example

**hello_world.xml**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<html xmlns="https://github.com/hongjinqiu/nanhu-print-java"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <body>
    <div>
      <span value="js:businessData" />
    </div>
  </body>
</html>
```

**hello_world.json**
```json
{ "businessData": "Hello, nanhu-print-java!" }
```

**Java call**
```java
NanhuprintInterpreter interpreter = new NanhuprintInterpreter();
String xml = /* read hello_world.xml as String */;
Map<String, Object> env = JSONObject.fromObject(/* read hello_world.json */);
// Save to file:
interpreter.interpreterString("output.pdf", xml, env);
// Or get bytes:
byte[] pdfBytes = interpreter.interpreterString(xml, env);
```

## Reference Files

- **XML template syntax, tags, CSS, dynamic tags**: See `references/xml-template.md`
- **Java API methods and integration patterns**: See `references/java-api.md`

## XSD Constraint

All XML templates must conform to the official XSD schema:

- Skill local copy: `references/nanhuprint.xsd`
- GitHub: https://github.com/hongjinqiu/nanhu-print-java/blob/main/src/main/resources/xsd/nanhuprint.xsd

**Before writing or reviewing any XML template, read the XSD to verify allowed elements, attributes, and nesting rules.** The XSD is the authoritative source of truth — it overrides any assumptions based on examples alone.
