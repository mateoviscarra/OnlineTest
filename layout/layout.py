from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_daq as daq


# logo Altitude en el Nav bar como barra de título
PLOTLY_LOGO = "https://raw.githubusercontent.com/joelsilva11/GIS/main/logo-blanco.png"

################################################ Opciones del boton tile layers
mapbox_style_dict = {
    'Dark':'dark',
    'Light':'streets',
    'Topo':'stamen-terrain',
    'Sate':'satellite-streets',
    'Open':'open-street-map',
}

################################################ Opciones del boton layers
options_layers_dict=[
            {'label': 'Puntos', 'value': 'puntos'},
            {'label': 'Contornos', 'value': 'contornos'}
        ]

################################################################ Creamos las opciones de los filtros para no hacerlos muy complicado
################################################Opciones clase
opciones_clases = [
    {'label': 'Agencia', 'value': 'AGNO'},
    #{'label': 'Agencia BNB', 'value': 'AGNB'},
    {'label': 'ATM', 'value': 'ATMO'},
    #{'label': 'ATM BNB', 'value': 'ATMB'},
    {'label': 'Centro Comercial', 'value': 'CCOM'},
    {'label': 'Mercado', 'value': 'MERC'},
    {'label': 'Supermercado', 'value': 'SUPE'},
    {'label': 'Restaurante', 'value': 'REST'},
    {'label': 'Hotel', 'value': 'HOTE'},
    {'label': 'Centro Médico', 'value': 'CMED'},
    {'label': 'Universidad', 'value': 'UNIV'}
    ]

################################################Opciones bancos
opciones_bancos = [
    {'label': 'Banco Bisa', 'value': 'BSA'},
    {'label': 'Banco de Crédito de Bolivia', 'value': 'BCP'},
    {'label': 'Banco Económico Bolivia', 'value': 'BEC'},
    {'label': 'Banco Fie', 'value': 'FIE'},
    {'label': 'Banco Ganadero', 'value': 'BGA'},
    {'label': 'Banco Mercantil Santa Cruz', 'value': 'MSC'},
    #{'label': 'Banco Nacional de Bolivia', 'value': 'BNB'},
    {'label': 'Banco Unión', 'value': 'BUN'}
    ]

################################################Opciones agencias
opciones_ag = [
    "Agencia",
    "Otro"
]
opciones_agencias = [{'label': opcion, 'value': opcion} for opcion in opciones_ag]

################################################Opciones atm
opciones_atm = [
    {'label': 'Permite depósitos', 'value': 'Si'},
    {'label': 'No Permite depósitos', 'value': 'No'}, 
    ]

################################################Opciones centros médicos
opciones_cm = [
    "Centro de salud",
    "Clínica",
    "Hospital"
]
opciones_ceme = [{'label': opcion, 'value': opcion} for opcion in opciones_cm]

################################################Opciones hoteles
opciones_ht = [
    "ApartHotel",
    "Apartment",
    "Bed and breakfast",
    "Guest house",
    "Holiday home",
    "Homestay",
    "Hostel",
    "Hotel",
    "Inn",
    "Resort"
]
opciones_hoteles = [{'label': opcion, 'value': opcion} for opcion in opciones_ht]
################################################################ fin de las opciones de los filtros para no hacerlos muy complicado

################################################Opciones BNB
options_bnb=[
            {"label": "Agencias", "value": 'AGNB'},
            {"label": "ATMs", "value": 'ATMB'}
        ]

###################################################################crea la barra de titulo
navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(html.Img(src=PLOTLY_LOGO, height="60px"),width=2,style={'padding-left': '75px'}),
                dbc.Col(dbc.NavbarBrand("VISUALIZACIÓN DE MAPAS DE CALOR CON CONTORNOS DE DENSIDAD",style={'font-size': '36px'}), width=7),
                ############################################### Inicio Div que contiene al Boton que ejecuta el KDE
                dbc.Col(
                    html.Div(
                        dbc.Button('Run KDE Analisys', id='kde-button', n_clicks=0, style={'width': '100%','height': '50px'}, color="success"),
                        id='kde-button_container', 
                        style={'display': 'none'},
                    )
                ),
                ############################################### Fin Div que contiene al Boton que ejecuta el KDE
            ],
            align="center",
            style={
                "margin": "0", 
                "width": "100%"
            },
            
        ),      
    ],
    color="#333",
    dark=True,
    style={'height': '8vh'}
)


