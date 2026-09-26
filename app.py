import streamlit as st
import numpy as np
import os, gdown
from tensorflow import keras
from PIL import Image
import time

st.set_page_config(page_title="SeisGas F3 Model - Public Secured", layout="wide")
st.title("🔥 SeisGasApp - F3 Netherlands Live")

# Model ko Secret se load karo - koi ID chori nahi kar payega
@st.cache_resource
def load_model():
    file_id = st.secrets.get("gdrive_id", "1m-s-xpTiZqw0ROvJvSMm9o0rloGP7iWo")
    output = "F3_gas_model.h5"
    if not os.path.exists(output):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output, quiet=True)
    model = keras.models.load_model(output)
    return model

model = load_model()
model_channels = model.input_shape[-1]

uploaded_file = st.file_uploader("Image upload karo (JPG/PNG)", type=["jpg","png","jpeg"])

if uploaded_file is not None:
    # 1. SIZE LIMIT - 5MB se bada file block
    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("File bahut badi hai! 5MB se kam upload karo.")
        st.stop()

    # 2. FILE VALIDATION - Virus ya fake file block
    try:
        img_original = Image.open(uploaded_file)
        img_original.verify()
        img_original = Image.open(uploaded_file)
    except:
        st.error("Ye valid image nahi hai!")
        st.stop()

    st.image(img_original, caption="Uploaded", width=350)

    # 3. RATE LIMIT - Baar baar predict se server down nahi hoga
    if "last_predict" in st.session_state:
        if time.time() - st.session_state["last_predict"] < 3:
            st.warning("Thoda slow bhai... 3 sec ruk ke dobara dabao")
            st.stop()

    if model_channels == 1:
        img = img_original.convert('L')
        img_resized = img.resize((128, 128))
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=(0, -1))
    else:
        img = img_original.convert('RGB')
        img_resized = img.resize((128, 128))
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

    if st.button("🚀 Predict Gas"):
        st.session_state["last_predict"] = time.time()
        pred = model.predict(img_array, verbose=0)

        if pred.shape[-1] == 2:
            class_id = int(np.argmax(pred[0]))
            conf = float(pred[0][class_id]*100)
            if class_id == 1:
                st.balloons()
                st.success(f"🔥 HIGH GAS ZONE! {conf:.2f}%")
            else:
                st.warning(f"💧 LOW GAS Zone. {conf:.2f}%")
        else:
            val = float(pred[0][0])
            if val > 0.5:
                st.balloons()
                st.success(f"🔥 HIGH GAS ZONE! {val*100:.2f}%")
            else:
                st.warning(f"💧 LOW GAS Zone. {(1-val)*100:.2f}%")

st.caption("© 2026 SeisGasApp | Public Secured")
