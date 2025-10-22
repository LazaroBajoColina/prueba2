import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import datetime

# --- Inicializar la App Dash ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN], suppress_callback_exceptions=True)
server = app.server # Para despliegue

# --- Funciones de Ayuda ---
def create_geoid_sphere_figure():
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x_s = 10 * np.outer(np.cos(u), np.sin(v))
    y_s = 10 * np.outer(np.sin(u), np.sin(v))
    z_s = 10 * np.outer(np.ones(np.size(u)), np.cos(v))
    x_g = 10.2 * np.outer(np.cos(u), np.sin(v))
    y_g = 10.2 * np.outer(np.sin(u), np.sin(v))
    z_g = 9.8 * np.outer(np.ones(np.size(u)), np.cos(v))
    fig = go.Figure()
    fig.add_trace(go.Surface(x=x_s, y=y_s, z=z_s, colorscale='Blues', showscale=False, opacity=0.7, name='Esfera Perfecta'))
    fig.add_trace(go.Surface(x=x_g, y=y_g, z=z_g, colorscale='Greys', showscale=False, opacity=0.6, name='Geoide (Exagerado)'))
    fig.update_layout(title='La Tierra: Geoide vs. Esfera Perfecta', scene=dict(xaxis_title='Eje X', yaxis_title='Eje Y', zaxis_title='Eje Z (Rotación)'), margin=dict(l=0, r=0, b=0, t=40))
    return fig

def create_lat_lon_sphere():
    """Crea una esfera 3D para ilustrar Latitud y Longitud."""
    fig = go.Figure()
    u, v = np.linspace(0, 2 * np.pi, 50), np.linspace(0, np.pi, 50)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    fig.add_trace(go.Surface(x=x, y=y, z=z, colorscale=[[0, 'lightblue'], [1, 'lightblue']], showscale=False, opacity=0.3))
    t = np.linspace(0, 2 * np.pi, 100)
    fig.add_trace(go.Scatter3d(x=np.cos(t), y=np.sin(t), z=np.zeros_like(t), mode='lines', line=dict(color='red', width=5), name='Ecuador (Latitud 0°)'))
    v_meridian = np.linspace(0, np.pi, 100)
    fig.add_trace(go.Scatter3d(x=np.cos(v_meridian), y=np.zeros_like(v_meridian), z=np.sin(v_meridian - np.pi/2), mode='lines', line=dict(color='green', width=5), name='Meridiano de Greenwich (Longitud 0°)'))
    
    # --- CORRECCIÓN APLICADA AQUÍ ---
    for lat in [-60, -30, 30, 60]:
        rad = np.deg2rad(lat)
        r = np.cos(rad)
        z_val = np.sin(rad)
        fig.add_trace(go.Scatter3d(x=r*np.cos(t), y=r*np.sin(t), z=np.full_like(t, z_val), mode='lines', line=dict(color='red', width=2, dash='dot'), showlegend=False))
    
    for lon in [-120, -60, 60, 120]:
        rad = np.deg2rad(lon)
        fig.add_trace(go.Scatter3d(x=np.cos(rad)*np.cos(v_meridian), y=np.sin(rad)*np.cos(v_meridian), z=np.sin(v_meridian - np.pi/2), mode='lines', line=dict(color='green', width=2, dash='dot'), showlegend=False))
    
    fig.update_layout(title="Sistema de Coordenadas Geográficas", margin=dict(l=0, r=0, b=0, t=40), scene=dict(aspectmode='data'), legend=dict(x=0, y=1))
    return fig

