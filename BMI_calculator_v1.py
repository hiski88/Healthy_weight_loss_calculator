import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import plotly.express as px
from PIL import Image

#%%% Advanced streamlit configurations
st.set_option('deprecation.showPyplotGlobalUse', False)

#Changing favicon
favicon = Image.open('favicon-health.png')
st.set_page_config(page_title='Weight Loss Calculator', page_icon = favicon, initial_sidebar_state = 'auto')

#Hiding streamlit menu and footer:
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

#%% Calculations:

def bmi_calc (my_weight,my_height):
    bmi= round (my_weight/ (my_height**2),3)
    if bmi<=18.5:
        status_bmi= "Underweight"
    elif 18.5<bmi<25:
        status_bmi= "Normal"
    elif 25<=bmi<30:
        status_bmi= "Overweight"
    elif bmi>=30:
        status_bmi= "Obesity"
    return bmi,status_bmi
    
def weight_dec (start_day,num_weeks,my_weight,my_height):
    dec_1percent= []
    dec_1percent.append(my_weight)
    dec_0_75percent= []
    dec_0_75percent.append(my_weight)
    dec_0_50percent= []
    dec_0_50percent.append(my_weight)
    dec_0_25percent= []
    dec_0_25percent.append(my_weight)
    date_list=[]
    
    for i in range(0,num_weeks):
        dec_1percent.append(dec_1percent[-1] *(1-0.01))
        dec_0_75percent.append(dec_0_75percent[-1] *(1-0.0075))
        dec_0_50percent.append(dec_0_50percent[-1] *(1-0.005))
        dec_0_25percent.append(dec_0_25percent[-1] *(1-0.0025))

    today=datetime.now().strftime("%d/%m/%Y")
    start_day_converted=start_day.strftime("%d/%m/%Y")
    if start_day_converted == today:
        for i in range(0,num_weeks+1): 
            date_list.append(((datetime.now() + timedelta(weeks=i)).strftime("%d/%m/%Y")))
    else:
        for i in range(0,num_weeks+1): 
            date_list.append(((start_day+ timedelta(weeks=i)).strftime("%d/%m/%Y")))
    
    df= pd.DataFrame(list(zip(date_list,dec_1percent,dec_0_75percent,dec_0_50percent,dec_0_25percent)),columns=['Date','1p','075p', '05p','025p'])
    df[['1p','075p', '05p','025p']].round(2)
    df["bmi1p"] = round(df["1p"]/ (my_height**2),2)
    df["bmi075p"] = round(df["075p"]/ (my_height**2),2)
    df["bmi05p"] = round(df["05p"]/ (my_height**2),2)
    df["bmi025p"] = round(df["025p"]/ (my_height**2),2) 
    
    return df

def convert_df(df):
   return df.to_csv().encode('utf-8')

