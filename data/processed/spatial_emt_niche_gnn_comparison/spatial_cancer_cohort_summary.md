# Spatial EMT Niche Multi-Cancer Cohort Comparison

This report compares the synthetic pipeline demo against a public 10x Visium FFPE human breast cancer dataset.

Interpretation rules:

- The synthetic demo validates workflow mechanics only.
- The real 10x run is still weak-label based because no spot-level pathologist labels are integrated yet.
- High stromal-inflated EMT fractions should be treated as a contamination warning, not tumor-cell EMT.
- Edge counts show graph construction behavior, not causal biology.

## Summary Table

| run | folder | spots | mean_emt_score | mean_partial_emt | emt_niche_fraction | tumor_cell_emt_fraction | stromal_inflated_fraction | mean_caf_tam | mean_hypoxia | mean_ecm_remodeling | mean_angiogenesis | mean_predicted_emt_niche_probability | high_probability_fraction | edges | spatial_knn_edges | ligand_receptor_edges | hypoxia_gradient_edges | ecm_gradient_edges | histology_similarity_edges | source_page |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| synthetic_demo | data\processed\spatial_emt_niche_gnn_demo | 144 | -1.4802973661668753e-16 | -0.5577219532085251 | 0.25 | 0.16666666666666666 | 0.08333333333333333 | 0.0 | -1.0485439677015367e-16 | 4.9343245538895844e-17 | -4.070817756958907e-16 | 0.25624170067407515 | 0.2638888888888889 | 1807 | 864 | 776 | 90 | 77 | 0 |  |
| 10x_breast_ffpe_idc | data\processed\spatial_emt_niche_gnn_10x_breast | 2518 | 5.643707194281971e-18 | -0.35892573189474997 | 0.25019857029388404 | 0.10127084988085783 | 0.1489277204130262 | -1.6931121582845915e-17 | 6.701902293209841e-18 | 1.1287414388563942e-17 | 2.3985755575698378e-17 | 0.2470744036312619 | 0.16401906274821287 | 32575 | 14724 | 8046 | 2596 | 3528 | 3681 | https://www.10xgenomics.com/datasets/human-breast-cancer-ductal-carcinoma-in-situ-invasive-carcinoma-ffpe-1-standard-1-3-0 |
| 10x_lung_lusc_cytassist | data\processed\spatial_emt_niche_gnn_10x_lung_lusc | 3858 | 5.525215674650857e-18 | -0.21287469612896245 | 0.2501296008294453 | 0.116381544841887 | 0.13374805598755832 | 7.366954232867809e-18 | 1.8417385582169523e-18 | -1.6575647023952572e-17 | 4.4201725397206854e-17 | 0.25078532255250247 | 0.12337998963193364 | 49593 | 22892 | 21018 | 3089 | 2594 | 0 | https://cf.10xgenomics.com/samples/spatial-exp/2.0.0/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma/CytAssist_FFPE_Human_Lung_Squamous_Cell_Carcinoma_web_summary.html |
| geo_pdac_gse274103 | data\processed\spatial_emt_niche_gnn_geo_pdac | 23436 | 1.4552846610549927e-17 | -0.1815755717899139 | 0.25 | 0.1354326676907322 | 0.1145673323092678 | -4.850948870183309e-18 | 1.9403795480733237e-17 | 0.0 | 1.4552846610549927e-17 | 0.2506086008003802 | 0.11358593616658133 | 432914 | 139518 | 251484 | 23809 | 18103 | 0 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274103 |
| geo_met_pdac_gse274557_pt1 | data\processed\spatial_emt_niche_gnn_geo_met_pdac_gse274557 | 8756 | 1.7852832556786437e-17 | -0.11209625671499739 | 0.25 | 0.10552763819095477 | 0.1444723618090452 | 1.2983878223117409e-17 | 0.0 | 2.5967756446234817e-17 | 1.9475817334676114e-17 | 0.2509086532892316 | 0.16491548652352672 | 277446 | 51597 | 210579 | 7185 | 8085 | 0 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE274557 |
| geo_brain_met_gse179572 | data\processed\spatial_emt_niche_gnn_geo_brain_met | 12566 | 0.0 | -0.21214018779894783 | 0.250039789909279 | 0.13528569154862327 | 0.11475409836065574 | 1.80943558366411e-17 | -9.04717791832055e-18 | 2.714153375496165e-17 | -3.3361468573807025e-17 | 0.2482463371602494 | 0.16011459493872354 | 370126 | 73584 | 269785 | 14904 | 11853 | 0 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE179572 |
| 10x_prostate_ffpe | data\processed\spatial_emt_niche_gnn_10x_prostate | 4371 | 1.0566295544362048e-17 | -0.27196238814191903 | 0.2500571951498513 | 0.15259665980324869 | 0.09746053534660261 | 1.6255839299018536e-18 | 1.1379087509312975e-17 | 2.4383758948527802e-18 | 4.8767517897055605e-18 | 0.2517040893692922 | 0.10043468313886983 | 66541 | 25904 | 26594 | 7518 | 6525 | 0 | https://www.10xgenomics.com/datasets/human-prostate-cancer-1-standard |
| 10x_ovarian_ffpe | data\processed\spatial_emt_niche_gnn_10x_ovarian | 3455 | -2.2622199980784667e-17 | -0.3439134819013579 | 0.25007235890014473 | 0.06685962373371925 | 0.18321273516642547 | -2.5707045432709847e-19 | -3.0848454519251818e-18 | 3.8560568149064774e-18 | 5.192823177407389e-17 | 0.25155957513272764 | 0.1869753979739508 | 38628 | 20472 | 11353 | 3304 | 3499 | 0 | https://www.10xgenomics.com/datasets/human-ovarian-cancer-1-standard |
| 10x_colorectal_intestinal_ffpe | data\processed\spatial_emt_niche_gnn_10x_colorectal | 2660 | -5.008524923121007e-18 | -0.3083825505088686 | 0.25 | 0.09360902255639098 | 0.15639097744360902 | -1.1352656492407616e-17 | 6.678033230828009e-18 | -4.674623261579606e-18 | -8.013639876993612e-18 | 0.2531242243165796 | 0.14661654135338345 | 33542 | 15664 | 12212 | 3532 | 2134 | 0 | https://www.10xgenomics.com/datasets/human-intestine-cancer-1-standard |

## Next Validation Moves

1. Add pathologist region labels from a cohort with spot-level annotations.
2. Add cell-type deconvolution to split malignant, CAF, TAM, and immune signal inside each spot.
3. Run leave-dataset-out validation after adding HEST-1k/HTAN/GEO cohorts.
4. Compare edge ablation on real data against randomized spatial coordinates and shuffled ligand-receptor edges.