###################################################################crea los slicers
def create_slider(Titulo,id_suffix):
    id_peso = f'sl-peso-{id_suffix}'
    id_radio = f'sl-radio-{id_suffix}'
    return html.Div([
                    html.Div([ #titulo
                        html.H6(Titulo,
                            style={
                                'padding-top':'7px',
                                'flex': '1',
                                'text-align': 'left'
                            }
                        ),
                        ], style={'display': 'flex'}
                    ),
                    
                    dbc.InputGroup( #boton y slider
                        [
                            dbc.Button( #boton
                                "P", 
                                color="primary",
                            style={
                                'flex': '0.04'
                                }
                            ),
                            html.Div([ # div que contiene al slider
                                html.Div(
                                    daq.Slider( #Slider
                                        id=id_peso,
                                        min=0,
                                        max=10,
                                        step=1,
                                        marks={i: str(i) for i in range(11)},
                                        value=0,
                                        color='#2A9FD6',
                                        className='my-slider' # parametro para personlizar la longitud maxima del slider con css
                                    ),
                                style={
                                    'margin-left': 25,
                                    'margin-right': 25,
                                    }
                                )
                                ],
                                style={
                                    'padding-top': '8px',
                                    'padding-bottom': '25px',
                                    "border": "1px solid rgba(42, 159, 214, 1)",
                                    #'borderColor': '#092533',
                                    'backgroundColor': 'rgba(42, 159, 214, 0.15)',
                                    'border-top-right-radius': '5px',
                                    'border-bottom-right-radius': '5px',
                                    #'borderRadius': '5px',
                                    'flex': '1',
                                },
                            ),
                        ],
                        style={
                            'display': 'flex',
                        }
                    ),
                    dbc.InputGroup( #boton y slider
                    [
                        dbc.Button( #boton
                            "R", 
                            #color="#6A72AC",
                        style={
                            'flex': '0.04',
                            'backgroundColor':"#2DB89E",
                            'borderColor':"#2DB89E"
                            }
                        ),
                        html.Div([ # Dvi que contien al slider
                            dcc.Slider( # Slider
                                id=id_radio,
                                min=0,
                                max=500,
                                step=50,
                                value=0, # Valor inicial del slider
                                marks=None,
                                #marks={i: str(i) for i in range(0, 501, 50)}, # Marca los puntos en el slider en incrementos de 50
                                tooltip={"placement": "bottom","always_visible": True},
                                className="dcc-slider-custom"
                            )
                        ],
                        style={
                            'padding-top': '8px',
                            #'backgroundColor': '#273B00',
                            'backgroundColor': 'rgba(45, 184, 158, 0.2)',
                            "border": "1px solid rgba(45, 184, 158, 1)",
                            'border-top-right-radius': '5px',
                            'border-bottom-right-radius': '5px',
                            'flex': '1',
                            #'borderRadius': '5px',
                        },
                        ),
                    ],
                    style={
                        'display': 'flex',    
                    }
                    )
                ],
            style={
                'margin-bottom': 7,
                'backgroundColor': '#333',
                'borderRadius': '5px',
                'padding-bottom': '10px',
                'padding-left': '10px',
                'padding-right': '10px',
            },
            )

###################################################################crea los dropdowns personalizados
def create_dropdown_p(id_suffix, dp_options,title_dp = 'Title'): 
    # Genera los IDs de los componentes con el sufijo proporcionado
    input_id = f'dp-input-{id_suffix}'
    button_id = f'dp-button-{id_suffix}'
    checklist_id = f'checklist-{id_suffix}'
    all_checklist_id = f'all-checklist-{id_suffix}'
    container_id = f'checklist_container-{id_suffix}'


    # Crea y devuelve el componente
    return html.Div(# Div que contiene todo el dropdrown con el espacio de 7px
    [
        html.Div([# Div que contiene todo el dropdrown
            html.Div(# Div que contine el título, casilla y boton 
            [
                html.H6(# Título
                    title_dp, 
                    style={
                        'margin-bottom': '5px'
                    }
                ),
                dbc.InputGroup( #Input y boton
                [
                    dbc.Input(id=input_id, value="", readonly=True,),
                    dbc.Button("▼", id=button_id, color="primary")
                ],
                ),
            ],
            style={
                'padding-left': '10px',
                'padding-right': '10px',
                'padding-top':'7px',
            },
            ),
        
            html.Div( # Div que contiene a los checklist y los centra
            [
                html.Div(# ventana que contiene a los divs con tamaño fijo y scroll
                    [   
                        dbc.Checklist(options=["All"], value=[], id=all_checklist_id, style={'padding-left': 8}),
                        dbc.Checklist(options=dp_options, value=[], id=checklist_id, style={'padding-left': 16}),
                    ],
                id=container_id,
                style={
                    'display':'none',
                    'backgroundColor': 'rgba(0, 0, 0, 0.92)', 
                    'borderRadius': '5px',
                    'overflow': 'auto',# hace que lo elementos no hagan crecen el Div y crea un scroll
                    'maxHeight': '180px', 
                    'position': 'absolute', 
                    'z-index': '9999',
                    'width': '100%',
                }
                ),
            ],
            style={
                'position': 'relative',
                'padding-left': '10px',
                'margin-right': '20px'
            }
            ),
        ],
        style={
            'backgroundColor': '#333',
            'borderRadius': '5px',
            'height': '100%',
        },
        ),
    ],
    style={
        'padding-bottom':7,
        'height': '10vh', # cada elemento ocupa el 10% de la pantalla asi si se expande tambien se expanden los drops
    },
    )

