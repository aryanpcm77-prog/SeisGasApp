import streamlit as st
import numpy as np

st.set_page_config(page_title="SeisGas Predictor", layout="centered")
st.title("SeisGas - Gas Prediction App")
st.write("Seismic data se gas predict karne wala demo")

seis = st.slider("Seismic Value", 0.0, 100.0, 50.0)
porosity = st.slider("Porosity", 0.0, 1.0, 0.3)

if st.button("Predict Gas"):
    result = (seis * 0.6 + porosity * 40)
    st.success(f"Predicted Gas: {result:.2f} units")
    st.balloons()