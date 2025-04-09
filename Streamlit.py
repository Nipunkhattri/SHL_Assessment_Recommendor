import streamlit as st
import requests
import pandas as pd 

st.title("SHL Assessment Recommender")

query = st.text_area("Enter your job description or skills needed:")

if st.button("Recommend"):
    with st.spinner("Thinking..."):
        response = requests.post(
            "https://shl-assessment-recommendor-wmhq.onrender.com/recommend",
            # "http://localhost:8000/recommend",
            json={"query": query}
        )
        data = response.json()

        rows = []
        for assessment in data["recommended_assessments"]:
            row = {
                'URL': assessment['url'],
                'Description': assessment['description'],
                'Duration (mins)': assessment['duration'],
                'Remote Testing': assessment['remote_support'],
                'Adaptive Support': assessment['adaptive_support'],
                'Test Types': ', '.join(assessment['test_type']) if assessment['test_type'] else 'N/A'
            }
            rows.append(row)
        
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df.style.set_properties(**{'width': '200px'}))  
        else:
            st.warning("No results found")