import streamlit as st
import pandas as pd
import plotly.express as px
from pandas.tseries.offsets import MonthEnd

# Load data
@st.cache
def load_data():
    # Load the data with the new column names
    data = pd.read_csv('eladasok.txt', delimiter='\t')  # Adjust delimiter if needed
    data['Date Created'] = pd.to_datetime(data['Date Created'])
    data['month'] = data['Date Created'].dt.to_period('M').dt.to_timestamp('M') + MonthEnd(0)
    data['year'] = data['Date Created'].dt.year
    return data

data = load_data()

# Streamlit title
st.title('Sales Data Visualization')

# Monthly summary
monthly_data = data.groupby('month').agg({
    'Product Gross Revenue': 'sum',  # Assuming this is equivalent to brutto_ertek
    'Order ID': 'nunique'
}).reset_index()

# Yearly summary
yearly_data = data.groupby('year').agg({
    'Product Gross Revenue': 'sum',  # Assuming this is equivalent to brutto_ertek
    'Order ID': 'nunique'
}).reset_index()

# Plotly monthly plot
fig_monthly = px.bar(
    monthly_data, 
    x='month', 
    y='Product Gross Revenue',
    text='Product Gross Revenue',
    hover_data=['Order ID'],
    labels={'Product Gross Revenue': 'Bruttó érték', 'month': 'Hónap', 'Order ID': 'Eladott Megrendelések Száma'},
    title='Havi Bruttó Értékek és Eladott Megrendelések Száma'
)
fig_monthly.update_traces(texttemplate='%{text:.2s}', textposition='outside')
st.plotly_chart(fig_monthly)

# Plotly yearly plot
fig_yearly = px.bar(
    yearly_data,
    x='year',
    y='Product Gross Revenue',
    text='Product Gross Revenue',
    hover_data=['Order ID'],
    labels={'Product Gross Revenue': 'Bruttó érték', 'year': 'Év', 'Order ID': 'Eladott Megrendelések Száma'},
    title='Éves Bruttó Értékek és Eladott Megrendelések Száma'
)
fig_yearly.update_traces(texttemplate='%{text:.2s}', textposition='outside')
st.plotly_chart(fig_yearly)
