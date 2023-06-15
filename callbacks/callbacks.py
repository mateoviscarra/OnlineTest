import os
os.environ['USE_PYGEOS'] = '0'
import dash
import base64
import io
import pandas as pd
import geopandas as gpd
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import plotly.graph_objects as go
from dash import html
from layout.layout import create_dropdown

token = 'pk.eyJ1Ijoiam1zczExIiwiYSI6ImNsN3RsbHpldDEwNDIzdm1rMG1qZWx6cmUifQ.svDPURTTxi1aHuHpzPU8sQ'

###################################################################### Funcion para verificar la carga del csv 
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return html.Div([
                'Archivo no soportado: {}'.format(filename)
            ])
    except Exception as e:
        print(e)
        return html.Div([
            'Hubo un error al procesar este archivo.'
        ])

    if 'Latitud' not in df.columns or 'Longitud' not in df.columns:
        return html.Div([
            'El archivo no contiene las columnas necesarias: Latitud y Longitud.'
        ])

    return df
###################################################################### Funcion para crear un geodataframe a partir del csv
def toGeojson(df,latitud,longitud):
    return gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df[longitud],df[latitud],crs="EPSG:4326"))
###################################################################### Funcion para crear la figura del mapa
def create_map_figure(df, polygon_geojson=None):

    fig = go.Figure()
    
    if polygon_geojson is not None:
        gdf = gpd.GeoDataFrame.from_features(polygon_geojson['features'])# crea un gejson a partir del dicionario features
        #print(len(polygon_geojson['features']))
        #print(gdf.index.astype(str))
        choropleth_layer = go.Choroplethmapbox(
            #pasa los valores a la variables geojson
            geojson=polygon_geojson,
            locations=gdf.index.astype(str), #enumera todos los poligonos y is indices los vuelve texto
            z=gdf['Nivel'], # Usar la columna '0' como valores de color 
            colorscale='Turbo',
            hoverinfo='all', # Muestra toda la información en el hover
            hovertemplate='Nivel: %{z}<extra></extra>', # Personaliza el hover para mostrar solo la información que deseas
            #marker_opacity=0.2,
            showscale=False,# oculta la barra fea
            #marker_line_width=10
            marker=go.choroplethmapbox.Marker(
                opacity=0.2,
                line_width=2,  # Ajustar este valor para cambiar el grosor de las líneas de contorno
                line_color='rgba(0,0,0,0.9)'  # Ajustar este valor para cambiar el color de las líneas de contorno
            )
            # Resto de las configuraciones para la capa de polígonos...
        )
        fig.add_trace(choropleth_layer)

    scatter_trace = go.Scattermapbox(
        lat= df.Latitud,
        lon= df.Longitud,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color=df['Color'],
        ),
        text=df['Clase'],  # Agrega el texto que deseas mostrar en cada punto
        hovertemplate=
        '<b>Latitud</b>: %{lat}<br>' +
        '<b>Longitud</b>: %{lon}<br>' +
        '<b>Tipo de punto</b>: %{text}<extra></extra>',
        #customdata=df[['Clase']].values
    )

    fig.add_trace(scatter_trace)

    fig.update_layout(
        autosize=True,
        #title="Holla",  # Establece el título como una cadena vacía
        hovermode='closest',
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox=dict(
            accesstoken = token,
            style='dark',
            center={'lat': df.Latitud.mean(), 'lon': df.Longitud.mean()},
            zoom = 11,
            uirevision = 'constant', # agrega esta línea para cogelar el mapa
            #title='',  # Quita el título del gráfico
            #visible=False  # Quita el texto de la barra de título
        ),
        
    )

    return fig
