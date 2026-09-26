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
                import streamlit as st
import numpy as np
import os, gdown
from tensorflow import keras
from PIL import Image
import time

st.set_page_config(page_title="SeisGas F3 Model - Secured", layout="wide")

# ========== 1. PASSWORD PROTECTION ==========
def check_password():
    def password_entered():
        # Password ko Secrets me rakho, code me nahi
        
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.title("🔒 SeisGasApp - Private")
        st.text_input("Password daalo", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 SeisGasApp - Private")
        st.text_input("Password daalo", type="password", on_change=password_entered, key="password")
        st.error("Galat Password")
        return False
    else:
        return True

if not check_password():
    st.stop()

# ========== MAIN APP ==========
st.title("🔥 SeisGasApp - F3 Netherlands Live | SECURED")
st.markdown("Authenticated Access Only")

@st.cache_resource
def load_model():
    # ========== 2. MODEL ID KO SECRET ME RAKHO ==========
    file_id = st.secrets.get("gdrive_id", "1m-s-xpTiZqw0ROvJvSMm9o0rloGP7iWo")
    output = "F3_gas_model.h5"
    if not os.path.exists(output):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output, quiet=True)
    model = keras.models.load_model(output)
    return model

model = load_model()
model_channels = model.input_shape[-1]

# ========== 3. FILE VALIDATION + SIZE LIMIT ==========
uploaded_file = st.file_uploader("Image upload karo", type=["jpg","png","jpeg"])

if uploaded_file is not None:
    # Hack rokne ke liye - 5MB se badi file block
    if uploaded_file.size > 5 * 1024 * 1024:
        st.error("File bahut badi hai! 5MB se kam upload karo.")
        st.stop()

    try:
        img_original = Image.open(uploaded_file)
        # Check karo image hi hai ya koi virus
        img_original.verify()
        img_original = Image.open(uploaded_file) # verify ke baad dobara open karna padta hai
    except:
        st.error("Ye valid image nahi hai!")
        st.stop()

    st.image(img_original, caption="Uploaded", width=350)

    # ========== 4. RATE LIMITING ==========
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

# ========== 5. FOOTER SE INFO HATAO ==========
st.markdown("---")
st.caption("© 2026 SeisGasApp | Protected | IIT KGP")
