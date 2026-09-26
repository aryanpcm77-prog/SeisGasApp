import streamlit as st
import numpy as np
import os
import gdown
from tensorflow import keras

st.set_page_config(page_title="SeisGas F3 Model", layout="wide")
st.title("🔥 SeisGasApp - F3 Netherlands Live")
st.markdown("F3 Dataset | IIT Kharagpur | Aryan")

# Google Drive se model download
@st.cache_resource
def load_model():
    file_id = "1m-s-xpTiZqw0ROvJvSMm9o0rloGP7iWo"
    output = "F3_gas_model.h5"

    if not os.path.exists(output):
        with st.spinner("F3 Model Drive se download ho raha hai... 1st time thoda time lagega"):
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, output, quiet=False)

    model = keras.models.load_model(output)
    return model

model = load_model()

col1, col2 = st.columns(2)
with col1:
    seismic = st.slider("Seismic Attribute", 0.0, 100.0, 26.99)
with col2:
    porosity = st.slider("Porosity", 0.0, 1.0, 0.30)

if st.button("🚀 Predict with F3 Model"):
    input_data = np.array([[seismic, porosity]])
    pred = model.predict(input_data)[0][0]

    st.success(f"### Predicted Gas: {pred:.2f}%")

    if pred > 25:
        st.balloons()
        st.info("🔥 High Gas Zone Detected in F3!")

st.divider()
st.caption("Model loaded from Google Drive | Size >100MB")