###################################################################### hace todo los calculos para generar el KDE
def perform_kde(df, contour_levels=12):

    #Creo el gdf y cambio a UTM
    gdf = toGeojson(df,'Latitud','Longitud')
    gdf2 = gdf.to_crs(32720)

    #Obtiene los valores UTM
    lon = gdf2.geometry.x
    lat = gdf2.geometry.y
    peso = gdf2.Peso
    radio = gdf2.Radio

    #Los convierte a listas
    x = lon.to_list()
    y = lat.to_list()
    weights = peso.to_list()
    radii = radio.to_list()

    # Crear una cuadrícula de puntos
    x_grid, y_grid = np.meshgrid(np.linspace(min(x), max(x), 400), np.linspace(min(y), max(y), 200))

    # Calcular la influencia de cada punto en la cuadrícula
    influence = np.zeros_like(x_grid)
    for xi, yi, w, r in zip(x, y, weights, radii):
        dist = np.sqrt((x_grid - xi)**2 + (y_grid - yi)**2)
        #influence += np.exp(-dist**2 / (2 * r**2)) * w #Gaussian 95.1%
        #influence += np.maximum(1 - dist / r, 0) * w #Triangular 98.6%
        influence += np.maximum((1 - (dist / r) ** 2) ** 3, 0) * w  #Triweight 98.7%
    
    # Obtener los contornos sin relleno
    contours = plt.contour(x_grid, y_grid, influence, levels=contour_levels, colors='k').allsegs
    # Cerrar la figura para evitar que se muestre
    plt.close()

    # Crear los polígonos y el diccionario de atributos
    polygons = []
    for level, contour in zip(range(contour_levels), contours):
        for segment in contour:
            if len(segment) > 4:
                polygon = Polygon(segment)
                polygons.append({'Nivel': level, 'geometry': polygon})

    # Crear el GeoDataFrame de polígonos
    gdf_polygons = gpd.GeoDataFrame(polygons,crs="EPSG:32720")

    return gdf_polygons.to_crs(epsg=4326)
###################################################################### hace obtine los valores peso y radio del df
def transform_df(df_t):

    df = pd.DataFrame(df_t)
    classes = ['Agencia', 'ATM', 'Supermercado', 'Centro Médico', 'Hotel']
    other_classes = ['Centro Comercial', 'Mercado','Restaurante','Universidad']
    store_data = {}
    
    for i, cls in enumerate(classes):
        if cls == 'Agencia':
            #saca el peso y radio de agencias BNB
            p = df[(df['Clase'] == cls) & (df['Banco'] == 'Banco Nacional de Bolivia S.A.')]['Peso'].iloc[0]
            r = df[(df['Clase'] == cls) & (df['Banco'] == 'Banco Nacional de Bolivia S.A.')]['Radio'].iloc[0]

            store_data[str(2*i)] = p
            store_data[str(2*i + 1)] = r

            #saca el peso y radio de agencias que no son BNB
            p = df[(df['Clase'] == cls) & (df['Banco'] != 'Banco Nacional de Bolivia S.A.')]['Peso'].iloc[0]
            r = df[(df['Clase'] == cls) & (df['Banco'] != 'Banco Nacional de Bolivia S.A.')]['Radio'].iloc[0]

            store_data[str(2*i + 2)] = p
            store_data[str(2*i + 3)] = r
        else:

            p = df[df['Clase'] == cls]['Peso'].iloc[0]
            r = df[df['Clase'] == cls]['Radio'].iloc[0]
            store_data[str(2*i + 2)] = p
            store_data[str(2*i + 3)] = r

    p = df[df['Clase'].isin(other_classes)]['Peso'].iloc[0]
    r = df[df['Clase'].isin(other_classes)]['Radio'].iloc[0]
    store_data[str(2*len(classes) + 2)] = p
    store_data[str(2*len(classes) + 3)] = r
    
    return store_data



