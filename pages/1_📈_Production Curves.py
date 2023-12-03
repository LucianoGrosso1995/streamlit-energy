import streamlit as st
from functions import log_in
import altair as alt
import pandas as pd

_PARQUET_CURVE= './data/database_curve.parquet'
alt.data_transformers.enable('default', max_rows=None)

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

def load_data():
    db = pd.read_parquet(_PARQUET_CURVE)
    cuencas = db['cuenca'].dropna().unique()
    anio_inicio = db['anio_inicio'].dropna().unique()
    well_type = db['tipopozo'].dropna().unique()
    return db,cuencas,anio_inicio,well_type

def sidebar(cuencas,anio_inicio,well_type):
    st.sidebar.markdown('## Select Resource Type')
    selected_resource = st.sidebar.multiselect(label='',label_visibility='collapsed',
                         default=['CONVENCIONAL','TIGHT','SHALE'],
                         options=['CONVENCIONAL','TIGHT','SHALE'])
    
    st.sidebar.markdown('## Select Basin')
    selected_basin = st.sidebar.multiselect(label='',label_visibility='collapsed',
                         default=cuencas,
                         options=cuencas)
    
    st.sidebar.markdown('## Select First Production Year')
    selected_anio = st.sidebar.slider(label="",
                                      value=[anio_inicio.min(),anio_inicio.max()],
                                      min_value=2007,max_value=anio_inicio.max())
    
    st.sidebar.markdown('## Select Well Type')
    selected_well = st.sidebar.multiselect(label='',label_visibility='collapsed',
                         default=well_type,
                         options=well_type)

    return selected_resource, selected_basin, selected_anio, selected_well

def charts(df):
    curve = df.groupby(by=['anio_inicio','mes_produccion']).aggregate({'Th boe/d':'sum','sigla':'sum'}).reset_index()
    curve['boe/d/pozo'] = curve['Th boe/d'] * 1000 / curve['sigla']
    curve.drop(columns=['Th boe/d','sigla'],inplace=True)


    fig = alt.Chart(
                curve,
                title='Well Production Curve by First Production Year'
            ).mark_line().encode(
            x=alt.X('mes_produccion:Q').title('Production Month'),
            y=alt.Y('sum(boe/d/pozo)').title('boe / d'),
            color=alt.Color('anio_inicio:N').title('First Production Year'),
            ).interactive()
    st.altair_chart(fig,use_container_width=True)
    
    
    acum = curve.groupby(by=['anio_inicio','mes_produccion']) \
                .sum().groupby(level=0).cumsum().reset_index()

    fig = alt.Chart(acum).mark_line().encode(
            x=alt.X('mes_produccion:Q').title('Production Month'),
            y=alt.Y('sum(boe/d/pozo)').title('boe / d'),
            color=alt.Color('anio_inicio:N').title('First Production Year'),
            ).interactive()
    st.altair_chart(fig,use_container_width=True)



def main():
    if not log_in.log_in():
        st.stop()
    else:
        db, cuencas, anio_inicio,well_type = load_data()
        selected_resource, selected_cuenca,selected_anio,selected_well = sidebar(cuencas,anio_inicio,well_type)
        query = """
                sub_tipo_recurso in @selected_resource \
                and cuenca in @selected_cuenca \
                and anio_inicio >= @selected_anio[0] \
                and anio_inicio <= @selected_anio[1] \
                and tipopozo in @selected_well
        """
        charts(db.query(query))


if __name__ == '__main__':
    st.title("Production Curves") 
    main()