# --- Layout de la App ---
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Dashboard de Conceptos de Geografía (U.1)", className="text-center my-4"))),
    dcc.Store(id='map-center-store', storage_type='session'),
    dbc.Tabs([
        dbc.Tab(label="La Tierra y Proyecciones", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Forma de la Tierra y Proyecciones Cartográficas", className="card-title"),
                dbc.Row([
                    dbc.Col([
                        html.H5("La Forma de la Tierra"),
                        html.P("La Tierra es un geoide. El gráfico compara una esfera (azul) con un geoide exagerado (gris) para resaltar el achatamiento polar."),
                        dcc.Graph(figure=create_geoid_sphere_figure())
                    ], md=6),
                    dbc.Col([
                        html.H5("Proyecciones Cartográficas"),
                        html.P("Método para representar la superficie curva de la Tierra en un plano."),
                        dbc.RadioItems(id='projection-selector', options=[{'label': 'Cilíndrica', 'value': 'cylindrical stereographic'}, {'label': 'Cónica', 'value': 'conic conformal'}, {'label': 'Azimutal / Polar', 'value': 'azimuthal equidistant'}], value='cylindrical stereographic', inline=True),
                        dcc.Graph(id='projection-map-graph'),
                        html.Div(id='projection-description', className="mt-2 text-muted")
                    ], md=6)
                ])
            ]), className="my-3")
        ]),
        dbc.Tab(label="Escalas Cartográficas", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Escalas de Mapas", className="card-title"),
                html.P("La escala indica la relación entre la distancia en el mapa y la realidad. Haz clic en el mapa para elegir un punto y luego usa el deslizador para hacer zoom."),
                dbc.Row([
                    dbc.Col([
                        html.Label("Nivel de Zoom (Simula la Escala):"),
                        dcc.Slider(id='map-scale-slider', min=0, max=15, step=1, value=4, marks={0: 'Global', 5: 'Continental', 10: 'Nacional', 15: 'Local'}),
                        html.Div(id='scale-info-text', className="lead mt-3")
                    ], md=4),
                    dbc.Col(dcc.Graph(id='scale-map-graph', style={'height': '60vh'}), md=8)
                ])
            ]), className="my-3")
        ]),
        dbc.Tab(label="Coordenadas Geográficas", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Latitud, Longitud, Paralelos y Meridianos", className="card-title"),
                dbc.Row([
                    dbc.Col([
                        html.P(html.B("Latitud:")), html.P("Distancia angular desde el Ecuador (0°). Las líneas horizontales se llaman Paralelos."),
                        html.P(html.B("Longitud:")), html.P("Distancia angular desde el Meridiano de Greenwich (0°). Las líneas verticales se llaman Meridianos."),
                        dcc.Graph(id='interactive-coord-map', style={'height': '40vh'}),
                        html.Div(id='coordinates-info-text', className="lead mt-3", children="Haz clic en el mapa 2D para ver las coordenadas.")
                    ], md=6),
                    dbc.Col(dcc.Graph(figure=create_lat_lon_sphere()), md=6)
                ])
            ]), className="my-3")
        ]),
        dbc.Tab(label="Husos Horarios", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Calculadora de Husos Horarios", className="card-title"),
                html.P("La Tierra se divide en 24 husos (15° c/u). El tiempo aumenta al Este (+) y disminuye al Oeste (-)."),
                dbc.Row([
                    dbc.Col([
                        html.Label("Hora de Referencia (24h):"),
                        dcc.Input(id='base-time-input', type='number', min=0, max=23, step=1, value=datetime.datetime.utcnow().hour, className="mb-2"),
                        html.Label("Huso Horario de Referencia (UTC):"),
                        dcc.Slider(id='base-timezone-slider', min=-12, max=14, step=1, value=0, marks={i: str(i) for i in range(-12, 15, 2)}),
                        html.Label("Huso Horario Objetivo (UTC):"),
                        dcc.Slider(id='target-timezone-slider', min=-12, max=14, step=1, value=-6, marks={i: str(i) for i in range(-12, 15, 2)}),
                        html.Div(id='timezone-result', className="lead fw-bold mt-4 p-3 bg-light rounded text-center")
                    ], md=5),
                    dbc.Col(dcc.Graph(id='timezone-map-graph'), md=7)
                ])
            ]), className="my-3")
        ]),
    ])
], fluid=True)

# --- Callbacks ---
@app.callback([Output('projection-map-graph', 'figure'), Output('projection-description', 'children')], Input('projection-selector', 'value'))
def update_map_projection(projection_type):
    fig = go.Figure(go.Scattergeo())
    fig.update_geos(projection_type=projection_type, showcoastlines=True, showland=True, landcolor="LightGreen", showocean=True, oceancolor="LightBlue")
    fig.update_layout(height=300, margin={"r":0,"t":20,"l":0,"b":0})
    descriptions = {'cylindrical stereographic': "Cilíndrica: Ideal para zonas ecuatoriales.", 'conic conformal': "Cónica: Adecuada para latitudes medias.", 'azimuthal equidistant': "Azimutal: Útil para regiones polares."}
    return fig, descriptions.get(projection_type, "")

