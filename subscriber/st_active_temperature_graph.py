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
	temperature1_sensor1_high = conn.query('SELECT MAX(reading), timestamp FROM temperature1 WHERE sensor_name = "DS18B20_1"')
	
	temperature1_sensor2 = conn.query('SELECT * FROM temperature1 WHERE sensor_name = "DS18B20_2" ORDER BY id')
	temperature1_sensor2_high = conn.query('SELECT MAX(reading), timestamp FROM temperature1 WHERE sensor_name = "DS18B20_2"')
	
	temperature1_sensor3 = conn.query('SELECT * FROM temperature1 WHERE sensor_name = "DS18B20_3" ORDER BY id')
	temperature1_sensor3_high = conn.query('SELECT MAX(reading), timestamp FROM temperature1 WHERE sensor_name = "DS18B20_3"')
	
	#Create dataframes
	temperature1_sensor1_df = pd.DataFrame(temperature1_sensor1)
	temperature1_sensor1_high_df = pd.DataFrame(temperature1_sensor1_high)
	temperature1_sensor1_high_string = temperature1_sensor1_high_df.to_string(header=False, index=False, index_names=False)
	
	temperature1_sensor2_df = pd.DataFrame(temperature1_sensor2)
	temperature1_sensor2_high_df = pd.DataFrame(temperature1_sensor2_high)
	temperature1_sensor2_high_string = temperature1_sensor2_high_df.to_string(header=False, index=False, index_names=False)
	#temperature1_sensor2_high_df = pd.Series({"DS18B20_2 High":[temperature1_sensor2_high]})
	
	temperature1_sensor3_df = pd.DataFrame(temperature1_sensor3)
	temperature1_sensor3_high_df = pd.DataFrame(temperature1_sensor3_high)
	temperature1_sensor3_high_string = temperature1_sensor3_high_df.to_string(header=False, index=False, index_names=False)
	
	#Append daraframe to return
	return temperature1_sensor1_df, temperature1_sensor2_df, temperature1_sensor3_df, temperature1_sensor1_high_string, temperature1_sensor2_high_string, temperature1_sensor3_high_string

# Main Streamlit app
placeholder = st.empty()
while True:
	
	#Append returned dataframe here
	sensor1_df, sensor2_df, sensor3_df, sensor1_high, sensor2_high, sensor3_high = updateGraph()
	
	with placeholder.container():
		line1 = (
			alt.Chart(sensor1_df)
			.mark_line()
			.encode(x="timestamp", y="reading", color=alt.value("red"))
		)
		line2 = (
			alt.Chart(sensor2_df)
			.mark_line()
			.encode(x="timestamp", y="reading", color=alt.value("green"))
		)
		line3 = (
			alt.Chart(sensor3_df)
			.mark_line()
			.encode(x="timestamp", y="reading")
		)
		
		st.altair_chart(line1+line2+line3)
		st.write("Sensor1 High: ", sensor1_high, "  \n", "Sensor2 High: ", sensor2_high, "  \n", "Sensor3 High: ", sensor3_high) 
		#st.write(sensor1_high_df)
	time.sleep(3)
	st.cache_data.clear()
	# Rerun Streamlit to update the chart
	st.rerun()
