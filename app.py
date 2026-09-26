import streamlit as st
import numpy as np
import os, gdown
from tensorflow import keras
from PIL import Image

st.set_page_config(page_title="SeisGas F3 Model", layout="wide")
st.title("🔥 SeisGasApp - F3 Netherlands Live | IIT KGP")
st.markdown("F3 Dataset | Works on Color & Grayscale")

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
# Model ko kya chahiye ye nikal lete hai
model_channels = model.input_shape[-1] # 1 ya 3
st.success(f"Model Loaded! Model expects {model_channels} channel(s)")

uploaded_file = st.file_uploader("Seismic Image upload karo (Color ya B&W dono chalega)", type=["jpg","png","jpeg"])

if uploaded_file is not None:
    img_original = Image.open(uploaded_file)
    st.image(img_original, caption=f"Original: {img_original.mode} Image", width=350)

    # --- YEHI MAIN FIX HAI DONO KE LIYE ---
    # Agar model ko 1 channel chahiye toh L me convert, 3 chahiye toh RGB me
    if model_channels == 1:
        img = img_original.convert('L')
        target_size = (128, 128)
        img_resized = img.resize(target_size)
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=(0, -1)) # (1,128,128,1)
    else:
        img = img_original.convert('RGB')
        target_size = (128, 128)
        img_resized = img.resize(target_size)
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0) # (1,128,128,3)

    st.info(f"Converted to model input shape: {img_array.shape}")

    if st.button("🚀 Predict Gas"):
        pred = model.predict(img_array)

        if pred.shape[-1] == 2: # Softmax - 2 class
            class_id = int(np.argmax(pred[0]))
            conf = float(pred[0][class_id]*100)
            if class_id == 1:
                st.balloons()
                st.success(f"🔥 HIGH GAS ZONE! Confidence: {conf:.2f}%")
            else:
                st.warning(f"💧 LOW GAS / Water Zone. Confidence: {conf:.2f}%")
        else: # Sigmoid - 1 class
            val = float(pred[0][0])
            if val > 0.5:
                st.balloons()
                st.success(f"🔥 HIGH GAS ZONE! Confidence: {val*100:.2f}%")
            else:
                st.warning(f"💧 LOW GAS Zone. Confidence: {(1-val)*100:.2f}%")
