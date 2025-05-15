import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import time
import altair as alt
from sqlalchemy import text

conn = st.connection('temperature_db', type='sql')

#Read data from db
def updateGraph():
	conn = st.connection('temperature_db', type='sql')
	
	#Add sensor query here
	temperature1_sensor1 = conn.query('SELECT * FROM temperature1 WHERE sensor_name = "DS18B20_1" ORDER BY id')
	temperature1_sensor2 = conn.query('SELECT * FROM temperature1 WHERE sensor_name = "DS18B20_2" ORDER BY id')
	
	temperature1_sensor1_df = pd.DataFrame(temperature1_sensor1)
	temperature1_sensor2_df = pd.DataFrame(temperature1_sensor2)
	
	#Append daraframe to return
	return temperature1_sensor1_df, temperature1_sensor2_df

# Main Streamlit app
placeholder = st.empty()
while True:
	
	#Append returned dataframe here
	sensor1_df, sensor2_df = updateGraph()
	
	with placeholder.container():
		line1 = (
			alt.Chart(sensor1_df)
			.mark_line()
			.encode(x="timestamp", y="reading", color=alt.value("red"))
		)
		line2 = (
			alt.Chart(sensor2_df)
			.mark_line()
			.encode(x="timestamp", y="reading")
		)
		
		st.altair_chart(line1+line2)
		print(sensor1_df["reading"])
		print(sensor2_df["reading"])
	time.sleep(5)
	st.cache_data.clear()
	# Rerun Streamlit to update the chart
	st.rerun()
