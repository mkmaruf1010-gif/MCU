import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Biometric Attendance Analytics", layout="wide")

st.title("🪪 Real-Time Biometric Attendance Analytics")
st.caption("Live Feed synced from NodeMCU via Google Sheets")

# গুগল শিটের পাবলিক CSV র-লিংক (আপনার শিটটি Share -> 'Anyone with link' করে নিন)
SHEET_ID = "1Vq-2uJYSyJA_XZcSNyNxkZVRuNz-rpMalQYAx9V1hxw"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=5) # প্রতি ৫ সেকেন্ডে নতুন ডেটা ফেচ হবে
def load_data():
    df = pd.read_csv(SHEET_URL)
    return df

try:
    df = load_data()
    df.columns = ["Timestamp", "User_ID", "Status"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Attendance Logs", len(df))
    col2.metric("Unique Users Today", df["User_ID"].nunique())
    col3.metric("Last Check-In User ID", df["User_ID"].iloc[-1] if not df.empty else "N/A")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📋 Recent Attendance Records")
        st.dataframe(df.tail(10), use_container_width=True)

    with col_right:
        st.subheader("📊 Check-In Distribution by User")
        user_counts = df["User_ID"].value_counts().reset_index()
        user_counts.columns = ["User_ID", "Logs Count"]
        fig = px.bar(user_counts, x="User_ID", y="Logs Count", color="Logs Count", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Waiting for first attendance entry from NodeMCU...")

# রিয়েল-টাইম রিফ্রেশ বাটনের বিকল্প
if st.button("🔄 Refresh Data"):
    st.rerun()
