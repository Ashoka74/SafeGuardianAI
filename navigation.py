import streamlit as st
from PIL import Image
import base64

# def get_base64_of_bin_file(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# def set_png_as_page_bg(png_file):
#     bin_str = get_base64_of_bin_file(png_file)
#     page_bg_img = '''
#     <style>
#     .stApp {
#         background-image: url("data:image/png;base64,%s");
#         background-size: cover;
#     }
#     </style>
#     ''' % bin_str
#     st.markdown(page_bg_img, unsafe_allow_html=True)


pg = st.navigation([
            # add a rescue related icon like cross
            st.Page("main.py", title="RescueLLM", icon="🚑"),
            st.Page("map.py", title="Interactive Map", icon="🗺️")
        ])

pg.run()