##########################################################################################################################################################
#Inicio Callback que almacena el df, crea los dropdowns y los botones
##########################################################################################################################################################
def load_data_and_dropdowns(contents, filename):
    # colores para los puntos
    colors = [
        '#26B460', #Agencias BNB
        '#66FF66', #Agencias Otro
        '#68478D', #Atm BNB
        '#ED5151', # atm otro
        '#F959A1', #centro comercial
        '#FC921F', #centro medico
        '#A7C636', #hotel
        '#FFDE3E', #mercado
        '#149ECE', #restaurante
        '#B7814A', #Supermercado
        '#406FC4'  #Universidad
        ]

    # No realiza todos los objetos mantienen sus estados
    if contents is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # comprueba si el csv es válido
    df = parse_contents(contents, filename)


    if isinstance(df, pd.DataFrame):
        # Generar la columna de colores según la categoría
        categories = np.sort(df['value_c'].unique())
        color_mapping = {category: colors[i % len(colors)] for i, category in enumerate(categories)}
        df['Color'] = df['value_c'].map(color_mapping)
        
        #retorna el estilo con que se debe ver el boton kde
        kde_style = {
            'display': 'block',
            'padding-left': '145px'
        }

        #retorna el estilo del contenedor de sliders
        slider_container_style ={
                'flex-direction': 'column',
                'display': 'block',
                'padding-bottom': 5, 
                'flex': 1,
                'overflow': 'auto', 
        }

        #hace visible el boton tile layer
        tile_style = {
            'display':'block'
        }

        #hace visible el contenerdor del mapa y le da estilo
        map_container_style = {
        'display': 'block',
        'height': '100%',
        'width': '100%',
        }

        #hace invisible el contenedor del upload
        upload_container_style = {'display': 'none'}

        #hace visible el boton tile layer
        layer_container_style = {
            'display':'block'
        }

        dp_style={
            'flex': 1, #ocupa un sexto de la pantalla horizontalmente
            'display': 'block'
        }

        return df.to_dict(),kde_style, slider_container_style, tile_style, map_container_style, upload_container_style, layer_container_style,dp_style
    else:
        raise dash.exceptions.PreventUpdate
##########################################################################################################################################################
#Fin Callback que almacena el df
##########################################################################################################################################################

mapbox_style_dict = {
    'Dark':'dark',
    'Light':'streets',
    'Topo':'stamen-terrain',
    'Sate':'satellite-streets',
    'Open':'open-street-map',
}

##########################################################################################################################################################
#Inicio Callback que crea el mapa
##########################################################################################################################################################
def generate_map(df_dict, kde_dict, tile_style, layer_value):

    # Si no se creo el df la funcion se sale directamente
    if df_dict is None:
        return dash.no_update

    #comprueba que el disparador fue el poligono kde retorna True
    ctx = dash.callback_context
    triggered_by_kde_output = ctx.triggered and ctx.triggered[0]['prop_id'] == 'kde-output.data'

    
    filtered_df = pd.DataFrame(df_dict)

    # esta es un verificacion de refuerzo para ver si el csv tien columnas latitud y longitud si no tiene sale del callback
    if 'Latitud' not in filtered_df.columns or 'Longitud' not in filtered_df.columns:
        raise dash.exceptions.PreventUpdate
    
    # Crea el objeto figura
    fig = go.Figure()


    # Añade un trazo invisible al mapa.
    fig.add_trace(
        go.Scattermapbox(
        lat=[-17.389717505931653],  # Estas coordenadas pueden ser cualquier punto dentro del rango visible del mapa.
        lon=[-66.17030830313263],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=0,  # El tamaño 0 hace el marcador invisible.
        ),
        hoverinfo='none'  # Esto evita que aparezca un tooltip cuando el usuario pasa el cursor sobre el marcador.
    )
    )


    if layer_value:         # Si hay alguna capa seleccionada

    #Si el disparo de dio por el poligono KDE entonces carga el json
        if (triggered_by_kde_output or kde_dict is not None) and 'contornos' in layer_value:

            kde_geojson = json.loads(kde_dict)
            gdf = gpd.GeoDataFrame.from_features(kde_geojson['features'])

            choropleth_layer = go.Choroplethmapbox(
                #pasa los valores a la variables geojson
                geojson=kde_geojson,
                locations=gdf.index.astype(str), #enumera todos los poligonos y is indices los vuelve texto
                z=gdf['Nivel'], # Usar la columna '0' como valores de color 
                colorscale='Turbo',
                hoverinfo='all', # Muestra toda la información en el hover
                hovertemplate='Nivel: %{z}<extra></extra>', # Personaliza el hover para mostrar solo la información que deseas
                #marker_opacity=0.2,
                showscale=False,# oculta la barra fea
                #marker_line_width=10
                marker=go.choroplethmapbox.Marker(
                    opacity=0.2,
                    line_width=2,  # Ajustar este valor para cambiar el grosor de las líneas de contorno
                    line_color='rgba(0,0,0,0.9)'  # Ajustar este valor para cambiar el color de las líneas de contorno
                ),
                name='Contornos',
            )
            fig.add_trace(choropleth_layer)
            #print(gdf)
            #print('='*20)

        if 'puntos' in layer_value:
            #le agrego el trace de los puntos
            fig.add_trace(
                go.Scattermapbox(
                    lat=filtered_df['Latitud'],
                    lon=filtered_df['Longitud'],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=12,  # Asegúrate de que este tamaño sea más grande que el de los puntos principales
                        color='black',  # Este será el color del "borde"
                    ),
                    hoverinfo='none'
                )
            )
            fig.add_trace(
                go.Scattermapbox(
                    lat= filtered_df['Latitud'],
                    lon= filtered_df['Longitud'],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=9,
                        color= filtered_df['Color'],
                    ),
                    text= filtered_df[['Clase']].values,
                    name='Puntos',
                )
            )


    #Este es el estilo principal del mapa debe mantenerse fijo en zoom y centro
    fig.update_layout(
        autosize=True,
        hovermode='closest',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        mapbox=dict(
            accesstoken=token,
            bearing=0,
            center=dict(
                lat=-17.389717505931653,
                lon=-66.17030830313263
            ),
            pitch=0,
            zoom=11,
            style=mapbox_style_dict[tile_style],  
            uirevision='constant'  # Mantener el estado del zoom/paneo entre actualizaciones
        ),
    )
    #print('Latitud:',filtered_df.Latitud.mean(),end='      ')
    #print('Longitud:',filtered_df.Longitud.mean())
    

    return fig
