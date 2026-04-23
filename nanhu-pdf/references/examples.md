# nanhu-print-java XML Template Examples

Real working examples from the project test suite. Each example is verified to produce a valid PDF.

---

## Example 1 — Basic multi-page document (twoPage1)

Demonstrates: `thead` firstPage + everyPage, `tbody` forEach, `tloop`, `tbottom` lastPage + everyPage with page numbers.

**XML**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<html xmlns="https://github.com/hongjinqiu/nanhu-print-java"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <style></style>
  <macros></macros>
  <body pageSizePdf="A4" rotate="false" paddingLeft="50px"
        paddingRight="50px" paddingTop="30px" paddingBottom="30px"
        width="685px" height="840px">
    <params>
      <param name="extendToFillBody" value="default" />
    </params>
    <table cellspacing="0" cellpadding="0" width="100%" tableLayout="fixed">
      <thead>
        <tr>
          <td width="100%">
            <span value="show only on first page, name is:" />
            <span value="js:data.firstPage" />
          </td>
        </tr>
      </thead>
      <thead showPosition="everyPage">
        <tr>
          <td width="100%">
            <span value="show on every page, name is:" />
            <span value="js:data.everyPage" />
          </td>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td width="100%">
            <div fontSize="20" textAlign="center">
              <span value="I am tbody"/>
            </div>
          </td>
        </tr>
        <forEach var="item" itemsJs="data.contentList" varStatus="index">
          <tr>
            <td width="100%">
              <div paddingTop="20">
                <span value="js:item"/>
              </div>
            </td>
          </tr>
        </forEach>
      </tbody>
      <tloop>
        <tr>
          <td width="100%">
            <span value="1" visibility="hidden"/>
            <span value=" "/>
          </td>
        </tr>
      </tloop>
      <tbottom>
        <tr>
          <td textAlign="center">
            <span value="I am lastPage, value is:"/>
            <span value="js:data.lastPageTbottom"/>
          </td>
        </tr>
      </tbottom>
      <tbottom showPosition="everyPage">
        <tr>
          <td textAlign="center">
            <div>
              <params>
                <param name="customContent" value="com.hongjinqiu.nanhuprint.eval.custom.CustomPageNumber" />
                <param name="customContentFormat" value="{currentPageNumber} /of/ {totalPageNumber}" />
              </params>
            </div>
          </td>
        </tr>
      </tbottom>
    </table>
  </body>
</html>
```

**JSON**
```json
{
  "data": {
    "firstPage": "this is firstPage",
    "everyPage": "this is everyPage",
    "lastPageTbottom": "this is lastPage tbottom",
    "contentList": ["content1", "content2", "content3"]
  }
}
```

---

## Example 2 — Watermark (text + image)

Demonstrates: body-level text watermark, tbottom-level image watermark, `waterMarkLayer`, `waterMarkOpacity`, `waterMarkRotation`.

**XML**
```xml
<body pageSizePdf="A4" rotate="false" paddingLeft="50px"
      paddingRight="50px" paddingTop="30px" paddingBottom="30px"
      width="685px" height="840px">
  <params>
    <param name="waterMark" value="default" />
    <param name="waterMarkText" value="I am water mark text" />
    <param name="waterMarkOpacity" value="1" />
    <param name="waterMarkTextFontSize" value="14" />
    <param name="waterMarkOffsetX" value="0" />
    <param name="waterMarkOffsetY" value="0" />
    <param name="waterMarkRotation" value="45" />
    <param name="waterMarkLayer" value="under" />
  </params>
  <table cellspacing="0" cellpadding="0" width="100%" tableLayout="fixed">
    <!-- ... thead / tbody / tloop ... -->
    <tbottom>
      <tr>
        <td>
          <params>
            <param name="waterMark" value="default" />
            <param name="waterMarkOpacity" value="0.9" />
            <param name="waterMarkImage" value="https://example.com/logo.png" />
            <param name="waterMarkImageWidth" value="200" />
            <param name="waterMarkImageHeight" value="200" />
            <param name="waterMarkRotation" value="45" />
            <param name="waterMarkLayer" value="under" />
          </params>
          <span value="js:data.lastPageTbottom" />
        </td>
      </tr>
    </tbottom>
  </table>
