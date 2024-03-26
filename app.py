from cmath import nan
from datetime import date
import streamlit as st
from helper import data, seconddata, match_elements, describe, outliers, drop_items, download_data, filter_data, num_filter_data, rename_columns, clear_image_cache, handling_missing_values, data_wrangling, replace_data, get_non_nulls, fill_missing_data
import numpy as np
import plotly.express as px
import pandas as pd
import seaborn as sns

st.set_page_config(
     page_title="Data Analysis Web App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://github.com/everydaycodings/Data-Analysis-Web-App',
         'Report a bug': "https://github.com/everydaycodings/Data-Analysis-Web-App/issues/new",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
)


st.sidebar.title("Data Analysis Web App")

file_format_type = ["csv", "txt", "xls", "xlsx", "ods", "odt"]
functions = ["Overview", "Outliers", "Display Plot", "Replace Categorical Values", "Replace Numeric Values", "Drop Columns", "Drop Categorical Rows", "Drop Numeric Rows", "Rename Columns", "Handling Missing Data", "Data Wrangling"]
excel_type =["vnd.ms-excel","vnd.openxmlformats-officedocument.spreadsheetml.sheet", "vnd.oasis.opendocument.spreadsheet", "vnd.oasis.opendocument.text"]

uploaded_file = st.sidebar.file_uploader("Upload Your file", type=file_format_type)

if uploaded_file is not None:
    
    file_type = uploaded_file.type.split("/")[1]
    
    if file_type == "plain":
        seperator = st.sidebar.text_input("Please Enter what seperates your data: ", max_chars=5) 
        data = data(uploaded_file, file_type,seperator)

        
    elif file_type in excel_type:
        data = data(uploaded_file, file_type)

    else:
        data = data(uploaded_file, file_type)

        
    if 'df' not in st.session_state:
            st.session_state.df = data

    num_describe, category_describe , shape, columns, num_category, str_category, null_values, dtypes, unique, str_category, column_with_null_values = describe(st.session_state.df)
    # num_category.append('count')
    
    multi_function_selector = st.sidebar.multiselect("Enter Name or Select the Column which you Want To Plot: ",functions, default=["Overview"])
    
        
    if st.button("Reset Data"):
            st.session_state.df = data
    
    st.subheader("Original Dataset Preview")
    st.dataframe(data)

    st.subheader("Edited Dataset Preview")        
    st.dataframe(st.session_state.df)    
    st.text(" ")
    st.text(" ")
    st.text(" ")

    if "Overview" in multi_function_selector:
        st.subheader("Overview For Edited Dataset")  
        num_describe, category_describe , shape, columns, num_category, str_category, null_values, dtypes, unique, str_category, column_with_null_values = describe(st.session_state.df)
        if not num_describe is None and not category_describe is None:
            cl1, cl2 = st.columns(2)
            with cl1:
                st.markdown("Numeric Data Description")
                st.write(num_describe)
            with cl2:    
                st.markdown("Categorical Data Description : ")
                st.write(category_describe)
        elif not num_describe:
            st.markdown("Categorical Data Description : ")
            st.write(category_describe)
        elif not category_describe:
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

# ==================================================================================================
    if "Outliers" in multi_function_selector:

        outliers_selection = st.multiselect("Enter or select Name of the columns to see Outliers:", num_category)
        outliers = outliers(st.session_state.df, outliers_selection)
        
        for i in range(len(outliers)):
            st.image(outliers[i])
# ===================================================================================================
    if "Replace Categorical Values" in multi_function_selector:
        filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=str_category)
        selection = get_non_nulls(st.session_state.df[filter_column_selection].unique())
        filtered_value_selection = st.multiselect("Enter Name or Select the value which you want to replcae in your {} column(You can choose multiple values): ".format(filter_column_selection), selection)
        value = st.text_input(label="Enter The Value To Replace")
        if st.button('See Draft'):
            replaced = replace_data(data=st.session_state.df, selected_column=filter_column_selection, to_replace=filtered_value_selection, val=value)
            st.write(replaced)
            if st.button('Apply Changes'):
                st.session_state.df = replaced
    # rep_export = download_data(st.session_state.df, label="replaed(edited)")
# ===================================================================================================        
    if "Replace Numeric Values" in multi_function_selector:
        filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=num_category)
        selection = get_non_nulls(st.session_state.df[filter_column_selection].unique())
        filtered_value_selection = st.multiselect("Enter Name or Select the value which you want to replcae in your {} column(You can choose multiple values): ".format(filter_column_selection), selection)
        value = st.number_input(label="Enter The Value To Replace",value=filtered_value_selection)
        if st.button('See Draft'):
            replaced = replace_data(data=st.session_state.df, selected_column=filter_column_selection, to_replace=filtered_value_selection, val=value)
            st.write(replaced)
            if st.button('Apply Changes'):
                st.session_state.df = replaced
        # rep_export = download_data(st.session_state.df, label="replaced numeric(edited)")        
