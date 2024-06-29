import pandas as pd
import streamlit as st
import datetime, pytz
import glob, os
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from pandasql import sqldf
import plotly.express as px

excel_type =["vnd.ms-excel","vnd.openxmlformats-officedocument.spreadsheetml.sheet", "vnd.oasis.opendocument.spreadsheet", "vnd.oasis.opendocument.text"]


@st.cache_data()
def data(file_path, file_type, separator=None):
    try:
        if file_type == "csv":
            data = pd.read_csv(file_path, parse_dates=True)
        elif file_type == "json":
            data = pd.read_json(file_path)
        elif file_type in excel_type:  
            data = pd.read_excel(file_path, parse_dates=True)
        elif file_type == "plain":
            try:
                data = pd.read_table(file_path, sep=separator)
            except ValueError:
                st.info("If you haven't Type the separator then dont worry about the error this error will go as you type the separator value and hit Enter.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

    # Check for unnamed index column
    if 0 in data.columns or 'Unnamed: 0' in data.columns:
        data.set_index(data.columns[0], inplace=True)

    return data
  

@st.cache_data()
def seconddata(file_path, file_type, separator=None):
    try:
        if file_type == "csv":
            data = pd.read_csv(file_path, parse_dates=True)
        elif file_type == "json":
            data = pd.read_json(file_path)
        elif file_type in ["xlsx", "xls"]:  
            data = pd.read_excel(file_path, parse_dates=True)
        elif file_type == "plain":
            try:
                data = pd.read_table(file_path, sep=separator, delimiter=separator)
            except ValueError:
                st.info("If you haven't Type the separator then dont worry about the error this error will go as you type the separator value and hit Enter.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

    # Check for unnamed index column
    if 0 in data.columns or 'Unnamed: 0' in data.columns:
        data.set_index(data.columns[0], inplace=True)

    return data

def match_elements(list_a, list_b):
   
    if not isinstance(list_a, list) or not isinstance(list_b, list):
        raise ValueError("Both inputs must be lists.")
    
    # Using list comprehension for concise and efficient matching
    matches = [element for element in list_a if element in list_b]
    return matches
    """
    This function takes two lists and returns a list of elements 
    from list_a that are also present in list_b.
    """

def download_data(data:pd.DataFrame, label):

    if not isinstance(data, pd.DataFrame):
        raise ValueError("The data parameter must be a pandas DataFrame.")
    
    if not isinstance(label, str):
        raise ValueError("The label parameter must be a string.")
    
    if data.empty:
        st.warning("The provided DataFrame is empty. Please provide a DataFrame with data.")
        return None

    # Generate current timestamp 
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Convert DataFrame to CSV and encode it
    csv_data = data.to_csv(encoding='utf-8-sig', index=False).encode('utf-8-sig') #why use encode twice?
    
    # Create and return the download button
    export_data = st.download_button(
        label=f"Download {label} data as CSV",
        data=csv_data,
        file_name=f"{label}_{timestamp}.csv",
        mime='text/csv',
        help=f"When you click on the Download button, you can download your {label} CSV file."
    )

    return export_data

def get_unique(data:pd.DataFrame):
    """
    Displays unique values of each column in a DataFrame in a 4-column Streamlit layout.
    """
    if not isinstance(data, pd.DataFrame):
        raise ValueError("The data parameter must be a pandas DataFrame.")
    
    # Initialize columns
    columns = st.columns(4)
    
    # Iterate through columns and display unique values
    for i, col_name in enumerate(data.columns):
        with columns[i % 4]:
            st.dataframe(data[col_name].drop_duplicates().reset_index(drop=True))
        
        # Reset columns after every 4 iterations
        if (i + 1) % 4 == 0 and (i + 1) != len(data.columns):
            columns = st.columns(4)
            
             
def describe(data):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("The data parameter must be a pandas DataFrame.")
    
    global num_category, str_category
    # Select numeric and categorical data
    numeric_data = data.select_dtypes(include=[np.number])
    categorical_data = data.select_dtypes(exclude=[np.number])
    
    # Identify numeric and categorical columns
    num_category = data.select_dtypes(include=[np.number]).columns.tolist()
    str_category = data.select_dtypes(exclude=[np.number]).columns.tolist()
    
    # Identify columns with null values
    column_with_null_values = data.columns[data.isnull().any()]
    
    # Descriptive statistics
    numeric_corr = numeric_data.corr() if not numeric_data.empty else None
    numeric_desc = numeric_data.describe() if not numeric_data.empty else None
    categorical_desc = categorical_data.describe() if not categorical_data.empty else None

    most_repeated = {col: numeric_data[col].mode().iloc[0] if not numeric_data[col].mode().empty else None for col in num_category}
    
    return (
        numeric_corr, 
        numeric_desc, 
        categorical_desc, 
        data.shape, 
        data.columns, 
        num_category, 
        str_category, 
        data.isnull().sum(), 
        data.dtypes.astype("str"), 
        data.nunique(), 
        str_category, 
        column_with_null_values,
        most_repeated
    )

def see_outliers(data, num_category_outliers):
    try:
        if num_category_outliers not in data.columns:
            st.error(f"Column '{num_category_outliers}' not found in data.")
            return
        
        # Plotting with Plotly
        box_plot = px.box(data_frame=data, x=num_category_outliers)
        st.plotly_chart(box_plot)

    except Exception as e:
        st.error(f"An error occurred while visualizing outliers: {e}")

def delete_outliers(data, col_name): 
    try:
        if col_name not in data.columns:
            raise ValueError(f"Column '{col_name}' not found in data.")
        if not np.issubdtype(data[col_name].dtype, np.number):
            raise TypeError(f"Column '{col_name}' must be numerical.")
        
        # Calculate Q1 (25th percentile) and Q3 (75th percentile)
        Q1 = data[col_name].quantile(0.25)
        Q3 = data[col_name].quantile(0.75)
        IQR = Q3 - Q1  # Interquartile Range

        # Determine the bounds for outliers
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Filter out the outliers
        no_outliers = data[(data[col_name] >= lower_bound) & (data[col_name] <= upper_bound)]

        return no_outliers.reset_index(drop=True)
    
    except Exception as e:
        st.error(f"An error occurred while deleting outliers: {e}")
        return data  

def replace_categorical(data:pd.DataFrame, selected_column, to_replace, val):
    try:
        if selected_column not in data.columns:
            raise ValueError(f"Column '{selected_column}' not found in the data.")
        if data[selected_column].dtype != 'O':
            raise TypeError(f"Column '{selected_column}' must be a categorical (object) type.")

        replaced = data.copy(deep=True)
        # Replace the specified value with the new value or NaN
        if val == 'Null':
            replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=np.nan)
        else:
            replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=val)

        replaced[selected_column] = pd.to_numeric(replaced[selected_column], errors='ignore')
        
        return replaced
    
    except Exception as e:
        st.error(f"An error occurred while replacing values: {e}")
        return data  

