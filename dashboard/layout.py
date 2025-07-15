"""
Dashboard layout components for the Debug Assistant application.
"""

from dash import dcc, html, dash_table
from datetime import datetime, timedelta


def create_header():
    """Create the dashboard header."""
    return html.Div([
        html.H1("Debug Assistant", 
               style={'margin': '0', 'fontSize': '2.5em', 'fontWeight': 'bold'}),
        html.P("Advanced Timestamp Correlation & Full Message Analysis", 
               style={'margin': '5px 0', 'fontSize': '1.2em', 'opacity': '0.9'}),
        html.Div([
            html.Span("⏰ Timestamp Analysis", style={'background': 'rgba(255,255,255,0.2)', 'padding': '5px 10px', 'marginRight': '10px', 'borderRadius': '15px', 'fontSize': '0.9em'}),
            html.Span("🔗 Event Correlation", style={'background': 'rgba(255,255,255,0.2)', 'padding': '5px 10px', 'marginRight': '10px', 'borderRadius': '15px', 'fontSize': '0.9em'}),
            html.Span("📊 Full Log Messages", style={'background': 'rgba(255,255,255,0.2)', 'padding': '5px 10px', 'marginRight': '10px', 'borderRadius': '15px', 'fontSize': '0.9em'}),
            html.Span("🏗️ Architecture Visualization", style={'background': 'rgba(255,255,255,0.2)', 'padding': '5px 10px', 'marginRight': '10px', 'borderRadius': '15px', 'fontSize': '0.9em'}),
        ], style={'marginTop': '10px'})
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'color': 'white',
        'padding': '20px',
        'marginBottom': '20px',
        'borderRadius': '10px'
    })


def create_control_panel():
    """Create the control panel."""
    return html.Div([
        html.Div([
            html.H3("🎯 Service Selection"),
            dcc.Dropdown(
                id='service-dropdown',
                placeholder="Type or select ServiceId for analysis...",
                searchable=True,
                clearable=True,
                style={'marginBottom': '10px'}
            ),
            html.Div(id='service-status', style={'fontSize': '0.9em', 'color': '#666'})
        ], style={'flex': '2'}),
        
        html.Div([
            html.H3("📋 Data Sources"),
            dcc.Checklist(
                id='data-sources',
                options=[
                    {'label': '📄 Log Files', 'value': 'log'},
                    {'label': '🔍 DLT Messages', 'value': 'dlt'},
                    {'label': '🌐 PCAP/SOME-IP', 'value': 'pcap'},
                    {'label': '📋 Other Logs', 'value': 'other'}
                ],
                value=['log', 'dlt', 'pcap', 'other']
            )
        ], style={'flex': '1'}),
        
        html.Div([
            html.Button("🚀 Run Analysis", id="run-button", 
                       style={'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px', 'fontWeight': 'bold', 'cursor': 'pointer', 'background': '#28a745', 'color': 'white', 'marginBottom': '10px', 'width': '100%'}),
            html.Button("⏹️ Stop", id="stop-button", 
                       style={'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px', 'fontWeight': 'bold', 'cursor': 'pointer', 'background': '#dc3545', 'color': 'white', 'marginBottom': '10px', 'width': '100%'}, disabled=True),
            html.Button("📊 Generate Report", id="report-button", 
                       style={'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px', 'fontWeight': 'bold', 'cursor': 'pointer', 'background': '#007bff', 'color': 'white', 'marginBottom': '10px', 'width': '100%'}),
            html.Button("🏗️ Generate UML", id="uml-button", 
                       style={'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px', 'fontWeight': 'bold', 'cursor': 'pointer', 'background': '#007bff', 'color': 'white', 'width': '100%'})
        ], style={'display': 'flex', 'flexDirection': 'column'})
    ], style={
        'display': 'flex',
        'gap': '20px',
        'marginBottom': '20px',
        'padding': '20px',
        'background': '#f8f9fa',
        'borderRadius': '10px'
    })


