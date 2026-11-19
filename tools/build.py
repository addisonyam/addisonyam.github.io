#!/usr/bin/env python3
"""Regenerates the site. Optional: the committed HTML is the deliverable.
Needs: Python 3, Pillow, Pygments, and local clones of the project repos (REPOS dir).
Usage: python3 tools/build.py /path/to/dir/with/cloned/repos"""
import re, sys, html
from pathlib import Path
from PIL import Image
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
REPOS = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent)
GH = "https://github.com/addisonyam/"
EMAIL, LINKEDIN = "addisony@bu.edu", "https://www.linkedin.com/in/addisonyam"
CV = "Addison_Yam_CV_Nov_2026.pdf"
T = lambda s: f'<span class="todo">[TODO: {s}]</span>'

# ---------- content (every number is from a repo file, the CV, or marked TODO) ----------
P = [
 dict(slug="rnaseq-tyk2", repo="RNAseq-Analysis-Pipeline", dir="RNAseq-Analysis-Pipeline",
  title="RNA-seq: TYK2 in Pancreatic β-Cell Development",
  what="Reproduction of Chandra et al. 2022 (Nature Communications): how TYK2 knockout changes gene expression at the S5 endocrine progenitor stage.",
  goal="Reproduce the differential-expression and pathway findings of a published study starting from raw reads, then compare conclusions.",
  methods="Nextflow handles QC and counting: FastQC and MultiQC, STAR alignment to GRCh38, and VERSE gene counts. In R, genes are filtered to at least 1 CPM in at least 3 samples, DESeq2 fits <code>~condition</code> for TYK2 KO vs wild type, and enrichment runs through Enrichr/Reactome and fgsea on MSigDB C2 pathways.",
  stats=[("1,116","significant genes (padj &lt; 0.05)"),("48 / 100","up / down at |log2FC| ≥ 1"),("84%","variance on PC1"),(T("metric"),"genes retained after CPM filter")],
  snips=[("R: expression filter and DESeq2 model","scripts/MainAnalysis.Rmd",r"cpm_matrix <- cpm",3,"r","scripts/MainAnalysis.Rmd|condition <- factor|8"),
         ("R: differential expression","scripts/MainAnalysis.Rmd",r"dds <- DESeq\(dds\)",3,"r",None)],
  figs=[("Figure_c_Volcano_S5_TYK2KO_vs_WT.png","Volcano plot of differentially expressed genes, TYK2 knockout versus wild type","Volcano plot, TYK2 KO vs WT (replicates paper Figure 3C)."),
        ("Figure_PCA_QC.png","PCA of variance-stabilized counts separating TYK2 knockout and wild-type samples","PCA of VST-normalized counts."),
        ("Figure_FGSEA_TopPathways.png","Top pathways from fgsea on ranked genes","Top pathways from fgsea (MSigDB C2).")],
  figdir="results", tools=["Nextflow","FastQC","MultiQC","STAR","VERSE","R","DESeq2","fgsea","Enrichr"],
  links=[("Repository",""),("Report (PDF)","blob/main/RNAseq_Project_Report.pdf")],
  take="TYK2 loss shifts extracellular-matrix and developmental programs: 1,116 genes pass padj &lt; 0.05, and 148 of them also change at least two-fold."),
 dict(slug="chipseq-runx1", repo="ChIPseq-Analysis-Pipeline", dir="ChIPseq-Analysis-Pipeline",
  title="ChIP-seq: RUNX1 Binding in MCF-7 Breast Cancer Cells",
  what="A Nextflow re-analysis of Barutcu et al. 2016 that maps RUNX1 binding genome-wide and ties it to gene expression after RUNX1 knockdown.",
  goal="Identify direct RUNX1 targets by combining ChIP-seq peaks with RNA-seq from RUNX1 knockdown cells.",
  methods="Each IP and input replicate is trimmed (Trimmomatic), checked (FastQC), aligned (Bowtie2) and converted to HOMER tag directories. HOMER calls factor-style peaks and discovers motifs, deepTools builds coverage, correlation and profile plots, and bedtools intersects peaks with the knockdown RNA-seq data (GSE75070). Enrichr summarizes target-gene pathways.",
  stats=[("6,462","RUNX1 binding sites (README)"),("2 + 2","IP + input replicates"),("14.7–18.7%","of DEGs are direct targets (README)")],
  snips=[("Nextflow process: HOMER peak calling against input","modules/homer_findpeaks/main.nf",r"^process HOMER_FINDPEAKS",19,"groovy",None)],
  figs=[("figure_2D_MALAT1.png","Genome browser view of RUNX1 ChIP signal at the MALAT1 promoter","RUNX1 signal at the MALAT1 promoter (replicates paper Figure 2D)."),
        ("supp_figure_S2C_venn.png","Venn diagram of peak overlap between the two IP replicates","Peak overlap between IP replicates."),
        ("known_homer_motif.png","Top known motifs enriched in RUNX1 peaks from HOMER","Top enriched motifs (HOMER).")],
  figdir="results", tools=["Nextflow","Trimmomatic","FastQC","Bowtie2","samtools","HOMER","deepTools","bedtools","Enrichr","Python"],
  links=[("Repository",""),("Report (PDF)","blob/main/Report_Latex_Version.pdf")],
  take="Peaks plus knockdown expression data point to direct RUNX1 regulation across cell-cycle, DNA-damage and metabolic genes."),
 dict(slug="atacseq-hdac1", repo="ATACseq-and-Differential-Chromatin-Accessibility-Analysis-Pipeline", dir="ATACseq-and-Differential-Chromatin-Accessibility-Analysis-Pipeline",
  title="ATAC-seq: Chromatin Accessibility in Dendritic Cells",
  what="A Nextflow reproduction of the HDAC1 dendritic-cell study (De Sá Fernandes et al., 2024, Cell Reports), from raw SRA reads to differentially accessible regions and motifs.",
  goal="Rebuild the study's ATAC-seq results to test how HDAC1 deletion changes chromatin accessibility in cDC1 and cDC2 cells.",
  methods="Reads from GEO GSE266584 are downloaded, trimmed (Trimmomatic), aligned to mm10 (Bowtie2) and called into peaks with HOMER. A Python script compares WT and KO peak counts per cell type with a relaxed cutoff (p &lt; 0.15, |log2FC| &gt; 0.5), chosen in the code for two replicates per group. HOMER then annotates regions and finds motifs, and deepTools makes coverage tracks. A companion RNA-seq workflow uses DESeq2.",
  stats=[("2","dendritic cell subsets (cDC1, cDC2)"),("2","replicates per group"),(T("metric"),"differentially accessible regions")],
  snips=[("Python: differential test thresholds","bin/diff_analysis.py",r"result\['log2FC'\] = ",1,"python","bin/diff_analysis.py|# Use p < 0\\.15|3"),
         ("Nextflow process: differential analysis per cell type","modules/deseq2/main.nf",r"^process DIFF_ANALYSIS",21,"groovy",None)],
  figs=[("Figure_6A_cDC1_combined.png","Differentially accessible regions summarized for cDC1 cells","cDC1 accessibility summary (Figure 6A)."),
        ("HomerMotifEnrichment_cDC1.png","HOMER motif enrichment in cDC1 differentially accessible regions","Motifs enriched in cDC1 regions."),
        ("cDC1_vs_cDC2_comparison.png","Comparison of accessibility changes between cDC1 and cDC2","cDC1 vs cDC2 comparison.")],
  figdir="figures", tools=["Nextflow","Singularity","Trimmomatic","Bowtie2","HOMER","deepTools","Python","DESeq2","Enrichr"],
  links=[("Repository",""),("Final report (PDF)","blob/main/FinalReport.pdf")],
  take="The pipeline rebuilds the study's Figure 6 panels from raw reads, with thresholds relaxed to suit two replicates per group."),
 dict(slug="genome-assembly", repo="Genome-Assembly-Pipeline", dir="Genome-Assembly-Pipeline",
  title="Bacterial Genome Assembly Pipeline",
  what="A Nextflow pipeline that assembles and evaluates a complete <i>Alteromonas macleodii</i> genome from long and short reads.",
  goal="Build a reproducible long-read assembly workflow, polish it with short reads, and measure quality against the RefSeq reference (BF528 course project).",
  methods="Short reads get FastQC; long reads are filtered with Filtlong (minimum length 500, best 90% kept) and assembled with Flye. Bowtie2 and samtools align short reads to the assembly for Pilon polishing. Prokka annotates, BUSCO (alteromonas_odb12) checks completeness, and QUAST compares polished and unpolished assemblies with RefSeq GCF_000172635.2.",
  stats=[("1","contig, 4,627,920 bp"),("99.6%","BUSCO complete (n = 1,828)"),("98.4%","genome fraction vs reference"),("18.18","mismatches / 100 kb (unpolished 18.33)")],
  snips=[("Nextflow process: long-read assembly with Flye","modules/flye/main.nf",r"^process FLYE",14,"groovy",None)],
  figs=[("circos_plot1.png","Circos plot of the polished assembly with Prokka annotations","Circos plot built from the Prokka GFF."),
        ("busco_figure.png","BUSCO completeness bar chart for the polished assembly","BUSCO: C:99.6% [S:99.5%, D:0.1%], F:0.0%, M:0.4%.")],
  figdir="figures", tools=["Nextflow","FastQC","Filtlong","Flye","Bowtie2","samtools","Pilon","Prokka","BUSCO","QUAST","Conda"],
  links=[("Repository",""),("Report (notebook)","blob/main/project1_report.ipynb"),("Report (PDF)","blob/main/project1_report.pdf")],
  take="A single 4.63 Mb contig with 99.6% BUSCO completeness; short-read polishing nudged QUAST mismatches from 18.33 to 18.18 per 100 kb."),
 dict(slug="cell2location", repo="Cell2location-Spatial-Mapping-Xenium-vs-Visium-Mouse-Human", dir="cell2location",
  title="Cell2location: Spatial Mapping of Cell Types",
  what="Reproduction and extension of cell2location (Kleshchevnikov et al., 2022, Nature Biotechnology) on mouse brain Visium, human glioblastoma Visium and Xenium.",
  goal="Map fine-grained cell types onto spatial transcriptomics spots by deconvolving Visium signal with a single-cell reference, then test the method on new tissue and a new platform.",
  methods="The reproduction uses mouse brain Visium and snRNA-seq. The glioblastoma extension builds a GBmap reference (14 cell types) and runs a 5-configuration parameter sweep over iterations, learning rate and posterior samples. A Xenium mouse brain extension runs near single-cell resolution. Everything runs in a Singularity container on a V100 GPU (cell2location v0.3, Theano backend).",
  note="<b>Team project (3 people).</b> My part: found the extension datasets, built the GBmap reference, led the glioblastoma extension and its parameter sweep, presented, and wrote those sections. Teammates produced the Visium reproduction figures and the Xenium extension. The repository holds the full team pipeline.",
  stats=[("14","GBmap cell types"),("39,355","cells in the GBmap reference"),("5","glioblastoma parameter configurations"),("36,602","Xenium cells (248 genes)")],
  snips=[("Python: GPU setup, imported before cell2location","scripts/00_gpu_setup.py",r"^# Force Theano",3,"python",None),
         ("Python: parameter sweep, baseline and final configs","scripts/06_gbm_parameter_sweep.py",r"^CONFIGS = \{",7,"python","scripts/06_gbm_parameter_sweep.py|^    \"run5_final\": \\{|6")],
  figs=[], figdir="", tools=["Python","cell2location","Theano","PyMC3","Singularity","NVIDIA V100"],
  links=[("Repository","")],
  take="Mesenchymal-like (MES-like) cells were the dominant glioblastoma cell state in all five parameter configurations."),
]
MORE = [("KLF4-Yamanaka-Pioneer-Factor-Project","KLF4 pioneer factor analysis","100+ public ChIP-seq samples unified; machine learning on integrated epigenomic and chromatin features."),
 ("All-About-Single-Cell","All About Single Cell","Review of single-cell sequencing technologies, analysis methods and pipelines."),
 ("Applied-Genetic-Analysis-Guide","Applied Genetic Analysis Guide","Notes on GWAS concepts, statistics and software."),
 ("TLS-Detection-in-Tumor-Spatial-Transcriptomics","TLS detection in tumor spatial transcriptomics","Characterizing tertiary lymphoid structures in kidney and lung tumors."),
 ("Validating-Chronic-Inflammation-Biomarkers-via-Integrated-Bioinformatics-ML","Chronic inflammation biomarkers","Recreating and extending a biomarker study with integrated bioinformatics and ML.")]
