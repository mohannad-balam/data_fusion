import pandas as pd
import streamlit as st
import datetime, pytz
import glob, os
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from pandasql import sqldf


excel_type =["vnd.ms-excel","vnd.openxmlformats-officedocument.spreadsheetml.sheet", "vnd.oasis.opendocument.spreadsheet", "vnd.oasis.opendocument.text"]


@st.cache_data()
def data(data, file_type, seperator=None):
    if file_type == "csv":
        data = pd.read_csv(data,parse_dates=True)
        
    elif file_type == "json":
        data = pd.read_json(data)
    
    elif file_type in excel_type:
        data = pd.read_excel(data, parse_dates=True)
    
    elif file_type == "plain":
        try:
            data = pd.read_table(data, sep=seperator)
        except ValueError:
            st.info("If you haven't Type the separator then dont worry about the error this error will go as you type the separator value and hit Enter.")
    if 0 in data.columns or 'Unnamed: 0' in data.columns:
        data.set_index(data.columns[0], inplace=True)
    return data

@st.cache_data()
def seconddata(data, file_type, seperator=None):

    if file_type == "csv":
        data = pd.read_csv(data,parse_dates=True)

    elif file_type == "json":
        data = pd.read_json(data)
    
    elif file_type in excel_type:
        data = pd.read_excel(data,parse_dates=True)
    
    elif file_type == "plain":
        try:
            data = pd.read_table(data, sep=seperator, delimiter=seperator)
        except ValueError:
            st.info("If you haven't Type the separator then dont worry about the error this error will go as you type the separator value and hit Enter.")
    if 0 in data.columns or 'Unnamed: 0' in data.columns:
        data.set_index(data.columns[0], inplace=True)
    return data


def match_elements(list_a, list_b):
    non_match = []
    for i in list_a:
        if i in list_b:
            non_match.append(i)
    return non_match


def download_data(data:pd.DataFrame, label):
    if not data.empty:
        current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        current_time = "{}.{}-{}-{}".format(current_time.date(), current_time.hour, current_time.minute, current_time.second)
        export_data = st.download_button(
                            label="Download {} data as CSV".format(label),
                            data=data.to_csv(encoding='utf-8-sig',index=False).encode('utf-8-sig'),
                            file_name='{}{}.csv'.format(label, current_time),
                            mime='text/csv',
                            help = "When You Click On Download Button You can download your {} CSV File".format(label)
                        )
        return export_data

def get_unique(data:pd.DataFrame):
    col1,col2,col3,col4 = st.columns(4)
    i = 1
    for col_name in data:
        if i == 1:
            with col1:
                st.dataframe(data[col_name].drop_duplicates().reset_index(drop=True))
                i+=1
        elif i == 2:
            with col2:
                st.dataframe(data[col_name].drop_duplicates().reset_index(drop=True))
                i+=1     
        elif i == 3:
            with col3:
                st.dataframe(data[col_name].drop_duplicates().reset_index(drop=True))   
                i+=1
        elif i == 4:
            with col4:
                st.dataframe(data[col_name].drop_duplicates().reset_index(drop=True))   
                i+=1       
        if i == 5:
            i = 1
            col1,col2,col3,col4 = st.columns(4)
            
             
def describe(data):
    global num_category, str_category
    numeric_data = data.select_dtypes(include=[np.number])
    categorical_data = data.select_dtypes(exclude=[np.number])

    num_category = [feature for feature in data.columns if data[feature].dtypes != "O"]
    str_category = [feature for feature in data.columns if data[feature].dtypes == "O"]
    column_with_null_values = data.columns[data.isnull().any()]
    if numeric_data.empty:
        return None, None, categorical_data.describe() , data.shape, data.columns, num_category, str_category, data.isnull().sum(),data.dtypes.astype("str"), data.nunique(), str_category, column_with_null_values
    elif categorical_data.empty:
        return numeric_data.corr(), numeric_data.describe(), None , data.shape, data.columns, num_category, str_category, data.isnull().sum(),data.dtypes.astype("str"), data.nunique(), str_category, column_with_null_values
    return numeric_data.corr(), numeric_data.describe(), categorical_data.describe() , data.shape, data.columns, num_category, str_category, data.isnull().sum(),data.dtypes.astype("str"), data.nunique(), str_category, column_with_null_values
        


def see_outliers(data, num_category_outliers):
    plt.figure(figsize=(12,6))
    flierprops = dict(marker='o', markerfacecolor='purple', markersize=6,
                    linestyle='none', markeredgecolor='black')
    column = num_category_outliers
    box_plot = px.box(data_frame=data, x=column)
    st.plotly_chart(box_plot)
    plot = sns.boxplot(x=column, flierprops=flierprops, data=data)
    fig = plot.get_figure()
    st.pyplot(fig)
    return

