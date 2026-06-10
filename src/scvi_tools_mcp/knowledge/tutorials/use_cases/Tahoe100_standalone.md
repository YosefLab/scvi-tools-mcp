# Use pretrained models of scVI-hub for Tahoe100M

This notebook represent an example of how to perform downstream anaylsis on a pretrained SCVI model that was minified and saved in a model hub.
In this case we use the model that was trained based on the [Tahoe100M](https://doi.org/10.1101/2025.02.20.639398) dataset , by [Vevo Therapuetics](https://www.tahoebio.ai/news/open-sourcing-tahoe-100m). See link to model hub [here](https://huggingface.co/tahoebio/Tahoe-100M-SCVI-v1)

**Steps performed**:

1. Loading the minified data from AWS
2. Setting up minified model with minified data
3. Visualize the latent space
4. Perform differential expression and visualize with interactive volcano plot and heatmap using Plotly








We start by downloading the model from its hub



We can see the model card



We will extract he model and the minifed adata







## Get the latent space and compute UMAP











### Visualization with batch correction (scVI)





### Clustering on the scVI latent space













### SCANVI

Running scanvi from the scvi model will require the original counts matrix and cant be done, as count matrix is all 0.













### Perform Integration Analysis





## Performing Differential Expression in scVI

While we only have access to the minified data, we can still perform downstream analysis using the generative part of the model.
For example here, we will do it on a cluster of DMSO_TF controls vs the drug Harringtonine that is used for protein synthesis inhibitor per the cell line CVCL_0459 which is typicaly associated with Lung large cell carcinoma, a sub type of NSCLC. 
We also choose to use the sub group of G2M cell cycle phase.





scVI provides several options to identify the two populations of interest.



A simple DE analysis can then be performed using the following command





Volcano plot with p-values



We will use external gene annotations data base to extend our data















Display generated counts from scVI model, for top 4 genes









## Future Work

Perform DE between each cell line and/or drug vs all other cell lines and/or drigs and make a dotplot of the result. In order to do this we will have to use a subset of data (both cells and genes) to save time.

Run advance models on this data such as SCANVI, MrVI using the AnnCollector dataloader.