SKILLS = [("Languages and tools","Python, R, UNIX/Linux, Bash, C++, Java, Git/GitHub, Docker, Singularity, LaTeX"),
 ("Sequencing and omics","Bulk RNA-seq, scRNA-seq, ChIP-seq, functional genomics, multi-omics integration, epigenetics, proteomics, genome assembly"),
 ("Bioinformatics tools","R/Bioconductor, Seurat, Scanpy, DESeq2, edgeR, STAR, HISAT2, BWA, Bowtie, FastQC, MACS2, HOMER, AlphaFold3, ChimeraX"),
 ("Workflows and compute","Nextflow, Snakemake, SLURM, LSF, HPC cluster management"),
 ("Machine learning and statistics","PyTorch, TensorFlow, scikit-learn, SVM, probabilistic graphical modeling, statistical analysis")]
JOBS = [("May – Sept 2026","Computational Biology Intern","AB Biosciences, Concord, MA","Predicted 500+ antibody-fusion structures with AlphaFold3 for oncology drug discovery, validated them in ChimeraX, benchmarked AlphaFold3 against ESMFold2, and wrote a company-wide reproducibility guide for 3D predictions."),
 ("Oct 2022 – Aug 2025","Computational Biology Researcher","Structural Biology Dept, Jacobs School of Medicine, Buffalo, NY","Built an ML classifier on 50+ regulatory features from ChIP-seq, ATAC-seq and RNA-seq to predict Yamanaka factor binding; benchmarked CASP structure predictions; improved the SCRMshaw enhancer-discovery tool."),
 ("May 2024 – May 2025","Genomics Research Assistant","Biological Sciences Dept, University at Buffalo","Wrote Bash/UNIX scripts for reproducible assembly of fish genomes from long-read data, troubleshot assembly tools on a SLURM cluster, and ran Nanopore library prep and DNA extraction."),
 ("May – Aug 2022","Biostatistics Intern","Columbia University, New York, NY","Analyzed ABCD study data on maternal substance use and adolescent neurodevelopment with inferential statistics.")]

# ---------- helpers ----------
FMT = HtmlFormatter(nowrap=True)
def esc(s): return html.escape(s)
def snippet(proj, label, path, start, n, lang, extra):
    lines = (REPOS / proj["dir"] / path).read_text().splitlines()
    def grab(p, rx, k):
        i = next(i for i, l in enumerate(lines) if re.search(rx, l)); return lines[i:i + k]
    chunk = grab(path, start, n)
    if extra:
        _, rx, k = extra.split("|"); chunk += ["# ..."] + grab(path, rx, int(k))
    code = "\n".join(l.rstrip() for l in chunk)
    body = highlight(code, get_lexer_by_name(lang), FMT)
    return f'<div class="code"><header><span>{esc(path)}</span><button type="button">Copy</button></header><pre class="hl"><code>{body}</code></pre></div><p class="num" style="font-size:var(--t-0);color:var(--muted);margin-top:calc(var(--s-3)*-1)">{esc(label)}</p>'
def img(name, alt, w=1400, lazy=True, srcdir=None, slug="x"):
    out = ROOT / "assets/img" / f"{slug}-{Path(name).stem.lower()}.webp"
    if not out.exists():
        im = Image.open(srcdir / name).convert("RGBA"); bg = Image.new("RGBA", im.size, "white"); im = Image.alpha_composite(bg, im).convert("RGB"); im.thumbnail((w, w * 3)); im.save(out, "WEBP", quality=80, method=6)
    W, H = Image.open(out).size
    return out.name, W, H
