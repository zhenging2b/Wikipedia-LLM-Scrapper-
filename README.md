# Wikipedia-LLM-Scrapper and Research Assistance
## Introduction
This project uses crawl4ai, openai strucutured outputs and function calling to help scrape and analyse wikipedia articles.The chosen examples are subfields of Artificial Intelligence. These fields are chosen because they are usually learned independently and sometimes the connection may not be so obvious. This Wikipedia Research assistance scrapes Wikipedia articles on selected topics and allow them to be compared. 

The general flow is as follows.
Scrap Wikipedia Article -> Process to Structured Outputs with openAI -> Function calling for answering natural queries. A full example can be found under the `notebook\notebook tutorial.ipynb`, and a working `basic_usage.py`. 

## Project structure
Under the folder `wikipedia_ai_scrapper`, the `utils.py` and `models.py` contains the methods and models for structured outputs respectively. They can be modified accordingly to capture and answer different aspects of a particular topic. In this example, 7 features are captured for each Wikipedia article. `main_topic`, `summary`, `evolution_timeline`, `key_innovations`, `major_contributors`, `main_techniques` and `applications`. 
Two methods are made to help with the research, namely `trace_evolution` and `compare_techonologies` 

# Installation and setup
Install required libraries
```commandline
pip install requirements.txt
playwright install
```
Create a .env folder with your openAI API key in the following format 

```
OPENAI_API_KEY=your_open_api_key
CACHE_DIR=./data/cache
OUTPUT_DIR=./data/outputs
```

After this, you can look through the notebook or run `basic_usage.py`