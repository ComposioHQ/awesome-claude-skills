# XML Template Reference

## Document Structure

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<html xmlns="https://github.com/hongjinqiu/nanhu-print-java"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <style>
    <!-- CSS class definitions -->
  </style>
  <body>
    <!-- page layout -->
  </body>
</html>
```

## CSS Definitions (`<style>`)

Define reusable CSS classes:
```xml
<style>
  <css name="f12">
    <fontSize js="12px" pdf="js:12/1.3" />
  </css>
  <css name="fwb">
    <fontWeight js="bold" />
  </css>
  <css name="tc">
    <textAlign js="center" />
  </css>
  <css name="borderAll">
    <borderLeftStyle js="solid" /><borderLeftWidth js="1px" pdf="0.1" /><borderLeftColor js="black" />
    <borderTopStyle js="solid" /><borderTopWidth js="1px" pdf="0.1" /><borderTopColor js="black" />
    <borderRightStyle js="solid" /><borderRightWidth js="1px" pdf="0.1" /><borderRightColor js="black" />
    <borderBottomStyle js="solid" /><borderBottomWidth js="1px" pdf="0.1" /><borderBottomColor js="black" />
  </css>
</style>
```

Apply with `cls` attribute: `<div cls="f12 fwb">`.

## Body Layout

### Page size and margins

```xml
<body width="595px" height="842px" paddingLeft="30px" paddingRight="30px"
      paddingTop="20px" paddingBottom="20px">
```

Default is A4 (595×842 pt). Use `<params>` for advanced layout:

```xml
<body>
  <params>
    <param name="extendToFillBody" value="default" />
  </params>
  ...
</body>
```

`extendToFillBody` enables fixed header/footer across pages. **When using this param, `<tloop>` is mandatory** — see RULE 3 in the table section below.

## Static Tags

### `<div>`

Block container. Supports: `width`, `height`, `paddingLeft/Right/Top/Bottom`, `cls`, `backgroundColor`, `backgroundImage`, `backgroundSize`, `whiteSpace`, `scaleToFitContentByPdf`.

```xml
<div width="200px" paddingTop="10px" cls="f12">
  <span value="Hello" />
</div>
```

### `<span>`

Inline text. Key attributes:
- `value="literal text"` or `value="js:varName"` for dynamic values
- `format="num|unitPrice|amt"` for number formatting
- `cls`, `fontFamily`, `fontSize`, `fontWeight`, `color`

```xml
<span value="js:order.totalAmt" format="amt" />
```

### `<table>`, `<thead>`, `<tbody>`, `<tloop>`, `<tbottom>`, `<tr>`, `<td>`

`showPosition` values: `firstPage`, `everyPage`, `lastPage`.

#### RULE 1 — Column count must be consistent across all sections

Every `<tr>` in `<thead>`, `<tbody>`, `<tloop>`, `<tbottom>` must produce the same number of columns as the table. Use `colspan` to merge cells when a row needs fewer `<td>` elements.

Error you'll see if violated: `表格列数与 tr 底下的表格列数不匹配` or `ArrayIndexOutOfBoundsException`.

#### RULE 2 — Multi-column table: define widths in a hidden first row

When the table has multiple columns AND you need a `<thead showPosition="firstPage">` with a spanning header (e.g., company name), use this pattern:

```xml
<table>
  <!-- Step 1: define column widths in an invisible row (height="1px") -->
  <thead showPosition="firstPage">
    <tr>
      <td width="6%"  height="1px"></td>
      <td width="40%" height="1px"></td>
      <td width="12%" height="1px"></td>
      <td width="21%" height="1px"></td>
      <td width="21%" height="1px"></td>
    </tr>
    <!-- Step 2: spanning header rows using colspan -->
    <tr>
      <td colspan="5">
        <div cls="f18 fwb tc"><span value="js:invoice.companyName" /></div>
      </td>
    </tr>
    <tr>
      <td colspan="3"><div cls="f12"><span value="js:invoice.billTo" /></div></td>
      <td colspan="2"><div cls="f12 tr"><span value="js:invoice.date" /></div></td>
    </tr>
  </thead>

  <!-- Step 3: column header row (everyPage) -->
  <thead showPosition="everyPage">
    <tr>
      <td width="6%"  cls="fwb tc"><span value="No." /></td>
      <td width="40%" cls="fwb tc"><span value="Description" /></td>
      <td width="12%" cls="fwb tc"><span value="Qty" /></td>
      <td width="21%" cls="fwb tc"><span value="Unit Price" /></td>
      <td width="21%" cls="fwb tc"><span value="Amount" /></td>
    </tr>
  </thead>

  <tbody>
    <!-- data rows, 5 columns each -->
  </tbody>

  <!-- Step 4: tloop filler (REQUIRED when using extendToFillBody) -->
  <tloop>
    <tr><td colspan="5"><span value=" " /></td></tr>
  </tloop>

  <!-- Step 5: tbottom must also match column count -->
  <tbottom>
    <tr>
      <td colspan="3"><!-- left content --></td>
      <td cls="fwb tr"><span value="Total:" /></td>
      <td cls="tr"><span value="js:invoice.total" format="amt" /></td>
    </tr>
  </tbottom>
