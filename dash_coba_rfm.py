#!/usr/bin/env python
# coding: utf-8

# ## Menyiapkan DataFrame

# ### Mengunduh Library yang Dibutuhkan

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')


# ### Membuat Helper Function

# In[2]:


def create_city_counts_df(df):
    city_counts_df = df.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=False)
    return city_counts_df


# In[3]:


def create_state_counts_df(df):
    state_counts_df = df.groupby(by="customer_state").customer_id.nunique().sort_values(ascending=False)
    return state_counts_df


# In[4]:


def create_delivery_df(df):
    delivery_df = df.groupby(by="delivery_status").order_id.nunique().sort_values(ascending=False)
    return delivery_df


# In[5]:


def create_seller_tinggi_df(df):
    seller_tinggi_df = df.groupby(by="seller_id").revenue.sum().sort_values(ascending=False).reset_index()
    return seller_tinggi_df


# In[6]:


def create_seller_rendah_df(df):
    seller_rendah_df = df.groupby(by="seller_id").revenue.sum().sort_values(ascending=False).reset_index()
    return seller_rendah_df


# In[7]:


def create_product_best_seller_df(df):
    product_best_seller_df = df.groupby(by="product_id").order_item_id.sum().sort_values(ascending=False).reset_index()
    return product_best_seller_df


# In[8]:


def create_monthly_orders_df(df):
    # Memastikan kolom "order_purchase_timestamp" memiliki tipe data datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    # Resample data berdasarkan bulan
    monthly_orders_df = df.resample(rule="M", on="order_purchase_timestamp").agg({
    "order_id": "nunique",
    "revenue": "sum"
    })

    # # Memformat indeks untuk menampilkan format tahun dan bulan
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')

    # Reset indeks
    monthly_orders_df = monthly_orders_df.reset_index()

    # Mengubah nama kolom
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "revenue": "revenue"
    }, inplace=True)

    return monthly_orders_df


# In[9]:


def create_rfm_df(df):
    analysis_date = df["order_purchase_timestamp"].max()
    rfm_df = df.groupby("customer_id").agg({
    "order_purchase_timestamp": lambda x: (analysis_date - x.max()).days,
    "order_id": "count",
    "revenue": "sum"
}).reset_index()
    # Memberi nama kolom sesuai RFM
    rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

    return rfm_df


# ### Load Data all_data

# In[10]:


all_df = pd.read_csv("all_dataa.csv")


# In[11]:


all_df.head()


# In[12]:


#memperbaiki tipe data
datetime_columns = ["order_purchase_timestamp"]

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)


# ### Membuat Komponen Filter 

# In[13]:


# Assuming 'order_purchase_timestamp' is a datetime column in 'all_df'
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


# In[14]:


main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]


# In[15]:


#helper code
city_counts_df = create_city_counts_df(main_df)
state_counts_df = create_state_counts_df(main_df)
delivery_df = create_delivery_df(main_df)
seller_tinggi_df = create_seller_tinggi_df(main_df)
seller_rendah_df = create_seller_rendah_df(main_df)
product_best_seller_df = create_product_best_seller_df(main_df)
monthly_orders_df = create_monthly_orders_df(main_df)
rfm_df = create_rfm_df(main_df)


# ## Melengkapi Dashboard dengan Berbagai Visualisasi Data

# In[16]:


#header
st.header('E-Commerce Performance Insights Dashboard')


# In[17]:


st.subheader("Customer Demographics")
 
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    top_five = city_counts_df.head(5)
    colors = ["#4CAF50", "#C8E6C9", "#C8E6C9", "#C8E6C9", "#C8E6C9"]

    top_five.plot(kind='bar', color=colors)
    plt.title('Customer Demographics by City', size=40)
    plt.xticks(rotation=45, ha='right')  # Optional: agar label sumbu x tidak tumpang tindih
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    top_five = state_counts_df.head(5)
    top_five.plot(kind='bar', color=colors)
    plt.title('Customer Demographics by State', size=40)
    plt.xticks(rotation=45, ha='right')  # Optional: agar label sumbu x tidak tumpang tindih
    st.pyplot(fig)


# In[18]:


st.subheader('Monthly Orders & Revenue Performance')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax=plt.subplots(nrows=1, ncols=2, figsize=(20, 5))

# Convert the columns to NumPy arrays
timestamps = monthly_orders_df["order_purchase_timestamp"].values
order_counts = monthly_orders_df["order_count"].values
revenue = monthly_orders_df["revenue"].values

# Plot using NumPy arrays
ax[0].plot(timestamps, order_counts, marker='o', linewidth=2, color="#90CAF9")
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=15)

# Plot using NumPy arrays
ax[1].plot(timestamps, revenue, marker='o', linewidth=2, color="#90CAF9")
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=15)

