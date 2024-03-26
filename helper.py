from sys import prefix
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime, pytz
import glob, os
import numpy as np


excel_type =["vnd.ms-excel","vnd.openxmlformats-officedocument.spreadsheetml.sheet", "vnd.oasis.opendocument.spreadsheet", "vnd.oasis.opendocument.text"]


@st.cache_data()
def data(data, file_type, seperator=None):

    if file_type == "csv":
        data = pd.read_csv(data, encoding='utf-8-sig')
        
    elif file_type == "json":
        data = pd.read_json(data)
        data = (data["devices"].apply(pd.Series))
    
    elif file_type in excel_type:
        data = pd.read_excel(data,index_col=0)
        st.sidebar.info("If you are using Excel file so there could be chance of getting minor error(temporary sollution: avoid the error by removing overview option from input box) so bear with it. It will be fixed soon")
    
    elif file_type == "plain":
        try:
            data = pd.read_table(data, sep=seperator, encoding='utf-8-sig')
        except ValueError:
            st.info("If you haven't Type the separator then dont worry about the error this error will go as you type the separator value and hit Enter.")

    return data

@st.cache_data()
def seconddata(data, file_type, seperator=None):

    if file_type == "csv":
        data = pd.read_csv(data,encoding='utf-8-sig',parse_dates=True)

    elif file_type == "json":
        data = pd.read_json(data,encoding='utf-8-sig')
        data = (data["devices"].apply(pd.Series))
    
    elif file_type in excel_type:
        data = pd.read_excel(data)
        st.sidebar.info("If you are using Excel file so there could be chance of getting minor error(temporary sollution: avoid the error by removing overview option from input box) so bear with it. It will be fixed soon")
    
    elif file_type == "plain":
        try:
            data = pd.read_table(data, sep=seperator,encoding='utf-8-sig')
        except ValueError:
            st.info("If you haven't Type the separator then dont worry about the error this error will go as you type the separator value and hit Enter.")

    return data


def match_elements(list_a, list_b):
    non_match = []
    for i in list_a:
        if i in list_b:
            non_match.append(i)
    return non_match


def download_data(data, label):
    if not data.empty:
        current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        current_time = "{}.{}-{}-{}".format(current_time.date(), current_time.hour, current_time.minute, current_time.second)
        export_data = st.download_button(
                            label="Download {} data as CSV".format(label),
                            data=data.to_csv(encoding='utf-8-sig',index=False),
                            file_name='{}{}.csv'.format(label, current_time),
                            mime='text/csv',
                            help = "When You Click On Download Button You can download your {} CSV File".format(label)
                        )
        return export_data


def describe(data):
    global num_category, str_category
    numeric_data = data.select_dtypes(include=[np.number])
    categorical_data = data.select_dtypes(exclude=[np.number])

    num_category = [feature for feature in data.columns if data[feature].dtypes != "O"]
    str_category = [feature for feature in data.columns if data[feature].dtypes == "O"]
    column_with_null_values = data.columns[data.isnull().any()]
    if numeric_data.empty:
        return None, categorical_data.describe() , data.shape, data.columns, num_category, str_category, data.isnull().sum(),data.dtypes.astype("str"), data.nunique(), str_category, column_with_null_values
    elif categorical_data.empty:
        return numeric_data.describe(), None , data.shape, data.columns, num_category, str_category, data.isnull().sum(),data.dtypes.astype("str"), data.nunique(), str_category, column_with_null_values
    return numeric_data.describe(), categorical_data.describe() , data.shape, data.columns, num_category, str_category, data.isnull().sum(),data.dtypes.astype("str"), data.nunique(), str_category, column_with_null_values
        


def outliers(data, num_category_outliers):
    plt.figure(figsize=(12,6))
    flierprops = dict(marker='o', markerfacecolor='purple', markersize=6,
                    linestyle='none', markeredgecolor='black')
    
    path_list = []
    for i in range(len(num_category_outliers)):
        
        column = num_category_outliers[i]
        plt.xlim(min(data[column]), max(data[column])) 
        plt.title("Checking Outliers for {} Column".format(column))
        plot = sns.boxplot(x=column, flierprops=flierprops, data=data)
        fig = plot.get_figure()

        path = 'temp/pic{}.png'.format(i)
        fig.savefig(path)
        path_list.append(path)

    return path_list

def replace_data(data:pd.DataFrame, selected_column, to_replace, val):
    replaced = data.copy(deep=True)
    if type(to_replace[0]) == str:
        if val == 'Null':
            replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=np.nan)
        else:        
            replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=val)    
    elif type(to_replace[0]) == np.int64 or type(to_replace[0]) == np.float64:
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
    return filtered_data


def num_filter_data(data, start_value, end_value, column, param):
    if param == "Delete data inside the range":
        if column in num_category:
            num_filtered_data = data[~data[column].isin(range(int(start_value), int(end_value)+1))]
    else:
        if column in num_category:
            num_filtered_data = data[data[column].isin(range(int(start_value), int(end_value)+1))]
    
    return num_filtered_data


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
    # elif option_type == "Filling in Missing Values":
    #     data = data.fillna(dict_value)
    return droped

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

def data_wrangling(data1, data2, key, usertype):
    if usertype == "Merging On Index":
        data = pd.merge(data1, data2, on=key, suffixes=("_extra", "_extra0"))
        data = data[data.columns.drop(list(data.filter(regex='_extra')))]
        return data
    
    elif usertype == "Concatenating On Axis":
        data = pd.concat([data1, data2], ignore_index=True)
    return data



def clear_image_cache():
    removing_files = glob.glob('temp/*.png')
    for i in removing_files:
        os.remove(i)   
    

def get_non_nulls(data):
    selection = data
    selection = [s for s in selection if pd.isnull(s) == False]
    return selection
     