</table>
```

#### RULE 3 — `extendToFillBody` requires a non-empty `<tloop>`

When `<body>` has `<param name="extendToFillBody" value="default" />`, you MUST include `<tloop>` with at least one row that has non-empty content. An empty `<tloop>` causes:

```
NanhuprintException: tloop中的数据高度不能为0
```

Minimum valid tloop:
```xml
<tloop>
  <tr><td colspan="N"><span value=" " /></td></tr>
</tloop>
```

#### RULE 4 — Do NOT put a `<table>` directly inside `<thead>/<tr>`

Nesting a `<table>` directly inside a `<tr>` of the outer table causes:
```
NanhuprintException: tr 下的表格元素不匹配
```

Instead, put the nested `<table>` inside a `<td>`:
```xml
<!-- WRONG -->
<thead showPosition="firstPage">
  <tr>
    <table>...</table>   <!-- ERROR: table directly under tr -->
  </tr>
</thead>

<!-- CORRECT -->
<thead showPosition="firstPage">
  <tr>
    <td colspan="5">
      <table>...</table>  <!-- OK: table inside td -->
    </td>
  </tr>
</thead>
```

#### RULE 5 — colspan in `<tbottom>` must align precisely with column headers

When a `<tbottom>` row needs a cell to align with a specific column (e.g., a "Total Price" label under the "Price" column), count the colspan values carefully so the cell lands on exactly the right column. Using `colspan` to span extra columns will shift the cell right of the intended column.

Example — 6-column table where "This is total Price" must align with column 5 (index 4):

```xml
<!-- WRONG: colspan="2" shifts the label into columns 5+6 -->
<tr>
  <td colspan="4"></td>
  <td colspan="2"><span value="This is total Price" /></td>
</tr>

<!-- CORRECT: one td per column, label only in column 5 -->
<tr>
  <td colspan="4"></td>
  <td cls="borderAll"><span value="This is total Price" /></td>
  <td></td>
</tr>
```

#### RULE 6 — Apply border CSS only to cells that need it

`borderAll` (or any border CSS) applies only to the `<td>` it is set on. To have a row where only one cell has a border and the rest are borderless, simply omit the border class from the other cells.

```xml
<!-- Only the middle cell has a border; left and right cells are borderless -->
<tr>
  <td colspan="4" cls="pad"></td>
  <td cls="f9 fwb tc pad borderAll"><span value="This is total Price" /></td>
  <td cls="pad"></td>
</tr>
```

#### Simple single-column table (no pitfalls)

```xml
<table>
  <thead showPosition="firstPage">
    <tr><td width="100%"><span value="Title" /></td></tr>
  </thead>
  <thead showPosition="everyPage">
    <tr><td width="100%"><span value="Column Header" /></td></tr>
  </thead>
  <tbody>
    <tr><td width="100%"><span value="js:item" /></td></tr>
  </tbody>
  <tloop>
    <tr><td width="100%"><span value=" " /></td></tr>
  </tloop>
  <tbottom>
    <tr><td width="100%"><span value="Footer" /></td></tr>
  </tbottom>