st.pyplot(fig)


# In[19]:


st.subheader('Delivery Status Distribution')

colors = ["#4CAF50", "#C8E6C9", "#C8E6C9"]
fig, ax = plt.subplots(figsize=(10, 5))

plt.pie(delivery_df, autopct='%1.1f%%', colors=colors, startangle=910)
plt.legend(delivery_df.index, title="Delivery Status", loc="upper right", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=13)
st.pyplot(fig)


# In[20]:


st.subheader("Best and Worst Performing Seller by Total Revenue")

fig, ax=plt.subplots(nrows=1, ncols=2, figsize=(20, 5))
colors = ["#4CAF50", "#C8E6C9", "#C8E6C9"]

sns.barplot(x="revenue", y="seller_id", data=seller_tinggi_df.head(3), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Seller", loc="center", fontsize=30)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="revenue", y="seller_id", data=seller_rendah_df.head(3), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Worst Performing Seller", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=12)
ax[1].invert_xaxis() #rata kanan
ax[1].yaxis.set_label_position("right") #posisi label product name
ax[1].yaxis.tick_right()  #posisi label product name

st.pyplot(fig)


# In[21]:


st.subheader("Best Performing Products")

fig, ax=plt.subplots(figsize=(15,10))
colors = ["#4CAF50", "#C8E6C9", "#C8E6C9", "#C8E6C9", "#C8E6C9"]

sns.barplot(x='order_item_id', y='product_id', data=product_best_seller_df.head(5), palette=colors, ax=ax)

plt.xlabel('Total Order', size=15)
plt.ylabel('Product ID', size=15)
plt.title("Best Performing Products by Total Orders", size=20)

st.pyplot(fig)


# In[22]:


st.subheader("Customer Segmentation")

# Menentukan Nilai Binning Range
recency_bins = [0, 119, 224, 354, 730]
frequency_bins = [0, 1, 22]
monetary_bins = [0, 48, 90, 160, 60480]

# Menerapkan binning range dengan menggunakan pd.cut()
rfm_df["R"] = pd.cut(rfm_df["recency"], bins=recency_bins, labels=["R4", "R3", "R2", "R1"])
rfm_df["F"] = pd.cut(rfm_df["frequency"], bins=frequency_bins, labels=["F1", "F2"])
rfm_df["M"] = pd.cut(rfm_df["monetary"], bins=monetary_bins, labels=["M1", "M2", "M3", "M4"])

# Menggabungkan RFM segment
rfm_df["RFM_Segment"] = rfm_df["R"].astype(str) + rfm_df["F"].astype(str) + rfm_df["M"].astype(str)

rfm_df[["customer_id", "recency", "frequency", "monetary", "RFM_Segment"]].head()

# Membuat kolom customer_segment
rfm_df["Customer_Segment"] = "Undefined"

# Mendefinisikan kondisi sesuai dengan segmentasi pelanggan yang diinginkan
champion_condition = (rfm_df["RFM_Segment"] == "R4F2M4")
loyal_condition = (rfm_df["RFM_Segment"] == "R3F2M4")
at_risk_condition = (rfm_df["RFM_Segment"] == "R2F1M2")
lost_condition = (rfm_df["RFM_Segment"] == "R1F1M1")

# Menetapkan segmentasi berdasarkan kondisi yang telah didefinisikan
rfm_df.loc[champion_condition, "Customer_Segment"] = "Champion Customers"
rfm_df.loc[loyal_condition, "Customer_Segment"] = "Loyal Customers"
rfm_df.loc[at_risk_condition, "Customer_Segment"] = "At Risk Customers"
rfm_df.loc[lost_condition, "Customer_Segment"] = "Lost Customers"

# Karna segment undefined tidak menggambarkan segmentasi pelanggan, maka dipilih segmentasi pelanggan dengan 4 kategori yang telah ditentukan
selected_segments = ["Champion Customers", "Loyal Customers", "At Risk Customers", "Lost Customers"]
selected_df = rfm_df[rfm_df["Customer_Segment"].isin(selected_segments)]

# Menghitung jumlah pelanggan dalam setiap segment
selected_df_counts = selected_df["Customer_Segment"].value_counts()

# Menghitung jumlah pelanggan dalam setiap segment
selected_df_counts = selected_df["Customer_Segment"].value_counts()

# Visualisasi data jumlah pelanggan dalam setiap segment
fig, ax=plt.subplots(figsize=(15,10))

sns.barplot(x=selected_df_counts.index, y=selected_df_counts.values, palette="viridis", ax=ax)
plt.title("Customer Segmentation Based on Number of Customers", size=20)
st.pyplot(fig)


# In[ ]:




