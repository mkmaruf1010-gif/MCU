import streamlit as st
import pandas as pd
import plotly.express as px
from flask import Flask, request, jsonify
import threading
import time

# ল্যাপটপে নোডএমসিইউ-র ডেটা রিসিভ করার জন্য ব্যাকগ্রাউন্ড ফ্লাস্ক সার্ভার
app = Flask(__name__)

# গ্লোবাল ডাটা স্টোর
sensor_data = {"distance": 100, "light": 0, "timestamp": time.time()}
data_history = []

@app.route('/update', methods=['POST'])
def update():
    global sensor_data
    content = request.json
    dist = content.get('distance', 100)
    light = content.get('light', 0)
    
    sensor_data["distance"] = dist
    sensor_data["light"] = light
    sensor_data["timestamp"] = time.strftime("%H:%M:%S")
    
    # ডেটা হিস্ট্রিতে সেভ করা
    if len(data_history) > 30:
        data_history.pop(0)
    data_history.append({"Time": sensor_data["timestamp"], "Distance (cm)": dist, "Aura Active": light})
    
    return jsonify({"status": "success"}), 200

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ব্যাকগ্রাউন্ডে ফ্লাস্ক চালু রাখা
if 'flask_started' not in st.session_state:
    threading.Thread(target=run_flask, daemon=True).start()
    st.session_state['flask_started'] = True

# ----------------- STREAMLIT UI DESIGN -----------------
st.set_page_config(page_title="AuraSync: Spatial Presence Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    .stMetric { background-color: #1a1f2c; padding: 15px; border-radius: 10px; border: 1px solid #2d3748; }
    </style>
""", unsafe_allow_unsafe_allow_html=True)

st.title("🌌 AuraSync: Spatial Presence & Aura Engine")
st.caption("Live Hardware-to-Dashboard Neural Mirror via ESP8266 NodeMCU")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Proximity Distance", value=f"{sensor_data['distance']} cm")

with col2:
    status_text = "AURA ACTIVE (Focus Mode)" if sensor_data['light'] == 1 else "IDLE (Space Empty)"
    st.metric(label="Room Status", value=status_text)

with col3:
    st.metric(label="Last Sync Time", value=sensor_data['timestamp'])

st.divider()

# রিয়েল-টাইম গ্রাফ ও হিটম্যাপ ভিজ্যুয়ালাইজেশন
st.subheader("📊 Live Proximity & Energy Matrix")

if data_history:
    df = pd.DataFrame(data_history)
    fig = px.line(df, x="Time", y="Distance (cm)", title="Spatial Distance Dynamics", template="plotly_dark")
    fig.update_traces(line_color="#00f2fe", line_width=3)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Waiting for NodeMCU data packet...")

# লাইভ অটো-রিফ্রেশ লুপ
time.sleep(1)
st.rerun()