</body>
```

---

## Example 3 — Alternating row colors with tloop mode="two"

Demonstrates: `<set>` + `<if>` for conditional background, `<tloop mode="two">` for two alternating filler rows.

**XML**
```xml
<body pageSizePdf="A4" rotate="false" paddingLeft="50px"
      paddingRight="50px" paddingTop="30px" paddingBottom="30px"
      width="685px" height="840px">
  <params>
    <param name="extendToFillBody" value="default" />
  </params>
  <table cellspacing="0" cellpadding="0" width="100%" tableLayout="fixed">
    <thead>
      <tr>
        <td width="100%">
          <span value="js:data.firstPage" />
        </td>
      </tr>
    </thead>
    <tbody>
      <forEach var="item" itemsJs="data.contentList" varStatus="index">
        <set valueJs="'white'" var="loopBgColor" />
        <if testJs="index % 2 == 0">
          <set valueJs="'orange'" var="loopBgColor" />
        </if>
        <tr backgroundColor="js:loopBgColor">
          <td width="100%">
            <div paddingTop="20">
              <span value="js:item"/>
            </div>
          </td>
        </tr>
      </forEach>
    </tbody>
    <tloop mode="two">
      <tr>
        <td width="100%" backgroundColor="black">
          <span value="1" visibility="hidden"/>
          <span value=" "/>
        </td>
      </tr>
      <tr>
        <td width="100%">
          <span value="1" visibility="hidden"/>
          <span value=" "/>
        </td>
      </tr>
    </tloop>
  </table>
</body>
```

---

## Example 4 — Dynamic border on page breaks (stackoverflow_2)

Demonstrates: `firstLineOfTbodyCss`, `lastLineofTbodyCss`, `firstLineOfPageCss`, `lastLineOfPageCss` params on `<td>` for smart border rendering across page breaks.

**XML**
```xml
<style>
  <css name="borderTopSolid">
    <borderTopStyle js="solid"/>
    <borderTopWidth js="1px" pdf="0.1"/>
    <borderTopColor js="black"/>
  </css>
  <css name="borderBottomSolid">
    <borderBottomStyle js="solid"/>
    <borderBottomWidth js="1px" pdf="0.1"/>
    <borderBottomColor js="black"/>
  </css>
  <css name="borderLeftSolid">
    <borderLeftStyle js="solid"/>
    <borderLeftWidth js="1px" pdf="0.1"/>
    <borderLeftColor js="black"/>
  </css>
  <css name="borderRightSolid">
    <borderRightStyle js="solid"/>
    <borderRightWidth js="1px" pdf="0.1"/>
    <borderRightColor js="black"/>
  </css>
  <css name="paddingAll">
    <paddingTop pdf="8" />
    <paddingBottom pdf="8" />
  </css>
</style>

<!-- In tbody forEach: -->
<forEach var="item" itemsJs="order.itemLi" varStatus="index">
  <tr>
    <td cls="borderLeftSolid textAlignCenter paddingAll">
      <params>
        <param name="firstLineOfTbodyCss" value="borderLeftSolid borderTopSolid textAlignCenter paddingAll" />
        <param name="lastLineofTbodyCss"  value="borderLeftSolid borderBottomSolid textAlignCenter paddingAll" />
        <param name="firstLineOfPageCss"  value="borderLeftSolid borderTopSolid textAlignCenter paddingAll" />
        <param name="lastLineOfPageCss"   value="borderLeftSolid borderBottomSolid textAlignCenter paddingAll" />
      </params>
      <span value="js:item.item" />
    </td>
    <!-- repeat params pattern for each td -->
    <td cls="borderRightSolid textAlignCenter paddingAll">
      <params>
        <param name="firstLineOfTbodyCss" value="borderRightSolid borderTopSolid textAlignCenter paddingAll" />
        <param name="lastLineofTbodyCss"  value="borderRightSolid borderBottomSolid textAlignCenter paddingAll" />
        <param name="firstLineOfPageCss"  value="borderRightSolid borderTopSolid textAlignCenter paddingAll" />
        <param name="lastLineOfPageCss"   value="borderRightSolid borderBottomSolid textAlignCenter paddingAll" />
      </params>
      <span value="js:item.summa" />
    </td>
  </tr>
