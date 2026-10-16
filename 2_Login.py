import streamlit as st
from utils import set_language, t, authenticate

st.set_page_config(page_title="Farmer Login", page_icon="🔐")
set_language()
st.title("🔐 " + t("login"))
with st.form("login_form"):
    username = st.text_input(t("username"))
    password = st.text_input(t("password"), type="password")
    submitted = st.form_submit_button(t("login_button"), use_container_width=True)
if submitted:
    farmer = authenticate(username, password)
    if farmer:
        st.session_state["farmer"] = farmer
        st.success(t("welcome") + ", " + farmer["full_name"] + "!")
        st.switch_page("pages/3_Dashboard.py")
    else:
        st.error(t("bad_login"))
st.page_link("app.py", label="← Home / मुख्यपृष्ठ")