def media(rel, alt, W, H, lazy=True, eager=False):
    return f'<div class="media"><img src="{rel}" alt="{esc(alt)}" width="{W}" height="{H}" loading="{"eager" if eager else "lazy"}" decoding="async"></div>'
def page(title, desc, body, prefix="", cur=""):
    nav = [("Home", "index.html"), ("Projects", "projects.html"), ("About", "about.html"), ("CV (PDF)", CV), ("Contact", "index.html#contact")]
    items = "".join(f'<li><a href="{prefix}{h}"{" aria-current=page" if n == cur else ""}>{n}</a></li>' for n, h in nav)
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="{prefix}style.css"></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap"><a class="brand" href="{prefix}index.html">Addison Yam</a><nav aria-label="Main"><ul>{items}</ul></nav></div></header>
<main id="main">{body}</main>
<footer><div class="wrap"><span>© 2026 Addison Yam · Boston, MA</span><span><a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{GH}">GitHub</a> · <a href="{LINKEDIN}">LinkedIn</a></span></div></footer>
<script src="{prefix}assets/main.js" defer></script></body></html>'''

# ---------- build ----------
cards = []
for i, p in enumerate(P):
    p["fig"] = []
    for f, alt, cap in p["figs"]:
        n, W, H = img(f, alt, srcdir=REPOS / p["dir"] / p["figdir"], slug=p["slug"]); p["fig"].append((n, alt, cap, W, H))
    thumb = media("assets/img/" + p["fig"][0][0], p["fig"][0][1], p["fig"][0][3], p["fig"][0][4], eager=(i == 0)) if p["fig"] else '<div class="media ph">Figure pending <span class="todo">[TODO: figure]</span></div>'
    cards.append(f'<a class="card{" lead" if i == 0 else ""}" href="projects/{p["slug"]}.html">{thumb}<div class="body"><h3>{p["title"]}</h3><p>{p["what"]}</p><span class="more">Read the case study →</span></div></a>')

index = f'''<div class="wrap"><section class="hero"><p class="eyebrow">Bioinformatics · Computational biology</p>
<h1>Bioinformatician building reproducible NGS pipelines and structure-prediction workflows for drug discovery.</h1>
<p class="lede">I recently finished my M.Sc. in Bioinformatics at Boston University. I work across sequencing analysis, machine learning and AlphaFold3 structure prediction, and I like analyses that someone else can rerun.</p>
<div class="actions"><a class="btn primary" href="mailto:{EMAIL}">Email me</a><a class="btn" href="projects.html">See the projects</a><a class="btn" href="{CV}">CV (PDF)</a></div>
<div class="facts"><div class="stat"><b>500+</b><span>antibody-fusion structures predicted with AlphaFold3 at AB Biosciences</span></div>
<div class="stat"><b>100+</b><span>public ChIP-seq samples unified for KLF4 pioneer-factor modeling</span></div>
<div class="stat"><b>99.6%</b><span>BUSCO completeness on a single-contig bacterial assembly</span></div></div></section>
<section id="projects"><p class="eyebrow">Selected work</p><h2>Five analyses, from raw reads to figures</h2>
<div class="grid">{"".join(cards)}</div><p style="margin-top:var(--s-5)"><a href="projects.html">All projects and repositories →</a></p></section>
<section><p class="eyebrow">Skills</p><h2>Tools I use</h2><div class="skills">{"".join(f"<div><h3>{a}</h3><p>{b}</p></div>" for a, b in SKILLS)}</div></section>
<section id="contact"><p class="eyebrow">Contact</p><h2>Hiring for a bioinformatics or computational biology role?</h2>
<p style="margin-top:var(--s-4)">I'd like to hear about it. Email is the fastest way to reach me.</p>
<div class="actions"><a class="btn primary" href="mailto:{EMAIL}">{EMAIL}</a><a class="btn" href="{LINKEDIN}">LinkedIn</a><a class="btn" href="{GH}">GitHub</a></div></section></div>'''
(ROOT / "index.html").write_text(page("Addison Yam | Bioinformatics and Computational Biology", "Bioinformatician building reproducible NGS pipelines and structure-prediction workflows for drug discovery.", index, cur="Home"))

more = "".join(f'<li><a href="{GH}{r}"><b>{t}</b></a><br><span style="font-size:var(--t-0)">{d}</span></li>' for r, t, d in MORE)
(ROOT / "projects.html").write_text(page("Projects | Addison Yam", "Five reproducible bioinformatics analyses with code, figures and results.", f'''<div class="wrap"><section class="hero"><p class="eyebrow">Projects</p><h1>Pipelines and analyses, with the code and the figures.</h1>
<p class="lede">Each page covers the problem, methods, real code from the repository, and results.</p><div class="grid">{"".join(cards)}</div></section>
<section><p class="eyebrow">More on GitHub</p><h2>Other repositories</h2><ul class="stack" style="list-style:none;padding:0;margin-top:var(--s-5)">{more}</ul></section></div>''', cur="Projects"))

jobs = "".join(f'<li><span class="when num">{w}</span><h3>{t}</h3><p><b>{o}</b></p><p>{d}</p></li>' for w, t, o, d in JOBS)
(ROOT / "about.html").write_text(page("About | Addison Yam", "Background, experience and education of Addison Yam, bioinformatician.", f'''<div class="wrap"><section class="hero"><p class="eyebrow">About</p><h1>I turn sequencing and structure data into results others can reproduce.</h1>
<p class="lede">I hold an M.Sc. in Bioinformatics from Boston University (2026) and a B.Sc. in Bioinformatics and Computational Biology from the University at Buffalo (2025). Outside the lab I served as a Student Ambassador for the BU Graduate Program in Bioinformatics and as Master's Student Advisory Chair of Bioinformatics Organized Students (BiOS).</p>
<div class="actions"><a class="btn primary" href="mailto:{EMAIL}">Email me</a><a class="btn" href="{CV}">CV (PDF)</a></div></section>
<section><p class="eyebrow">Experience</p><h2>Where I've worked</h2><ul class="tl">{jobs}</ul>
<p style="margin-top:var(--s-5)">My KLF4 work from the Buffalo role is on GitHub: <a href="{GH}KLF4-Yamanaka-Pioneer-Factor-Project">KLF4-Yamanaka-Pioneer-Factor-Project</a>.</p></section>
<section><p class="eyebrow">Education</p><ul class="tl"><li><span class="when num">2026</span><h3>M.Sc. Bioinformatics</h3><p>Boston University</p></li><li><span class="when num">2025</span><h3>B.Sc. Bioinformatics and Computational Biology</h3><p>University at Buffalo, Computer Science concentration</p></li></ul></section>
<section><p class="eyebrow">Skills</p><div class="skills">{"".join(f"<div><h3>{a}</h3><p>{b}</p></div>" for a, b in SKILLS)}</div></section></div>''', cur="About"))

for p in P:
    figs = "".join(f'<figure>{media("../assets/img/" + n, alt, W, H)}<figcaption>{cap}</figcaption></figure>' for n, alt, cap, W, H in p["fig"]) if p["fig"] else f'<p>{T("figures: not committed to the repo")}</p>'
    sn = "".join(snippet(p, *s) for s in p["snips"])
    stats = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in p["stats"])
    links = "".join(f'<li><a class="btn" href="{GH}{p["repo"]}{"/" + h if h else ""}">{l}</a></li>' for l, h in p["links"])
    note = f'<p class="note">{p["note"]}</p>' if p.get("note") else ""
    body = f'''<div class="wrap"><a class="back" href="../projects.html">← All projects</a>
