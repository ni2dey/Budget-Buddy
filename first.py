import streamlit as st
from PIL import Image
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import calendar
from streamlit_option_menu import option_menu

page_title="Income & Expense Tracker"
page_icon=":money_with_wings:"
layout="centered"
st.set_page_config(page_title=page_title,page_icon=page_icon,layout=layout)
excel_file = 'Excel.xlsx'

#Title bar
st.sidebar.title(f"Welcome")
with st.sidebar:
    selected=option_menu(
        menu_title="Main Menu",
        options=["Data Entry","Data Visualization"]
    )

#Creating excel sheet if not present and loading data from excel
def load_data():
    if os.path.exists(excel_file):
        return pd.read_excel(excel_file)
    else:
        return pd.DataFrame(columns=['Date', 'Item', 'Category', 'Price'])

#Title image
image=Image.open("expense.jpeg")
w,h=image.size
new_w = w
new_h= int(new_w*(12/35))
if new_h > h:
    new_h = h
    new_w = int(new_h * (35 /12))
resized_image = image.resize((new_w, new_h))
st.title(page_icon+" "+page_title)
st.image(resized_image)


#Tab1
if selected=="Data Entry":
    "_________"
    name=st.text_input("Enter your name:")

    st.radio('Pick your gender',["Male","Female"],index=None)
    "___"


    selected_option= option_menu(
        menu_title=None,
        options=[ "Income","Expense"],
        icons=['bar-chart-fill','pencil-fill'],
        orientation='horizontal'
    )
    if selected_option == 'Income':
        st.session_state.income = st.number_input("Enter your income:", min_value=0, value=0, step=500)
        st.session_state.target_saving = st.slider("Enter your target saving:", min_value=0,
                                                   max_value=max(st.session_state.income, 100), step=500)
        st.write(f"Your Target saving:{st.session_state.target_saving}")


    if selected_option=='Expense':
        st.markdown("<h3 style='text-align: center;'>Enter your expense data 💶</h3>", unsafe_allow_html=True)
        def add_data(i):

            date = st.date_input(f"Enter date :", key=f'date{i}')
            item = st.text_input(f"Item bought \:", key=f'item{i}',placeholder='Enter item name')
            category = st.selectbox(
                f"Category of item :",
                ("<select>", "Grocery", "Stationary", "Cosmetics", "Clothing", "Medicines", "Eatery", "Miscellaneous"),
                key=f'category{i}',
                index=None
            )
            price = st.number_input(f"Enter price of item :", key=f'price{i}',step=5)
            new_data = {'Date': date, 'Item': item, 'Category': category, "Price": price}
            return new_data

        def savetodatabase():
            if 'df' not in st.session_state:
                st.session_state.df = load_data()

            st.session_state.df = st.session_state.df._append(new_data,ignore_index=True)
            st.session_state.df.to_excel('Excel.xlsx', index=False)



        def reset_fields():
            st.session_state.date = None
            st.session_state.item = ''
            st.session_state.category = '<Select>'
            st.session_state.price = 0

        load_data()
        new_data=add_data(0)
        if st.button("Save"):
            if new_data['Category'] == "<select>" or new_data['Item']==None:
                st.info("Invalid Category/Item data")
            else:
             st.success('Data Saved')
             savetodatabase()
        i=1
        agree=st.radio('Want to add more data',["No","Yes"],index=None)
        st.markdown("----")
        while agree!="No":
            if agree=="Yes":
                load_data()
                new_data = add_data(i)
                if st.button("Save",key=f'save{i}'):
                    if new_data['Category'] == "<select>" or new_data['Item'] == None:
                        st.info("Invalid Category/Item data")
                    else:
                        st.success('Data Saved')
                        savetodatabase()
                agree = st.radio('Want to add more data?', ["No","Yes"],key=f'radio{i}',index=None)
                i+=1
                st.markdown("----")

#Tab2
if selected=="Data Visualization":
    "_____"
    df = load_data()
    df = df[(df['Category'] != "<select>") & (df['Item'].notna()) & (df['Price'] > 0)]
    df['Date'] = pd.to_datetime(df['Date'])
    current_month = datetime.now().month
    current_year = datetime.now().year
    month=calendar.month_name[current_month]

    def filter_current_month(df):
        return df[(df['Date'].dt.month == current_month) & (df['Date'].dt.year == current_year)]


    current_month_df = filter_current_month(df)
    current_month_expense=sum(current_month_df['Price'])

    col1,col2=st.columns(2)
    with col1:
        st.info("Total Income:",icon='📌')
        st.metric(label='this month',value=f"Rs.{st.session_state.income}")
    with col2:
        st.info("Target savings:",icon='📌')
        st.metric(label='',value=f"Rs.{st.session_state.target_saving}")
    col3, col4 = st.columns(2)
    with col3:
        st.info("Monthly Expense:",icon='📌')
        st.metric(label='this month',value=f"Rs.{current_month_expense}")
    with col4:
        st.info("Remaining Budget",icon='📌')
        st.metric(label='this month',value=f"Rs.{max((st.session_state.income-current_month_expense),0)}")


    #Total expense table
    st.markdown("----")
    with st.expander("Total Expenses"):
        with st.container(height=300,border=True):
            st.write("Total Expenses Table:")
            st.table(df)
        category_expenses=pd.DataFrame()

        #barchart
        category_expenses = df.groupby('Category')['Price'].sum().reset_index()
        category_expenses = category_expenses[category_expenses['Category'] != "<select>"]
        st.markdown("<h3 style='text-align: center;'>Total Expense per Category</h3>", unsafe_allow_html=True)
        st.bar_chart(category_expenses, x='Category', y='Price')

        #piechart
        st.markdown("<h3 style='text-align: center;'>Percent Expense per Category</h3>", unsafe_allow_html=True)
        fig = px.pie(df, values=category_expenses['Price'], names=category_expenses['Category'], color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, theme=None)




    # Displaying the DataFrame of expense of current month
    with st.expander(f"Expenses for current month({month}):"):
        with st.container(height=300):
            st.table(current_month_df)

        daily_expenses = current_month_df.groupby(current_month_df['Date'].dt.date)['Price'].sum().reset_index()

        # Plotting
        fig = px.line(daily_expenses, x="Date", y='Price', title='Trajectory of Expense this month',markers=True)
        fig.update_traces(textposition="bottom right")
        st.plotly_chart(fig,theme=None)
        cat_expenses = current_month_df.groupby(current_month_df['Category'])['Price'].sum().reset_index()
        st.bar_chart(cat_expenses, x='Category', y='Price')

    #Date of your choice
    with st.expander(f"Select Date"):
        year=st.selectbox(
            "Select Year ",("<select>",2023, 2024),
        )
        month =st.selectbox(
            "Select month", ("<select>",1,2,3,4,5,6,7,8,9,10,11,12),
        )
        if st.button("Submit"):
            if year == "<select>" or month == "<select>":
                st.error("Please select a valid option.")


            else:
                st.success(f"You selected: {year}-{month}")
                df['Date'] = pd.to_datetime(df['Date'])
                filtered_df = df[(df['Date'].dt.year == year) & (df['Date'].dt.month == month)]
                with st.container(height=300):
                    st.table(filtered_df)
