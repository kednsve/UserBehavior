import streamlit as st

from src import analysis_funnel_pie, basic_analysis, rfm_analysis, hot_analysis


@st.cache_data
def get_funnel_pie():
    return analysis_funnel_pie()


@st.cache_data
def get_basic_analysis():
    return basic_analysis()


@st.cache_data
def get_rfm_analysis():
    return rfm_analysis()


@st.cache_data
def get_hot_analysis():
    return hot_analysis()


funnel_html, pie_html = get_funnel_pie()
basic_fig = get_basic_analysis()
rfm_bar = get_rfm_analysis()
hot_fig = get_hot_analysis()

st.set_page_config(page_title="UserBehavior", layout="wide")
st.title("User Behavior")
st.markdown("---")
basic, hot, pie, funnel, rfm = st.tabs(
    ["流量分析", "热门商品", "用户行为分布", "用户转化", "RFM"]
)
with basic:
    col, _ = st.columns([4, 3])
    with col:
        st.header("日PV/BUY")
        st.pyplot(basic_fig)
with hot:
    col, _ = st.columns([4, 3])
    with col:
        st.header("热门商品")
        st.pyplot(hot_fig)
with pie:
    st.header("用户行为分布")
    st.iframe(pie_html.render_embed(), height=600, width=1000)
with funnel:
    st.header("用户转化率")
    st.iframe(funnel_html.render_embed(), height=600, width=1000)
with rfm:
    st.header("RFM")
    st.iframe(rfm_bar.render_embed(), height=600, width=1000)