##########################################################################################################################################################
#Fin Callback que crea el mapa
##########################################################################################################################################################


##########################################################################################################################################################
#Inicio Callback para modificar el dataframe
##########################################################################################################################################################
def filter_df(dropdown_value_1, dropdown_value_2, dropdown_value_3, dropdown_value_4, dropdown_value_5, dropdown_value_6, switch_bnb, df_dict):
    
    # Si no se creo el df la funcion se sale directamente
    if df_dict is None:
        return dash.no_update,dash.no_update

    #convierte la entrada df_dict en un df
    df = pd.DataFrame(df_dict)

    # esta es un verificacion de refuerzo para ver si el csv tien columnas latitud y longitud si no tiene sale del callback
    if 'Latitud' not in df.columns or 'Longitud' not in df.columns:
        raise dash.exceptions.PreventUpdate


    #filtra los tipos de puntos
    if dropdown_value_1 is None or len(dropdown_value_1) == 0:
        df_t = df
    else:
        df_t = df[df['value_c'].isin(dropdown_value_1)]

    #filtra los Bancos
    if dropdown_value_2 is None or len(dropdown_value_2) == 0:
        df_banco = df_t
    else:
        df_banco = df_t[df_t['IDBN'].isin(dropdown_value_2)]

    #Separa solo Tipo agencias
    _df_agn = df_banco[df_banco['Clase'] == 'Agencia']
    
    _df_atm = df_banco[df_banco['Clase']== 'ATM']

    df_poi = df_t[df_t['Clase'].isin(['Centro Comercial','Mercado','Supermercado','Restaurante','Universidad'])]

    _df_hot = df_t[df_t['Clase']== 'Hotel']

    _df_cem = df_t[df_t['Clase']== 'Centro Médico']


    #filtra los BNB
    if switch_bnb is None or len(switch_bnb) == 0:
        df_bnb = pd.DataFrame()
    else:
        df_bnb = df[df['value_c'].isin(switch_bnb)]


    #filtra los tipo de agencias
    if dropdown_value_3 is None or len(dropdown_value_3) == 0:
        df_agn =_df_agn
    else:
        df_agn = _df_agn[_df_agn['TipoAgencia'].isin(dropdown_value_3)]

    #filtra los tipo de ATM
    if dropdown_value_4 is None or len(dropdown_value_4) == 0:
        df_atm = _df_atm
    else:
        df_atm = _df_atm[_df_atm['DepositoATM'].isin(dropdown_value_4)]

    #filtra los tipo de centros medicos
    if dropdown_value_5 is None or len(dropdown_value_5) == 0:
        df_cem = _df_cem
    else:
        df_cem = _df_cem[_df_cem['TipoCentroMedico'].isin(dropdown_value_5)]

    #filtra los tipo de hotel
    if dropdown_value_6 is None or len(dropdown_value_6) == 0:
        df_hot = _df_hot
    else:
        df_hot = _df_hot[_df_hot['TipoHotel'].isin(dropdown_value_6)]


    filtered_df = pd.concat([df_agn,df_atm,df_poi,df_hot,df_cem,df_bnb])
    #print(filtered_df.Peso.unique())

    #print('El numero de datos es:', len(filtered_df))

    if isinstance(filtered_df, pd.DataFrame):
        return filtered_df.to_dict('records'),len(filtered_df)
    else:
        raise dash.exceptions.PreventUpdate
