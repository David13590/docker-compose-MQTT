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
	temperature1_table = conn.query('SELECT * FROM temperature1 ORDER BY id')
	temperature_df = pd.DataFrame(temperature1_table)
	#selected_columns = temperature_df.loc[:, ['timestamp', 'reading']]
	#return selected_columns
	return temperature_df

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
