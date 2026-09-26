import streamlit as st
import numpy as np
import os, gdown
from tensorflow import keras
from PIL import Image

st.set_page_config(page_title="SeisGas F3 Model", layout="wide")
st.title("🔥 SeisGasApp - F3 Netherlands Live")

@st.cache_resource
def load_model():
    file_id = "1m-s-xpTiZqw0ROvJvSMm9o0rloGP7iWo"
    output = "F3_gas_model.h5"
    if not os.path.exists(output):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output, quiet=False)
    model = keras.models.load_model(output)
    return model

model = load_model()
st.success("Model Loaded! CNN 128x128")

uploaded_file = st.file_uploader("Apni F3 Seismic Image upload karo", type=["jpg","png","jpeg"])

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert('RGB')
    st.image(img, width=300)
    img_resized = img.resize((128, 128))
    img_array = np.array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    if st.button("🚀 Predict Gas"):
        pred = model.predict(img_array)[0][0]
        if pred > 0.5:
            st.balloons()
            st.success(f"HIGH GAS ZONE! {pred*100:.2f}%")
        else:
            st.warning(f"Low Gas Zone { (1-pred)*100:.2f}%")