###################################################################funciones para crear los inputs
def generate_inputs (num_of_inputs):
    inputs = []
    texts = [
        'Banco BNB',
        'Otros Bancos',
        'ATMs',
        'SuperMercados',
        'Centros Médicos',
        'Hoteles',
        'Otros'
    ]
    for i in range(num_of_inputs):
        if i % 2 == 0:
            text_index = i // 2  # Índice para determinar el texto correspondiente
            input_item = dbc.Row(
                [
                    dbc.Col(html.H5(texts[text_index]), width=12),  # Texto en la parte superior
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Peso",style={'width': '60px'}),
                                dcc.Input(
                                    id={'type': 'input', 'index': i},
                                    type='number',
                                    min=0,
                                    max=10,
                                    placeholder=f'Enter something here...',
                                ),
                            ]
                        ), width=12
                    )
                ]
            )
        else:
            input_item = dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Radio",style={'width': '60px'}),
                                dcc.Input(
                                    id={'type': 'input', 'index': i},
                                    type='number',
                                    min=0,
                                    max=500,
                                    placeholder=f'Enter something here...',
                                ),
                            ]
                        ), width=12
                    )
                ]
            )
        inputs.append(input_item)
    return inputs

#funcion para crear el dropdown aun no existe solo hasta que el callback recibe el csv
def create_dropdown(df,selected_column,dropdown_id,titulo='Sin nombre'):
    unique_values = df[selected_column].dropna().unique()
    unique_values = sorted(unique_values, key=str)  # Ordenar los valores
    ############################################## Inicio del Div que contiene el Dropdown
    dropdown = html.Div(children=[
                    html.Label(titulo),
                    dcc.Dropdown(
                                id=dropdown_id,
                                options=[{'label': str(i), 'value': str(i)} for i in unique_values],
                                value=None,  # No se selecciona ninguna opción por defecto
                                multi=True,
                                style={
                                    'backgroundColor': '#333',
                                    'color': '#fff',
                                    'width': '100%'
                                }
                    ),
                ], 
                style={
                    'width': '100%',
                    #'padding': 5,
                    #'padding-top': 2,
                    'padding-right': 5,
                    'padding-bottom': 7,
                    'padding-left': 5,
                    'backgroundColor': '#333'
                }
                )
    ############################################## Fin del Div que contiene el Dropdown
    return dropdown

#funcion para crear los switches
def create_switch(id_suffix,Titulo,options_sw):
    input_id = f'switches-{id_suffix}'
    return html.Div( # retorna el div que contiene los switches 
    [
        html.H6(Titulo, style={'margin-bottom': 10}),
        dbc.Checklist(
            options = options_sw,
            value=[i['value'] for i in options_sw],# inicia los valores en ON
            id = input_id,
            switch=True,
        style={
            #'padding-left': '10px',
        },
        ), 
    ],
    style={
        'padding-top':'7px',
        'padding-left': '10px',
        'padding-bottom': 15,
    },
    )

#funcion para crear el dropdwon de tiles
def create_droptiles(id_tile, opt_tiles):
    return html.Div(
    [
        dcc.Dropdown(
            id=id_tile,
            options=[{'label': i, 'value': i} for i in opt_tiles.keys()],
            value='Dark',
            searchable=False,
            clearable=False,
        style={
        'backgroundColor': '#222',
        'width': '100%'
        },
        ),
    ],
    style={
        'position': 'absolute', 
        'top': '10px', 
        'left': '10px', 
        'z-index': '100',
        'width':'70px'
    },
    )

