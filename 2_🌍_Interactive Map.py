import streamlit as st
from functions import log_in

st.markdown("""
        <style>
               .block-container{
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                }
                span[data-baseweb="tag"] {
                 background-color: #3182BD !important;
                }

        </style>
        """, unsafe_allow_html=True)

def main():
    if not log_in.log_in():
        st.stop()
    else:
        pass

if __name__ == '__main__':
    st.title("Interactive Map") 
    main()