# ===================================================================================================
    if "Drop Columns" in multi_function_selector:
        
        multiselected_drop = st.multiselect("Please Type or select one or Multipe Columns you want to drop: ", st.session_state.df.columns)
        
        droped = drop_items(st.session_state.df, multiselected_drop)
        st.write(droped)
        
        if st.button('Apply Changes'):
            st.session_state.df = droped
            # drop_export = download_data(st.session_state.df, label="Droped(edited)")
# =====================================================================================================================================
    if "Drop Categorical Rows" in multi_function_selector:

        filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=st.session_state.df.columns)
        selection = get_non_nulls(st.session_state.df[filter_column_selection].unique())
        filtered_value_selection = st.multiselect("Enter Name or Select the value which you don't want in your {} column(You can choose multiple values): ".format(filter_column_selection), st.session_state.df[filter_column_selection].unique())
        
        st.subheader("Dataset Draft")
        filtered_data = filter_data(st.session_state.df, filter_column_selection, filtered_value_selection)
        st.write(filtered_data)
        
        if st.button('Apply Changes'):
            st.session_state.df = filtered_data
            # filtered_export = download_data(st.session_state.df, label="filtered")

# =============================================================================================================================

    if "Drop Numeric Rows" in multi_function_selector:

        option = st.radio(
        "Which kind of Filteration you want",
        ('Delete data inside the range', 'Delete data outside the range'))

        num_filter_column_selection = st.selectbox("Please Select or Enter a column Name: ", options=num_category)
        selection_range = get_non_nulls(st.session_state.df[num_filter_column_selection].unique())
        selection_range.sort()
        # selection_range = st.session_state.df[num_filter_column_selection].unique()

        # for i in range(0, len(selection_range)) :
        #     selection_range[i] = selection_range[i]
        # selection_range.sort()

        # selection_range = [x for x in selection_range if np.isnan(x) == False]

        start_value, end_value = st.select_slider(
        'Select a range of Numbers you want to edit or keep',
        options=selection_range,
        value=(min(selection_range), max(selection_range))
        )
        
        if option == "Delete data inside the range":
            st.write('We will be removing all the values between ', int(start_value), 'and', int(end_value))
            num_filtered_data = num_filter_data(st.session_state.df, start_value, end_value, num_filter_column_selection, param=option)
        else:
            st.write('We will be Keeping all the values between', int(start_value), 'and', int(end_value))
            num_filtered_data = num_filter_data(st.session_state.df, start_value, end_value, num_filter_column_selection, param=option)
        st.write(num_filtered_data)    
        if st.button('Apply Changes'):
            st.session_state.df = num_filtered_data
            # num_filtered_export = download_data(st.session_state.df, label="num_filtered")


# =======================================================================================================================================

    if "Rename Columns" in multi_function_selector:

        if 'rename_dict' not in st.session_state:
            st.session_state.rename_dict = {}

        rename_dict = {}
        rename_column_selector = st.selectbox("Please Select or Enter a column Name you want to rename: ", options=st.session_state.df.columns)
        rename_text_data = st.text_input("Enter the New Name for the {} column".format(rename_column_selector), max_chars=50)


        if st.button("Draft Changes", help="when you want to rename multiple columns/single column  so first you have to click Save Draft button this updates the data and then press Rename Columns Button."):
            st.session_state.rename_dict[rename_column_selector] = rename_text_data
        st.code(st.session_state.rename_dict)

        if st.button("Apply Changes", help="Takes your data and rename the column as your wish."):
            st.session_state.df = rename_columns(st.session_state.df, st.session_state.rename_dict)
            st.write(st.session_state.df)
            # export_rename_column = download_data(st.session_state.df, label="rename_column")
            st.session_state.rename_dict = {}
    
