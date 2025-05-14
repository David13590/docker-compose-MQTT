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
	return temperature1_sensor1_df

# Main Streamlit app
placeholder = st.empty()
while True:
	df = updateGraph()
	with placeholder.container():
		#st.altair_chart(df)
		#st.dataframe(df)
		st.line_chart(df, y=["reading"])
		print(df["reading"])
	time.sleep(5)
	st.cache_data.clear()
	# Rerun Streamlit to update the chart
	st.rerun()