</table>
```

## Dynamic Tags

### `<if>`

```xml
<if testJs="order.showRemark">
  <span value="js:order.remark" />
</if>
```

### `<forEach>`

```xml
<forEach var="item" itemsJs="order.itemList" varStatus="index">
  <tr>
    <td><span value="js:item.name" /></td>
    <td><span value="js:item.qty" format="num" /></td>
    <td><span value="js:item.price" format="unitPrice" /></td>
  </tr>
</forEach>
```

### `<set>`

```xml
<set var="bgColor" valueJs="index % 2 == 0 ? 'white' : '#f5f5f5'" />
<tr backgroundColor="js:bgColor">...</tr>
```

### `<macro>` and `<macroRef>`

Define reusable blocks:
```xml
<macro name="companyHeader">
  <div cls="f16 fwb tc"><span value="js:company.name" /></div>
</macro>

<!-- use it -->
<macroRef name="companyHeader" />
```

## Special Features

### Page numbers

```xml
<div>
  <params>
    <param name="customContent" value="com.hongjinqiu.nanhuprint.eval.custom.CustomPageNumber" />
    <param name="customContentFormat" value="{currentPageNumber} / {totalPageNumber}" />
  </params>
</div>
```

### Watermark (text)

```xml
<div>
  <params>
    <param name="waterMark" value="default" />
    <param name="waterMarkText" value="CONFIDENTIAL" />
    <param name="waterMarkOpacity" value="0.3" />
    <param name="waterMarkTextFontSize" value="36" />
    <param name="waterMarkRotation" value="45" />
    <param name="waterMarkLayer" value="under" />
  </params>
</div>
```

### Watermark (image)

```xml
<div>
  <params>
    <param name="waterMark" value="default" />
    <param name="waterMarkImage" value="http://host/logo.png" />
    <param name="waterMarkImageWidth" value="200" />
    <param name="waterMarkImageHeight" value="78" />
    <param name="waterMarkOpacity" value="0.5" />
    <param name="waterMarkRotation" value="45" />
    <param name="waterMarkLayer" value="default" />
  </params>
</div>
```

### Table border control on page breaks

```xml
<td>
  <params>
    <param name="firstLineOfTbodyCss" value="borderTopSolid" />
    <param name="lastLineofTbodyCss" value="borderBottomSolid" />
    <param name="firstLineOfPageCss" value="borderTopSolid" />
    <param name="lastLineOfPageCss" value="borderBottomSolid" />
  </params>
  <span value="js:item.name" />
</td>
```

### Scale content to fit cell

```xml
<div width="60px" scaleToFitContentByPdf="true">
  <span value="js:item.longText" />
</div>
```

### Dynamic cell width

```xml
<td>
  <params>
    <param name="calcWidth" value="com.hongjinqiu.nanhuprint.eval.custom.CalcWidth" />
    <param name="calcWidthTagId" value="myCell" />
  </params>
  <div id="myCell" whiteSpace="nowrap"><span value="js:item.label" /></div>
</td>
```

## Expression Syntax

All `js:` expressions use JavaScript syntax:
- `js:varName` — variable reference
- `js:obj.field` — object property
- `js:arr[0]` — array index
- `js:a + ' ' + b` — string concat
- `js:index % 2 == 0 ? 'white' : 'gray'` — ternary
- `js:item.price * item.qty` — arithmetic

## Lessons Learned

### LESSON 1 — Do NOT nest `<table>` inside `<thead>/<tr>` for company-info + logo layout

When the header has a two-column layout (e.g., company info on the left, logo on the right), the instinct is to put a nested `<table>` directly inside the `<thead><tr>`. This violates RULE 4 and causes a runtime error.

**Wrong approach (causes error):**
```xml
<thead showPosition="firstPage">
  <tr>
    <td colspan="6">
      <table>          <!-- nested table inside td is OK -->
        <thead showPosition="everyPage">   <!-- ERROR: inner thead repeats on every page -->
          ...
        </thead>
        <tbody>...</tbody>
      </table>
    </td>
  </tr>
