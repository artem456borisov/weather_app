import streamlit as st
import  pandas as pd
from streamlit_utils import current_weather, prepare_dataframe, get_season_stats
import matplotlib.pyplot as plt
import plotly.graph_objects as go


st.title("Weather App")
st.write("Get the current data for your city and find out if there is an anomaly")


uploaded_file = st.file_uploader("Выберите CSV-файл", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("Превью данных:")
    st.table(data.head())
    data = prepare_dataframe(data)
    KEY = st.text_input("Please enter you OpenWeatherAPI Key")
    st.session_state.city = st.selectbox("Where do you live?",data.city.unique())
    current_temp, anomaly = current_weather(st.session_state.city, KEY, data)

    if anomaly is not None:

        st.write(f"The current weather in {st.session_state.city} is {current_temp}. This weather is {'not normal' if anomaly else 'normal'}")

        st.write("Here are some desriptive statistics")
        st.table(data[data.city == st.session_state.city].describe())
        st.write("Also a time series graph with anomaly detection (You can scroll it)")
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data[data.city == st.session_state.city].timestamp,
            y=data[data.city == st.session_state.city].temperature,
            mode='lines',
            name='Temperature',
            line={'color':'blue'}
        ))

        fig.add_trace(go.Scatter(
            x=data[data.city == st.session_state.city].timestamp,
            y=data[data.city == st.session_state.city].lower_boundary,
            mode='lines',
            name='lower_boundary',
            line={'color':'red'}
        ))

        fig.add_trace(go.Scatter(
            x=data[data.city == st.session_state.city].timestamp,
            y=data[data.city == st.session_state.city].upper_boundary,
            mode='lines',
            name='upper_boundary',
            line={'color':'red'}
        ))


        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(visible=True),
                type="date"
            ),
            height=600,
            title="Temperature Over Time",
            xaxis_title="Timestamp",
            yaxis_title="Temperature",
        )

        st.plotly_chart(fig)

        # We also add some stats
        st.write("Stats for every season for your city.")
        st.table(pd.DataFrame(get_season_stats(data, st.session_state.city)))
        
    else:
        st.write(f"Invalid key! Got this response from OpenWeatherAPI: {current_temp}")
else:
    st.write("Пожалуйста, загрузите CSV-файл.")
