import streamlit as st
import pandas as pd
from pandas.tseries.offsets import MonthEnd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('eladasok.txt', delimiter='\t')
    data['Date Created'] = pd.to_datetime(data['Date Created'])
    data['month'] = data['Date Created'].dt.to_period('M').dt.to_timestamp('M') + MonthEnd(0)
    data['year'] = data['Date Created'].dt.year
    return data

data = load_data()

# Streamlit title
st.title('Sales Data Visualization')

# Time Series Analysis (Monthly Sales)
monthly_sales = data.groupby('month').agg({'Product Gross Revenue': 'sum'}).reset_index()
fig_time_series = px.line(monthly_sales, x='month', y='Product Gross Revenue', title='Monthly Sales Over Time')
st.plotly_chart(fig_time_series)

# Monthly summary with year
monthly_data = data.groupby(['year', 'month']).agg({
    'Product Gross Revenue': 'sum', 
    'Order ID': 'nunique'
}).reset_index()

# Calculate Average Order Value
monthly_data['Average Order Value'] = monthly_data['Product Gross Revenue'] / monthly_data['Order ID']

# Converting 'month' to month names and 'year' to string for plotting
monthly_data['month_name'] = monthly_data['month'].dt.strftime('%B')
monthly_data['year_str'] = monthly_data['year'].astype(str)

# Yearly summary
yearly_data = data.groupby('year').agg({
    'Product Gross Revenue': 'sum', 
    'Order ID': 'nunique'
}).reset_index()

# Dual-axis monthly plot
fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])

# Gross Revenue bar chart
fig_monthly.add_trace(
    go.Bar(
        x=monthly_data['month'], 
        y=monthly_data['Product Gross Revenue'],
        name='Gross Revenue',
        text=monthly_data['Product Gross Revenue'],
        textposition='outside'
    ),
    secondary_y=False,
)

# Number of Orders line chart
fig_monthly.add_trace(
    go.Scatter(
        x=monthly_data['month'], 
        y=monthly_data['Order ID'],
        name='Number of Orders',
        mode='lines+markers'
    ),
    secondary_y=True,
)

# Update axes titles
fig_monthly.update_yaxes(title_text="Gross Revenue", secondary_y=False)
fig_monthly.update_yaxes(title_text="Number of Orders", secondary_y=True)
fig_monthly.update_layout(
    title='Monthly Gross Revenue and Number of Orders',
    xaxis_title='Month'
)
st.plotly_chart(fig_monthly)

# Yearly plot
fig_yearly = px.bar(
    yearly_data,
    x='year',
    y='Product Gross Revenue',
    text='Product Gross Revenue',
    hover_data=['Order ID'],
    labels={'Product Gross Revenue': 'Gross Revenue', 'year': 'Year', 'Order ID': 'Number of Orders'},
    title='Annual Gross Revenue and Number of Orders'
)
fig_yearly.update_traces(texttemplate='%{text:.2s}', textposition='outside')
fig_yearly.update_xaxes(type='category')
st.plotly_chart(fig_yearly)

# Plot for Product Gross Revenue
fig_product_gross_revenue = px.line(
    monthly_data,
    x='month_name',
    y='Product Gross Revenue',
    color='year_str',
    labels={'month_name': 'Month', 'Product Gross Revenue': 'Product Gross Revenue', 'year_str': 'Year'},
    title='Monthly Product Gross Revenue Over the Years'
)
st.plotly_chart(fig_product_gross_revenue)

# Plot for Number of Unique Orders
fig_unique_orders = px.line(
    monthly_data,
    x='month_name',
    y='Order ID',
    color='year_str',
    labels={'month_name': 'Month', 'Order ID': 'Number of Unique Orders', 'year_str': 'Year'},
    title='Monthly Number of Unique Orders Over the Years'
)
st.plotly_chart(fig_unique_orders)

# Plot for Average Order Value
fig_avg_order_value = px.line(
    monthly_data,
    x='month_name',
    y='Average Order Value',
    color='year_str',
    labels={'month_name': 'Month', 'Average Order Value': 'Average Order Value', 'year_str': 'Year'},
    title='Monthly Average Order Value Over the Years'
)
st.plotly_chart(fig_avg_order_value)

# Category-wise Sales Analysis (Top 20 Categories)
category_sales = data.groupby('Category Name').agg({'Product Gross Revenue': 'sum'}).reset_index()
category_sales = category_sales.sort_values(by='Product Gross Revenue', ascending=False).head(20)
fig_category_sales = px.bar(category_sales, x='Category Name', y='Product Gross Revenue', title='Top 20 Categories by Sales')
st.plotly_chart(fig_category_sales)

# Product Performance Analysis (Top 20 Products)
product_performance = data.groupby('Product Name').agg({'Product Gross Revenue': 'sum'}).sort_values(by='Product Gross Revenue', ascending=False).head(20)
fig_product_performance = px.bar(product_performance, x=product_performance.index, y='Product Gross Revenue', title='Top 20 Products by Sales')
st.plotly_chart(fig_product_performance)
