import streamlit as st
from functions import log_in
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide",
                   page_title='O&G Dashboard',
                   page_icon="🛢")

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

make_map_responsive= """
 <style>
 [title~="st.iframe"] { width: 100%}
 </style>
"""
st.markdown(make_map_responsive, unsafe_allow_html=True)


@st.cache_resource
def load_data():
    concesiones = gpd.read_file('./data/geo/concesiones/concesiones.shp')
    concesiones = concesiones[['NOMBRE_DE_', 'CODIGO_DE_', 'EMPRESA_OP', 'PARTICIPAC','geometry']]
    gasoductos = gpd.read_file('./data/geo/gasoductos/gasoductos.shp')
    gasoductos =  gasoductos[['NOMBRE', 'NOMBRE_DE_', 'EMPRESA_LI', 'TIPO_DE_TR', 'SUBTIPO_DE', 'geometry']]
    ductos_hc = gpd.read_file('./data/geo/ductos-hidrocarburos/ductos-hidrocarburos.shp')
    ductos_hc = ductos_hc [['DUCTO', 'TRAMO', 'EMPRESA', 'TIPO_DUCTO', 'JURIDICCIO', 'ESTADO', 'geometry']]
    return concesiones, gasoductos, ductos_hc

def map(concesiones, gasoductos, ductos_hc):

    col1,col2 = st.columns(2)
    with col1:
        m = folium.Map(location=[-36, -65], zoom_start=5)

        c_tooltip = folium.GeoJsonTooltip(fields=['NOMBRE_DE_', 'CODIGO_DE_', 'EMPRESA_OP', 'PARTICIPAC'])
        g_tooltip = folium.GeoJsonTooltip(fields=['NOMBRE', 'NOMBRE_DE_', 'EMPRESA_LI', 'TIPO_DE_TR', 'SUBTIPO_DE'])
        g_style = {'fillColor': '#046E46', 'color': '#046E46'}
        hc_tooltip = folium.GeoJsonTooltip(fields=['DUCTO', 'TRAMO', 'EMPRESA', 'TIPO_DUCTO', 'JURIDICCIO', 'ESTADO'])
        hc_style = {'fillColor': '#9e0740', 'color': '#9e0740'}

        folium.GeoJson(concesiones,name="concesiones",tooltip=c_tooltip).add_to(m)
        folium.GeoJson(gasoductos,name="gasoductos",tooltip=g_tooltip,style_function=lambda x:g_style).add_to(m)
        folium.GeoJson(ductos_hc,name="ductos de hidrocaburos",tooltip=hc_tooltip,style_function=lambda x:hc_style).add_to(m)
        folium.LayerControl().add_to(m)

        st_folium(m)



def main():
    if not log_in.log_in():
        st.stop()
    else:
        concesiones,gasoductos,ductos_hc = load_data()
        map(concesiones,gasoductos,ductos_hc)

if __name__ == '__main__':
    st.title("Interactive Map") 
    main()