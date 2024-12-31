# Extension Decisions in Open Source Software Ecosystem


## Abstract
GitHub Marketplace, as an open source software platform, is rapidly evolving, with an average annual increase of 41.23% in new tools by new or existing providers. 
In such a dynamic software ecosystem (SECO), making informed decisions about market entry and product extension is critical for success and requires careful consideration. GitHub Marketplace offers an environment where developers can openly share tools for automating workflows in open source software. However, our preliminary analysis of this ecosystem revealed a significant functional redundancy among the provided tools in this SECO.
We employed a graph-based approach to analyze the functional relationships between 6,983 ``Continuous Integration" Actions and 3,869 providers. We investigated the birth of functionalities and their evolutionary trajectory over time by mining the version control history and different releases of the actions and identified early adopters. Understanding the dynamics of the GitHub Marketplace is crucial for developers and organizations aiming to innovate and remain competitive in this rapidly evolving environment. By identifying patterns of functional redundancy and tracing the evolution of tools, we provide valuable insights that can inform strategic decisions on market entry and product development. Our analysis of early adopters and the evolutionary trajectory of functionalities offers developers a roadmap for anticipating future trends and aligning their products with emerging needs.

## Prerequisites
Check the requiremnets.txt file for the dependencies. To install dependencies use the following line:
```
pip install -r requirements.txt

```
## Installation
Make a `fork` or `clone` the repository. 

## Dataset
This study focuses on the "Continuous Integration" category in the GitHub Marketplace Ecosystem, which includes automation tools for continuous integration. We scraped data from 6,983 Actions in this category using the BeautifulSoup package due to the lack of a public API. Actions without an action.yaml file or resulting in 404 errors were excluded. The Marketplace restricts access to the first 1,000 actions per category, so we utilized search algorithms and bi-grams to retrieve 96.34% of the available Actions in this category. For each Action, we collected metadata (e.g., name, description, publisher, stars) and cloned repositories to extract action.yaml files for further analysis. We extracted data at two time points t0 and t1 and for each time point, we extracted features using LLMs (refer to the paper for more details). 

The data can be found in `Data` folder. We are sharing both data with raw and processed features. 

## Code Structure
1. `Auxiliary files` directory: contains scripts for adding publishers to the data
2. `Data` directory: contains action datasets with raw and processed features at t0 and t1.
3. `Feature Extraction` directory: contains script used to extract features from descriptions using LLMs and CRISPE framework.
4. `Feature preprocessing` directory: contains scripts required to create a dataset of unique features and clean the extracted feature by comparing it to this unique feature set using embeddings.
5. `Research Questions` directory: contains Google Colab notebook to process the data and answer the research questions noted in the manuscript.
6. `t0_analysis` directory: contains necessary scripts for analysis and visualization of feature network at t0 (for more detail refer to the paper).
7. `t1_analysis` directory: contains necessary scripts for analysis and visualization of feature network at t1 (for more detail refer to the paper). 


