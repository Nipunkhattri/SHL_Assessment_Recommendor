# 🔍 SHL Assessment Recommender

An AI-powered recommendation system that helps hiring managers quickly discover the most relevant **SHL assessments** based on natural language queries or job descriptions.

---

## 🚀 Live Demo & API

- 🔗 **Live Demo**: [Hosted Streamlit App](#)
- 🔗 **API Endpoint**: [API URL](#)
- 🔗 **GitHub Repo**: [GitHub](https://github.com/Nipunkhattri/SHL_Assessment_Recommendor)

---

## 🧠 Problem Statement

Hiring managers typically rely on filters or keywords to find assessments—a tedious and time-consuming process.  
This system solves the problem by allowing natural language inputs (e.g., "I need a test for a backend software engineer") or job description links to **automatically fetch and recommend** suitable SHL assessments using an intelligent retrieval pipeline.

---

## 💡 Key Features

- 🔍 Accepts **free-form queries** or **job description URLs/text**
- 🎯 Recommends up to **10 most relevant SHL assessments**
- 📋 Each recommendation includes:
  - Assessment name + clickable URL
  - Remote testing support (✅/❌)
  - Adaptive/IRT support (✅/❌)
  - Duration of the test
  - Type of assessment

- ⚡ Powered by **LLMs**, **Vector Search**, and an intuitive **UI + API** using **Streamlit** and **FastAPI**

---

## 🧰 Tech Stack

| Tool | Purpose |
|------|---------|
| 🧠 OpenAI API | Embedding job descriptions and assessments |
| 🧲 Pinecone | Vector database for similarity search |
| 🧮 `text-embedding-ada-002` | Embedding model |
| 🧱 FastAPI | API backend |
| 🖥️ Streamlit | Web-based interactive frontend |
| 🧼 BeautifulSoup | Web scraping SHL catalog |
| 🧠 LlamaIndex | Query processing and document indexing |

---

## 📁 Project Structure

```bash
SHL_Assessment_Recommendor/
├── app.py                 # FastAPI backend
├── Streamlit.py           # Streamlit frontend
├── catalog_scraper.py     # Scrapes SHL assessment data
├── pipeline.py            # Core logic: embeddings, GPT reranking, retrieval
├── assessments.json       # Structured SHL catalog data
├── models/                # Request/response schemas for API
├── views/                 # Streamlit component views
├── requirements.txt       # Dependencies
```

## 🔍 System Architecture & Approach

### 1. 📦 Data Collection

- SHL assessment catalog is scraped using `catalog_scraper.py`.
- Extracts:
  - Assessment Name  
  - URL  
  - Duration  
  - Remote Testing & IRT Support  
  - Test Type  

### 2. 🔧 Data Preprocessing

- Descriptions are embedded using OpenAI’s `text-embedding-ada-002` model.
- Making scraped data in proper format to create embeddings.
- Stored in Pinecone along with metadata.
- `LlamaIndex` builds the `VectorStoreIndex` from these embeddings.

### 3. 🤖 Query Processing

- User inputs:
  - Free-text query  
  - Job description text  
  - LinkedIn Job URLs *(⚠️ Note: Use BeautifulSoup cautiously as LinkedIn has scraping limitations)*  
- Uses `LlamaIndex`'s retriever for semantic search.
- Filters is applied based on test duration.
- Reranking the result based on GPT Reranker.

### 4. 🎨 Frontend Presentation

- Interactive results via Streamlit.
- Clean UI showing:
  - Clickable assessment names  
  - Remote/IRT tags  
  - Duration and test type  

## 🧪 Setup Instructions

### 1. Clone repo
- git clone https://github.com/Nipunkhattri/SHL_Assessment_Recommendor.git
- cd SHL_Assessment_Recommendor

### 2. Install dependencies
- pip install -r requirements.txt

### 3. Start Streamlit UI
- streamlit run Streamlit.py

### 4. Start FastAPI backend
- fastapi run app.py