def replace_numeric(data:pd.DataFrame, selected_column, to_replace, val):
    try:
        if selected_column not in data.columns:
            raise ValueError(f"Column '{selected_column}' not found in the data.")
        if not pd.api.types.is_numeric_dtype(data[selected_column]):
            raise TypeError(f"Column '{selected_column}' must be a numeric type.")
        
        replaced = data.copy(deep=True)
        # Replace the specified value with the new value or NaN
        if val == -1:
            replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=np.nan)
        else:
            replaced[selected_column] = data[selected_column].replace(to_replace=to_replace, value=val)
        
        replaced[selected_column] = pd.to_numeric(replaced[selected_column], errors='ignore') #why?
        
        return replaced
    
    except Exception as e:
        st.error(f"An error occurred while replacing values: {e}")
        return data  

def drop_columns(data, selected_name):
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

def plot_Chart(first_plot,selection,second_plot=None):
    all_category = num_category+str_category
    try:
        if selection == 'Line Chart':
            for i in range(len(first_plot)):
                            column1 = first_plot[i]
                            for i in range(len(second_plot)):
                                column2 = second_plot[i]
                                all_category.append('none')
                                color = st.selectbox("Choose Color",all_category)
                                st.markdown("#### Bar Plot for {} and {} columns colored with {}".format(column1,column2,color))
                                if color != 'none':
                                    line = px.line(data_frame=st.session_state.df, x=column1, y=column2,color=color) 
                                else:
                                    line = px.line(data_frame=st.session_state.df, x=column1, y=column2) 
                                st.plotly_chart(line)
                            all_category.remove('none')
        elif selection == 'Bar Chart':
            for i in range(len(first_plot)):
                        column1 = first_plot[i]
                        for i in range(len(second_plot)):
                            column2 = second_plot[i]
                            if column2 == 'count':
                                all_category.append('none')
                                color = st.selectbox("Choose Color",all_category)
                                st.markdown("#### Plot for {} and {} columns Colored With {}".format(column1,column2,color))
                                if color != 'none':  
                                    histo = px.histogram(data_frame=st.session_state.df,x=column1,color=color)
                                else:
                                    histo = px.histogram(data_frame=st.session_state.df,x=column1)    
                                st.plotly_chart(histo)
                            else:
                                str_category.append('none')
                                index = str_category.index('none')
                                hue = st.selectbox("input the 3rd column", str_category, index=index)
                                if hue != 'none':
                                    st.markdown("#### Bar Plot for {} and {} column, grouped by {}".format(column1,column2,hue))
                                    bar = px.bar(data_frame=st.session_state.df, x=column1, y=column2, color=hue, barmode='overlay', orientation='v',opacity=1,facet_col=hue)
                                    st.plotly_chart(bar)
                                else:      
                                    st.markdown("#### Bar Plot for {} and {} columns".format(column1,column2))
                                    bar = px.bar(data_frame=st.session_state.df, x=column1, y=column2, color=column1, barmode='overlay', orientation='v',opacity=1)
                                    st.plotly_chart(bar)
                                str_category.remove('none')
                        num_category.remove('count')
        elif selection == 'Scatter Chart':
            for i in range(len(first_plot)):
                        column1 = first_plot[i]
                        for i in range(len(second_plot)):
                            column2 = second_plot[i]
                            all_category.append('none')
                            color = st.selectbox("Choose Color",all_category)
                            st.markdown("#### Bar Plot for {} and {} columns colored with {}".format(column1,column2,color))
                            if color == 'none' :
                                scatter = px.scatter(data_frame=st.session_state.df, x=column1, y=column2)
                            else :
                                scatter = px.scatter(data_frame=st.session_state.df, x=column1, y=column2, color=color)  
                            st.plotly_chart(scatter)
                        all_category.remove('none')
        elif selection == 'Histogram':
            for i in range(len(first_plot)):
                        column1 = first_plot[i]
                        st.markdown("#### Hist Plot for {} column".format(column1))
                        histo = px.histogram(data_frame=st.session_state.df,x=column1,color=column1)
                        histo = px.histogram(data_frame=st.session_state.df,x=column1)
                        st.plotly_chart(histo)
        elif selection == 'Pie Chart':
            for val in first_plot:
                            d = st.session_state.df[val].value_counts().reset_index()
                            d.columns = [val,'count']
                            value = st.selectbox("Enter Names: ", all_category)
                            st.markdown("#### Pie Plot for {} column".format(val))
                            if value == 'count':
                                pie_chart = px.pie(d,values='count', names=val)
                            else:
                                pie_chart = px.pie(st.session_state.df,values=val, names=value)
                            st.plotly_chart(pie_chart)
            all_category.remove('count')
        elif selection == 'heatmap':
            heat_map = px.imshow(st.session_state.df.corr(method=first_plot))
            st.plotly_chart(heat_map)
    except Exception as e:
        st.error(f"An error occurred: {e}")
                
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