# ===================================================================================================================
 
    if "Display Plot" in multi_function_selector:
        all_category = num_category+str_category
        selection = st.selectbox("Select The Type of Chart", ['Line Chart','Bar Chart','Histogram','Scatter Chart','Pie Chart'])
        if selection == 'Line Chart':
            st.subheader("Numeric")
            num1_multi_bar_plotting = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", num_category)
            st.subheader("Numeric")
            num_category.append('')
            num2_multi_bar_plotting = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", num_category)
            for i in range(len(num1_multi_bar_plotting)):
                column1 = num1_multi_bar_plotting[i]
                for i in range(len(num2_multi_bar_plotting)):
                    column2 = num2_multi_bar_plotting[i]
                    st.markdown("#### Bar Plot for {} and {} columns".format(column1,column2))
                    #st.line_chart(data=st.session_state.df, x=column1, y=column2)     
                    line = px.line(data_frame=st.session_state.df, x=column1, y=column2) 
                    st.plotly_chart(line)
        elif selection == 'Bar Chart':
            num_category.append('count')
            st.subheader("Categories")
            str_multi_bar_plotting = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", str_category)
            st.subheader("Numeric")
            num_multi_bar_plotting = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", num_category)
            for i in range(len(str_multi_bar_plotting)):
                column1 = str_multi_bar_plotting[i]
                for i in range(len(num_multi_bar_plotting)):
                    column2 = num_multi_bar_plotting[i]
                    if column2 == 'count':
                        st.markdown("#### Plot for {} and {} columns".format(column1,column2))
                        histo = px.histogram(data_frame=st.session_state.df,x=column1)
                        st.plotly_chart(histo)
                    else:
                        str_category.append('none')
                        index = str_category.index('none')
                        hue = st.selectbox("input the 3rd column", str_category, index=index)
                        if hue != 'none':
                            st.markdown("#### Bar Plot for {} and {} column, grouped by {}".format(column1,column2,hue))
                            bar = px.bar(data_frame=st.session_state.df, x=column1, y=column2, color=hue,barmode='overlay', orientation='v',opacity=1,facet_col=hue)
                            st.plotly_chart(bar)
                        else:      
                            st.markdown("#### Bar Plot for {} and {} columns".format(column1,column2))
                            st.bar_chart(st.session_state.df[[column1,column2]])
                        str_category.remove('none')
            num_category.remove('count')            
        elif selection == 'Scatter Chart':
            all_category = num_category+str_category
            st.subheader("All Values")
            str_multi_bar_plotting = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", all_category)
            st.subheader("All Values")
            all_category.append('')
            num_multi_bar_plotting = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", all_category)
            for i in range(len(str_multi_bar_plotting)):
                column1 = str_multi_bar_plotting[i]
                for i in range(len(num_multi_bar_plotting)):
                    column2 = num_multi_bar_plotting[i]
                    st.markdown("#### Bar Plot for {} and {} columns".format(column1,column2))
                    #st.scatter_chart(data=st.session_state.df, x=column1, y=column2)
                    scatter = px.scatter(data_frame=st.session_state.df, x=column1, y=column2)
                    st.plotly_chart(scatter)
            all_category.remove('')
        elif selection == 'Histogram':
            st.subheader("All Values")
            num_multi_bar_plotting = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", all_category)
            for i in range(len(num_multi_bar_plotting)):
                column1 = num_multi_bar_plotting[i]
                st.markdown("#### Hist Plot for {} column".format(column1))
                histo = px.histogram(data_frame=st.session_state.df,x=column1)
                st.plotly_chart(histo)
        elif selection == 'Pie Chart':
                values = st.multiselect("Enter Name or Select the Column which you Want To Plot: ", all_category)
                for val in values:
                    d = st.session_state.df[val].value_counts().reset_index()
                    d.columns = [val,'count']
                    st.markdown("#### Pie Plot for {} column".format(val))
                    pie_chart = px.pie(d,values='count', names=val)
                    st.plotly_chart(pie_chart)
# ====================================================================================================================    

    if "Handling Missing Data" in multi_function_selector:
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
                # export_rename_column = download_data(droped_null_value, label="fillna_column")
            
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
                    filled_values = fill_missing_data(st.session_state.df, fill_null_values_option, fillna_column_selector)
                st.write(filled_values)
                if st.button("Apply Changes", help="Takes your data and Fill NaN Values for columns as your wish."):
                    st.session_state.df = filled_values       

# ==========================================================================================================================================

    if "Data Wrangling" in multi_function_selector:
        data_wrangling_option = st.radio("Choose your option as suted: ", ("Merging On Index", "Concatenating On Axis"))

        if data_wrangling_option == "Merging On Index":
            data_wrangling_merging_uploaded_file = st.file_uploader("Upload Your Second file you want to merge", type=uploaded_file.name.split(".")[1])

            if data_wrangling_merging_uploaded_file is not None:

                second_data = seconddata(data_wrangling_merging_uploaded_file, file_type=data_wrangling_merging_uploaded_file.type.split("/")[1])
                same_columns = match_elements(data, second_data)
                merge_key_selector = st.selectbox("Select A Comlumn by which you want to merge on two Dataset", options=same_columns)
                
                merge_data = data_wrangling(data, second_data, merge_key_selector, data_wrangling_option)
                st.write(merge_data)
                download_data(merge_data, label="merging_on_index")

        if data_wrangling_option == "Concatenating On Axis":

            data_wrangling_concatenating_uploaded_file = st.file_uploader("Upload Your Second file you want to Concatenate", type=uploaded_file.name.split(".")[1])

            if data_wrangling_concatenating_uploaded_file is not None:

                second_data = seconddata(data_wrangling_concatenating_uploaded_file, file_type=data_wrangling_concatenating_uploaded_file.type.split("/")[1])
                concatenating_data = data_wrangling(data, second_data, None, data_wrangling_option)
                st.write(concatenating_data)
                download_data(concatenating_data, label="concatenating_on_axis")
    export = download_data(st.session_state.df, label="Edited")    
# ==========================================================================================================================================
    st.sidebar.info("After using this app please Click Clear Cache button so that your all data is removed from the folder.")
    if st.sidebar.button("Clear Cache"):
        clear_image_cache()

else:
    with open('samples/sample.zip', 'rb') as f:
        st.sidebar.download_button(
                label="Download Sample Data and Use It",
                data=f,
                file_name='smaple_data.zip',
                help = "Download some sample data and use it to explore this web app."
            )