<header class="proj-head"><p class="eyebrow">Project</p><h1>{p["title"]}</h1><p class="lede">{p["what"]}</p></header>{note}
<div class="stats">{stats}</div>
<section style="padding-top:var(--s-6)"><h2>Goal</h2><p style="margin-top:var(--s-3)">{p["goal"]}</p></section>
<section style="padding-top:var(--s-6)"><h2>Data and methods</h2><p style="margin-top:var(--s-3)">{p["methods"]}</p></section>
<section style="padding-top:var(--s-6)"><h2>Code</h2>{sn}</section>
<section style="padding-top:var(--s-6)"><h2>Results</h2><div class="figs">{figs}</div></section>
<section style="padding-top:var(--s-6)"><h2>Tools</h2><ul class="tags" style="margin-top:var(--s-4)">{"".join(f"<li>{t}</li>" for t in p["tools"])}</ul></section>
<section style="padding-top:var(--s-6)"><h2>Links</h2><ul class="links" style="margin-top:var(--s-4)">{links}</ul></section>
<p class="takeaway">{p["take"]}</p></div>'''
    (ROOT / "projects" / f'{p["slug"]}.html').write_text(page(p["title"] + " | Addison Yam", p["what"], body, prefix="../", cur="Projects"))
print("built", len(P), "project pages")