</forEach>
```

**JSON**
```json
{
  "order": {
    "itemLi": [
      { "item": "Apple",  "quantity": 2, "price": "1.00", "summa": "2.00" },
      { "item": "Banana", "quantity": 5, "price": "0.50", "summa": "2.50" }
    ]
  }
}
```

---

## Example 5 — Multi-column invoice with everyPage header (stackoverflow_1)

Demonstrates: 7-column table, `showPosition="everyPage"` thead with company name + Bill To / Ship To + invoice metadata, nested tables inside `<td>`, `tloop` with partial borders, `tbottom` lastPage + everyPage page numbers.

**Key pattern — width-definition row + spanning header rows:**
```xml
<thead showPosition="everyPage">
  <!-- Row 1: invisible width-definition row -->
  <tr>
    <td width="14%" height="1px"></td>
    <td width="14%" height="1px"></td>
    <td width=""    height="1px"></td>
    <td width="14%" height="1px"></td>
    <td width="14%" height="1px"></td>
    <td width="14%" height="1px"></td>
    <td width="14%" height="1px"></td>
  </tr>
  <!-- Row 2: company name spanning all 7 columns -->
  <tr>
    <td colspan="7">
      <div cls="lineHeightAll">
        <span value="Acme Paper Co LLC" cls="title0" />
      </div>
    </td>
  </tr>
  <!-- Row 3: Bill To (left) + Invoice metadata (right) -->
  <tr>
    <td colspan="3">
      <!-- nested table for Bill To / Ship To -->
    </td>
    <td colspan="4">
      <!-- nested table for Invoice Number, Date, Due Date, Tax Id -->
    </td>
  </tr>
  <!-- Row 4: column headers -->
  <tr>
    <td cls="borderAll fontWeightBold textAlignCenter paddingAll"><span value="Quantity" /></td>
    <td cls="borderAll fontWeightBold textAlignCenter paddingAll"><span value="Code" /></td>
    <td cls="borderAll fontWeightBold textAlignCenter paddingAll"><span value="Description" /></td>
    <td cls="borderAll fontWeightBold textAlignCenter paddingAll"><span value="Unit Price" /></td>
    <td cls="borderAll fontWeightBold textAlignCenter paddingAll"><span value="Tax1" /></td>
    <td cls="borderAll fontWeightBold textAlignCenter paddingAll"><span value="Tax2" /></td>
    <td cls="borderAll fontWeightBold textAlignCenter paddingAll"><span value="Line Total" /></td>
  </tr>
</thead>
```

**tloop with partial left/right borders only (no top/bottom):**
```xml
<tloop>
  <tr>
    <td cls="borderLeftSolid"><span value=" " /></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td cls="borderRightSolid"></td>
  </tr>
</tloop>
```

---

## Example 6 — Dynamic row count with JavaScript array expression

Demonstrates: generating rows from a JS inline array (no JSON data needed), `Array.apply` pattern.

```xml
<tbody>
  <forEach var="i"
           itemsJs="Array.apply(null, {length: 50}).map(function(_, i) { return i + 1; })"
           varStatus="index">
    <tr>
      <td width="50%" cls="border1px tdPadding">
        <span value="js:'Row ' + i + ' - Data 1'" />
      </td>
      <td width="50%" cls="border1px tdPadding">
        <span value="js:'Row ' + i + ' - Data 2'" />
      </td>
    </tr>
  </forEach>
</tbody>
```

---

## Example 7 — Background image on body + `<div>` + `scaleToFitContentByPdf`

Demonstrates: body-level background image with opacity, element-level background image, `scaleToFitContentByPdf` to shrink overflowing content.

```xml
<!-- Body-level background image -->
<body ...>
  <css>
    <backgroundImage pdf="url('http://example.com/bg.jpg')" />
    <backgroundSize js="50%" />
    <backgroundPositionX js="center" />
    <backgroundPositionY js="center" />
    <backgroundImageOpacityByPdf js="0.3" />
  </css>
  ...
</body>

<!-- Element-level background image on a div -->
<div width="100px" height="100px">
  <css>
    <backgroundImage pdf="url('http://example.com/logo.jpg')" />
    <backgroundSize js="50%" />
    <backgroundPositionX js="left" />
    <backgroundPositionY js="25%" />
  </css>
</div>

<!-- Scale content to fit cell width -->
<div cls="f13" scaleToFitContentByPdf="true">
  <span value="RMB" />
  <span value="js:bodyVo.originAmtWithouDiscount" />
