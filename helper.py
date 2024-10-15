import pandas as pd
import streamlit as st
import datetime
import numpy as np
import plotly.express as px
from pandasql import sqldf

excel_type =["vnd.ms-excel","vnd.openxmlformats-officedocument.spreadsheetml.sheet", "vnd.oasis.opendocument.spreadsheet", "vnd.oasis.opendocument.text"]

def data(file_path, file_type, separator=None):
    try:
        if file_type == "csv":
            data = pd.read_csv(file_path)
        elif file_type == "json":
            data = pd.read_json(file_path)
        elif file_type in excel_type:  
            data = pd.read_excel(file_path)
        elif file_type == "plain":
            try:
                data = pd.read_table(file_path, sep=separator)
            except ValueError:
                st.info("If you haven't Type the separator then dont worry about the error this error will go as you type the separator value and hit Enter.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

    # Check for unnamed index column
    # if 0 in data.columns or 'Unnamed: 0' in data.columns:
    #     data.set_index(data.columns[0], inplace=True)

    return data
  


def seconddata(file_path, file_type, separator=None):
    try:
        if file_type == "csv":
            data = pd.read_csv(file_path, parse_dates=True)
        elif file_type == "json":
            data = pd.read_json(file_path)
        elif file_type in excel_type:  
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
    # if 0 in data.columns or 'Unnamed: 0' in data.columns:
    #     data.set_index(data.columns[0], inplace=True)

    return data

def match_elements(list_a, list_b):
    match = []
    for i in list_a:
        if i in list_b:
            match.append(i)
    return match
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
    csv_data = data.to_csv(index=False).encode('utf-8-sig')
    
    # Create and return the download button
    export_data = st.download_button(
        label=f"Download {label} Data as CSV",
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
        data.nunique(), 
        str_category, 
        column_with_null_values,
        most_repeated
    )

def see_outliers(data, num_category_outliers):
    try:
        if num_category_outliers not in data.columns:
            st.markdown(f"####Column '{num_category_outliers}' not found in data.")
            return
        
        # Plotting with Plotly
        box_plot = px.box(data_frame=data, x=num_category_outliers)
        st.plotly_chart(box_plot)

    except Exception as e:
        st.error(f"An error occurred while visualizing outliers: {e}")

def delete_outliers(data:pd.DataFrame, col_name): 
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
        data.reset_index()
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
        
        #replaced[selected_column] = pd.to_numeric(replaced[selected_column], errors='ignore') #why?
        
        return replaced
    
    except Exception as e:
        st.error(f"An error occurred while replacing values: {e}")
        return data  

def drop_columns(data:pd.DataFrame, selected_name):
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
            num_filtered_data = data[~((data[column] >= float(start_value)) & (data[column] <= float(end_value)))]
    else:
        if column in num_category:
            num_filtered_data = data[data[column].isin(range(int(start_value), int(end_value)+1))]

    return num_filtered_data.reset_index(drop=True)


def rename_columns(data:pd.DataFrame, column_name):
    rename_column = data.rename(columns=column_name)
    return rename_column

def plot_Chart(selection):
    all_category = num_category + str_category
    try:
        if selection == 'Line Chart':
            st.subheader("All Columns")
            column1 = st.selectbox("Enter Name or Select the Column which you Want To Plot: ", all_category)
            st.subheader("Numeric Columns")
            column2 = st.selectbox("Enter Name or Select the 2nd Column which you Want To Plot: ", num_category)
            str_category.append('none')
            color = st.selectbox("input a categorical column to group by",str_category,index=str_category.index('none'))
            st.markdown("#### Line Chart for {} and {} columns Gouped By {}".format(column1,column2,color))
            if color != 'none':
                line = px.line(data_frame=st.session_state.df, x=column1, y=column2,color=color) 
            else:
                line = px.line(data_frame=st.session_state.df, x=column1, y=column2) 
            st.plotly_chart(line)
            str_category.remove('none')
        elif selection == 'Bar Chart':
            num_category.append('count')
            st.subheader("Categorical Columns")     
            column1 = st.selectbox("Enter Name or Select the Column which you Want To Plot: ", str_category)
            st.subheader("Numeric Columns")
            column2 = st.selectbox("Enter Name or Select the 2nd Column which you Want To Plot: ", num_category)
            str_category.append('none')
            if column2 == 'count':
                color = st.selectbox("input a categorical column to group by",str_category,index=str_category.index('none'))
                st.markdown("#### Bar Chart for {} and {} columns Colored With {}".format(column1,column2,color))
                if color != 'none':  
                    histo = px.histogram(data_frame=st.session_state.df,x=column1,color=color)
                else:
                    histo = px.histogram(data_frame=st.session_state.df,x=column1)    
                st.plotly_chart(histo)
            else:
                hue = st.selectbox("input a categorical column to group by", str_category, index=str_category.index('none'))
                if hue != 'none':
                    st.markdown("#### Bar chart for {} and {} column, grouped by {}".format(column1,column2,hue))
                    bar = px.bar(data_frame=st.session_state.df, x=column1, y=column2, color=hue, barmode='overlay', orientation='v',opacity=1,facet_col=hue)
                    st.plotly_chart(bar)
                else:      
                    st.markdown("#### Bar chart for {} and {} columns".format(column1,column2))
                    bar = px.bar(data_frame=st.session_state.df, x=column1, y=column2, barmode='overlay', orientation='v',opacity=1)
                    st.plotly_chart(bar)
            str_category.remove('none')    
            num_category.remove('count')
        elif selection == 'Scatter Chart':
            st.subheader("Numerical Columns")
            column1 = st.selectbox("Enter Name or Select the Column which you Want To Plot: ", num_category)
            st.subheader("Numerical Columns")
            column2 = st.selectbox("Enter Name or Select the 2nd Column which you Want To Plot: ", num_category)
            str_category.append('none')
            color = st.selectbox("input a categorical column to group by",str_category,index=str_category.index('none'))
            if color == 'none' :
                st.markdown("#### Scatter Chart for {} and {} columns".format(column1,column2))
                scatter = px.scatter(data_frame=st.session_state.df, x=column1, y=column2)
            else :
                st.markdown("#### Scatter Chart for {} and {} columns grouped by {}".format(column1,column2,color))
                scatter = px.scatter(data_frame=st.session_state.df, x=column1, y=column2, color=color)  
            st.plotly_chart(scatter)
            str_category.remove('none')
        elif selection == 'Histogram':
            st.subheader("Numerical Columns")
            column1 = st.selectbox("Enter Name or Select the Column which you Want To Plot: ", num_category)
            str_category.append('none')
            color = st.selectbox("input a categorical column to group by",str_category,index=str_category.index('none'))
            if color == 'none':
                st.markdown("#### Histogram for {} column".format(column1))
                histo = px.histogram(data_frame=st.session_state.df,x=column1)
            else:
                st.markdown("#### Histogram for {} column grouped by {}".format(column1,color))
                histo = px.histogram(data_frame=st.session_state.df,x=column1,color=color)
            st.plotly_chart(histo)
            str_category.remove('none')      
        elif selection == 'Pie Chart':
            val = st.selectbox("Enter Name or Select the Column which you Want To Plot: ", str_category)
            data_count = st.session_state.df[val].value_counts().reset_index()
            data_count.columns = [val,'count']
            st.markdown("#### Pie Chart for {} column".format(val))
            pie_chart = px.pie(data_count,values='count', names=val)
            st.plotly_chart(pie_chart)
        elif selection == 'heatmap':
            corr_type = st.selectbox('choose the correlation type', options= ['pearson', 'spearman', 'kendall'])
            st.markdown("#### The {} correlation between variables".format(corr_type))
            heat_map = px.imshow(st.session_state.df.corr(method=corr_type))
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
        try:
            filled[col_name] = data[col_name].fillna(to_rep)
        except ValueError:
            st.dialog("s")
    elif option_type == 'Backward Fill':
        filled[col_name] = data[col_name].fillna(method='bfill')
    elif option_type == 'Forward Fill':
        filled[col_name] = data[col_name].fillna(method='ffill')
    elif option_type == 'Most Appeared Fill':
        filled[col_name] = data[col_name].fillna(data[col_name].mode()[0])
    elif option_type == 'Mean Fill':
        filled[col_name] = data[col_name].fillna(data[col_name].mean())    
    return filled

def merge(data1, data2=None, key=None):
    data = pd.merge(data1, data2, on=key)
    return data

def group_data(data:pd.DataFrame, col_names, group_type, col_name=None):
    #todo
    if group_type == "mean":
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].mean().round(2)
    elif group_type == "median":
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].median().round(2)
    elif group_type == 'count':
        grouped = data.groupby([col for col in col_names])[col_name[0]].count()
    elif group_type == 'max':
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].max()
    elif group_type == 'min':
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].min()
    elif group_type == 'standard deviation':
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].std().round(2)
    elif group_type == '1st quartile':
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].quantile(0.25)
    elif group_type == '3rd qurtile':
        grouped = data.groupby([col for col in col_names])[[col for col in col_name]].quantile(0.75)
    elif group_type == 'normal':
        grouped = data.groupby([col for col in col_names])
        normal_grouping = pd.DataFrame()
        for _, rows in grouped:
            if normal_grouping.empty:
                normal_grouping = pd.DataFrame(data=rows)
            normal_grouping = pd.concat([normal_grouping,rows])
        return normal_grouping.reset_index()
    return grouped
    

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