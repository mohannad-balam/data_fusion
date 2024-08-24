import streamlit as st
from helper import data, seconddata, match_elements, describe, see_outliers, drop_columns, download_data, filter_data, num_filter_data, rename_columns, handling_missing_values, data_wrangling, replace_categorical, replace_numeric, get_non_nulls, fill_missing_data, group_data, delete_outliers, get_query,get_unique,plot_Chart
import plotly.express as px
import pandas as pd
import seaborn as sns
import time
from streamlit_option_menu import option_menu

try:
    
    st.set_page_config(
        page_title="Data Fusion",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/sohailelabeidi',
        }
    )

    st.sidebar.title("Data Fusion")

    file_format_type = ["csv", "txt", "xls", "xlsx", "ods", "odt", "json"]
    excel_type =["vnd.ms-excel","vnd.openxmlformats-officedocument.spreadsheetml.sheet", "vnd.oasis.opendocument.spreadsheet", "vnd.oasis.opendocument.text"]

    uploaded_file = st.sidebar.file_uploader("Upload Your file", type=file_format_type)
    # st.code(uploaded_file)
    # uploaded_file = pd.read_csv('Titanic-Dataset.csv')
    #st.code(uploaded_file)
    if uploaded_file is None : 
        st.header("Welcome to DataFusion")
        st.subheader("Upload a Dataset To Start Exploring")
    if uploaded_file is not None:
        
        #start_time = time.time()
        file_type = uploaded_file.type.split("/")[1]
        
        if file_type == "plain":
            seperator = st.sidebar.text_input("Please Enter what seperates your data: ", max_chars=5) 
            data = data(uploaded_file, file_type,seperator)
            
        elif file_type in excel_type:
            data = data(uploaded_file, file_type)
        else:
            data = data(uploaded_file, file_type)
            
        #end_time = time.time() - start_time   
        
        if 'df' not in st.session_state:
            st.session_state.df = data.copy(deep=True)

        with st.sidebar:
            menu = option_menu(
            "Operations", 
            ["Overview", "Outlier Detection", "Data Visualization", "Data Pre-processing", "Group By", "Execute Custom Queries"], 
            icons=["layout-text-sidebar-reverse", "exclamation-circle", "pie-chart-fill", "filter", "columns-gap", "search"],
            menu_icon="cast", 
            default_index=0,
        )

        correlation, num_describe, category_describe , shape, columns, num_category, str_category, null_values, dtypes, unique, str_category,column_with_null_values,most_repeated = describe(st.session_state.df)
                
        with st.expander("Original Dataset"):

            st.subheader("Original Dataset Preview")
            st.dataframe(data)

        with st.expander("Edited Dataset"):
            if st.button("Reset Data"):
                st.session_state.df = data.copy(deep=True)
                st.rerun()
            st.subheader("Edited Dataset Preview")        
            st.dataframe(st.session_state.df)    
            st.text(" ")
            st.text(" ")
            st.text(" ")

    # ==================================================================================================
        if "Overview" in menu:
            st.subheader("Overview For Dataset") 
            
            with st.expander("See Unique Values"):
                st.markdown('Unique Values For Each Column')
                get_unique(st.session_state.df) 

            correlation, num_describe, category_describe , shape, columns, num_category, str_category, null_values, dtypes, unique, str_category, column_with_null_values,most_repeated = describe(st.session_state.df)
            if not num_describe is None and not category_describe is None:
                cl1, cl2 = st.columns(2)
                with cl1:
                    st.markdown("Numeric Data Description")
                    st.write(num_describe)
                with cl2:    
                    st.markdown("Categorical Data Description : ")
                    st.write(category_describe)
            
            elif num_describe is None:
                st.markdown("Categorical Data Description : ")
                st.write(category_describe)
            elif category_describe is None:
                st.markdown("Numeric Data Description")
                st.write(num_describe)
            st.text(" ")
            st.text(" ")
            st.text(" ")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.text("Basic Information")
                st.write("Dataset Name")
                st.text(uploaded_file.name)

                st.write("Dataset Size(MB)")
                number = round((uploaded_file.size*0.000977)*0.000977,2)
                st.write(number)

                st.write("Dataset Shape")
                st.write(shape)
                
            with col2:
                st.text("Dataset Columns")
                st.write(columns)
            
            with col3:
                st.text("Numeric Columns")
                st.dataframe(num_category)
            
            with col4:
                st.text("Categorical Columns")
                st.dataframe(str_category)
    
            col5, col6, col7, col8= st.columns(4)

            with col6:
                st.text("Columns Data-Type")
                st.dataframe(dtypes)
            
            with col7:
                st.text("Counted Unique Values")
                st.write(unique)
            
            with col5:
                st.write("Counted Null Values")
                st.dataframe(null_values)
            
            with col8:
                st.write("Most Repeated")
                st.dataframe(most_repeated)
            
            st.write("Correlation")
            st.dataframe(correlation)

    # ==================================================================================================
        if "Outlier Detection" in menu:
            st.subheader("Outlier Detection")

            try:
                outliers_selection = st.selectbox("Enter or select Name of the columns to see Outliers:", num_category)
                outliers = see_outliers(st.session_state.df, outliers_selection)
                decisison = st.selectbox('What To do with the outliers ?',['Delete Outliers'])
                if decisison == 'Delete Outliers':
                    no_outliers = delete_outliers(st.session_state.df, outliers_selection)
                    if st.button('Apply Changes'):
                        st.session_state.df = no_outliers
                        st.rerun()
            except Exception as e:
                st.error(f"Error during outlier detection or handling: {e}")
    # ===================================================================================================
        if "Data Pre-processing" in menu:
            options = st.selectbox('Pre-processing operations:', ["Replace Categorical Values", "Replace Numeric Values", "Drop Columns" , "Drop Categorical Rows", "Drop Numeric Rows","Rename Columns","Handling Missing Data","Join Tabels"])
            if "Replace Categorical Values" in options:
                filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=str_category)
                selection = get_non_nulls(st.session_state.df[filter_column_selection].unique())
                filtered_value_selection = st.multiselect("Enter Name or Select the value which you want to replcae in your {} column(You can choose multiple values): ".format(filter_column_selection), selection, default=[selection[0]])
                value = st.text_input(label="Enter The Value To Replace")
                if value != '':
                    replaced = replace_categorical(data=st.session_state.df, selected_column=filter_column_selection, to_replace=filtered_value_selection, val=value)
                    st.write(replaced)
                if st.button('Apply Changes'):
                    st.session_state.df = replaced
                    st.rerun()

            elif "Replace Numeric Values" in options:
                try:
                    filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=num_category)
                    selection = get_non_nulls(st.session_state.df[filter_column_selection].unique())
                    filtered_value_selection = st.multiselect("Enter Name or Select the value which you want to replcae in your {} column(You can choose multiple values): ".format(filter_column_selection), selection, default=[selection[0]])
                    value = st.number_input(label="Enter The Value To Replace" ,value=filtered_value_selection[0])
                    if value != '':
                        replaced = replace_numeric(data=st.session_state.df, selected_column=filter_column_selection, to_replace=filtered_value_selection, val=value)
                        st.write(replaced)
                except:
                    value = st.number_input(label="Enter The Value To Replace" ,value=0)          
                if st.button('Apply Changes'):
                    st.session_state.df = replaced
                    st.rerun()
            
            elif "Drop Columns" in options:
                multiselected_drop = st.multiselect("Please Type or select one or Multipe Columns you want to drop: ", st.session_state.df.columns)
            
                droped = drop_columns(st.session_state.df, multiselected_drop)
                st.write(droped)
                if st.button('Apply Changes'):
                    st.session_state.df = droped
                    st.rerun()
            
            elif "Drop Categorical Rows" in options:
                try: #st.session_state.df.columns
                    filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=str_category)
                    
                    if filter_column_selection not in st.session_state.df.columns:
                        raise ValueError(f"Selected column '{filter_column_selection}' is not in the DataFrame")

                    selection = get_non_nulls(st.session_state.df[filter_column_selection].unique())
                    if not selection:
                        raise ValueError(f"No valid data in the selected column '{filter_column_selection}'")

                    filtered_value_selection = st.multiselect(
                        "Enter Name or Select the value which you don't want in your {} column (You can choose multiple values):".format(filter_column_selection),
                        options=selection
                    )

                    st.subheader("Dataset Draft")
                    filtered_data = filter_data(st.session_state.df, filter_column_selection, filtered_value_selection)
                    st.write(filtered_data)

                    if st.button('Apply Changes'):
                        st.session_state.df = filtered_data
                        st.experimental_rerun()

                except ValueError as ve:
                    st.error(f"ValueError: {ve}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

            elif "Drop Numeric Rows" in options:
                try:
                    option = st.radio(
                        "Which kind of Filtration you want",
                        ('Delete data inside the range', 'Delete data outside the range')
                    )

                    num_filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=num_category)

                    if num_filter_column_selection not in st.session_state.df.columns:
                        raise ValueError(f"Selected column '{num_filter_column_selection}' is not in the DataFrame")

                    selection_range = get_non_nulls(st.session_state.df[num_filter_column_selection].unique())
                    if not selection_range:
                        raise ValueError(f"No valid data in the selected column '{num_filter_column_selection}'")

                    selection_range.sort()

                    start_value, end_value = st.select_slider(
                        'Select a range of Numbers you want to edit or keep',
                        options=selection_range,
                        value=(min(selection_range), max(selection_range))
                    )

                    if option == "Delete data inside the range":
                        st.write(f'We will be removing all the values between {int(start_value)} and {int(end_value)}')
                        num_filtered_data = num_filter_data(st.session_state.df, start_value, end_value, num_filter_column_selection, param=option)
                    else:
                        st.write(f'We will be Keeping all the values between {int(start_value)} and {int(end_value)}')
                        num_filtered_data = num_filter_data(st.session_state.df, start_value, end_value, num_filter_column_selection, param=option)

                    st.write(num_filtered_data)

                    if st.button('Apply Changes'):
                        st.session_state.df = num_filtered_data
                        st.experimental_rerun()

                except ValueError as ve:
                    st.error(f"ValueError: {ve}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

            elif "Rename Columns" in options:
                if 'rename_dict' not in st.session_state:
                    st.session_state.rename_dict = {}

                rename_dict = {}
                rename_column_selector = st.selectbox("Please Select or Enter a column Name you want to rename: ", options=st.session_state.df.columns)
                rename_text_data = st.text_input("Enter the New Name for the {} column".format(rename_column_selector), max_chars=50)


                # if st.button("Draft Changes", help="when you want to rename multiple columns/single column  so first you have to click Save Draft button this updates the data and then press Rename Columns Button."):
                #     st.session_state.rename_dict[rename_column_selector] = rename_text_data
                # st.code(st.session_state.rename_dict)

                if st.button("Apply Changes", help="Takes your data and rename the column as your wish."):
                    st.session_state.rename_dict[rename_column_selector] = rename_text_data
                    st.session_state.df = rename_columns(st.session_state.df, st.session_state.rename_dict)
                    #st.write(st.session_state.df)
                    st.session_state.rename_dict = {}
                    st.rerun()
            
            elif "Handling Missing Data" in options:
                if column_with_null_values.empty:
                    st.subheader("The Dataset is Clean")
                else:    
                    handling_missing_value_option = st.radio("Select What you want to do", ("Drop Null Values", "Filling in Missing Values"))
                    if handling_missing_value_option == "Drop Null Values":
                        drop_null_values_option = st.selectbox("Choose your option as suted: ", ["Drop all null value rows", "Only Drop Rows that contanines all null values",'Only Drop Null Rows For a Specific Column'])
                        if drop_null_values_option == 'Only Drop Null Rows For a Specific Column':
                            selcted_columns = st.multiselect("Choose a specific column/s", options=column_with_null_values)
                            droped_null_value = handling_missing_values(data=st.session_state.df, option_type=drop_null_values_option, col_names=selcted_columns)
                        else:
                            droped_null_value = handling_missing_values(st.session_state.df, drop_null_values_option)
                        st.code(droped_null_value.isnull().sum())
                        st.write(droped_null_value)      
                        if st.button("Apply Changes"):
                            st.session_state.df = droped_null_value
                            st.rerun()
                    
                    elif handling_missing_value_option == "Filling in Missing Values":
                        fillna_column_selector = st.selectbox("Please Select or Enter a column Name you want to fill the NaN Values: ", options=column_with_null_values)
                        options = ["Backward Fill", "Forward Fill",'Most Appeared Fill', 'Mean Fill', 'Custom Fill']
                        fill_null_values_option = st.selectbox("Choose your option as suted: ",options , index=options.index('Custom Fill'))
                        filled_values = st.session_state.df
                        if fill_null_values_option == 'Custom Fill':
                            fillna_text_data = st.text_input("Enter the New Value for the {} Column NaN Value".format(fillna_column_selector), max_chars=50)
                            if fillna_text_data != '':
                                if fillna_column_selector in num_category:
                                    try:
                                        fillna_text_data = float(fillna_text_data)
                                    except:
                                        fillna_text_data = int(fillna_text_data)
                                else:
                                    fillna_text_data = fillna_text_data
                                filled_values = fill_missing_data(st.session_state.df, fill_null_values_option, fillna_column_selector, fillna_text_data)
                        elif fill_null_values_option == 'Backward Fill':
                            filled_values = fill_missing_data(st.session_state.df, fill_null_values_option, fillna_column_selector)
                        elif fill_null_values_option == 'Forward Fill':
                            filled_values = fill_missing_data(st.session_state.df, fill_null_values_option, fillna_column_selector)
                        elif fill_null_values_option == 'Most Appeared Fill':
                            filled_values = fill_missing_data(st.session_state.df, fill_null_values_option, fillna_column_selector)
                        elif fill_null_values_option == 'Mean Fill':
                            filled_values = fill_missing_data(filled_values, fill_null_values_option, fillna_column_selector)
                        st.write(filled_values)
                        if st.button("Apply Changes", help="Takes your data and Fill NaN Values for columns as your wish."):
                            st.session_state.df = filled_values   
                            st.rerun()    
            elif "Join Tabels" in options:
                data_wrangling_merging_uploaded_file = st.file_uploader("Upload Your Second file you want to merge", type=file_format_type)

                if data_wrangling_merging_uploaded_file is not None:

                    second_data = seconddata(data_wrangling_merging_uploaded_file, file_type=data_wrangling_merging_uploaded_file.type.split("/")[1])
                    same_columns = match_elements(data, second_data)
                    merge_key_selector = st.selectbox("Select A Comlumn by which you want to merge on two Dataset", options=same_columns)
                    
                    merge_data = data_wrangling(data, second_data, merge_key_selector, options)
                    st.write(merge_data)
                    if st.button("Apply Changes"):
                        st.session_state.df = merge_data
                        st.rerun()

    # ===================================================================================================================
    
        if "Data Visualization" in menu:
            all_category = num_category+str_category
            selection = st.selectbox("Select The Type of Chart", ['Line Chart','Bar Chart','Histogram','Scatter Chart','Pie Chart', 'heatmap'])
            plot_Chart(selection)    
    # ==========================================================================================================================================

        if "Group By" in menu:

            group_by_columns = st.multiselect("Select Column/s on Which You Want to Group By", options=st.session_state.df.columns)
            if group_by_columns != []:
                group_type = st.selectbox("Choose what you want to do with returned data", options=['mean','median','count','max','min','standard deviation','1st quartile','3rd quartile','normal'])
                if group_type != '':
                    if group_type != 'normal':
                        cols = st.multiselect("Choose the Columns you want the {} for".format(group_type), options=num_category)
                        grouped_data = group_data(data=st.session_state.df, col_names=group_by_columns, group_type=group_type,col_name=cols)
                    else:
                        grouped_data = group_data(data=st.session_state.df, col_names=group_by_columns, group_type=group_type)        
                    st.dataframe(grouped_data)
                    download_data(grouped_data, label=" Grouped")

     # ==========================================================================================================================================   
        if "Execute Custom Queries" in menu:
            st.header("Custom Queries")
            query_type = st.selectbox("Query Type",['Pure Python','SQL'])
            query = st.text_input("Type Your Query Here", help='ex : Age < 35')
            result = get_query(data=st.session_state.df,query=query,query_type=query_type)
            st.subheader("Query Result")
            st.dataframe(result)
            if st.button("Apply Changes"):
                st.session_state.df = result
                st.rerun()
                # download_data(result, label="Download Query Data")      
        export = download_data(st.session_state.df, label="Edited")
    # ==========================================================================================================================================

    #st.code("Processed time is : " + str(end_time.__round__(2)) + " seconds")
    
except Exception as e:
    st.warning(e)