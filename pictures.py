import streamlit as st

def pic(pic_url=None,pic_caption=None,pic_width='content'):
    if pic_url is not None:
        st.image(pic_url, caption=pic_caption, width=pic_width)