def delete_outliers(data, col_name): 
    Q1 = data[col_name].quantile(0.25)
    Q3 = data[col_name].quantile(0.75)
    IQR = Q3 - Q1
    no_outliers = data[(data[col_name] >= Q1 - 1.5 * IQR) & (data[col_name] <= Q3 + 1.5 * IQR)]
    return no_outliers.reset_index(drop=True)


def replace_categorical(data:pd.DataFrame, selected_column, to_replace, val):
    replaced = data.copy(deep=True)
    if val == 'Null':
        replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=np.nan)
    else:        
        replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=val) 
    replaced[selected_column] = pd.to_numeric(replaced[selected_column], errors='ignore')  
    return replaced     


def replace_numeric(data:pd.DataFrame, selected_column, to_replace, val):
    replaced = data.copy(deep=True)
    if val == -1:
        replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=np.nan)  
    else:        
        replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=val)
    replaced[selected_column] = pd.to_numeric(replaced[selected_column], errors='ignore')   
    return replaced

def drop_items(data, selected_name):
    droped =  data.drop(selected_name, axis = 1)
    return droped


def filter_data(data, selected_column, selected_name):
    if selected_name == []:
        filtered_data = data
    else:
        filtered_data = data[~ data[selected_column].isin(selected_name)]
    return filtered_data.reset_index(drop=True)


def num_filter_data(data, start_value, end_value, column, param):
    if param == "Delete data inside the range":
        if column in num_category:
            num_filtered_data = data[~data[column].isin(range(int(start_value), int(end_value)+1))]
    else:
        if column in num_category:
            num_filtered_data = data[data[column].isin(range(int(start_value), int(end_value)+1))]
    
    return num_filtered_data.reset_index(drop=True)


def rename_columns(data, column_names):
    rename_column = data.rename(columns=column_names)
    return rename_column


def handling_missing_values(data:pd.DataFrame, option_type, col_names=None):
    if option_type == "Drop all null value rows":
        droped = data.dropna()
    elif option_type == "Only Drop Rows that contanines all null values":
        droped = data.dropna(how="all")
    elif option_type == 'Only Drop Null Rows For a Specific Column':
        droped = data.dropna(subset=[col for col in col_names])
    return droped.reset_index(drop=True)

def fill_missing_data(data:pd.DataFrame, option_type, col_name=None, to_rep=None):
    filled = data.copy(deep=True)
    if option_type == 'Custom Fill':
        filled[col_name] = data[col_name].fillna(to_rep)
    elif option_type == 'Backward Fill':
        filled[col_name] = data[col_name].fillna(method='bfill')
    elif option_type == 'Forward Fill':
        filled[col_name] = data[col_name].fillna(method='ffill')
    elif option_type == 'Most Appeared Fill':
        filled[col_name] = data[col_name].fillna(data[col_name].mode()[0])
    elif option_type == 'Mean Fill':
        filled[col_name] = data[col_name].fillna(data[col_name].mean())    
    return filled

def data_wrangling(data1, data2=None, key=None, usertype=None):
    if usertype == "Merging On Index":
        data = pd.merge(data1, data2, on=key, suffixes=("_extra", "_extra0"))
        data = data[data.columns.drop(list(data.filter(regex='_extra')))]
        return data
    
    elif usertype == "Concatenating On Axis":
        data = pd.concat([data1, data2], ignore_index=True)
         
    return data

def group_data(data:pd.DataFrame, col_names, group_type, col_name=None):
    if group_type == "mean":
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].mean().round()
    elif group_type == "median":
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].median().round()
    elif group_type == "des":
        grouped = data.groupby([col for col in col_names]).count()
    return grouped

def clear_image_cache():
    removing_files = glob.glob('temp/*.png')
    for i in removing_files:
        os.remove(i)   
    

def get_non_nulls(data):
    selection = data
    selection = [s for s in selection if pd.isnull(s) == False]
    return selection

def get_query(data:pd.DataFrame,query,query_type):
    qr = data.copy(deep=True)
    if query_type == 'Pure Python':
        res =  qr.query(query).reset_index(drop=True)
    elif query_type == 'SQL':
        res =  sqldf(query=query, env=locals())
    return res

def sql_query(data:pd.DataFrame,query):
    qr = data.copy(deep=True)
    return sqldf(query=query, env=locals())

def python_query(data:pd.DataFrame,query):
    qr = data.copy(deep=True)
    res = qr.query(query).reset_index(drop=True)
    return res
