import streamlit as st
from utils import set_language, t

st.set_page_config(page_title="Crop Recommendation System", page_icon="🌱", layout="wide")
set_language()
st.title("🌱 " + t("app_title"))
st.write(t("home_intro"))
st.info(t("home_note"))

c1, c2 = st.columns(2)
with c1:
    st.subheader(t("register"))
    st.write(t("register_desc"))
    if st.button(t("register"), use_container_width=True):
        st.switch_page("pages/1_Register.py")
with c2:
    st.subheader(t("login"))
    st.write(t("login_desc"))
    if st.button(t("login"), use_container_width=True):
        st.switch_page("pages/2_Login.py")

st.divider()
st.subheader(t("features_title"))
for item in t("features"):
    st.write("• " + item)
