import streamlit as st
import pandas as pd
from pandas.tseries.offsets import MonthEnd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# Load sales data
@st.cache_data
def load_sales_data():
    sales_data = pd.read_csv('sales.txt', delimiter='\t')
    sales_data['Date Created'] = pd.to_datetime(sales_data['Date Created'])
    sales_data['month'] = sales_data['Date Created'].dt.to_period('M').dt.to_timestamp('M') + MonthEnd(0)
    sales_data['year'] = sales_data['Date Created'].dt.year
    return sales_data

# Load postal code data
@st.cache_data
def load_postal_code_data():
    postal_code_data = pd.read_csv('postal_codes.csv', delimiter=',')
    return postal_code_data

# Function to calculate returning customer ratio
def calculate_returning_customer_ratio(sales_data):
    unique_customer_hashes = sales_data['Customer Email Hash'].nunique()
    returning_customers_count = sales_data.groupby('Customer Email Hash')['Order ID'].nunique()
    returning_customers_count = returning_customers_count[returning_customers_count > 1].count()
    returning_customer_ratio = returning_customers_count / unique_customer_hashes
    return returning_customer_ratio

sales_data = load_sales_data()
postal_code_data = load_postal_code_data()

# Streamlit title
st.title('📈 Sales Data Visualization')

# Calculate and display returning customer ratio
returning_ratio = calculate_returning_customer_ratio(sales_data)
st.write(f"Ratio of Returning Customers: {returning_ratio:.2%}")

# Merge sales data with postal code data
merged_data = pd.merge(sales_data, postal_code_data, how='left', left_on='Shipping Postcode', right_on='Postal_Code')

# Time Series Analysis (Monthly Sales)
monthly_sales = sales_data.groupby('month').agg({'Product Gross Revenue': 'sum'}).reset_index()
fig_time_series = px.line(monthly_sales, x='month', y='Product Gross Revenue', title='Monthly Sales Over Time')
st.plotly_chart(fig_time_series)

# Monthly summary with year
monthly_data = sales_data.groupby(['year', 'month']).agg({
    'Product Gross Revenue': 'sum', 
    'Order ID': 'nunique'
}).reset_index()

# Calculate Average Order Value
monthly_data['Average Order Value'] = monthly_data['Product Gross Revenue'] / monthly_data['Order ID']

# Converting 'month' to month names and 'year' to string for plotting
monthly_data['month_name'] = monthly_data['month'].dt.strftime('%B')
monthly_data['year_str'] = monthly_data['year'].astype(str)

# Yearly summary
yearly_data = sales_data.groupby('year').agg({
    'Product Gross Revenue': 'sum', 
    'Order ID': 'nunique'
}).reset_index()

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

# Category-wise Sales Analysis with grouped categories
def extract_secondary_category(category_chain):
    parts = category_chain.split(' > ')
    if len(parts) > 1:
        return parts[1]
    else:
        return "N/A"

sales_data['Secondary Category'] = sales_data['Category Name'].apply(extract_secondary_category)
category_performance = sales_data.groupby('Secondary Category').agg({'Product Gross Revenue': 'sum'}).reset_index()
category_performance = category_performance.sort_values(by='Product Gross Revenue', ascending=False)
fig_secondary_category_performance = px.bar(category_performance, x='Secondary Category', y='Product Gross Revenue', title='Performance by Category groups')
st.plotly_chart(fig_secondary_category_performance)

# Category-wise Sales Analysis (Top 20 Categories)
category_sales = sales_data.groupby('Category Name').agg({'Product Gross Revenue': 'sum'}).reset_index()
category_sales = category_sales.sort_values(by='Product Gross Revenue', ascending=False).head(20)
fig_category_sales = px.bar(category_sales, x='Category Name', y='Product Gross Revenue', title='Top 20 Categories by Sales')
st.plotly_chart(fig_category_sales)

# Product Performance Analysis (Top 20 Products)
product_performance = sales_data.groupby('Product Name').agg({'Product Gross Revenue': 'sum'}).sort_values(by='Product Gross Revenue', ascending=False).head(20)
fig_product_performance = px.bar(product_performance, x=product_performance.index, y='Product Gross Revenue', title='Top 20 Products by Sales')
st.plotly_chart(fig_product_performance)

# Geographical Analysis by County
county_sales = merged_data.groupby('County').agg({'Product Gross Revenue': 'sum'}).reset_index()
county_sales = county_sales.sort_values(by='Product Gross Revenue', ascending=False)

# Plotting Sales by County
fig_county_sales = px.bar(county_sales, x='County', y='Product Gross Revenue', title='Sales by County')
st.plotly_chart(fig_county_sales)