def create_overview_and_timeline():
    """Create the service overview and timeline section."""
    now = datetime.now()
    start_time = (now - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    return html.Div([
        # Service Overview
        html.Div([
            html.H3("🎯 Service Overview"),
            html.Div(id='service-overview')
        ], style={
            'flex': '1',
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }),
        # Timestamp Correlation
        html.Div([
            html.H3("⏰ Timestamp Correlation"),
            dcc.Graph(
                id='correlation-timeline',
                style={'height': '300px'},
                config={'responsive': True},
                figure={
                    'data': [],
                    'layout': {
                        'xaxis': {
                            'type': 'date',
                            'range': [start_time, end_time],
                            'title': 'Time',
                            'fixedrange': False
                        },
                        'yaxis': {
                            'title': 'Event Index',
                            'fixedrange': False
                        },
                        'uirevision': 'timestamp-correlation-dynamic',
                        'margin': {'l': 40, 'r': 20, 't': 30, 'b': 40},
                        'height': 300
                    }
                }
            ),
            html.Div(id='correlation-stats')
        ], style={
            'flex': '1',
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        })
    ], style={
        'display': 'flex',
        'gap': '20px',
        'marginBottom': '20px'
    })


def create_data_table(table_id: str, title: str, columns: list):
    """Create a data table with search indicator and progress bar."""
    return html.Div([
        html.Div([
            html.H3(title, style={'display': 'inline-block', 'margin': '0'}),
            html.Div(id=f'{table_id}-search-indicator', style={'display': 'inline-block', 'marginLeft': '10px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
        html.Div(id=f'{table_id}-message-count', style={'marginBottom': '10px', 'fontWeight': 'bold', 'color': '#666'}),
        html.Div(id=f'{table_id}-progress-bar', style={'marginBottom': '10px'}),
        dash_table.DataTable(
            id=f'{table_id}-table',
            columns=columns,
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'monospace',
                'fontSize': '12px',
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{level} = ERROR'},
                    'backgroundColor': '#ffebee',
                    'color': 'red'
                },
                {
                    'if': {'filter_query': '{level} = WARN'},
                    'backgroundColor': '#fff3e0',
                    'color': 'orange'
                },
                {
                    'if': {'filter_query': '{level} = INFO'},
                    'backgroundColor': '#e8f5e8',
                    'color': 'green'
                },
                {
                    'if': {'filter_query': '{log_level} = VERBOSE'},
                    'backgroundColor': '#f3e5f5',
                    'color': 'purple'
                }
            ],
            page_size=10,
            sort_action="native",
            filter_action="native"
        )
    ], style={
        'padding': '20px',
        'background': 'white',
        'borderRadius': '10px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
        'minHeight': '400px'
    })


def create_data_windows():
    """Create the four data windows."""
    
    # Define columns for each table
    log_columns = [
        {'name': 'Timestamp', 'id': 'timestamp', 'type': 'text'},
        {'name': 'ServiceId', 'id': 'service_id', 'type': 'text'},
        {'name': 'Level', 'id': 'level', 'type': 'text'},
        {'name': 'Component', 'id': 'component', 'type': 'text'},
        {'name': 'Full Message', 'id': 'full_message', 'type': 'text'}
    ]
    
    dlt_columns = [
        {'name': 'Timestamp', 'id': 'timestamp', 'type': 'text'},
        {'name': 'ServiceId', 'id': 'service_id', 'type': 'text'},
        {'name': 'App ID', 'id': 'app_id', 'type': 'text'},
        {'name': 'Context ID', 'id': 'context_id', 'type': 'text'},
        {'name': 'Level', 'id': 'log_level', 'type': 'text'},
        {'name': 'Full Message', 'id': 'full_message', 'type': 'text'}
    ]
    
    pcap_columns = [
        {'name': 'Timestamp', 'id': 'timestamp', 'type': 'text'},
        {'name': 'ServiceId', 'id': 'service_id', 'type': 'text'},
        {'name': 'Method ID', 'id': 'method_id', 'type': 'text'},
        {'name': 'Source IP', 'id': 'source_ip', 'type': 'text'},
        {'name': 'Dest IP', 'id': 'dest_ip', 'type': 'text'},
        {'name': 'Protocol', 'id': 'protocol', 'type': 'text'},
        {'name': 'Full Message', 'id': 'full_message', 'type': 'text'}
    ]
    
    other_columns = [
        {'name': 'Timestamp', 'id': 'timestamp', 'type': 'text'},
        {'name': 'Source', 'id': 'source', 'type': 'text'},
        {'name': 'Level', 'id': 'level', 'type': 'text'},
        {'name': 'Category', 'id': 'category', 'type': 'text'},
        {'name': 'Full Message', 'id': 'full_message', 'type': 'text'}
    ]
    
    return html.Div([
        html.Div([
            create_data_table('log-messages', '📄 Log Messages', log_columns),
            create_data_table('dlt-messages', '🔍 DLT Messages', dlt_columns),
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),
        
        html.Div([
            create_data_table('pcap-messages', '🌐 SOME/IP Messages', pcap_columns),
            create_data_table('other-messages', '📋 Other Logs', other_columns),
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'})
    ])


def create_analysis_results():
    """Create the analysis results section."""
    return html.Div([
        html.Div([
            html.H3("📊 Correlation Analysis"),
            html.Div(id='correlation-report', style={
                'fontFamily': 'monospace',
                'fontSize': '12px',
                'whiteSpace': 'pre-wrap',
                'maxHeight': '300px',
                'overflowY': 'auto',
                'background': '#f8f9fa',
                'padding': '10px',
                'borderRadius': '5px'
            })
        ], style={
            'flex': '1',
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }),
        
        html.Div([
            html.H3("⚠️ Anomaly Detection"),
            html.Div(id='anomaly-report', style={
                'fontFamily': 'monospace',
                'fontSize': '12px',
                'whiteSpace': 'pre-wrap',
                'maxHeight': '300px',
                'overflowY': 'auto',
                'background': '#f8f9fa',
                'padding': '10px',
                'borderRadius': '5px'
            })
        ], style={
            'flex': '1',
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }),
        
        html.Div([
            html.H3("🏗️ Architecture"),
            html.Div(id='architecture-status', style={
                'fontFamily': 'monospace',
                'fontSize': '12px',
                'whiteSpace': 'pre-wrap',
                'maxHeight': '300px',
                'overflowY': 'auto',
                'background': '#f8f9fa',
                'padding': '10px',
                'borderRadius': '5px'
            })
        ], style={
            'flex': '1',
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        })
    ], style={
        'display': 'flex',
        'gap': '20px',
        'marginBottom': '20px'
    })


def create_main_layout():
    """Create the main dashboard layout."""
    return html.Div([
        # Header
        create_header(),
        
        # Control Panel
        create_control_panel(),
        
        # Main Analysis Windows
        create_overview_and_timeline(),
        
        # Four Independent Data Windows
        create_data_windows(),
        
        # Analysis Results
        create_analysis_results(),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=500,  # Update every 500ms
            n_intervals=0
        ),
        
        # Hidden div to store search state
        html.Div(id='search-state', style={'display': 'none'})
        
    ], style={
        'fontFamily': 'Arial, sans-serif',
        'margin': '20px',
        'backgroundColor': '#f5f5f5'
    })

