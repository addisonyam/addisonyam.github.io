#!/usr/bin/env python3
"""Regenerates the site. Optional: the committed HTML is the deliverable.
Needs: Python 3, Pillow, Pygments, local clones of the project repos (REPOS dir).
Figures that came from reports/posters are committed as WebP in assets/img; repo figures are converted when missing.
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
SEEK = "Open to full-time bioinformatics and computational biology roles in the US: Boston, New York City or California, in person, hybrid or remote."
T = lambda s: f'<span class="todo">[TODO: {s}]</span>'

def tbl(head, rows, cap=""):
    h = "".join(f"<th scope='col'>{c}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<{'th scope=row' if i == 0 else 'td'}>{c}</{'th' if i == 0 else 'td'}>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table>{f"<caption>{cap}</caption>" if cap else ""}<thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

# ---------- content: every number is from a repo file, a report/poster you supplied, the CV, or marked TODO ----------
P = [
 dict(slug="ab-biosciences", group="work", repo=None, dir=None,
  title="Triaging AlphaFold3 Predictions for Therapeutic Fc-Fusion Proteins",
  meta="Computational Biology Intern, Protein Engineering Group, AB Biosciences · Summer 2026",
  what="I built a four-step triage framework that ranks AlphaFold3 predictions of trimerized Fc-fusion designs, so protein engineers can pick candidates before booking bench time.",
  why=["AB Biosciences engineers therapeutic fusion proteins. My project covered homotrimeric Fc-fusions: an antibody Fc fused to a trimerization module so that three identical chains assemble into one molecule with three binding interfaces instead of one.",
       "Gluing domains together that never shared a chain can go wrong in many ways: steric clashes, failed trimerization, broken folds. Testing every candidate at the bench is slow and expensive, so the question was whether AlphaFold3 could act as a pre-filter."],
  approach=[("Run AlphaFold3 safely and flexibly","The group works on an air-gapped Ubuntu workstation to protect IP, with local databases. I documented three ways to run AlphaFold3 (interactive, a CSV-driven batch queue, and hand-built JSON for heteromers and protein/DNA/RNA/ligand complexes) and validated them on seven test inputs, from a monomer to a protein-RNA-ligand complex. Getting there meant working through an outdated Python, then Docker, then a FASTA-only CLI, before settling on the local setup."),
            ("Screen linkers systematically","More than 100 structures across about 78 design variants. Scanning linker length from 0 to 15 residues in single steps showed that 4 to 5 residues collided sterically, 14 to 15 interfered with the Ig fold, and about 7 worked best. Placing a matrilin-derived trimerization module at the C-terminus produced a helical bundle far more reliably than the N-terminus, and a serine scan through a 7-residue glycine/serine linker favored the canonical spacing."),
            ("Shrink the construct","A designed cysteine mutation made the light chain and CH1 domain unnecessary, giving a construct about 33% smaller while keeping the fold."),
            ("Turn judgment into a decision tree","With my supervisor I wrote down how we were actually deciding, then tested it on new designs until it held. The result is a four-step filter: is there a helical bundle, are the interactions cis or trans, is the symmetry C3, and are the cysteine pairs close enough for a disulfide (under 2.4 Å)? Passing designs are then ranked by overall size."),
            ("Automate the tedious parts","A Python parser pulls pLDDT, inter-chain PAE and ranking-score components from AlphaFold3 confidence files, and a ChimeraX script scans every cysteine pair for disulfide-range distances. I also benchmarked AlphaFold3 against ESMFold2 on the same seven inputs; ESMFold2 handles only protein chains, which is why AlphaFold3 stayed primary."),
            ("Write it down so it outlives me","User guide for the three run methods, the input schema, the confidence metrics and a ChimeraX quick reference, plus a sequence ID record and a data workbook, handed to the group.")],
  stats=[("100+","structures predicted"),("~78","design variants screened"),("~33%","smaller construct after domain minimization"),("4","step triage framework")],
  snips=[], figs=[("image4.png","Decision tree for triaging AlphaFold3 predictions: helical bundle, cis versus trans, C3 symmetry, disulfide distance under 2.4 angstroms, then overall size","The triage framework: any 'no' lowers a design's priority.","ab"),
                  ("image2.png","Five AlphaFold3 predicted structures of fusion constructs shown side by side","Predicted structures of five constructs.","ab"),
                  ("image3.png","Plot of cysteine pair distance against linker length across designs","Disulfide-range distance versus linker length.","ab")],
  lessons=["My supervisor's feedback that changed how I present results: state the question, show the data, then give the conclusion. By the end of the summer I was walking him through the AlphaFold3 workflow.",
           "Triage criteria are hypotheses too. Ours changed over several rounds as predictions came back, and the final tree is the version that survived.",
           "AlphaFold3 ranks designs; it does not replace the bench. The value is spending wet-lab time on better candidates."],
  tools=["AlphaFold3","ChimeraX","Python","Docker","ESMFold2","Google Colab","Linux"],
  links=[("CV (PDF)","cv")], take="A reusable triage framework and a documented set of linker rules turned a pile of AlphaFold3 outputs into a ranked shortlist a bench scientist can act on."),
 dict(slug="klf4-pioneer-factor", group="work", repo="KLF4-Yamanaka-Pioneer-Factor-Project", dir="KLF4-Yamanaka-Pioneer-Factor-Project",
  title="Predicting Where the Pioneer Factor KLF4 Binds, and Why",
  meta="Computational Biology Researcher, Jacobs School of Medicine, University at Buffalo (mentor: Dr. Michael Buck) · McNair Scholars · 2022 to 2025",
  what="A machine-learning study of what separates KLF4 binding in one cell type from another, built on a compendium of public ChIP-seq data.",
  why=["KLF4 is a Yamanaka factor and a pioneer transcription factor: it can bind DNA wrapped in nucleosomes. Its core motif does not explain everything, since KLF4 also binds where the motif is absent, so cofactors and histone marks must matter.",
       "The goal was to curate the data, engineer the features, and train models that show which features separate KLF4 binding in one cell type from another."],
  approach=[("Build a clean compendium","KLF4 ChIP-seq samples from the Cistrome database, filtered for quality (FastQC median at least 25, more than 1,000 peaks, fraction of peaks in DNase-hypersensitive sites above 0.7). Samples were concatenated, irregular chromosomes dropped, overlapping peaks merged keeping the first, and every peak tagged by cell line. Result: 203,018 human and 323,112 mouse binding peaks."),
            ("Engineer features per peak","FIMO scores for the KLF4 motif (presence, score, count, strand, total score), 10 cofactor motifs found by MEME-ChIP in discriminative mode (MCF7 versus iPSC), and overlaps with 13 histone marks in MCF7 and 5 in head and neck squamous carcinoma (HNSCC) from ENCODE. That is 56 columns per peak."),
            ("Look at the nucleosome context","MNase-seq at several digestion levels, visualized with ArchTEx. The 64-unit sample gave the sharpest nucleosome positioning, so it became the reference for plotting KLF4 binding."),
            ("Train and compare models","Random forests (500 trees) separating cell-line-exclusive peaks: MCF7 versus HNSCC, then BJ-derived iPSC versus HNSCC.")],
  stats=[("203,018","human KLF4 peaks"),("323,112","mouse KLF4 peaks"),("56","features per peak"),("10","cofactor motifs identified")],
  snips=[("Bash: merge samples, keep valid chromosomes, sort","CompileDataset/Concatenate_BED.sh",r"^# Sorts first",4,"bash",None),
         ("Bash: FIMO motif scan on peak sequences","ProcessData/FIMO.sh",r"^bedtools getfasta",1,"bash","ProcessData/FIMO.sh|^fimo --thresh|1"),
         ("Bash: which peaks overlap a histone mark","ProcessData/HistoneOverlap.sh",r"^bedtools intersect",1,"bash",None),
         ("R: random forest on cell-line-exclusive peaks","ModelTraining/iPSCvsHNSCC.R",r"randomForest\(",6,"r",None)],
  figs=[("klf_histone.png","Histone modification signal around KLF4 binding sites in MCF7 but not HNSCC, and in HNSCC but not MCF7","Histone marks around KLF4 sites that are exclusive to one cell line.","crops"),
        ("klf_motif.png","Bar charts and tables of the percentage of KLF4 binding peaks containing the KLF4 motif in human and mouse cell lines","How often peaks contain the KLF4 motif, by cell line.","crops"),
        ("klf_mnase.png","Average nucleosome positioning from MNase-seq at four digestion levels in mouse embryonic fibroblasts","MNase-seq at 1, 4, 16 and 64 units.","crops"),
        ("klf_nuc.png","Average MNase-seq signal around KLF4 binding sites","Nucleosome signal centered on KLF4 binding sites.","crops")],
  tables=[tbl(["Model","Accuracy (95% CI)","No-information rate","Balanced accuracy","Kappa"],
              [["MCF7 vs HNSCC","94.14% (93.77 to 94.50)","90.05%","0.753","0.607"],["BJ iPSC vs HNSCC","84.47% (84.09 to 84.85)","65.67%","0.818","0.649"]],
              "Held-out performance. The first model's headline accuracy is mostly the majority class, so balanced accuracy is the fairer number."),
          tbl(["Top features, BJ iPSC vs HNSCC","Mean decrease in Gini"],
              [["ZNF213 motif score","3,368"],["ZBTB6 motif score","3,174"],["ZNF460 motif score","2,134"],["FOSL2 motif score","2,006"],["Total motif score","1,740"]])],
  lessons=["The 94% model is less impressive than it looks: HNSCC peaks outnumber MCF7 peaks about nine to one (47,700 versus 5,276), the no-information rate is already 90%, and specificity is only 52%. Swapping MCF7 for BJ-derived iPSC (78,287 peaks) balanced the classes and accuracy fell to 84%, which tells me the two cell lines share much of their feature space.",
           "Next time I would split train and test by chromosome so neighboring peaks cannot leak across the split, add class weights, and use permutation importance, since Gini importance favors continuous features.",
           "The most useful result is the plain one: KLF4 binds many sites with no canonical motif, and cofactor motif scores rank above the KLF4 motif score for telling cell lines apart."],
  tools=["Python","R","Bash","randomForest","FIMO","MEME-ChIP","GREAT","bedtools","ArchTEx","Cistrome"],
  links=[("Repository",""),("Research paper (PDF)","docs/KLF4_McNair_Research_Paper.pdf")], take="KLF4 binding is shaped by cofactor motifs and histone context, not the KLF4 motif alone."),
 dict(slug="razorback-sucker-genome", group="work", repo=None, dir=None,
  title="Reassembling the Razorback Sucker Genome with Newer Long-Read Tools",
  meta="Genomics Research Assistant, Krabbenhoft Lab, University at Buffalo · 2024 to 2025",
  what="Does a newer toolchain build a better genome from the same old sequencing data? I rebuilt the endangered razorback sucker genome to find out.",
  why=["The razorback sucker (<i>Xyrauchen texanus</i>) is an endangered fish in the sucker family. Its genome had been assembled twice before, in 2018 and 2021, from the same Nanopore reads.",
       "If new tools can improve an assembly built from old data, researchers may not need to re-sequence samples that are hard to get. That matters most for rare species."],
  approach=[("Wet lab to reads","I ran the DNA extraction and Nanopore library preparation, including QC for downstream assembly."),
            ("A scripted, reproducible pipeline","Custom Bash scripts chained the stages below, and I troubleshot the assembly tools for parallel execution on a SLURM-managed cluster."),
            ("Compare like with like","The 2018, 2021 and new 2024 assemblies all start from the same sequencing data, and are compared by length, N50 and BUSCO completeness.")],
  stats=[("2.12 Gb","assembled genome size"),("43.18 Mb","scaffold N50"),("97.0%","BUSCO complete"),("3","assemblies compared")],
  snips=[],
  extra_html=tbl(["Stage","Tool"],[["Basecalling","Dorado"],["Read filter","fastp, reads over 10 kb"],["Read correction","Dorado Herro"],["Contig assembly","Hifiasm with Hi-C data"],["Polishing","Pilon, with BUSCO between rounds"],["Quality filter","fastq, Q20"],["Duplicate removal","Purge Dups"],["Contamination check","Kraken"],["Scaffolding","Yahs, reviewed in Juicebox 3D"]],"Pipeline stages"),
  figs=[("fish_circos.png","Circos plot of the razorback sucker genome showing chromosomes and duplicated gene relationships","Circos plot: rearrangements and duplicated genes across chromosomes.","crops"),
        ("fish_hic.png","Hi-C contact heatmap showing contigs scaffolded into chromosomes","Hi-C heatmap from scaffolding, visualized in Juicebox.","crops"),
        ("fish_syn.png","Syntenic dot plot comparing the 2018 assembly with the new assembly","Synteny: 2018 assembly versus the new one.","crops")],
  tables=[tbl(["","2018","2021","2024"],
              [["Final assembly length (Gb)","2.39","2.15","2.12"],["N50 (Mb)","48.60","43.77","43.18"],["BUSCO complete (%)","97.6","98.2","97.0"],["Complete, single copy (%)","52.7","51.6","51.6"],["Complete, duplicated (%)","44.9","46.6","45.4"],["Fragmented (%)","0.6","0.4","0.7"],["Missing (%)","1.8","1.4","2.3"]],
              "Assemblies built from the same sequencing data (BUSCO v5, actinopterygii_odb10).")],
  lessons=["The new assembly is comparable to the earlier ones, not better. The likely reason is the read-correction step: Herro recommends reads longer than 10 kb, and this older dataset has many shorter reads, so a large share was filtered out at the start.",
           f"That filter is exactly the kind of failure I look for. The pipeline finished cleanly and every stage reported success, yet a large share of the data was gone before assembly began. Share of reads removed: {T('% of reads under 10 kb')}.",
           "A pipeline is only as good as its worst edge case. Next steps are lowering the length cutoff, annotating the assembly, and repeating the process on other organisms."],
  tools=["Bash","SLURM","Dorado","Hifiasm","Pilon","BUSCO","Purge Dups","Kraken","Yahs","Juicebox","Nanopore"],
  links=[("Poster (PDF)","docs/Razorback_Genome_Poster.pdf")], take="Re-assembling from the same reads showed where newer tools help and where a single default can quietly cap the result."),
 dict(slug="cell2location", group="pipe", repo="Cell2location-Spatial-Mapping-Xenium-vs-Visium-Mouse-Human", dir="cell2location",
  title="Cell2location: Spatial Mapping of Cell Types",
  meta="Team project (3 people), DS 596 at Boston University · April 2026",
  what="Reproduction and extension of cell2location (Kleshchevnikov et al., 2022, Nature Biotechnology) on mouse brain Visium, human glioblastoma Visium and Xenium.",
  why=["Visium spots hold several cells each, so a spot's expression is a mixture. Cell2location untangles it with a Bayesian model: it learns a signature for each cell type from single-cell data, then estimates how many cells of each type sit in each spot, while modeling technical noise separately.",
       "We asked two questions the paper left open: does it work in a heterogeneous tumor, and can it handle single-cell-resolution data from Xenium?"],
  note="<b>Team project.</b> With Vaidehi Gupta and Chloe Ploss. My part: found and downloaded all the datasets, built the GBmap reference, ran the glioblastoma extension and its five-configuration sweep, presented the method and that extension, and wrote those sections. Teammates produced the mouse Visium reproduction and the Xenium extension.",
  approach=[("Reproduce first","Figures 2b to 2e of the paper from the authors' public mouse brain data. The full 30,000-iteration run took about 22 minutes on a V100 GPU."),
            ("Glioblastoma extension","No ready-made reference existed, so I built one from GBmap (39,355 cells from 110 patients, 14 cell types), joining the count matrix and annotations by hand. After QC, 25,731 genes were shared with the 3,468-spot Visium section. The cell-number prior of 15 per spot came from the histology, since tumors are dense."),
            ("Five-run sensitivity sweep","Regression iterations, spatial iterations, combinations, learning rate and posterior samples were varied over five configurations, from a quick test to near paper settings."),
            ("Xenium extension","36,602 cells and 248 genes, 247 of them shared with the reference, mapped against 59 mouse cell types across five runs that varied iterations, learning rate, train/validation split and posterior sampling.")],
  stats=[("39,355","cells in the GBmap reference"),("3,468","glioblastoma Visium spots mapped"),("5","configurations in the sweep"),("36,602","Xenium cells mapped")],
  snips=[("Python: force Theano onto the GPU before anything imports it","scripts/00_gpu_setup.py",r"^# Force Theano",3,"python",None),
         ("Python: the five-configuration sweep (first and last)","scripts/06_gbm_parameter_sweep.py",r"^CONFIGS = \{",7,"python","scripts/06_gbm_parameter_sweep.py|^    \"run5_final\": \\{|6")],
  figs=[("c2l_D.png","Reproduced spatial maps of three rare inhibitory neuron types next to the paper's Figure 2e","Reproduction of the paper's Figure 2e (left) beside the original (right).","crops"),
        ("c2l_dom.png","Dominant cell type per spot across the five glioblastoma configurations, from the quick test to the final run","Dominant cell type per spot, runs 1 to 5: the map consolidates as training lengthens.","crops"),
        ("c2l_xen8.png","Xenium mouse brain abundance maps of eight cell types across five runs","Xenium, five runs (rows), eight cell types each.","crops"),
        ("c2l_C.png","Reproduced spatial maps of six major mouse brain cell types next to the paper's Figure 2d","Reproduction of Figure 2d (left) beside the original (right).","crops")],
  tables=[tbl(["Run","Reg. iter","Spatial iter","Combos","Learning rate","Posterior samples"],
              [["1 Test","100","500","20","0.005","200"],["2 More samples","100","500","20","0.005","500"],["3 Higher LR","100","500","20","0.025","200"],["4 Intermediate","500","5,000","30","0.005","500"],["5 Final","2,000","10,000","30","0.005","500"]],
              "Glioblastoma sweep.")],
  lessons=["MES-like cells came out as the dominant malignant state in all five configurations, the top three (MES-like, astrocyte, CD4/CD8) matched between the quick test and the final run, and endothelial cells landed on vessels, a useful internal check. A higher learning rate ran faster but reordered the low-abundance types.",
           "In the Xenium runs, the one with a 70/30 train/validation split and doubled posterior samples produced two rectangular patches of inflated abundance across every cell type, and no other run did. Artifacts like that are how you learn what a parameter really changes.",
           "Constraints we worked around: the newest release did not fit in our 10 GB cluster quota, so we used the authors' Singularity container with the older PyMC3/Theano version, which in turn needed an older V100 GPU. The tool outputs one cell type at a time, so the paper's multi-color composites were out of reach."],
  tools=["Python","cell2location","Theano","PyMC3","Scanpy","Singularity","NVIDIA V100"],
  links=[("Repository","")], take="Mesenchymal-like (MES-like) cells were the dominant glioblastoma cell state in every one of the five parameter configurations."),
 dict(slug="rnaseq-tyk2", group="pipe", repo="RNAseq-Analysis-Pipeline", dir="RNAseq-Analysis-Pipeline",
  title="RNA-seq: TYK2 in Pancreatic β-Cell Development",
  meta="Course project · Nextflow and R",
  what="Reproduction of Chandra et al. 2022 (Nature Communications): how TYK2 knockout changes gene expression at the S5 endocrine progenitor stage.",
  why=["Take a published study and rebuild its differential-expression and pathway results from raw reads, then compare conclusions honestly, including where mine differ."],
  approach=[("Reads to counts, in Nextflow","FastQC and MultiQC, STAR alignment to GRCh38, and VERSE gene counts, with each tool in its own process."),
            ("Filter, model, test","Genes need at least 1 CPM in at least 3 samples. DESeq2 fits <code>~condition</code> for TYK2 KO against wild type."),
            ("Interpret","Volcano plot, then Enrichr/Reactome on the significant genes and fgsea on ranked genes against MSigDB C2 pathways.")],
  stats=[("1,116","significant genes (padj &lt; 0.05)"),("48 / 100","up / down at |log2FC| ≥ 1"),("84%","variance on PC1"),(T("metric"),"genes retained after CPM filter")],
  snips=[("R: expression filter and DESeq2 model","scripts/MainAnalysis.Rmd",r"cpm_matrix <- cpm",3,"r","scripts/MainAnalysis.Rmd|condition <- factor|8"),
         ("R: differential expression","scripts/MainAnalysis.Rmd",r"dds <- DESeq\(dds\)",3,"r",None),
         ("R: volcano categories from the paper's cutoffs","scripts/MainAnalysis.Rmd",r"log2FoldChange >= ",4,"r",None)],
  figs=[("Figure_c_Volcano_S5_TYK2KO_vs_WT.png","Volcano plot of differentially expressed genes, TYK2 knockout versus wild type","Volcano plot, TYK2 KO vs WT (replicates paper Figure 3C).","repo"),
        ("Figure_PCA_QC.png","PCA of variance-stabilized counts for TYK2 knockout and wild-type samples","PCA of VST-normalized counts.","repo"),
        ("Figure_FGSEA_TopPathways.png","Top pathways from fgsea on ranked genes","Top pathways from fgsea (MSigDB C2).","repo")],
  figdir="results", lessons=["Before trusting a top hit, check the metadata for confounds. The most significant gene is Y-linked, which suggests sex or cell-line composition differs between groups.",
   "One knockout replicate sits apart from its group on the PCA, so I would not describe the replicates as tightly clustered.",
   "My count of 1,116 genes and the paper's smaller number probably reflect different thresholds. Matching their cutoffs before comparing counts is the fair test."],
  tools=["Nextflow","FastQC","MultiQC","STAR","VERSE","R","DESeq2","fgsea","Enrichr"],
  links=[("Repository",""),("Report (PDF)","blob/main/RNAseq_Project_Report.pdf")],
  take="TYK2 loss shifts extracellular-matrix and developmental programs: 1,116 genes pass padj &lt; 0.05, and 148 of them also change at least two-fold."),
 dict(slug="chipseq-runx1", group="pipe", repo="ChIPseq-Analysis-Pipeline", dir="ChIPseq-Analysis-Pipeline",
  title="ChIP-seq: RUNX1 Binding in MCF-7 Breast Cancer Cells",
  meta="Course project · Nextflow, HOMER and Python",
  what="A Nextflow re-analysis of Barutcu et al. 2016 that maps RUNX1 binding genome-wide and ties it to gene expression after RUNX1 knockdown.",
  why=["A transcription factor's binding sites only matter if they change gene expression. The aim was to find direct RUNX1 targets by combining ChIP-seq peaks with RNA-seq from RUNX1-knockdown cells."],
  approach=[("From reads to peaks","Trimmomatic, FastQC, Bowtie2 and samtools, then HOMER tag directories and factor-style peak calling against matched input."),
            ("Motifs and coverage","HOMER motif discovery, and deepTools for coverage, correlation and profile plots."),
            ("Link to expression","A Python script intersects peaks with the knockdown RNA-seq (GSE75070) using the paper's thresholds, and Enrichr summarizes target pathways.")],
  stats=[("6,462","RUNX1 binding sites (README)"),("2 + 2","IP + input replicates"),("14.7–18.7%","of DEGs are direct targets (README)")],
  snips=[("Nextflow: HOMER peak calling against input","modules/homer_findpeaks/main.nf",r"^process HOMER_FINDPEAKS",19,"groovy",None),
         ("Nextflow: de novo motif discovery","modules/homer_findmotifsgenome/main.nf",r"^process HOMER_FINDMOTIFSGENOME",16,"groovy",None),
         ("Python: apply the paper's thresholds to the knockdown data","scripts/OverlapChIPvsRNA.py",r"^# Apply thresholds",7,"python",None)],
  figs=[("figure_2D_MALAT1.png","Genome browser view of RUNX1 ChIP signal at the MALAT1 promoter","RUNX1 signal at the MALAT1 promoter (replicates paper Figure 2D).","repo"),
        ("supp_figure_S2C_venn.png","Venn diagram of peak overlap between the two IP replicates","Peak overlap between IP replicates.","repo"),
        ("known_homer_motif.png","Top known motifs enriched in RUNX1 peaks from HOMER","Top enriched motifs (HOMER).","repo")],
  figdir="results", lessons=["Two IP replicates is enough to check agreement but not to estimate reproducibility with much confidence; an IDR-style analysis needs more.",
   "Assigning a peak to its nearest gene misses distal enhancers, so the direct-target fraction is probably a lower bound."],
  tools=["Nextflow","Trimmomatic","FastQC","Bowtie2","samtools","HOMER","deepTools","bedtools","Enrichr","Python"],
  links=[("Repository",""),("Report (PDF)","blob/main/Report_Latex_Version.pdf")],
  take="Peaks plus knockdown expression data point to direct RUNX1 regulation across cell-cycle, DNA-damage and metabolic genes."),
 dict(slug="atacseq-hdac1", group="pipe", repo="ATACseq-and-Differential-Chromatin-Accessibility-Analysis-Pipeline", dir="ATACseq-and-Differential-Chromatin-Accessibility-Analysis-Pipeline",
  title="ATAC-seq: Chromatin Accessibility in Dendritic Cells",
  meta="Course project · Nextflow, HOMER and Python",
  what="A Nextflow reproduction of the HDAC1 dendritic-cell study (De Sá Fernandes et al., 2024, Cell Reports), from raw SRA reads to differentially accessible regions and motifs.",
  why=["Deleting HDAC1 in dendritic cells should change which chromatin is open. This pipeline rebuilds that analysis for two subsets, cDC1 and cDC2, from public data."],
  approach=[("Reads to peaks","Public data from GEO GSE266584 is downloaded, trimmed with Trimmomatic, aligned to mm10 with Bowtie2 and called into peaks with HOMER."),
            ("Differential accessibility","A Python script compares WT and KO peak counts per cell type with a relaxed cutoff (p &lt; 0.15 and |log2FC| &gt; 0.5), because there are only two replicates per group."),
            ("Annotate","HOMER annotation and motif enrichment, deepTools tracks, and a companion RNA-seq workflow that uses DESeq2.")],
  stats=[("2","dendritic cell subsets (cDC1, cDC2)"),("2","replicates per group"),(T("metric"),"differentially accessible regions")],
  snips=[("Python: the differential test thresholds","bin/diff_analysis.py",r"result\['log2FC'\] = ",1,"python","bin/diff_analysis.py|# Use p < 0\\.15|3"),
         ("Nextflow: differential analysis per cell type","modules/deseq2/main.nf",r"^process DIFF_ANALYSIS",21,"groovy",None)],
  figs=[("Figure_6A_cDC1_combined.png","Accessibility profiles and heatmaps for WT and KO cDC1 cells","cDC1 accessibility summary (Figure 6A).","repo"),
        ("HomerMotifEnrichment_cDC1.png","HOMER motif enrichment in cDC1 differentially accessible regions","Motifs enriched in cDC1 regions.","repo"),
        ("cDC1_vs_cDC2_comparison.png","Comparison of accessibility changes between cDC1 and cDC2","cDC1 vs cDC2 comparison.","repo")],
  figdir="figures", lessons=["With two replicates per group, the differential step is exploratory. The script uses a t-like statistic with an approximate p-value, which is why the cutoff is relaxed. A count-based model such as DESeq2 or edgeR with FDR control is the right tool, and swapping it in is the first thing I would do.",
   "Reproducing the figures taught me how many silent choices sit between a methods paragraph and a plot."],
  tools=["Nextflow","Singularity","Trimmomatic","Bowtie2","HOMER","deepTools","Python","DESeq2","Enrichr"],
  links=[("Repository",""),("Final report (PDF)","blob/main/FinalReport.pdf")],
  take="The pipeline rebuilds the study's Figure 6 panels from raw reads, with thresholds relaxed to suit two replicates per group."),
 dict(slug="genome-assembly", group="pipe", repo="Genome-Assembly-Pipeline", dir="Genome-Assembly-Pipeline",
  title="Bacterial Genome Assembly Pipeline",
  meta="Course project (BF528) · Nextflow",
  what="A Nextflow pipeline that assembles and evaluates a complete <i>Alteromonas macleodii</i> genome from long and short reads.",
  why=["A genome assembly is only useful if you can say how good it is. The pipeline assembles, polishes, annotates and then measures the result against the RefSeq reference, both before and after polishing."],
  approach=[("Reads","FastQC on short reads; Filtlong on long reads (minimum length 500, best 90% kept)."),
            ("Assemble and polish","Flye builds the assembly; short reads are aligned with Bowtie2 and samtools and Pilon polishes."),
            ("Annotate and judge","Prokka annotates, BUSCO checks completeness, and QUAST compares polished and unpolished assemblies with RefSeq GCF_000172635.2.")],
  stats=[("1","contig, 4,627,920 bp"),("99.6%","BUSCO complete (n = 1,828)"),("98.4%","genome fraction vs reference"),("18.18","mismatches / 100 kb (unpolished 18.33)")],
  snips=[("Nextflow: long-read assembly with Flye","modules/flye/main.nf",r"^process FLYE",14,"groovy",None),
         ("Nextflow: polishing with Pilon","modules/pilon/main.nf",r"^process PILON",14,"groovy",None),
         ("Nextflow: completeness with BUSCO","modules/busco/main.nf",r"^process BUSCO",14,"groovy",None)],
  figs=[("circos_plot1.png","Circos plot of the polished assembly with Prokka annotations","Circos plot built from the Prokka GFF.","repo"),
        ("busco_figure.png","BUSCO completeness bar chart for the polished assembly","BUSCO: C:99.6% [S:99.5%, D:0.1%], F:0.0%, M:0.4%.","repo")],
  figdir="figures", lessons=["Polishing moved QUAST mismatches only from 18.33 to 18.18 per 100 kb. The long-read assembly did most of the work, which is useful to know before spending compute on extra polishing rounds."],
  tools=["Nextflow","FastQC","Filtlong","Flye","Bowtie2","samtools","Pilon","Prokka","BUSCO","QUAST","Conda"],
  links=[("Repository",""),("Report (notebook)","blob/main/project1_report.ipynb"),("Report (PDF)","blob/main/project1_report.pdf")],
  take="A single 4.63 Mb contig with 99.6% BUSCO completeness; short-read polishing nudged QUAST mismatches from 18.33 to 18.18 per 100 kb."),
]
MORE = [("All-About-Single-Cell","All About Single Cell","Review of single-cell sequencing technologies, analysis methods and pipelines."),
 ("Applied-Genetic-Analysis-Guide","Applied Genetic Analysis Guide","Notes on GWAS concepts, statistics and software."),
 ("TLS-Detection-in-Tumor-Spatial-Transcriptomics","TLS detection in tumor spatial transcriptomics","Characterizing tertiary lymphoid structures in kidney and lung tumors."),
 ("Validating-Chronic-Inflammation-Biomarkers-via-Integrated-Bioinformatics-ML","Chronic inflammation biomarkers","Recreating and extending a biomarker study with integrated bioinformatics and ML.")]
SKILLS = [("Languages and tools","Python, R, UNIX/Linux, Bash, C++, Java, Git/GitHub, Docker, Singularity, LaTeX"),
 ("Sequencing and omics","Bulk RNA-seq, scRNA-seq, ChIP-seq, functional genomics, multi-omics integration, epigenetics, proteomics, genome assembly"),
 ("Bioinformatics tools","R/Bioconductor, Seurat, Scanpy, DESeq2, edgeR, STAR, HISAT2, BWA, Bowtie, FastQC, MACS2, HOMER, AlphaFold3, ChimeraX"),
 ("Workflows and compute","Nextflow, Snakemake, SLURM, LSF, HPC cluster management"),
 ("Machine learning and statistics","PyTorch, TensorFlow, scikit-learn, SVM, probabilistic graphical modeling, statistical analysis")]
JOBS = [("Summer 2026","Computational Biology Intern","AB Biosciences, Concord, MA","AlphaFold3 triage framework for Fc-fusion proteins: 100+ predicted structures, linker rules, a decision tree and a documented workflow the group now uses.","ab-biosciences"),
 ("Oct 2022 – Aug 2025","Computational Biology Researcher","Structural Biology Dept, Jacobs School of Medicine, Buffalo, NY","Built an ML classifier on 50+ regulatory features from ChIP-seq, ATAC-seq and RNA-seq to predict Yamanaka factor binding; benchmarked CASP structure predictions; improved the SCRMshaw enhancer-discovery tool.","klf4-pioneer-factor"),
 ("May 2024 – May 2025","Genomics Research Assistant","Biological Sciences Dept, University at Buffalo","Scripted reproducible assembly of the razorback sucker genome from long reads, troubleshot assembly tools on a SLURM cluster, and ran the Nanopore library prep and DNA extraction.","razorback-sucker-genome"),
 ("May – Aug 2022","Biostatistics Intern","Columbia University, New York, NY","Analyzed ABCD study data on maternal substance use and adolescent neurodevelopment with inferential statistics.",None)]
HOW = [("Translation","I like getting a complex analysis across to people who do not live in code. At AB Biosciences my supervisor taught me to state the question, show the data, then give the conclusion. By the end of the summer I was teaching him the AlphaFold3 workflow."),
 ("Immersion","I keep a running movie in my head of what is happening biologically at each step. It is how I catch a pipeline that finishes successfully and is quietly wrong, like a filter that dropped most of a genome's reads."),
 ("Community","I directed UB Hacking, an 800+ participant hackathon. As Master's Student Advisory Chair of BU's Bioinformatics Organized Students I formed a committee of 7, presented to faculty, and our work led to real program changes and a guide for future students. I have also been a cell biology TA and a first-gen mentor.")]

# ---------- helpers ----------
FMT = HtmlFormatter(nowrap=True)
esc = html.escape
CROPS = Path("/home/claude/src/crops"); ABM = Path("/home/claude/src/ab_media")
def snippet(proj, label, path, start, n, lang, extra):
    lines = (REPOS / proj["dir"] / path).read_text().splitlines()
    def grab(rx, k):
        i = next(i for i, l in enumerate(lines) if re.search(rx, l)); return lines[i:i + k]
    chunk = grab(start, n)
    if extra:
        _, rx, k = extra.split("|"); chunk += ["# ..."] + grab(rx, int(k))
    code = "\n".join(l.rstrip() for l in chunk)
    return f'<div class="code"><header><span>{esc(path)}</span><button type="button">Copy</button></header><pre class="hl"><code>{highlight(code, get_lexer_by_name(lang), FMT)}</code></pre></div><p class="cap">{esc(label)}</p>'
def img(name, kind, p):
    out = ROOT / "assets/img" / f"{p['slug']}-{Path(name).stem.lower()}.webp"
    if not out.exists():
        src = {"repo": REPOS / (p["dir"] or "") / p.get("figdir", ""), "crops": CROPS, "ab": ABM}[kind] / name
        im = Image.open(src).convert("RGBA"); im = Image.alpha_composite(Image.new("RGBA", im.size, "white"), im).convert("RGB")
        im.thumbnail((1400, 4200)); im.save(out, "WEBP", quality=80, method=6)
    W, H = Image.open(out).size; return out.name, W, H
def media(rel, alt, W, H, eager=False):
    return f'<div class="media"><img src="{rel}" alt="{esc(alt)}" width="{W}" height="{H}" loading="{"eager" if eager else "lazy"}" decoding="async"></div>'
def page(title, desc, body, prefix="", cur=""):
    nav = [("Home", "index.html"), ("Projects", "projects.html"), ("About", "about.html"), ("CV (PDF)", CV), ("Contact", "index.html#contact")]
    items = "".join(f'<li><a href="{prefix}{h}"{" aria-current=page" if n == cur else ""}>{n}</a></li>' for n, h in nav)
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="{prefix}style.css?v=3"></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap"><a class="brand" href="{prefix}index.html">Addison Yam</a><nav aria-label="Main"><ul>{items}</ul></nav></div></header>
<main id="main">{body}</main>
<footer><div class="wrap"><span>© 2026 Addison Yam · Boston, MA</span><span><a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="{GH}">GitHub</a> · <a href="{LINKEDIN}">LinkedIn</a></span></div></footer>
<script src="{prefix}assets/main.js" defer></script></body></html>'''

# ---------- build ----------
for p in P:
    p["fig"] = []
    for f, alt, cap, k in p["figs"]:
        n, W, H = img(f, k, p); p["fig"].append((n, alt, cap, W, H))
def card(p, lead=False):
    f = p["fig"][0]
    return f'<a class="card{" lead" if lead else ""}" href="projects/{p["slug"]}.html">{media("assets/img/" + f[0], f[1], f[3], f[4], eager=lead)}<div class="body"><p class="eyebrow">{p["meta"].split(" · ")[0]}</p><h3>{p["title"]}</h3><p>{p["what"]}</p><span class="more">Read the case study →</span></div></a>'
work = [p for p in P if p["group"] == "work"]; pipe = [p for p in P if p["group"] == "pipe"]
wcards = card(work[0], True) + "".join(card(p) for p in work[1:]); pcards = "".join(card(p) for p in pipe)
how = "".join(f"<div><h3>{a}</h3><p>{b}</p></div>" for a, b in HOW)
skills = "".join(f"<div><h3>{a}</h3><p>{b}</p></div>" for a, b in SKILLS)
mailbtn = f'<a class="btn primary" href="mailto:{EMAIL}">Email me</a>'
(ROOT / "index.html").write_text(page("Addison Yam | Bioinformatics and Computational Biology", "Bioinformatician building reproducible NGS pipelines and structure-prediction workflows for drug discovery.", f'''<div class="wrap"><section class="hero"><p class="eyebrow">Bioinformatics · Computational biology</p>
<h1>Bioinformatician building reproducible NGS pipelines and structure-prediction workflows for drug discovery.</h1>
<p class="lede">M.Sc. in Bioinformatics from Boston University, 2026. I work across sequencing analysis, machine learning and AlphaFold3 structure prediction, and I like analyses that someone else can rerun.</p>
<p class="seek">{SEEK}</p>
<div class="actions">{mailbtn}<a class="btn" href="projects.html">See the projects</a><a class="btn" href="{CV}">CV (PDF)</a></div>
<div class="facts"><div class="stat"><b>100+</b><span>AlphaFold3 structures predicted and triaged at AB Biosciences</span></div>
<div class="stat"><b>526K</b><span>KLF4 binding peaks curated across human and mouse cell lines</span></div>
<div class="stat"><b>4</b><span>Nextflow pipelines that run from raw reads to figures</span></div></div></section>
<section><p class="eyebrow">How I work</p><h2>What you get besides the code</h2><div class="skills">{how}</div></section>
<section id="projects"><p class="eyebrow">Industry and research</p><h2>The work I would start with</h2><div class="grid">{wcards}</div></section>
<section><p class="eyebrow">Pipelines and reproductions</p><h2>From raw reads to figures</h2><div class="grid">{pcards}</div><p style="margin-top:var(--s-5)"><a href="projects.html">All projects and repositories →</a></p></section>
<section><p class="eyebrow">Skills</p><h2>Tools I use</h2><div class="skills">{skills}</div></section>
<section id="contact"><p class="eyebrow">Contact</p><h2>Hiring for a bioinformatics or computational biology role?</h2>
<p style="margin-top:var(--s-4)">{SEEK} Email is the fastest way to reach me.</p>
<div class="actions"><a class="btn primary" href="mailto:{EMAIL}">{EMAIL}</a><a class="btn" href="{LINKEDIN}">LinkedIn</a><a class="btn" href="{GH}">GitHub</a></div></section></div>''', cur="Home"))

more = "".join(f'<li><a href="{GH}{r}"><b>{t}</b></a><br><span style="font-size:var(--t-0)">{d}</span></li>' for r, t, d in MORE)
(ROOT / "projects.html").write_text(page("Projects | Addison Yam", "Industry, research and pipeline projects with code, figures and results.", f'''<div class="wrap"><section class="hero"><p class="eyebrow">Projects</p><h1>Case studies with the code, the figures and the caveats.</h1>
<p class="lede">Each page covers the problem, what I did and why, real code, results, and what I would do differently.</p></section>
<section><p class="eyebrow">Industry and research</p><div class="grid">{wcards}</div></section>
<section><p class="eyebrow">Pipelines and reproductions</p><div class="grid">{pcards}</div></section>
<section><p class="eyebrow">More on GitHub</p><h2>Other repositories</h2><ul class="stack" style="list-style:none;padding:0;margin-top:var(--s-5)">{more}</ul></section></div>''', cur="Projects"))

jobs = "".join(f'<li><span class="when num">{w}</span><h3>{t}</h3><p><b>{o}</b></p><p>{d}{f" <a href=projects/{s}.html>Read the case study →</a>" if s else ""}</p></li>' for w, t, o, d, s in JOBS)
(ROOT / "about.html").write_text(page("About | Addison Yam", "Background, experience and education of Addison Yam, bioinformatician.", f'''<div class="wrap"><section class="hero"><p class="eyebrow">About</p><h1>I turn sequencing and structure data into results others can reproduce.</h1>
<p class="lede">I'm one of six kids, which includes two sets of triplets, so I grew up cataloguing who had which earlobes and hair texture in a crowded New York City apartment. Genetics was that hobby with better data. I was the first in my family to go to college, and I came out of it a bioinformatician.</p>
<p>I hold an M.Sc. in Bioinformatics from Boston University (2026) and a B.Sc. in Bioinformatics and Computational Biology from the University at Buffalo (2025). I like building things that help people and helping people build things.</p>
<p class="seek">{SEEK}</p>
<div class="actions">{mailbtn}<a class="btn" href="{CV}">CV (PDF)</a></div></section>
<section><p class="eyebrow">How I work</p><div class="skills">{how}</div></section>
<section><p class="eyebrow">Experience</p><h2>Where I've worked</h2><ul class="tl">{jobs}</ul></section>
<section><p class="eyebrow">Education</p><ul class="tl"><li><span class="when num">2026</span><h3>M.Sc. Bioinformatics</h3><p>Boston University. Student Ambassador, Graduate Program in Bioinformatics; Master's Student Advisory Chair, Bioinformatics Organized Students.</p></li><li><span class="when num">2025</span><h3>B.Sc. Bioinformatics and Computational Biology</h3><p>University at Buffalo, Computer Science concentration. McNair Scholar, Honors College, Director of UB Hacking, Resident Advisor.</p></li></ul></section>
<section><p class="eyebrow">Skills</p><div class="skills">{skills}</div></section></div>''', cur="About"))

def sec(h, inner): return f'<section style="padding-top:var(--s-6)"><h2>{h}</h2><div style="margin-top:var(--s-4)">{inner}</div></section>'
for p in P:
    figs = "".join(f'<figure>{media("../assets/img/" + n, alt, W, H)}<figcaption>{cap}</figcaption></figure>' for n, alt, cap, W, H in p["fig"])
    stats = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in p["stats"])
    links = "".join(f'<li><a class="btn" href="{"../" + CV if h == "cv" else "../" + h if h.startswith("docs/") else GH + p["repo"] + ("/" + h if h else "")}">{l}</a></li>' for l, h in p["links"])
    note = f'<p class="note">{p["note"]}</p>' if p.get("note") else ""
    why = "".join(f"<p>{x}</p>" for x in p["why"])
    appr = "".join(f"<li><h3>{h}</h3><p>{t}</p></li>" for h, t in p["approach"])
    sn = "".join(snippet(p, *s) for s in p["snips"])
    tabs = "".join(p.get("tables", [])) + p.get("extra_html", "")
    less = "".join(f"<li>{x}</li>" for x in p["lessons"])
    body = f'''<div class="wrap"><a class="back" href="../projects.html">← All projects</a>
<header class="proj-head"><p class="eyebrow">{p["meta"]}</p><h1>{p["title"]}</h1><p class="lede">{p["what"]}</p></header>{note}
<div class="stats">{stats}</div>
{sec("The problem", why)}
{sec("What I did", f'<ol class="steps">{appr}</ol>')}
{sec("Code", sn) if sn else ""}
{sec("Results", f'<div class="figs">{figs}</div>' + tabs)}
{sec("What I learned and what I would do differently", f'<ul class="bul">{less}</ul>')}
{sec("Tools", '<ul class="tags">' + "".join(f"<li>{t}</li>" for t in p["tools"]) + "</ul>")}
{sec("Links", f'<ul class="links">{links}</ul>')}
<p class="takeaway">{p["take"]}</p></div>'''
    (ROOT / "projects" / f'{p["slug"]}.html').write_text(page(p["title"] + " | Addison Yam", p["what"], body, prefix="../", cur="Projects"))
print("built", len(P), "project pages")
