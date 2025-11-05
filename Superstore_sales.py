import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from kaggle.api.kaggle_api_extended import KaggleApi
from jinja2 import Template

# 1️⃣ Kaggle API Download

api = KaggleApi()
api.authenticate()

dataset = "vivek468/superstore-dataset-final"
dest_folder = r"C:\Users\lahaa\PycharmProjects\PythonProject"

api.dataset_download_files(dataset, path=dest_folder, unzip=True)

csv_files = [f for f in os.listdir(dest_folder) if f.endswith('.csv')]
if not csv_files:
    raise FileNotFoundError("No CSV file found")
csv_path = os.path.join(dest_folder, csv_files[0])

# 2️⃣ Load Dataset

df = pd.read_csv(csv_path, encoding='ISO-8859-1')
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])
df['Order Year'] = df['Order Date'].dt.year
df['Order Month'] = df['Order Date'].dt.month
df['Profit Margin'] = df['Profit'] / df['Sales']


# 3️⃣ Generate Charts

charts_folder = os.path.join(dest_folder, "charts")
os.makedirs(charts_folder, exist_ok=True)

# Category Sales
plt.figure(figsize=(6,4))
category_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
sns.barplot(x=category_sales.index, y=category_sales.values)
plt.title("Sales by Category")
plt.ylabel("Sales")
plt.tight_layout()
cat_sales_path = os.path.join(charts_folder, "category_sales.png")
plt.savefig(cat_sales_path)
plt.close()

# Profit by Region
plt.figure(figsize=(6,4))
region_profit = df.groupby('Region')['Profit'].sum()
sns.barplot(x=region_profit.index, y=region_profit.values)
plt.title("Profit by Region")
plt.ylabel("Profit")
plt.tight_layout()
region_profit_path = os.path.join(charts_folder, "region_profit.png")
plt.savefig(region_profit_path)
plt.close()

# Discount vs Profit
plt.figure(figsize=(6,4))
sns.scatterplot(x='Discount', y='Profit', data=df)
plt.title("Discount vs Profit")
plt.tight_layout()
discount_profit_path = os.path.join(charts_folder, "discount_profit.png")
plt.savefig(discount_profit_path)
plt.close()

# Monthly Sales Trend
plt.figure(figsize=(6,4))
monthly_sales = df.groupby(['Order Year','Order Month'])['Sales'].sum()
monthly_sales.plot(kind='line')
plt.title("Monthly Sales Trend")
plt.ylabel("Sales")
plt.tight_layout()
monthly_sales_path = os.path.join(charts_folder, "monthly_sales.png")
plt.savefig(monthly_sales_path)
plt.close()

# 4️⃣ Prepare Tables

category_table = df.groupby('Category')[['Sales','Profit']].sum().reset_index()
subcat_table = df.groupby('Sub-Category')[['Sales','Profit']].sum().reset_index()
top_customers = df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()

# 5️⃣ Generate HTML Report

html_template = """
<html>
<head><title>Superstore Analysis Report</title></head>
<body>
<h1>Superstore Analysis Report</h1>

<h2>Category Sales</h2>
<img src="{{cat_sales}}" width="600">

<h2>Profit by Region</h2>
<img src="{{region_profit}}" width="600">

<h2>Discount vs Profit</h2>
<img src="{{discount_profit}}" width="600">

<h2>Monthly Sales Trend</h2>
<img src="{{monthly_sales}}" width="600">

<h2>Category Summary</h2>
{{category_table}}

<h2>Sub-Category Summary</h2>
{{subcat_table}}

<h2>Top 10 Customers</h2>
{{top_customers}}

</body>
</html>
"""

template = Template(html_template)
html_content = template.render(
    cat_sales=cat_sales_path,
    region_profit=region_profit_path,
    discount_profit=discount_profit_path,
    monthly_sales=monthly_sales_path,
    category_table=category_table.to_html(index=False),
    subcat_table=subcat_table.to_html(index=False),
    top_customers=top_customers.to_html(index=False)
)

report_path = os.path.join(dest_folder, "Superstore_Report.html")
with open(report_path, "w") as f:
    f.write(html_content)

print(f"Report generated successfully: {report_path}")


