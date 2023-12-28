import streamlit as st
import pandas as pd
import plotly.express as px
from pandas.tseries.offsets import MonthEnd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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

# Modified Plotly monthly plot with dual-axis
fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])

# Add Product Gross Revenue to the main y-axis
fig_monthly.add_trace(
    go.Bar(
        x=monthly_data['month'], 
        y=monthly_data['Product Gross Revenue'],
        name='Bruttó érték',
        text=monthly_data['Product Gross Revenue'],
        textposition='outside'
    ),
    secondary_y=False,
)

# Add Order ID to the secondary y-axis
fig_monthly.add_trace(
    go.Scatter(
        x=monthly_data['month'], 
        y=monthly_data['Order ID'],
        name='Eladott Megrendelések Száma',
        mode='lines+markers'
    ),
    secondary_y=True,
)

# Set y-axes titles
fig_monthly.update_yaxes(title_text="Bruttó érték", secondary_y=False)
fig_monthly.update_yaxes(title_text="Eladott Megrendelések Száma", secondary_y=True)

# Set other chart properties
fig_monthly.update_layout(
    title='Havi Bruttó Értékek és Eladott Megrendelések Száma',
    xaxis_title='Hónap'
)

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
