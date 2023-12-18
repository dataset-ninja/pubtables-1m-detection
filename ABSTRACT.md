This is a **Detection** part of Microsoft **PubTables-1M** dataset, which is designed to address the limitations for table structure inference and extraction from unstructured documents. It comprises nearly one million tables extracted from scientific articles, offering support for multiple input modalities. Crucially, it includes detailed header and location information for table structures, enhancing its utility for diverse modeling approaches. The dataset not only quantifies improvements in training performance but also provides a more reliable estimate of model performance during evaluation for table structure recognition.

## Motivation

A table serves as a compact, structured representation for data storage and communication. However, the challenge arises when the logical structure of a presented table does not explicitly align with its visual representation, hindering data utilization in documents.

Table extraction (TE) task involves three subtasks: table detection (TD), table structure recognition (TSR), and functional analysis (FA). These tasks are particularly challenging due to the varied formats, styles, and layouts encountered in presented tables. The shift from traditional rule-based methods to deep learning has been notable, yet manual annotation for TSR remains arduous.

<img src="https://github.com/dataset-ninja/pubtables-1m-detection/assets/78355358/cd367500-4e02-474a-ab15-37a0f127866a" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Illustration of the three subtasks of table extraction addressed by the PubTables-1M dataset.</span>

## Challenges with crowdsourced markup annotations

Crowdsourcing has been employed to construct larger datasets, using documents from numerous authors. However, repurposing annotations for TE poses challenges related to completeness, consistency, quality, and explicitness of information. Markup lacks spatial coordinates for cells and relies on implicit cues, limiting potential modeling approaches and quality control for annotation correctness.

A critical issue in crowdsourced markup annotations is oversegmentation, where a spanning cell in a header is erroneously split into multiple grid cells. This introduces inconsistencies in the logical interpretation of a table, violating the assumption of a single correct ground truth. Oversegmented annotations lead to contradictory feedback during training and an underestimated model performance during evaluation.

## PubTables-1M data source selection

To build PubTables-1M, the authors chose the PMCOA corpus, comprising millions of scientific articles in PDF and XML formats. Each table's content and structure are annotated using standard HTML tags in the XML document, providing a rich source of annotated tables.

## Annotation verification and canonicalization

Given that the PMCOA corpus was not intended for TE ground truth, the authors undertook a multi-step process to enhance data quality and consistency. This involved inferring missing annotation information, verifying text annotation quality, and addressing oversegmentation issues through a novel canonicalization procedure (see the full algorithm [in the paper](https://openaccess.thecvf.com/content/CVPR2022/papers/Smock_PubTables-1M_Towards_Comprehensive_Table_Extraction_From_Unstructured_Documents_CVPR_2022_paper.pdf)).

## Quality control measures

Automated checks were implemented to ensure data quality. Tables with overlapping rows or columns, as these likely indicated errors, were discarded. Text annotation quality was ensured by comparing text from XML annotations with extracted text from PDFs. Additionally, tables with more than 100 objects were considered outliers and removed.

## Dataset statistics and splits

PubTables-1M stands out as the first dataset to verify annotations at the cell level, ensuring measurable assurance of consistency in ground truth. The dataset includes 947,642 tables for TSR, with 52.7% classified as complex. Canonicalization adjusted annotations for 34.7% of all tables, or 65.8% of complex tables.

Comparisons with other datasets highlight PubTables-1M's diversity, complexity, and a significant reduction in oversegmentation. The dataset was split randomly into *train*, *val*, and *test* sets, providing a comprehensive resource for advancing table extraction research.