#%% Main
def main():
    st.sidebar.title("Healthy weight loss calculator")
    menu = ["BMI Calculator","About The App"]
    choice = st.sidebar.selectbox("Menu", menu)
    st.sidebar.subheader("The app will calculate a 0.25-1% loss of your weight per week")
    st.sidebar.markdown("""<a href="https://www.linkedin.com/in/yair-heskiau-shteinberg-056bb080">**Dr. Yair Heskiau Shteinberg**</a>""", unsafe_allow_html=True)
    st.sidebar.markdown("""<a href="https://github.com/hiski88/Healthy_weight_loss_calculator">**Github**</a>""", unsafe_allow_html=True)
    st.sidebar.markdown("""<a href="https://bmmil.org/donate/">**Donate to our NPO Health, Research and Science in Israel**</a>""", unsafe_allow_html=True)
    st.sidebar.markdown("""<a href="https://bmmil.org/donate/">**לתרומה לעמותת בריאות מחקר ומדע בישראל ע.ר**</a>""", unsafe_allow_html=True) 

    if choice == "BMI Calculator":
        st.title("Calculate your future weight and BMI")
        st.header("Enter your Weight in Kilograms and your Height in Meters")      
        col1, col2 = st.columns(2)
        with col1: user_weight = float(st.number_input(label='Weight in Kilograms', min_value=0.0,max_value=180.0, step=0.1,help ="Example: 100.5", format="%.1f"))
        with col2: user_height = float(st.number_input(label='Height in Meters', value=1.75,min_value=0.5,max_value=2.5, step=0.01,help ="Example: 1.80", format="%.2f"))
        col3, col4 = st.columns(2)
        with col3: user_num_weeks = st.number_input(label='Enter the number of weeks to calculate:',min_value=1,max_value=400, value=13, step=1, help ="Example: 13")
        with col4: start_day= st.date_input("Starting Date", min_value=None, max_value=None, key=None, help='Default=Today. Otherwise: enter the exact day that you have started your weight loss program')
        
        submit_button= st.button("Submit")
        
        if submit_button:
            if user_weight is None or user_height is None:
                st.error("Please fill your weight and height")
            else:
                st.write("Your weight: ", user_weight, "kilograms. Your height", user_height, "meters. Current BMI is: ", bmi_calc(user_weight,user_height))
                st.info("BMI range:")
                type_bmi= ["Underweight","Normal weight","Overweight","Obesity"]
                bmi_values= ["<=18.5","18.5–24.9","25–29.9",">=30"]
                df_bmi_general= pd.DataFrame(list(zip(type_bmi,bmi_values)),columns=['BMI Type','Values'])
                st.dataframe(df_bmi_general)
                
                df= weight_dec(start_day,user_num_weeks,user_weight,user_height)
                df_weight = pd.melt(df, id_vars='Date', value_vars=['1p','075p', '05p','025p'])
                df_weight["variable"].replace({"1p":"1%","075p":"0.75%","05p":"0.5%","025p":"0.25%"}, inplace=True)
                df_bmi = pd.melt(df, id_vars='Date', value_vars=['bmi1p','bmi075p', 'bmi05p','bmi025p'])
                df_bmi["variable"].replace({"bmi1p":"1%","bmi075p":"0.75%","bmi05p":"0.5%","bmi025p":"0.25%"}, inplace=True)
                

                #Plotly figures (weight and BMI)
                fig = px.line(df_weight, x="Date", y="value", color="variable", line_dash ="variable", symbol ="variable", title="Weight loss per week", labels={"value": "Weight [Kg]", "variable": "% of Weight decrease"})
                fig.update_layout(font_color="blue", title_font_color="blue", legend_title_font_color="blue",title_font_size=22, font_size=18)
                fig2= px.line(df_bmi, x="Date", y="value", color="variable", line_dash ="variable", symbol ="variable", title="BMI change per week", labels={"value": "BMI [Kg/m^2]", "variable": "% of Weight decrease"})                
                fig2.update_layout(font_color="blue", title_font_color="blue", legend_title_font_color="blue", title_font_size=22, font_size=18, yaxis_title='BMI [Kg/m<sup>2</sup>]')
                #adding BMI info:
                fig2.add_hrect(y0=18.5, y1=25, line_width=0, fillcolor="green", opacity=0.4, annotation_text="Normal Weight",annotation_position="top left")
                fig2.add_hrect(y0=30, y1=40, line_width=0, fillcolor="red", opacity=0.4, annotation_text="Obesity",annotation_position="top left")
                fig2.add_hrect(y0=25, y1=30, line_width=0, fillcolor="red", opacity=0.2, annotation_text="Overweight",annotation_position="top left")
                fig2.add_hrect(y0=17.5, y1=18.5, line_width=0, fillcolor="red", opacity=0.4, annotation_text="Underweight",annotation_position="top left")
                #fig2.add_hrect(y0=15, y1=17.5, line_width=0, fillcolor="red", opacity=0.6, annotation_text="Anorexia",annotation_position="top left")
                fig2.add_hrect(y0=40, y1=45, line_width=0, fillcolor="red", opacity=0.6, annotation_text="Morbid Obesity",annotation_position="top left")
                
                st.plotly_chart(fig, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=True)
                
                st.subheader("Your Data in a Table")
                st.dataframe(df.style.format({'1p': '{:.2f}','075p': '{:.2f}','05p': '{:.2f}','025p': '{:.2f}', 
                                              'bmi1p': '{:.2f}', 'bmi075p': '{:.2f}', 'bmi05p': '{:.2f}', 'bmi025p': '{:.2f}'}))
                st.download_button(data=convert_df(df), file_name='WeightLossData.csv', label='Download Table', mime='text/csv')

    else: 
        #About
        st.subheader("About The App")
        st.info("BMI applies to most adults 18-65 years.")
        st.error("**Who shouldn't use a BMI calculator?**")
        st.write("BMI is not used for muscle builders, long distance athletes, pregnant women, the elderly or young children.")
        st.write("This is because BMI does not take into account whether the weight is carried as muscle or fat, just the number.")
        st.write("Those with a higher muscle mass, such as athletes, may have a high BMI but not be at greater health risk.")
        st.write("Those with a lower muscle mass, such as children who have not completed their growth or the elderly who may be losing some muscle mass may have a lower BMI. ")
        st.write("During pregnancy and lactation, a woman's body composition changes, so using BMI is not appropriate.")
        st.write("The app doesn't offer medical consultation nor any medical recommendations. please refer to your physician or nutritionist.")
        st.error("**BMI less than 17.5 can be used to diagnose Anorexia nervosa (mild: 17-17.5, moderate: 16-17, severe: 15-16).**")
        st.error("**BMI less than 13.5 may lead to organ failure**")
        st.info("The app doesn't offer medical consultation nor any medical recommendations. please refer to your physician or nutritionist.")
        st.info(" For more information about weight loss: https://www.mayoclinic.org/healthy-lifestyle/weight-loss/in-depth/weight-loss/art-20047752 ")

if __name__ == '__main__':
    main()
