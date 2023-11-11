import streamlit as st
import pandas as pd
import altair as alt

_PARQUET_PROD = './data/database_prod_resource_basin.parquet'
_PARQUET_DATABASE = './data/database.parquet'
_PARQUET_NEW_WELLS = './data/database_new_wells.parquet'

alt.data_transformers.enable('default', max_rows=None)
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


def load_data():
    db = pd.read_parquet(_PARQUET_PROD)
    db_new_wells = pd.read_parquet(_PARQUET_NEW_WELLS)
    cuencas = db['cuenca'].dropna().unique()
    return db, db_new_wells, cuencas

def sidebar(cuencas):
    st.sidebar.markdown('## Select Resource Type')
    selected_resource = st.sidebar.multiselect(label='',label_visibility='collapsed',
                         default=['CONVENCIONAL','TIGHT','SHALE'],
                         options=['CONVENCIONAL','TIGHT','SHALE'])
    
    st.sidebar.markdown('## Select Basin')
    selected_basin = st.sidebar.multiselect(label='',label_visibility='collapsed',
                         default=cuencas,
                         options=cuencas)

    return selected_resource, selected_basin


def charts(df,df_new_wells):
    
    col1, col2, col3 = st.columns(3,gap="small")
    with col1:
        # Oil Production by Rouserce Type Chart

        source = df.groupby(by=['Date','sub_tipo_recurso'])['Th bbl/d'].sum().reset_index()
        fig = alt.Chart(
                    source,
                    title = alt.Title('Oil Production by Resource Type')
                ).mark_area().encode(
                    x=alt.X("Date:T").axis(format="%y-%m").title(None),
                    y=alt.Y("sum(Th bbl/d):Q").title('Th bbl/d'),
                    color=alt.Color("sub_tipo_recurso").legend(
                        orient='bottom-left',
                        title=None,
                        fillColor='lightgray').scale(scheme='category20c')
                ).properties(
                    height=300
                ).interactive()
        st.altair_chart(fig,use_container_width=True)

        # Oil Production by Basin Chart

        source = df.groupby(by=['Date','cuenca'])['Th bbl/d'].sum().reset_index()
        fig = alt.Chart(
                    source,
                    title = alt.Title('Oil Production by Basin')
                ).mark_area().encode(
                    x=alt.X("Date:T").axis(format="%y-%m").title(None),
                    y=alt.Y("sum(Th bbl/d):Q").title('Th bbl/d'),
                    color=alt.Color("cuenca").legend(
                        orient='bottom-left',
                        title=None,
                        fillColor='lightgray').scale(scheme='category20c')
                ).properties(
                    height=300
                ).interactive()
        st.altair_chart(fig,use_container_width=True)

    with col2:
        
        # Gas Production by Resource Type Chart 

        source = df.groupby(by=['Date','sub_tipo_recurso'])['Mm3/d'].sum().reset_index()
        fig = alt.Chart(
                    source,
                    title = alt.Title('Gas Production by Resource Type')
                ).mark_area().encode(
                    x=alt.X("Date:T").axis(format="%y-%m").title(None),
                    y=alt.Y("sum(Mm3/d):Q").title('Mm3/d'),
                    color=alt.Color("sub_tipo_recurso:N").legend(
                        orient='bottom-left',
                        title=None,
                        fillColor='lightgray').scale(scheme='category20c')
                ).properties(
                    height=300
                ).interactive()
        st.altair_chart(fig,use_container_width=True)

        # Gas Production by Basin Chart 

        source = df.groupby(by=['Date','cuenca'])['Mm3/d'].sum().reset_index()
        fig = alt.Chart(
                    source,
                    title = alt.Title('Gas Production by Basin')
                ).mark_area().encode(
                    x=alt.X("Date:T").axis(format="%y-%m").title(None),
                    y=alt.Y("sum(Mm3/d):Q").title('Mm3/d'),
                    color=alt.Color("cuenca:N").legend(
                        orient='bottom-left',
                        title=None,
                        fillColor='lightgray').scale(scheme='category20c')
                ).properties(
                    height=300
                ).interactive()
        st.altair_chart(fig,use_container_width=True)

    with col3: 

        # New Wells in Production
        source = df_new_wells[df_new_wells['Date'] >= '2020-01-01']
        source = source.groupby( by = ['Date','sub_tipo_recurso'])['sigla'].count().reset_index()

        fig = alt.Chart(
                    source,
                    title = alt.Title('New Wells in Production by Resource Type')).mark_bar().encode(
                x=alt.X("Date:T").axis(format="%y-%m").title(None),
                y=alt.Y("sigla:Q").title('New Wells'),
                color=alt.Color("sub_tipo_recurso:N").legend(
                        orient='bottom-left',
                        title=None,
                        fillColor='lightgray').scale(scheme='category20c')
            ).properties(
                    height=300
            ).interactive()
        st.altair_chart(fig,use_container_width=True)

        # Production by Operator

        last_date = max(df['Date'])

        source = df[df['Date'] == last_date]
        
        source = source.groupby(by=['empresa'])['Th boe/d'].sum().reset_index()

        fig = alt.Chart(
                    source,
                    title = alt.Title('Last Month Production in Th Boe/d by Company')).mark_arc().encode(
                theta='Th boe/d',
                order='Th boe/d',
                color=alt.Color(field='empresa').legend(None),
            ).properties(
                    height=300
            ).interactive()
        
        fig = alt.Chart(
                    source,
                    title = alt.Title('Last Month Production in Th Boe/d by Company')).mark_bar().encode(
                    x=alt.X('sum(Th boe/d):Q',title='Th boe/d'),
                    y=alt.Y('empresa:N').sort('-x')
             ).properties(
                 height = 300
             ).interactive()


        st.altair_chart(fig,use_container_width=True)




def kpis(db,db_new_wells):

    col1, col2, col3 = st.columns(3)
    last_date = max(db['Date'])
    prev_month = max(db.query('Date < @last_date')['Date'])

    with col1:
        last_oil = db[db['Date'] == last_date]['Th bbl/d'].sum().round(2)
        prev_oil = db[db['Date'] == prev_month]['Th bbl/d'].sum().round(2)
        delta_oil = (last_oil - prev_oil).round(2)
        st.metric(label=f'{last_date.strftime("%b %Y")} Oil Production [Th bbl/d]', value=last_oil,delta=delta_oil)

    with col2:
        last_gas = db[db['Date'] == last_date]['Mm3/d'].sum().round(2)
        prev_gas = db[db['Date'] == prev_month]['Mm3/d'].sum().round(2)
        delta_gas= (last_gas - prev_gas).round(2)
        st.metric(label=f'{last_date.strftime("%b %Y")} Gas Production [Mm3/d]', value=last_gas,delta=delta_gas)

    with col3:
        last_wells = len(db_new_wells[db_new_wells['Date'] == last_date])
        prev_wells = len(db_new_wells[db_new_wells['Date'] == prev_month])
        delta_wells= (last_wells - prev_wells)
        st.metric(label=f'{last_date.strftime("%b %Y")} New Wells in Production', value=last_wells,delta=delta_wells)

def main():
    st.title("Oil & Gas Dashboard")
    db, db_new_wells, cuencas = load_data()

    selected_resource, selected_cuenca = sidebar(cuencas)
    query = """
            sub_tipo_recurso in @selected_resource \
            and cuenca in @selected_cuenca
    """
    kpis(db.query(query), db_new_wells.query(query))
    charts(db.query(query), db_new_wells.query(query))
    
if __name__ == '__main__':
    main()    