##########################################################################################################################################################
#Fin Callback para modificar el dataframe
##########################################################################################################################################################


##########################################################################################################################################################
#Inicio Callback para actualizar las opciones de los dropdowns
##########################################################################################################################################################
def update_options_dp(df_dict, dropdown_value_2):
    
    opt = ['Banco Bisa S.A.', 'Banco de Crédito de Bolivia S.A.',
       'Banco Económico Bolivia', 'Banco Fie S.A.', 'Banco Ganadero S.A.',
       'Banco Mercantil Santa Cruz S.A.', 'Banco Unión S.A.']
    
    if df_dict is None:
        return dash.no_update
    
    df = pd.DataFrame(df_dict)

    if len(dropdown_value_2) == 0:
        dropdown_value_2 = opt
  

    data = df[df['Banco'].isin(dropdown_value_2)]['TipoAgencia'].dropna().unique()
    data = sorted(data, key=str) 
    options =[{'label': str(i), 'value': str(i)} for i in data]

    return options
##########################################################################################################################################################
#Fin Callback para actualizar las opciones de los dropdowns
##########################################################################################################################################################


##########################################################################################################################################################
#Inicio Callback que despliega el off-canvas
##########################################################################################################################################################
def toggle_offcanvas(n1,n2,df_dict, is_open, input_values, store_data):

    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, input_values, store_data
    else:
        prop_id = ctx.triggered[0]['prop_id']

        if 'open-offcanvas' in prop_id:
            # Si 'store_data' está vacío, entonces inicializa con 'intermediate-value', 'data'
            if not store_data:
                store_data = transform_df(df_dict) # carga los valores a los inputs pero no abre la ventana
            return not is_open, [store_data.get(str(i), '') for i in range(14)], store_data
        
        elif 'input' in prop_id:
            index = json.loads(prop_id.split('.')[0])['index']
            if input_values[index] is None:
                input_values[index] = store_data.get(str(index), '')
                return is_open, input_values, store_data
            else:
                store_data[str(index)] = input_values[index]
                return is_open, input_values, store_data
    return is_open, input_values, store_data
##########################################################################################################################################################
#Fin Callback que despliega el off-canvas
##########################################################################################################################################################


##########################################################################################################################################################
#Inicio Callback que muestra los valores inicales de pesos y radios
##########################################################################################################################################################
def update_slider(df_dict):

    if df_dict is None:
        raise dash.exceptions.PreventUpdate
    df = pd.DataFrame(df_dict)
    valores = df.groupby(by='value_c')[['Peso','Radio']].max().to_dict()
    
    peso = [
        valores['Peso']['AGNB'],
        valores['Peso']['AGNO'],
        valores['Peso']['ATMO'],
        valores['Peso']['SUPE'],
        valores['Peso']['CMED'],
        valores['Peso']['HOTE'],
        valores['Peso']['CCOM']
    ]
    radio = [
        valores['Radio']['AGNB'],
        valores['Radio']['AGNO'],
        valores['Radio']['ATMO'],
        valores['Radio']['SUPE'],
        valores['Radio']['CMED'],
        valores['Radio']['HOTE'],
        valores['Radio']['CCOM']
    ]

    return peso + radio
##########################################################################################################################################################
#Fin Callback que muestra los valores inicales de pesos y radios
##########################################################################################################################################################