</thead>
```

**Correct approach — use two `<td>` cells side by side in the outer `<tr>`:**
```xml
<thead showPosition="firstPage">
  <tr>
    <!-- invisible width-definition row first -->
    <td width="12%" height="1px"></td>
    ...
  </tr>
  <tr>
    <td colspan="3" cls="pad">
      <!-- company info stacked in divs -->
      <div cls="f12"><span value="js:header.name" /></div>
      <div cls="f12"><span value="js:header.address" /></div>
      <div cls="f12"><span value="js:header.phone" /></div>
    </td>
    <td colspan="3" cls="pad tr">
      <!-- logo as background image -->
      <div width="238px" height="72px">
        <css>
          <backgroundImage pdf="js:&quot;url('&quot; + header.logoUrl + &quot;')&quot;" />
          <backgroundSize js="contain" />
        </css>
      </div>
    </td>
  </tr>
</thead>
```

### LESSON 2 — italic currency prefix: use separate `<span>` with `cls="fi"`

In the HTML source, currency symbols like "SGB " are rendered in italic while the amount is normal weight. In the XML template, split them into two `<span>` elements:

```xml
<!-- WRONG: single span loses the italic on the currency prefix -->
<span value="js:'SGB ' + summary.subtotal" />

<!-- CORRECT: two spans, first one italic -->
<span value="js:summary.subtotalCurrency" cls="fi" />
<span value="js:summary.subtotal" />
```

And in the JSON data, store currency and amount separately:
```json
"summary": {
  "subtotalCurrency": "SGB ",
  "subtotal": "2.00",
  ...
}
```

### LESSON 3 — Read large HTML source files in chunks before writing the XML

When converting an existing HTML file to a nanhu-print-java XML template, the HTML can be 40–50 KB. The Read tool returns at most ~200 lines per call. **Read the entire HTML first (multiple Read calls with offset) before writing any XML.** Writing the XML before fully understanding the HTML structure leads to mistakes that require costly rewrites.

Recommended approach:
1. Read HTML lines 1–200
2. Read HTML lines 200–400
3. Read HTML lines 400–end
4. Only then start writing the XML template

### LESSON 4 — Write the complete XML in one Write call, not incremental Edits

When generating a new XML template file, write the entire file content in a single `Write` call. Using `Write` for the first part and then `Edit` to append the rest is error-prone: if the `old_string` in `Edit` contains trailing whitespace or newline differences, the match fails and you must rewrite the whole file anyway.

If the file exceeds 50 lines, split into: one `Write` for the first ~50 lines, then use `Edit` to replace the last line with the remaining content (ensuring the `old_string` is a unique, short anchor like the last line written).

### LESSON 5 — XSD allows only one `<thead>`/`<tbottom>` per `<table>`, but the runtime supports multiple

The XSD definition for `<table>` lists `<thead>`, `<tbody>`, `<tloop>`, `<tbottom>` without `maxOccurs="unbounded"`, which implies only one of each is allowed. **This is misleading.** The runtime actually supports multiple elements of the same type, each with a different `showPosition`:

```xml
<!-- Two <thead> elements: one for first page, one for every page -->
<thead showPosition="firstPage">...</thead>
<thead showPosition="everyPage">...</thead>

<!-- Two <tbottom> elements: one for last page, one for every page -->
<tbottom showPosition="lastPage">...</tbottom>
<tbottom showPosition="everyPage">...</tbottom>
```

**Rule of thumb: trust working test cases over the XSD.** The project's own test files (e.g., `twoPage/twoPage1.xml`, `fixedHeaderFooter3/fixedHeaderFooter3.xml`) are the authoritative source for what the runtime actually supports.