@app.callback(Output('map-center-store', 'data'), Input('scale-map-graph', 'clickData'), prevent_initial_call=True)
def store_map_center(click_data):
    if click_data:
        point = click_data['points'][0]
        return {'lat': point['lat'], 'lon': point['lon']}
    return dash.no_update

@app.callback(Output('scale-map-graph', 'figure'), Output('scale-info-text', 'children'), Input('map-scale-slider', 'value'), Input('map-center-store', 'data'))
def update_scale_map(zoom_level, center_data):
    if center_data:
        lat, lon = center_data['lat'], center_data['lon']
    else:
        lat, lon = 19.4326, -99.1332
    fig = go.Figure(go.Scattermapbox(lat=[lat], lon=[lon], mode='markers', marker=go.scattermapbox.Marker(size=10, color='red')))
    fig.update_layout(mapbox_style="open-street-map", mapbox=dict(center=go.layout.mapbox.Center(lat=lat, lon=lon), zoom=zoom_level), margin={"r":0,"t":0,"l":0,"b":0})
    if zoom_level >= 10:
        scale_text = [html.B("Escala Grande:"), " Menor reducción (ej. 1:50,000). Muestra gran detalle de áreas pequeñas."]
    elif zoom_level >= 4:
        scale_text = [html.B("Escala Mediana:"), " Reducción intermedia. Muestra países o regiones."]
    else:
        scale_text = [html.B("Escala Pequeña:"), " Mayor reducción (ej. 1:250,000+). Muestra poco detalle de grandes áreas."]
    return fig, html.P(scale_text)

@app.callback([Output('interactive-coord-map', 'figure'), Output('coordinates-info-text', 'children')], Input('interactive-coord-map', 'clickData'))
def update_interactive_coord_map(click_data):
    lat, lon = 23.63, -102.55
    coord_text = "Haz clic en el mapa para obtener las coordenadas."
    if click_data:
        point = click_data['points'][0]
        lat, lon = point['lat'], point['lon']
        coord_text = f"Coordenadas: Latitud {lat:.4f}, Longitud {lon:.4f}"
    fig = go.Figure(go.Scattermapbox(lat=[lat], lon=[lon], mode='markers', marker=go.scattermapbox.Marker(size=14, color='red')))
    fig.update_layout(mapbox_style="open-street-map", mapbox=dict(center=go.layout.mapbox.Center(lat=lat, lon=lon), zoom=3), margin={"r":0,"t":0,"l":0,"b":0})
    return fig, html.P(coord_text)

@app.callback([Output('timezone-result', 'children'), Output('timezone-map-graph', 'figure')], [Input('base-time-input', 'value'), Input('base-timezone-slider', 'value'), Input('target-timezone-slider', 'value')])
def calculate_time_zone(base_time, base_tz, target_tz):
    if base_time is None: return "Introduce una hora.", go.Figure()
    time_difference = target_tz - base_tz
    target_time = (base_time + time_difference + 24) % 24
    base_tz_str = f"UTC{base_tz:+.0f}" if base_tz != 0 else "UTC"
    target_tz_str = f"UTC{target_tz:+.0f}" if target_tz != 0 else "UTC"
    result_text = f"Si son las {base_time:02d}:00 en {base_tz_str}, son las {target_time:02d}:00 en {target_tz_str}."
    fig = go.Figure(go.Scattergeo(lon=[-180, 180], lat=[0,0], mode='lines', line=dict(width=1, color='lightgrey')))
    for i in range(-180, 181, 15):
        fig.add_trace(go.Scattergeo(lon=[i, i], lat=[-90, 90], mode='lines', line=dict(width=0.5, color='gray', dash='dot'), showlegend=False))
    base_lon, target_lon = base_tz * 15, target_tz * 15
    fig.add_trace(go.Scattergeo(lon=[base_lon], lat=[30], mode='markers', marker=dict(color='blue', size=10, symbol='star'), name='Referencia'))
    fig.add_trace(go.Scattergeo(lon=[target_lon], lat=[30], mode='markers', marker=dict(color='red', size=10, symbol='star'), name='Objetivo'))
    fig.update_geos(projection_type="natural earth", showland=True, landcolor="lightgrey", showocean=True, oceancolor="lightblue")
    fig.update_layout(height=400, margin={"r":0,"t":20,"l":0,"b":0}, legend=dict(x=0.01, y=0.99))
    return result_text, fig

# --- Ejecutar la App ---
if __name__ == '__main__':

    app.run(debug=False)

