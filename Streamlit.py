import streamlit as st
import requests
import pandas as pd 

st.title("SHL Assessment Recommender")

query = st.text_area("Enter your job description or skills needed:")

if st.button("Recommend"):
    with st.spinner("Thinking..."):
        response = requests.post(
            "http://localhost:8000/api/v1/shl/query",
            json={"query": query}
        )
        print(response)
        data = response.json()

        rows = []
        for item in data:
            metadata = item.get('metadata', {})
            test_types = metadata.get('TestTypes', [])
            
            row = {
                'Assessment': item['text'],
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