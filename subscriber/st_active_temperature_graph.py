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
	#pd.merge(temperature1_sensor1_df, temperature1_sensor2_df)
	
	#temperature1_sensor1_df["datetime"] = pd.to_datetime(temperature1_sensor1_df["timestamp"], format="%Y%m%d %H:%M:%S")
	
	
	return temperature1_sensor1_df, temperature1_sensor2_df

# Main Streamlit app
placeholder = st.empty()
while True:
	df1,df2 = updateGraph()
	with placeholder.container():
		lines1 = (
			alt.Chart(df1)
			.mark_line()
			.encode(x="timestamp", y="reading", color=alt.value("red"))
		)
		lines2 = (
			alt.Chart(df2)
			.mark_line()
			.encode(x="timestamp", y="reading")
		)
		
		st.altair_chart(lines1+lines2)
		#st.dataframe(df)
		#st.line_chart(df, y=["reading"])
		print(df1["reading"])
		print(df2["reading"])
	time.sleep(5)
	st.cache_data.clear()
	# Rerun Streamlit to update the chart
	st.rerun()
