import json
from pathlib import Path
import pandas as pd
BASE=Path(__file__).resolve().parents[2]
def model_metrics():
    df=pd.read_csv(BASE/'models/model_comparison.csv')
    return df.to_dict(orient='records')
def metadata():
    return json.loads((BASE/'models/metadata.json').read_text())
def dataset_stats():
    df=pd.read_csv(BASE/'data/spam_data.csv')
    return {'samples':len(df),'spam':int((df.label=='spam').sum()),'ham':int((df.label=='ham').sum()),'spam_rate':round((df.label=='spam').mean()*100,2),'avg_length':round(df.message.str.len().mean(),1),'median_length':round(df.message.str.len().median(),1),'avg_words':round(df.message.str.split().str.len().mean(),1),'vocabulary':len(set(__import__('re').findall(r'\b\w+\b',' '.join(df.message.astype(str)).lower())))}
