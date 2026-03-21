# Venue Search Reference (Internal — for Claude's use during setup)

This file is used by the skill to suggest and infer appropriate venues when the user
doesn't specify them. Users never need to read or edit this file.

When inferring venues for a user's field:
1. Pick the 4-6 most prominent venues for their area from the tables below
2. State your choice to the user: "I'll watch X, Y, Z for you — correct me if you'd like others"
3. Save the chosen venues to the user's profile

For venues not listed here, use: `site:[proceedings-url] [keywords]`

---

## Machine Learning / AI

| Venue | Search pattern |
|---|---|
| NeurIPS | `site:proceedings.neurips.cc [keywords]` |
| ICML | `site:proceedings.mlr.press [keywords]` |
| ICLR | `site:openreview.net [keywords]` |
| AAAI | `site:ojs.aaai.org [keywords]` |
| JMLR | `site:jmlr.org [keywords]` |

## Computer Vision

| Venue | Search pattern |
|---|---|
| CVPR | `site:openaccess.thecvf.com CVPR [keywords]` |
| ICCV | `site:openaccess.thecvf.com ICCV [keywords]` |
| ECCV | `site:ecva.net [keywords]` |

## NLP

| Venue | Search pattern |
|---|---|
| ACL | `site:aclanthology.org ACL [keywords]` |
| EMNLP | `site:aclanthology.org EMNLP [keywords]` |
| NAACL | `site:aclanthology.org NAACL [keywords]` |

## Robotics

| Venue | Search pattern |
|---|---|
| ICRA | `site:ieeexplore.ieee.org ICRA [keywords]` |
| RSS | `site:roboticsproceedings.org [keywords]` |
| CoRL | `site:proceedings.mlr.press CoRL [keywords]` |

## Biology / Bioinformatics

| Venue | Search pattern |
|---|---|
| Nature | `site:nature.com [keywords]` |
| Science | `site:science.org [keywords]` |
| Cell | `site:cell.com [keywords]` |
| Bioinformatics | `site:academic.oup.com/bioinformatics [keywords]` |
| NeurIPS Comp Bio | `site:proceedings.neurips.cc computational biology [keywords]` |

## Physics

| Venue | Search pattern |
|---|---|
| Physical Review Letters | `site:journals.aps.org/prl [keywords]` |
| Physical Review X | `site:journals.aps.org/prx [keywords]` |
| Nature Physics | `site:nature.com/nphys [keywords]` |

## Economics / Statistics

| Venue | Search pattern |
|---|---|
| Econometrica | `site:econometricsociety.org [keywords]` |
| AER | `site:aeaweb.org/articles [keywords]` |
| Annals of Statistics | `site:projecteuclid.org/aos [keywords]` |
| JRSS-B | `site:academic.oup.com/jrsssb [keywords]` |

## Systems / HCI

| Venue | Search pattern |
|---|---|
| SOSP / OSDI | `site:usenix.org [keywords]` |
| SIGCHI | `site:dl.acm.org CHI [keywords]` |
| UIST | `site:dl.acm.org UIST [keywords]` |

---

## Arxiv Category Codes by Field

| Field | Categories |
|---|---|
| Machine Learning | cs.LG, stat.ML |
| Computer Vision | cs.CV |
| NLP | cs.CL |
| AI (general) | cs.AI |
| Robotics | cs.RO |
| Computational Biology | q-bio.GN, q-bio.QM, cs.LG |
| Physics (general) | physics.gen-ph, cond-mat |
| Economics | econ.EM, econ.TH |
| Statistics | stat.ME, stat.TH |
| Quantum Computing | quant-ph |
| Systems | cs.OS, cs.DC |
| HCI | cs.HC |