##########################################################################################################################################################
#Inicio Callback que actualiza el datraframe
##########################################################################################################################################################
def update_dataframe(*args):

    n_clicks = args[-2]
    data = args[-1]
    if data is None:
        raise dash.exceptions.PreventUpdate
    print('Se generó un cambio')
    #print('valor del in: ', args[-2])
    data = args[-1]
    pesos = args[:7]
    radios = args[7:14]

    valores = sorted(set(data['value_c'].values()))

    df = pd.DataFrame(data)
    df.loc[df.value_c == 'AGNB',['Peso', 'Radio'] ]=pesos[0],radios[0]
    df.loc[df.value_c == 'AGNO',['Peso', 'Radio'] ]=pesos[1],radios[1]
    df.loc[df.value_c == 'ATMO',['Peso', 'Radio'] ]=pesos[2],radios[2]
    df.loc[df.value_c == 'SUPE',['Peso', 'Radio'] ]=pesos[3],radios[3]
    df.loc[df.value_c == 'CMED',['Peso', 'Radio'] ]=pesos[4],radios[4]
    df.loc[df.value_c == 'HOTE',['Peso', 'Radio'] ]=pesos[5],radios[5]
    df.loc[df.value_c.isin(['CCOM', 'MERC', 'REST', 'UNIV']),['Peso', 'Radio'] ]=pesos[6],radios[6]

    
    return df.to_dict()
##########################################################################################################################################################
#Inicio Callback que transforma los datos
##########################################################################################################################################################


##########################################################################################################################################################
#Inicio Callback que transforma los datos
##########################################################################################################################################################
def export_dataframe(n_clicks, store_data, intermediate_data):
    if n_clicks is None:  # el botón no ha sido presionado
        return intermediate_data
    else:
        df = pd.DataFrame(intermediate_data)
        # debes reordenar los valores en el store_data para que coincidan con las columnas correspondientes en tu dataframe
        # por ejemplo:
        new_weights = [store_data[str(i)] for i in range(0, 14, 2)]
        new_radii = [store_data[str(i)] for i in range(1, 14, 2)]
        df.loc[(df['Clase'] == 'Agencia') & (df['Banco'] == 'Banco Nacional de Bolivia S.A.'), 'Peso']= new_weights[0]
        df.loc[(df['Clase'] == 'Agencia') & (df['Banco'] == 'Banco Nacional de Bolivia S.A.'), 'Radio']= new_radii[0]
        df.loc[(df['Clase'] == 'Agencia') & (df['Banco'] != 'Banco Nacional de Bolivia S.A.'), 'Peso']= new_weights[1]
        df.loc[(df['Clase'] == 'Agencia') & (df['Banco'] != 'Banco Nacional de Bolivia S.A.'), 'Radio']= new_radii[1]
        df.loc[df['Clase'] == 'ATM', 'Peso'] = new_weights[2]
        df.loc[df['Clase'] == 'ATM', 'Radio'] = new_radii[2]
        df.loc[df['Clase'] == 'Supermercado', 'Peso'] = new_weights[3]
        df.loc[df['Clase'] == 'Supermercado', 'Radio'] = new_radii[3]
        df.loc[df['Clase'] == 'Centro Médico', 'Peso'] = new_weights[4]
        df.loc[df['Clase'] == 'Centro Médico', 'Radio'] = new_radii[4]
        df.loc[df['Clase'] == 'Hotel', 'Peso'] = new_weights[5]
        df.loc[df['Clase'] == 'Hotel', 'Radio'] = new_radii[5]
        df.loc[df['Clase'].isin(['Centro Comercial', 'Mercado', 'Restaurante', 'Universidad']), 'Peso'] = new_weights[6]
        df.loc[df['Clase'].isin(['Centro Comercial', 'Mercado', 'Restaurante', 'Universidad']), 'Radio'] = new_radii[6]

        return df.to_dict(orient='records')
##########################################################################################################################################################
#Fin Callback que transforma los datos
##########################################################################################################################################################



##########################################################################################################################################################
#Inicio Callback desarrolla el KDE
##########################################################################################################################################################
def generate_gson(n_clicks, df_dict):

    if n_clicks is None or df_dict is None:
        raise dash.exceptions.PreventUpdate
    
    #genero el df
    df = pd.DataFrame(df_dict)
    
    if len(df)<2:
        raise dash.exceptions.PreventUpdate
    
    levels = 12  # Número de niveles de contorno
    kde_gdf = perform_kde(df,levels)

    #convierte el geodataframe en json
    kde_geojson = kde_gdf.to_json()
    print('Se genero el KDE')
    return kde_geojson
##########################################################################################################################################################
#Fin Callback desarrolla el KDE
##########################################################################################################################################################

