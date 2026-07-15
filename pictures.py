import streamlit as st
import os

def pic(pic_url=None,pic_caption=None,pic_width='content'):
    if pic_url is not None:
        st.image(pic_url, caption=pic_caption, width=pic_width)

def pic_list():
    for x in os.listdir('.//images'):
        if x.endswith(".jpg") or x.endswith(".png"):
            #st.badge(x, icon=":material/check:", color="green")
            pic('./images/'+x, pic_caption=x)
            #st.image('./images/'+x, caption=x)
        else:
            st.text(x)