#funcion para crear el dropdwon de layers
def create_droplayers(id_tile, opt_tiles):
    return html.Div(
    [
        dcc.Dropdown(
            id=id_tile,
            options=opt_tiles,
            value=['puntos'],
            searchable=False,
            multi=True,
            clearable=False,
            placeholder="",
        style={
        'backgroundColor': '#222',
        'width': '100%'
        },
        ),
    ],
    style={
        'position': 'absolute', 
        'top': '10px', 
        'left': '80px', 
        'z-index': '12',
        'width':'140px',
        
    },
    )




#############################################################################################################################################
#Estructura principal de la pagina
#############################################################################################################################################

layout = html.Div([
    ################################################### Inicio Barra de título
    navbar,
    ################################################### Fin Barra de título

    #Main screen
    ################################################################################ Inicio Div pantalla principal
    html.Div([
        #Dropdowns
        ############################################### Inicio Div que contiene los dropdowns personalizados
        html.Div([
            ################################################### Dropdown1
            create_dropdown_p('1',opciones_clases,'Tipos de Puntos'),

            ################################################### Dropdown2
            create_dropdown_p('2',opciones_bancos,'Bancos'),

            ################################################### Dropdown3
            create_dropdown_p('3',opciones_agencias,'Tipos de Agencias'),

            ################################################### Dropdown4
            create_dropdown_p('4',opciones_atm,'ATM con depósito'),

            ################################################### Dropdown5
            create_dropdown_p('5',opciones_ceme,'Tipos de Centros Médicos'),

            ################################################### Dropdown6
            create_dropdown_p('6',opciones_hoteles,'Tipos de Hospedaje'),

            ################################################### Selector Agencias y ATMs BNB
            html.Div(create_switch('bnb','Puntos BNB',options_bnb),
            style={
                'margin-bottom': '7px',
                'backgroundColor': '#333',
                'borderRadius': '5px',
                'height': '11%'
            }
            ),

            ################################################### Indicador de numero de puntos
            html.Div([# Div Card
                html.Div([
                    html.H6("Número de puntos")
                ],
                style={'padding-left':7,
                       'padding-top':7,
                       'border-bottom': '1px solid #222'
                },
                ),
                html.Div([
                    html.H1("9999",id="num_puntos_id", style={'font-size': '110px'})
                ],
                style={
                    'display': 'flex',
                    'justify-content': 'center',
                    'align-items': 'center',
                },
                ),
            ],
            style={
                'backgroundColor': '#333',
                'borderRadius': '5px',
                'height': '22%',
            },
            
            ),
        ],
        id='dp_container',
        style={
            'flex': 1, #ocupa un sexto de la pantalla horizontalmente
            'display': 'none'
        },
        ),
        ############################################### Fin Div que contiene los dropdowns personalizados

        #map and upload
        ############################################### Inicio Div que contiene el upload y el mapa a la vez
        html.Div([
            ############################################### Inicio Div que contiene upload
            html.Div([
                ############################################### Inicio objeto Upload
                dcc.Upload(
                    id='upload-csv', #Id Upload
                    children=html.Div(['Arrastre y suelte o ',html.A('Seleccione Archivos')]),
                    style={
                        'width': '100%',
                        'height': '90.7vh',
                        'display': 'flex',  # Esto permite utilizar las propiedades flexbox para centrar el contenido
                        'justify-content': 'center',  # Centra el contenido horizontalmente
                        'align-items': 'center',  # Centra el contenido verticalmente
                        'borderWidth': '3px',
                        'borderStyle': 'dashed',
                        'borderRadius': '20px',
                        'textAlign': 'center',
                        'backgroundColor':'#333',
                    }
                ),
                ############################################### Fin objeto Upload
            ], 
            id='upload-container', #Id contenedor del Upload
            style={
                'display':'block'
            }
            ),
            ############################################### Fin Div que contiene upload

            ############################################### Inicio Div que contiene Grafico mapa
            html.Div([
                dcc.Graph(
                    id='map-scatter',
                    style={'height': '100%'},
                    config = {
                        'scrollZoom': True,
                        'displayModeBar': True,
                        'editable': True,
                        'displaylogo': False,
                        'autosizable': True,
                    }
                ),
            ],
            id='map-container',
            style={
                'display': 'none',
                'height': '100%',
                'width': '100%',
            }
            ),
            ############################################### Fin Div que contiene Grafico mapa

            ############################################### Inicio dropdown tile layers
            html.Div([
            create_droptiles('id_tile', mapbox_style_dict)
            ],
            id='tile_container',
            style={
                'display':'none'
            },
            ),
            ############################################### Fin dropdown tile layers

            ############################################### Inicio dropdown layers
            html.Div([
            create_droplayers('id_layer', options_layers_dict)
            ],
            id='layer_container',
            style={
                'display':'none'
            }
            )
            ############################################### Fin dropdown layers
        ],
        style={
            'flex': 4,
            'width': '100%',
            'margin-left': 7,
            'margin-right': 7,
            'borderRadius': '5px',
            'height': '100%',
            'position': 'relative',   
        }
        ),
        ############################################### Fin Div que contiene upload y mapa a la vez

        #slider
        ############################################### Inicio Div que contiene los sliders
        html.Div([
            ############################################### Slider 1
            create_slider('Banco BNB','1'),
            ############################################### Slider 2
            create_slider('Otros Bancos','2'),
            ############################################### Slider 3
            create_slider('ATMs','3'),
            ############################################### Slider 4
            create_slider('Supermercados','4'),
            ############################################### Slider 5
            create_slider('Centros Médicos','5'),
            ############################################### Slider 6
            create_slider('Hotels','6'),
            ############################################### Slider 7
            create_slider('Otros','7'),

            ############################################### Inicio Div que contiene al Boton que oculta el canvas
            html.Div([
                dbc.Button(
                    'Editar parámetros', 
                    id='open-offcanvas', 
                    n_clicks=0, 
                    style={
                        'width': '100%',
                        #'height': '7vh',
                    }, 
                    color='primary'
                ),
            ],
            style={
                'margin-bottom': 7,
                'display': 'none',
            },
            ),
            ############################################### Fin Div que contiene al Boton que oculta el canvas
        ],
        id='sliders_contain',
        style={
                #'flex-direction': 'column',
                'flex': 1,
                'display': 'none',
                #'padding-top': 7,
                'padding-bottom': 5,
                'height': '100%',
                'overflow': 'auto', 
        }
        ),
        ############################################### Fin Div que contiene los sliders
    ], 
    style={
        'display': 'flex', #hace que la pantalla se pueda dividir en porcentajes
        'flex-direction': 'row', #hace que la direccion de division sea horizontal
        'height': '92vh',# ocupa el 92% de la pantalla horizontalmente
        'padding-top':7,
        'padding-bottom':7,
    }
    ),
    ################################################################################ Inicio Div pantalla principal

    #Slice screen
    ################################################################################ Inicio de la ventana desplegable
    dbc.Offcanvas(
        dbc.Container([
            dbc.Row(
                dbc.Col(
                    generate_inputs(14),
                    width=12
                ),
                justify="center"
            ),
            dbc.Row(  # Agregamos una nueva fila para el botón
                dbc.Col(
                    dbc.Button("Cargar Datos", id="export-button", color="success",
                               style={"marginTop": "50px", "width": "100%"}
                               ),
                    width=12,
                ),
                justify="center",
            )
        ]),
        id="offcanvas",
        title="Editar Peso y Radios",
        is_open=False,
        scrollable=True,
    ),
    ################################################################################ Fin de la ventana desplegable


    ################################################### Inicio Stores inputs
    dcc.Store(id='store-inputs'),
    ################################################### Fin Stores inputs

    
    ################################################### Inicio para almacenar el df para que pueda ser usado en otros callbacks
    dcc.Store(id='intermediate-value'),
    ################################################### Fin para almacenar el df para que pueda ser usado en otros callbacks

    
    ################################################### Inicio para almacenar el KDE en un geojson
    dcc.Store(id='kde-output'),
    ################################################### Fin para almacenar el KDE en un geojson
    
    
    ################################################### Inicio para almacenar el df que sera filtado por los dropdowns
    dcc.Store(id='filter-value'),
    ################################################### Fin para almacenar el df que sera filtado por los dropdowns
    
    
    ################################################### Inicio para almacenar el df tranformado por los inputs
    dcc.Store(id='store-transformed')
    ################################################### Fin para almacenar el df tranformado por los inputs
])

#############################################################################################################################################
#Estructura principal de la pagina
#############################################################################################################################################
