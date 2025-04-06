import streamlit as st
import requests
import pandas as pd 

st.title("SHL Assessment Recommender")

query = st.text_area("Enter your job description or skills needed:")

if st.button("Recommend"):
    with st.spinner("Thinking..."):
        response = requests.post(
            "https://shl-assessment-recommendor-wmhq.onrender.com/api/v1/shl/query",
            json={"query": query}
        )
        data = response.json()

        rows = []
        for item in data:
            metadata = item.get('metadata', {})
            test_types = metadata.get('TestTypes', [])
            
            row = {
                'Score': f"{item['score']:.2f}",
                'Name': metadata.get('name', 'N/A'),
                'Duration (mins)': metadata.get('duration', 'N/A'),
                'URL': metadata.get('url', 'N/A'),
                'Remote Testing': metadata.get('RemoteTesting', 'N/A'),
                'Adaptive/IRT Support': metadata.get('Adaptive/IRT Support', 'N/A'),
                'Test Types': ', '.join(test_types) if test_types else 'N/A'
            }
            rows.append(row)
        
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df.style.set_properties(**{'width': '200px'}))  
        else:
            st.warning("No results found")