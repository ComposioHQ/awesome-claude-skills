# Graph Report - /Users/kevinliu/awesome-claude-skills  (2026-04-16)

## Corpus Check
- 63 files · ~503,523 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 718 nodes · 1238 edges · 39 communities detected
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 346 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]

## God Nodes (most connected - your core abstractions)
1. `DOCXSchemaValidator` - 61 edges
2. `XMLEditor` - 59 edges
3. `RedliningValidator` - 58 edges
4. `BaseSchemaValidator` - 41 edges
5. `GIFBuilder` - 41 edges
6. `Document` - 32 edges
7. `create_blank_frame()` - 22 edges
8. `convert()` - 21 edges
9. `DocxXMLEditor` - 20 edges
10. `interpolate()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `Apply kaleidoscope effect by mirroring/rotating frame sections.      Args:` --uses--> `GIFBuilder`  [INFERRED]
  /Users/kevinliu/awesome-claude-skills/slack-gif-creator/templates/kaleidoscope.py → /Users/kevinliu/awesome-claude-skills/slack-gif-creator/core/gif_builder.py
- `Apply simple mirror effect (faster than full kaleidoscope).      Args:         f` --uses--> `GIFBuilder`  [INFERRED]
  /Users/kevinliu/awesome-claude-skills/slack-gif-creator/templates/kaleidoscope.py → /Users/kevinliu/awesome-claude-skills/slack-gif-creator/core/gif_builder.py
- `Create animated kaleidoscope effect.      Args:         base_frame: Frame to app` --uses--> `GIFBuilder`  [INFERRED]
  /Users/kevinliu/awesome-claude-skills/slack-gif-creator/templates/kaleidoscope.py → /Users/kevinliu/awesome-claude-skills/slack-gif-creator/core/gif_builder.py
- `draw_text_in_box()` --calls--> `convert()`  [INFERRED]
  /Users/kevinliu/awesome-claude-skills/slack-gif-creator/core/typography.py → /Users/kevinliu/awesome-claude-skills/document-skills/pdf/scripts/convert_pdf_to_images.py
- `create_impact_flash()` --calls--> `convert()`  [INFERRED]
  /Users/kevinliu/awesome-claude-skills/slack-gif-creator/core/visual_effects.py → /Users/kevinliu/awesome-claude-skills/document-skills/pdf/scripts/convert_pdf_to_images.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (62): Document, DocxXMLEditor, _generate_hex_id(), _generate_rsid(), Add a single comment to comments.xml., Ensure w14 namespace is declared on the root element., Add a single comment to commentsExtended.xml., Add a single comment to commentsIds.xml. (+54 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (87): create_bounce_animation(), Create frames for a bouncing animation.      Args:         object_type: 'circle', convert(), create_validation_image(), interpolate(), Interpolate between two values with easing.      Args:         start: Start valu, create_explode_animation(), Create explosion animation.      Args:         object_type: 'emoji', 'circle', ' (+79 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (41): BaseSchemaValidator, Base validator with common validation logic for document files., Base validator with common validation logic for document files., Run all validation checks and return True if all pass., Validate that all XML files are well-formed., Validate that namespace prefixes in Ignorable attributes are declared., Validate that specific IDs are unique according to OOXML requirements., Validate that all .rels files properly reference files and that all files are re (+33 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (41): calculate_overlap(), collect_shapes_with_absolute_positions(), detect_overlaps(), emu_to_inches(), extract_text_inventory(), get_default_font_size(), get_font_path(), get_inventory_as_dict() (+33 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (35): ABC, create_connection(), MCPConnection, MCPConnectionHTTP, MCPConnectionSSE, MCPConnectionStdio, Lightweight connection handling for MCP servers., MCP connection using Streamable HTTP. (+27 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (36): create_particle_burst(), Create simple particle burst effect.      Args:         num_frames: Number of fr, add_drop_shadow(), add_glow_effect(), add_motion_blur(), apply_screen_shake(), create_explosion_effect(), create_impact_flash() (+28 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (33): apply_squash_stretch(), calculate_arc_motion(), ease_back_in(), ease_back_in_out(), ease_back_out(), ease_in_bounce(), ease_in_cubic(), ease_in_elastic() (+25 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (14): get_bounding_box_messages(), RectAndField, Test that entry box height is checked against font size, Helper to create a JSON stream from data, Test that adequate entry box height passes, Test that default font size is used when not specified, Test case with no bounding box intersections, Test that missing entry_text doesn't cause height check (+6 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (24): blend_colors(), create_gradient_colors(), darken_color(), get_complementary_color(), get_emoji_palette(), get_impact_color(), get_palette(), get_text_color_for_background() (+16 more)

### Community 9 - "Community 9"
Cohesion: 0.1
Nodes (20): add_vignette(), composite_layers(), create_gradient_background(), draw_circle_with_shadow(), draw_line(), draw_rectangle(), draw_rounded_rectangle(), draw_star() (+12 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (17): Clear all frames (useful for creating multiple GIFs)., apply_font_properties(), apply_paragraph_properties(), apply_replacements(), check_duplicate_keys(), clear_paragraph_bullets(), detect_frame_overflow(), main() (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.16
Nodes (16): draw_text_in_box(), draw_text_with_glow(), draw_text_with_outline(), draw_text_with_shadow(), get_font(), get_optimal_font_size(), get_text_size(), Draw text with drop shadow for depth.      Args:         frame: PIL Image to dra (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.27
Nodes (10): check_slack_size(), get_optimization_suggestions(), is_slack_ready(), Check if GIF meets Slack size limits.      Args:         gif_path: Path to GIF f, Run all validations on a GIF file.      Args:         gif_path: Path to GIF file, Get suggestions for optimizing a GIF based on validation results.      Args:, Quick check if GIF is ready for Slack.      Args:         gif_path: Path to GIF, Check if dimensions are suitable for Slack.      Args:         width: Frame widt (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.2
Nodes (5): Generate detailed word-level differences using git word diff., Generate word diff using git with character-level precision., Remove tracked changes authored by Claude from the XML root., Main validation method that returns True if valid, False otherwise., Extract text content from Word XML, preserving paragraph structure.          Emp

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (9): delete_slide(), duplicate_slide(), main(), Delete a slide from the presentation., Move a slide from one position to another., Create a new presentation with slides from template in specified order.      Arg, Duplicate a slide in the presentation., rearrange_presentation() (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.2
Nodes (5): Replace a DOM element with new XML content.          Args:             elem: def, Insert XML content after a DOM element.          Args:             elem: defused, Insert XML content before a DOM element.          Args:             elem: defuse, Append XML content as a child of a DOM element.          Args:             elem:, Parse XML fragment and return list of imported nodes.          Args:

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (6): get_field_info(), get_full_annotation_field_id(), make_field_dict(), write_field_info(), fill_pdf_fields(), validation_error_for_field_value()

### Community 17 - "Community 17"
Cohesion: 0.39
Nodes (7): condense_xml(), main(), pack_document(), Strip unnecessary whitespace and remove comments., Pack a directory into an Office file (.docx/.pptx/.xlsx).      Args:         inp, Validate document by converting to HTML with soffice., validate_document()

### Community 18 - "Community 18"
Cohesion: 0.46
Nodes (7): addBackground(), addElements(), extractSlideData(), getBodyDimensions(), html2pptx(), validateDimensions(), validateTextBoxPosition()

### Community 19 - "Community 19"
Cohesion: 0.36
Nodes (7): check_yt_dlp(), download_video(), get_video_info(), main(), Check if yt-dlp is installed, install if not., Get information about the video without downloading., Download a YouTube video.          Args:         url: YouTube video URL

### Community 20 - "Community 20"
Cohesion: 0.38
Nodes (6): init_skill(), main(), # TODO: Add actual script logic here, Convert hyphenated skill name to Title Case for display., Initialize a new skill directory with template SKILL.md.      Args:         skil, title_case_skill_name()

### Community 21 - "Community 21"
Cohesion: 0.33
Nodes (5): main(), package_skill(), Package a skill folder into a zip file.      Args:         skill_path: Path to t, Basic validation of a skill, validate_skill()

### Community 22 - "Community 22"
Cohesion: 0.47
Nodes (5): main(), Setup LibreOffice macro for recalculation if not already configured, Recalculate formulas in Excel file and report any errors          Args:, recalc(), setup_libreoffice_macro()

### Community 23 - "Community 23"
Cohesion: 0.5
Nodes (4): fill_pdf_form(), Transform bounding box from image coordinates to PDF coordinates, Fill the PDF form with data from fields.json, transform_coordinates()

### Community 24 - "Community 24"
Cohesion: 0.67
Nodes (1): main()

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Convert EMUs (English Metric Units) to inches.

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Convert inches to pixels at given DPI.

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Get the font file path for a given font name.          Args:             font_na

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Get slide dimensions from slide object.          Args:             slide: Slide

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Calculate paragraphs from the shape's text frame.

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Check if shape has any issues (overflow, overlap, or warnings).

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Create the connection context based on connection type.

## Knowledge Gaps
- **212 isolated node(s):** `Setup LibreOffice macro for recalculation if not already configured`, `Recalculate formulas in Excel file and report any errors          Args:`, `Helper to create a JSON stream from data`, `Test case with no bounding box intersections`, `Test intersection between label and entry of the same field` (+207 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 25`** (2 nodes): `handle_console_message()`, `console_logging.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `check_fillable_fields.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `unpack.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Convert EMUs (English Metric Units) to inches.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Convert inches to pixels at given DPI.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Get the font file path for a given font name.          Args:             font_na`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Get slide dimensions from slide object.          Args:             slide: Slide`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Calculate paragraphs from the shape's text frame.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Check if shape has any issues (overflow, overlap, or warnings).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `unpack.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `static_html_automation.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `element_discovery.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Create the connection context based on connection type.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `apply_replacements()` connect `Community 10` to `Community 1`, `Community 3`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `convert()` connect `Community 1` to `Community 9`, `Community 11`, `Community 5`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `GIFBuilder` connect `Community 1` to `Community 8`, `Community 10`, `Community 5`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `DOCXSchemaValidator` (e.g. with `BaseSchemaValidator` and `Validation modules for Word document processing.`) actually correct?**
  _`DOCXSchemaValidator` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `XMLEditor` (e.g. with `DocxXMLEditor` and `Document`) actually correct?**
  _`XMLEditor` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `RedliningValidator` (e.g. with `Validation modules for Word document processing.` and `DocxXMLEditor`) actually correct?**
  _`RedliningValidator` has 49 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `BaseSchemaValidator` (e.g. with `DOCXSchemaValidator` and `Validator for Word document XML files against XSD schemas.`) actually correct?**
  _`BaseSchemaValidator` has 20 INFERRED edges - model-reasoned connections that need verification._