</div>
```

---

## Example 8 — Macro with parameter

Demonstrates: `<macro name="..." paramJs="obj">` definition and `<macroRef name="..." paramJs="macroObj" />` usage.

```xml
<macros>
  <macro name="personTable" paramJs="obj">
    <table width="100%" cellspacing="0" cellpadding="">
      <if testJs="2+3">
        <tbody>
          <tr>
            <td cls="border1px"><span value="Name" /></td>
            <td cls="border1px"><span value="Age" /></td>
          </tr>
          <tr>
            <td cls="border1px"><span value="js:obj.name" /></td>
            <td cls="border1px"><span value="js:obj.age" format="num" /></td>
          </tr>
          <forEach var="item" itemsJs="obj.loopLi" varStatus="index">
            <tr>
              <td cls="border1px"><span value="js:item.name" /></td>
              <td cls="border1px"><span value="js:item.age" /></td>
            </tr>
          </forEach>
        </tbody>
      </if>
    </table>
  </macro>
</macros>

<!-- Usage: pass data object via paramJs -->
<macroRef name="personTable" paramJs="macroObj" />
```

---

## Example 9 — Dynamic colspan with `<set>` variable

Demonstrates: storing a number in a variable and using it as `colspan`.

```xml
<set var="colspanCount" valueJs="4" />

<!-- Later in the table: -->
<td colspan="js:colspanCount">
  ...
</td>

<!-- Or arithmetic: -->
<td colspan="js:colspanCount - 1">
  ...
</td>
```

---

## Example 10 — `calcWidth` for auto-sized label column

Demonstrates: `calcWidth` custom param to make a `<td>` auto-size to its content width (useful for "ISSUED BY:" label + underline signature line).

```xml
<table cellspacing="0" cellpadding="0" tableLayout="auto">
  <tbody>
    <tr>
      <td textAlign="left">
        <params>
          <param name="calcWidth" value="com.hongjinqiu.nanhuprint.eval.custom.CalcWidth" />
          <param name="calcWidthTagId" value="leftIssueBy" />
        </params>
        <div id="leftIssueBy" whiteSpace="nowrap" paddingRight="5px">
          <span value="ISSUED BY:" />
        </div>
      </td>
      <td>
        <css>
          <width pdf="150px" />
        </css>
        <div width="150px"
             borderBottomStyle="solid" borderBottomColor="black" borderBottomWidth="1px">
          <span value=" " color="white" />
        </div>
      </td>
    </tr>
  </tbody>
</table>
```

---

## Example 11 — `tloop countJs` to fill exactly N rows

Demonstrates: `<tloop countJs="20">` to always fill 20 filler rows regardless of data count (useful for fixed-height invoice forms).

```xml
<tloop countJs="20">
  <tr>
    <td cls="borderLeft borderRight tc tdPadding bodyLineHeight">
      <span value=" " />
    </td>
    <td cls="borderRight tdPadding"></td>
    <td cls="borderRight tc tdPadding"></td>
    <td cls="borderRight tc tdPadding"></td>
  </tr>
</tloop>
```

---

## Example 12 — `minHeight` / `maxHeight` / `height` on `<td>`

Demonstrates: controlling cell height constraints.

```xml
<!-- minHeight: cell grows to at least this height -->
<td minHeight="20px">...</td>

<!-- maxHeight: cell is capped at this height (content may be clipped) -->
<td maxHeight="180px">...</td>

<!-- height: fixed height (overrides content) -->
<td height="30px">...</td>

<!-- Combined: min 20px, max 40px -->
<td minHeight="20px" maxHeight="40px">...</td>
```

---

## Example 13 — `rowspan` in nested table

Demonstrates: `rowspan` attribute on `<td>` inside a nested table.

```xml
<table cellspacing="0" cellpadding="0" tableLayout="fixed">
  <tbody>
    <tr>
      <td width="20px">
        <div width="20px" height="20px" borderLeftWidth="0.1px" borderTopWidth="0.1px"></div>
      </td>
      <td width="300px" rowspan="2">
        <forEach var="item" itemsJs="[1,2,3]" varStatus="index">
          <div><span value="js:'line_' + index" /></div>
        </forEach>
      </td>
      <td width="20px">
        <div width="20px" height="20px" borderRightWidth="0.1px" borderTopWidth="0.1px"></div>
      </td>
    </tr>
    <tr>
      <td verticalAlign="bottom">
        <div width="20px" height="20px" borderLeftWidth="0.1px" borderBottomWidth="0.1px"></div>
      </td>
      <td verticalAlign="bottom">
        <div width="20px" height="20px" borderRightWidth="0.1px" borderBottomWidth="0.1px"></div>
      </td>
    </tr>
  </tbody>
