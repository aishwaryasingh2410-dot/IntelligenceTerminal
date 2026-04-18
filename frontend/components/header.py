import streamlit as st

def show_header():

    st.markdown(
        """
        <div class="main-title">
        📊 Team Rocket Options Analytics Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("Real-time options market analytics")