</table>
```

---

## Example 14 — `floatAlign="right"` for right-aligned nested table

Demonstrates: `floatAlign="right"` on a nested table to push it to the right side of its container.

```xml
<td textAlign="right">
  <table cellspacing="0" cellpadding="0" tableLayout="fixed" floatAlign="right">
    <tbody>
      <tr>
        <td width="50px" textAlign="right">
          <div whiteSpace="nowrap">
            <span value="ISSUED BY:" />
          </div>
        </td>
        <td width="150px">
          <div width="150px"
               borderBottomStyle="solid" borderBottomColor="black" borderBottomWidth="1px">
            <span value=" " color="white" />
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</td>
```

---

## Example 15 — `explain="true"` for debug layout

Demonstrates: `explain="true"` on a `<div>` or `<td>` to render a visible debug border around the element (useful during development).

```xml
<div fontFamily="arial" explain="true">
  <span value="this text has a debug border" />
</div>

<td cls="borderLeftSolid" explain="true">
  <span value="js:item.item" />
</td>
```

---

## CSS Quick Reference

All CSS properties used across the test suite:

```xml
<style>
  <!-- Font -->
  <css name="f12"><fontSize js="12px" pdf="js:12/1.3" /></css>
  <css name="f13"><fontSize js="13px" pdf="js:13/1.3" /></css>
  <css name="f16"><fontSize js="16px" pdf="js:16/1.3" /></css>
  <css name="f24"><fontSize js="24px" pdf="js:24/1.3" /></css>
  <css name="f32"><fontSize js="32px" pdf="js:32/1.3" /></css>
  <css name="fwb"><fontWeight js="bold" /></css>
  <css name="fi"><fontStyle js="italic" /></css>

  <!-- Text alignment -->
  <css name="tc"><textAlign js="center" /></css>
  <css name="tr"><textAlign js="right" /></css>
  <css name="tl"><textAlign js="left" /></css>

  <!-- Word wrap -->
  <css name="breakWord">
    <whiteSpace js="pre-wrap" />
    <wordWrap js="break-word" />
  </css>

  <!-- Borders — full -->
  <css name="borderAll">
    <borderLeftStyle js="solid" /><borderLeftWidth js="1px" pdf="0.1" /><borderLeftColor js="black" />
    <borderTopStyle js="solid" /><borderTopWidth js="1px" pdf="0.1" /><borderTopColor js="black" />
    <borderRightStyle js="solid" /><borderRightWidth js="1px" pdf="0.1" /><borderRightColor js="black" />
    <borderBottomStyle js="solid" /><borderBottomWidth js="1px" pdf="0.1" /><borderBottomColor js="black" />
  </css>

  <!-- Borders — individual sides -->
  <css name="borderTopSolid">
    <borderTopStyle js="solid" /><borderTopWidth js="1px" pdf="0.1" /><borderTopColor js="black" />
  </css>
  <css name="borderBottomSolid">
    <borderBottomStyle js="solid" /><borderBottomWidth js="1px" pdf="0.1" /><borderBottomColor js="black" />
  </css>
  <css name="borderLeftSolid">
    <borderLeftStyle js="solid" /><borderLeftWidth js="1px" pdf="0.1" /><borderLeftColor js="black" />
  </css>
  <css name="borderRightSolid">
    <borderRightStyle js="solid" /><borderRightWidth js="1px" pdf="0.1" /><borderRightColor js="black" />
  </css>

  <!-- Padding -->
  <css name="tdPadding">
    <paddingLeft js="8px" /><paddingRight js="8px" />
    <paddingTop js="2px" /><paddingBottom js="2px" />
  </css>
  <css name="paddingAll">
    <paddingTop pdf="8" /><paddingBottom pdf="8" />
  </css>

  <!-- Line height -->
  <css name="lineHeightAll"><lineHeight pdf="30" /></css>
</style>
```
