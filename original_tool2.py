#!/usr/bin/env python3
"""
Professional ServiceId Analyzer Dashboard - FIXED VERSION
Advanced analytics with full log messages, timestamp correlation, and comprehensive reporting
Perfect for technical promotion demonstrations
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import json
import threading
import time
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta


class ProfessionalDashboard:
    def __init__(self, data_directory: str = "./data"):
        self.app = dash.Dash(__name__)
        self.app.title = "Debug Assistant"

        self.data_dir = data_directory
        self.log_file = os.path.join(data_directory, "adaptive.log")
        self.dlt_file = os.path.join(data_directory, "dltlog_0.dlt")
        self.pcap_json_file = os.path.join(data_directory, "full_pcap.json")
        

        # Check if files exist
        self.check_data_files()
        
        # Data storage
        self.log_data = {}
        self.dlt_data = {}
        self.pcap_data = {}
        self.other_logs = {}
        self.discovered_services = set()
        
        # Processing status
        self.processing_status = {
            'log': {'status': 'ready', 'progress': 0, 'message': 'Ready'},
            'dlt': {'status': 'ready', 'progress': 0, 'message': 'Ready'},
            'pcap': {'status': 'ready', 'progress': 0, 'message': 'Ready'},
            'other': {'status': 'ready', 'progress': 0, 'message': 'Ready'}
        }
        # Threading control
        self.processing_threads = {}
        self.stop_processing = threading.Event()
        
        # Initialize with service discovery
        self.discover_all_services()
        self.setup_layout()
        self.setup_callbacks()
    
    def check_data_files(self):
        """Check if data files exist and provide guidance"""
        print("🔍 Checking for data files...")
        
        if not os.path.exists(self.data_dir):
            print(f"📁 Creating data directory: {self.data_dir}")
            os.makedirs(self.data_dir, exist_ok=True)
        
        files_status = {
            "Log file": (self.log_file, os.path.exists(self.log_file)),
            "DLT file": (self.dlt_file, os.path.exists(self.dlt_file)),
            "PCAP JSON": (self.pcap_json_file, os.path.exists(self.pcap_json_file))
        }
        
        for file_type, (file_path, exists) in files_status.items():
            if exists:
                size = os.path.getsize(file_path) / (1024*1024)  # MB
                print(f"✅ {file_type}: {file_path} ({size:.1f} MB)")
            else:
                print(f"❌ {file_type}: {file_path} (NOT FOUND)")
        
        missing_files = [path for _, (path, exists) in files_status.items() if not exists]
        if missing_files:
            print("\n📋 TO USE YOUR REAL DATA:")
            print("1. Copy your files to the data directory:")
            for file_path in missing_files:
                print(f"   cp your_file {file_path}")
            print("2. Restart the dashboard")
            print("3. Your real data will be automatically loaded!")
      
    def setup_layout(self):
        """Setup the professional dashboard layout"""
        now = datetime.now()
        start_time = (now - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        end_time = now.strftime('%Y-%m-%d %H:%M:%S')
        self.app.layout = html.Div([
            # Header
            html.Div([
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
            }),
            
            # Control Panel
            html.Div([
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
            }),
            
            # Main Analysis Windows
            html.Div([
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
                            'data': [],  # To be updated via callback
                            'layout': {
                                'xaxis': {
                                    'type': 'date',
                                    'range': [start_time, end_time],  # Example range
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
            }),
            
            # Four Independent Data Windows
            html.Div([
                # Log Messages Window
                html.Div([
                    html.Div([
                        html.H3("📄 Log Messages", style={'display': 'inline-block', 'margin': '0'}),
                        html.Div(id='log-search-indicator', style={'display': 'inline-block', 'marginLeft': '10px'})
                
		     ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                     html.Div(id='log-message-count', style={'marginBottom': '10px', 'fontWeight': 'bold', 'color': '#666'}),
                     html.Div(id='log-progress-bar', style={'marginBottom': '10px'}),
                        dash_table.DataTable(
                            id='log-messages-table',
                            columns=[
                                {'name': 'Timestamp', 'id': 'timestamp', 'type': 'text'},
                                {'name': 'ServiceId', 'id': 'service_id', 'type': 'text'},
                                {'name': 'Level', 'id': 'level', 'type': 'text'},
                                {'name': 'Component', 'id': 'component', 'type': 'text'},
                                {'name': 'Full Message', 'id': 'full_message', 'type': 'text'}
                            ],
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
                }),
                
                # DLT Window
                html.Div([
                    html.Div([
                        html.H3("🔍 DLT Messages", style={'display': 'inline-block', 'margin': '0'}),
                        html.Div(id='dlt-search-indicator', style={'display': 'inline-block', 'marginLeft': '10px'})
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                    html.Div(id='dlt-message-count', style={'marginBottom': '10px', 'fontWeight': 'bold', 'color': '#666'}),
                    html.Div(id='dlt-progress-bar', style={'marginBottom': '10px'}),
                    dash_table.DataTable(
                        id='dlt-messages-table',
                        columns=[
                           {'name': 'Timestamp', 'id': 'timestamp', 'type': 'text'},
                           {'name': 'ServiceId', 'id': 'service_id', 'type': 'text'},
                           {'name': 'App ID', 'id': 'app_id', 'type': 'text'},
                           {'name': 'Context ID', 'id': 'context_id', 'type': 'text'},
                           {'name': 'Level', 'id': 'log_level', 'type': 'text'},
                           {'name': 'Full Message', 'id': 'full_message', 'type': 'text'}
                        ],
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
                                    'if': {'filter_query': '{log_level} = ERROR'},
                                    'backgroundColor': '#ffebee',
                                    'color': 'red'
                                },
                                {
                                    'if': {'filter_query': '{log_level} = WARN'},
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
		                'flex': '1',
                        'padding': '20px',
                        'background': 'white',
                        'borderRadius': '10px',
                        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                        'minHeight': '400px'
                    }),
                    ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}),
                # PCAP/SOME-IP Window
                html.Div([
		            html.Div([
                        html.Div([
                            html.H3("🌐 SOME/IP Messages", style={'display': 'inline-block', 'margin': '0'}),
                            html.Div(id='pcap-search-indicator', style={'display': 'inline-block', 'marginLeft': '10px'})
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                        html.Div(id='pcap-message-count', style={'marginBottom': '10px', 'fontWeight': 'bold', 'color': '#666'}),
                        html.Div(id='pcap-progress-bar', style={'marginBottom': '10px'}),
                        dash_table.DataTable(
                            id='pcap-messages-table',
                            columns=[
                                {'name': 'Timestamp', 'id': 'timestamp', 'type': 'text'},
                                {'name': 'ServiceId', 'id': 'service_id', 'type': 'text'},
                                {'name': 'Method ID', 'id': 'method_id', 'type': 'text'},
                                {'name': 'Source IP', 'id': 'source_ip', 'type': 'text'},
                                {'name': 'Dest IP', 'id': 'dest_ip', 'type': 'text'},
                                {'name': 'Protocol', 'id': 'protocol', 'type': 'text'},
                                {'name': 'Full Message', 'id': 'full_message', 'type': 'text'}
                            ],
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
                                    'if': {'filter_query': '{protocol} contains SOME/IP-SD'},
                                    'backgroundColor': '#e3f2fd',
                                    'color': 'blue'
                                },
                                {
                                    'if': {'filter_query': '{protocol} contains SOME/IP'},
                                    'backgroundColor': '#f1f8e9',
                                    'color': 'green'
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
                }),
                
               
         # Other Logs Window
 		html.Div([
            html.Div([
                html.H3("📋 Other Logs", style={'display': 'inline-block', 'margin': '0'}),
                html.Div(id='other-search-indicator', style={'display': 'inline-block', 'marginLeft': '10px'})
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                html.Div(id='other-message-count', style={'marginBottom': '10px', 'fontWeight': 'bold', 'color': '#666'}),
                html.Div(id='other-progress-bar', style={'marginBottom': '10px'}),
            dash_table.DataTable(
                id='other-messages-table',
                columns=[
                    {'name': 'Timestamp', 'id': 'timestamp', 'type': 'text'},
                    {'name': 'Source', 'id': 'source', 'type': 'text'},
                    {'name': 'Level', 'id': 'level', 'type': 'text'},
                    {'name': 'Category', 'id': 'category', 'type': 'text'},
                    {'name': 'Full Message', 'id': 'full_message', 'type': 'text'}
                ],
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
                        'if': {'filter_query': '{level} = FATAL'},
                        'backgroundColor': '#ffcdd2',
                        'color': 'darkred'
                    },
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
                })],
                style={
                    'display': 'grid',
                    'gridTemplateColumns': '1fr 1fr',
                    'gap': '20px',
                    'marginBottom': '20px'
            }),
            # Analysis Results
            html.Div([
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
            }),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=500,  # Update every second
                n_intervals=0
            ),
            html.Div(id='search-state', style={'display': 'none'})
        ], style={
            'fontFamily': 'Arial, sans-serif',
            'margin': '20px',
            'backgroundColor': '#f5f5f5'
        })
    
    def discover_services_from_log(self):
        """Discover services from log file"""
        try:
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i > 1000:  # Limit for quick discovery
                        break
                    service_match = re.search(r'ServiceId:\s*(0x[0-9a-fA-F]+)', line)
                    if service_match:
                        self.discovered_services.add(service_match.group(1))
        except Exception as e:
            print(f"⚠️ Error discovering services from log: {e}")
    
    def discover_services_from_dlt(self):
        """Discover services from DLT file"""
        try:
            # Simple pattern-based discovery for DLT
            with open(self.dlt_file, 'rb') as f:
                content = f.read(10000)  # Read first 10KB
                # Look for service ID patterns in binary data
                text_content = content.decode('utf-8', errors='ignore')
                service_matches = re.findall(r'0x[0-9a-fA-F]{4}', text_content)
                for match in service_matches[:10]:  # Limit results
                    self.discovered_services.add(match)
                    print(f"🔍 Discovered service from DLT: {match}")
        except Exception as e:
            print(f"⚠️ Error discovering services from DLT: {e}")
    
    def discover_services_from_pcap(self):
        """Discover services from PCAP JSON file"""
        try:
            with open(self.pcap_json_file, 'r', encoding='utf-8') as f:
                # Read first few lines to discover services
                for i, line in enumerate(f):
                    if i > 100:  # Limit for quick discovery
                        break
                    try:
                        data = json.loads(line)
                        if 'service_id' in data:
                            self.discovered_services.add(data['service_id'])
                        # Look for service patterns in the data
                        line_str = str(data)
                        service_matches = re.findall(r'0x[0-9a-fA-F]{4}', line_str)
                        for match in service_matches[:5]:
                            self.discovered_services.add(match)
                    except:
                        continue
        except Exception as e:
            print(f"⚠️ Error discovering services from PCAP: {e}")
    
    def discover_all_services(self):
        """Discover all available services from all data sources"""
        print("🔍 Discovering services from all data sources...")
        
        # Discover from log file
        if os.path.exists(self.log_file):
            self.discover_services_from_log()
        
        # Discover from DLT file
        if os.path.exists(self.dlt_file):
            self.discover_services_from_dlt()
        
        # Discover from PCAP file
        if os.path.exists(self.pcap_json_file):
            self.discover_services_from_pcap()
        
        # # Add sample services if none found
        # if not self.discovered_services:
        #     self.discovered_services.update(['0x1234', '0x5678', '0x9ABC', '0xDEF0'])
        #     print("📋 Added sample services for demonstration")
        
        print(f"✅ Discovered {len(self.discovered_services)} unique services: {sorted(self.discovered_services)}")
    
    def create_search_indicator(self, is_searching: bool, progress: int = 0) -> html.Div:
        """Create animated search indicator"""
        if is_searching:
            return html.Div([
                html.Span("🔍", style={
                    'animation': 'spin 1s linear infinite',
                    'display': 'inline-block',
                    'marginRight': '5px'
                }),
                html.Span(f"Searching... {progress}%", style={'color': '#007bff', 'fontSize': '0.9em'})
            ], style={
                'display': 'inline-block',
                'padding': '2px 8px',
                'background': '#e3f2fd',
                'borderRadius': '10px',
                'border': '1px solid #2196f3'
            })
        else:
            return html.Div()
    
    def create_progress_bar(self, progress: int, is_active: bool = False) -> html.Div:
        """Create progress bar for search operations"""
        if not is_active:
            return html.Div()
        
        return html.Div([
            html.Div(
                style={
                    'width': f'{progress}%',
                    'height': '4px',
                    'background': 'linear-gradient(90deg, #4CAF50, #2196F3)',
                    'borderRadius': '2px',
                    'transition': 'width 0.3s ease'
                }
            )
        ], style={
            'width': '100%',
            'height': '4px',
            'background': '#e0e0e0',
            'borderRadius': '2px',
            'overflow': 'hidden'
        })

    def background_search_log(self, service_id: str):
        """Background search for log messages with progress updates"""
        try:
            self.processing_status['log']['searching'] = True
            self.processing_status['log']['status'] = 'searching'
            self.processing_status['log']['progress'] = 0
            self.processing_status['log']['message'] = 'Starting log search...'
            
            messages = []
            if not os.path.exists(self.log_file):
                # Generate sample data with progress simulation
                for i in range(10):
                    if self.stop_processing.is_set():
                        break
                    time.sleep(0.1)  # Simulate processing time
                    self.processing_status['log']['progress'] = (i + 1) * 10
                    self.processing_status['log']['message'] = f'Generating sample data... {(i+1)*10}%'
                
                messages = self.get_sample_log_data(service_id)
            else:
                # Real file processing with progress
                total_lines = sum(1 for _ in open(self.log_file, 'r', encoding='utf-8', errors='ignore'))
                processed_lines = 0
                
                with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f):
                        if self.stop_processing.is_set():
                            break
                        
                        processed_lines += 1
                        if processed_lines % 100 == 0:  # Update progress every 100 lines
                            progress = min((processed_lines / total_lines) * 100, 100)
                            self.processing_status['log']['progress'] = int(progress)
                            self.processing_status['log']['message'] = f'Processing line {processed_lines}/{total_lines}...'
                        
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Extract ServiceId
                        service_match = re.search(r'ServiceId:\s*(0x[0-9a-fA-F]+)', line)
                        msg_service_id = service_match.group(1) if service_match else None
                        
                        if not msg_service_id or (service_id and msg_service_id.upper() != service_id.upper()):
                            continue
                        
                        # Extract other fields
                        timestamp_match = re.search(r'\[(\d+)\]', line)
                        timestamp = timestamp_match.group(1) if timestamp_match else str(line_num)
                        
                        level_match = re.search(r'\]\[([A-Z]+)\]\s', line)
                        level = level_match.group(1) if level_match else 'INFO'
                        
                        component_match = re.search(r'\]([^[]+)\]\[', line)
                        component = component_match.group(1) if component_match else 'Unknown'
                        
                        try:
                            ts_int = int(timestamp)
                            dt = datetime.fromtimestamp(ts_int / 1000000)
                            formatted_time = dt.strftime('%H:%M:%S.%f')[:-3]
                        except:
                            formatted_time = timestamp
                        
                        messages.append({
                            'timestamp': formatted_time,
                            'service_id': msg_service_id,
                            'level': level,
                            'component': component,
                            'full_message': line
                        })
                        
                        if len(messages) >= 500:  # Limit for performance
                            break
            
            # Store results
            self.log_data[service_id] = messages
            self.processing_status['log']['count'] = len(messages)
            self.processing_status['log']['progress'] = 100
            self.processing_status['log']['message'] = f'Found {len(messages)} messages'
            self.processing_status['log']['status'] = 'complete'
            
        except Exception as e:
            self.processing_status['log']['status'] = 'error'
            self.processing_status['log']['message'] = f'Error: {str(e)}'
            print(f"❌ Error in log search: {e}")
        finally:
            self.processing_status['log']['searching'] = False
    
    def background_search_dlt(self, service_id: str):
        """Background search for DLT messages with progress updates"""
        try:
            self.processing_status['dlt']['searching'] = True
            self.processing_status['dlt']['status'] = 'searching'
            self.processing_status['dlt']['progress'] = 0
            self.processing_status['dlt']['message'] = 'Starting DLT search...'
            
            messages = []
            if not os.path.exists(self.dlt_file):
                # Generate sample data with progress simulation
                for i in range(8):
                    if self.stop_processing.is_set():
                        break
                    time.sleep(0.15)
                    self.processing_status['dlt']['progress'] = (i + 1) * 12.5
                    self.processing_status['dlt']['message'] = f'Generating DLT sample data... {int((i+1)*12.5)}%'
                
                messages = self.get_sample_dlt_data(service_id)
            else:
                # Simulate DLT processing (since pydlt might not be available)
                for i in range(20):
                    if self.stop_processing.is_set():
                        break
                    time.sleep(0.05)
                    self.processing_status['dlt']['progress'] = (i + 1) * 5
                    self.processing_status['dlt']['message'] = f'Processing DLT file... {(i+1)*5}%'
                
                messages = self.get_sample_dlt_data(service_id)
            
            # Store results
            self.dlt_data[service_id] = messages
            self.processing_status['dlt']['count'] = len(messages)
            self.processing_status['dlt']['progress'] = 100
            self.processing_status['dlt']['message'] = f'Found {len(messages)} DLT messages'
            self.processing_status['dlt']['status'] = 'complete'
            
        except Exception as e:
            self.processing_status['dlt']['status'] = 'error'
            self.processing_status['dlt']['message'] = f'Error: {str(e)}'
            print(f"❌ Error in DLT search: {e}")
        finally:
            self.processing_status['dlt']['searching'] = False
    
    def background_search_pcap(self, service_id: str):
        """Background search for PCAP messages with progress updates"""
        try:
            self.processing_status['pcap']['searching'] = True
            self.processing_status['pcap']['status'] = 'searching'
            self.processing_status['pcap']['progress'] = 0
            self.processing_status['pcap']['message'] = 'Starting PCAP search...'
            
            messages = []
            if not os.path.exists(self.pcap_json_file):
                # Generate sample data with progress simulation
                for i in range(12):
                    if self.stop_processing.is_set():
                        break
                    time.sleep(0.1)
                    self.processing_status['pcap']['progress'] = (i + 1) * 8.33
                    self.processing_status['pcap']['message'] = f'Generating PCAP sample data... {int((i+1)*8.33)}%'
                
                messages = self.get_sample_pcap_data(service_id)
            else:
                # Real PCAP JSON processing with progress
                line_count = 0
                with open(self.pcap_json_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        if self.stop_processing.is_set():
                            break
                        
                        line_count += 1
                        if line_count % 50 == 0:  # Update progress every 50 lines
                            progress = min((line_count / 1000) * 100, 100)  # Assume max 1000 lines for progress
                            self.processing_status['pcap']['progress'] = int(progress)
                            self.processing_status['pcap']['message'] = f'Processing PCAP line {line_count}...'
                        
                        try:
                            data = json.loads(line)
                            # Extract service information
                            if 'service_id' in data and (not service_id or data['service_id'] == service_id):
                                messages.append({
                                    'timestamp': data.get('timestamp', ''),
                                    'service_id': data.get('service_id', ''),
                                    'method_id': data.get('method_id', ''),
                                    'source_ip': data.get('source_ip', ''),
                                    'protocol': data.get('protocol', ''),
                                    'full_message': str(data)
                                })
                        except:
                            continue
                        
                        if len(messages) >= 200:  # Limit for performance
                            break
            
            # Store results
            self.pcap_data[service_id] = messages
            self.processing_status['pcap']['count'] = len(messages)
            self.processing_status['pcap']['progress'] = 100
            self.processing_status['pcap']['message'] = f'Found {len(messages)} PCAP messages'
            self.processing_status['pcap']['status'] = 'complete'
            
        except Exception as e:
            self.processing_status['pcap']['status'] = 'error'
            self.processing_status['pcap']['message'] = f'Error: {str(e)}'
            print(f"❌ Error in PCAP search: {e}")
        finally:
            self.processing_status['pcap']['searching'] = False
    
    def background_search_other(self, service_id: str):
        """Background search for other logs with progress updates"""
        try:
            self.processing_status['other']['searching'] = True
            self.processing_status['other']['status'] = 'searching'
            self.processing_status['other']['progress'] = 0
            self.processing_status['other']['message'] = 'Starting other logs search...'
            
            # Simulate other logs processing
            for i in range(6):
                if self.stop_processing.is_set():
                    break
                time.sleep(0.2)
                self.processing_status['other']['progress'] = (i + 1) * 16.67
                self.processing_status['other']['message'] = f'Processing system logs... {int((i+1)*16.67)}%'
            
            messages = self.get_sample_other_data()
            
            # Store results
            self.other_logs[service_id] = messages
            self.processing_status['other']['count'] = len(messages)
            self.processing_status['other']['progress'] = 100
            self.processing_status['other']['message'] = f'Found {len(messages)} other messages'
            self.processing_status['other']['status'] = 'complete'
            
        except Exception as e:
            self.processing_status['other']['status'] = 'error'
            self.processing_status['other']['message'] = f'Error: {str(e)}'
            print(f"❌ Error in other logs search: {e}")
        finally:
            self.processing_status['other']['searching'] = False
    
    def start_background_search(self, service_id: str, data_sources: List[str]):
        """Start background search for selected service and data sources"""
        print(f"🔍 Starting background search for service {service_id} in sources: {data_sources}")
        
        # Stop any existing searches
        self.stop_processing.set()
        time.sleep(0.1)  # Brief pause to allow threads to stop
        self.stop_processing.clear()
        
        # Start new search threads
        if 'log' in data_sources:
            thread = threading.Thread(target=self.background_search_log, args=(service_id,), daemon=True)
            thread.start()
            self.processing_threads['log'] = thread
        
        if 'dlt' in data_sources:
            thread = threading.Thread(target=self.background_search_dlt, args=(service_id,), daemon=True)
            thread.start()
            self.processing_threads['dlt'] = thread
        
        if 'pcap' in data_sources:
            thread = threading.Thread(target=self.background_search_pcap, args=(service_id,), daemon=True)
            thread.start()
            self.processing_threads['pcap'] = thread
        
        if 'other' in data_sources:
            thread = threading.Thread(target=self.background_search_other, args=(service_id,), daemon=True)
            thread.start()
            self.processing_threads['other'] = thread
    
    def stop_background_search(self):
        """Stop all background search operations"""
        print("⏹️ Stopping all background searches...")
        self.stop_processing.set()
        
        # Reset all processing status
        for source in self.processing_status:
            self.processing_status[source]['searching'] = False
            self.processing_status[source]['status'] = 'stopped'
            self.processing_status[source]['message'] = 'Search stopped'
    
    def get_sample_log_data(self, service_id: str) -> List[Dict]:
        """Generate sample log data for demonstration"""
        sample_data = []
        for i in range(15):
            sample_data.append({
                'timestamp': f"12:34:{56+i:02d}.{i*100:03d}",
                'service_id': service_id or '0x1234',
                'level': ['INFO', 'WARN', 'ERROR', 'DEBUG'][i % 4],
                'component': ['ServiceManager', 'NetworkHandler', 'DataProcessor', 'EventDispatcher'][i % 4],
                'full_message': f"[{12345678+i}][{['INFO', 'WARN', 'ERROR', 'DEBUG'][i % 4]}] Sample log message {i+1} for service {service_id or '0x1234'}"
            })
        return sample_data
    
    def get_sample_dlt_data(self, service_id: str) -> List[Dict]:
        """Generate sample DLT data for demonstration"""
        sample_data = []
        for i in range(12):
            sample_data.append({
                'timestamp': f"12:34:{56+i:02d}.{i*150:03d}",
                'app_id': f"APP{i%3+1}",
                'context_id': f"CTX{i%4+1}",
                'log_level': ['INFO', 'WARN', 'ERROR', 'VERBOSE'][i % 4],
                'full_message': f"DLT sample message {i+1} for service {service_id or '0x1234'} - Application context data"
            })
        return sample_data
    
    def get_sample_pcap_data(self, service_id: str) -> List[Dict]:
        """Generate sample PCAP data for demonstration"""
        sample_data = []
        for i in range(10):
            sample_data.append({
                'timestamp': f"12:34:{56+i:02d}.{i*200:03d}",
                'service_id': service_id or '0x1234',
                'method_id': f"0x{100+i:04x}",
                'source_ip': f"192.168.1.{10+i}",
                'protocol': ['SOME/IP', 'SOME/IP-SD'][i % 2],
                'full_message': f"SOME/IP packet {i+1} for service {service_id or '0x1234'} - Method call data"
            })
        return sample_data
    
    def get_sample_other_data(self) -> List[Dict]:
        """Generate sample other logs data for demonstration"""
        sample_data = []
        for i in range(8):
            sample_data.append({
                'timestamp': f"12:34:{56+i:02d}.{i*250:03d}",
                'source': ['System', 'Network', 'Security', 'Performance'][i % 4],
                'level': ['INFO', 'WARN', 'ERROR'][i % 3],
                'category': ['Startup', 'Runtime', 'Shutdown', 'Monitoring'][i % 4],
                'full_message': f"System message {i+1} - {['Normal operation', 'Warning condition', 'Error detected'][i % 3]}"
            })
        return sample_data
        
    def setup_callbacks(self):
        """Setup dashboard callbacks with professional search functionality"""
        
        # Service dropdown population and selection
        @self.app.callback(
            [Output('service-dropdown', 'options'),
             Output('service-dropdown', 'value')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_service_dropdown(n, current_value):
            """Update service dropdown with discovered services"""
            options = [{'label': f'ServiceId: {s}', 'value': s} for s in sorted(self.discovered_services)]
            
            # Keep current selection if valid, otherwise select first
            if current_value and current_value in self.discovered_services:
                return options, current_value
            elif options:
                return options, options[0]['value']
            else:
                return options, None
        
        # Service status display
        @self.app.callback(
            Output('service-status', 'children'),
            [Input('service-dropdown', 'value')]
        )
        def update_service_status(selected_service):
            """Update service status information"""
            if not selected_service:
                return "No service selected"
            
            return f"Selected: {selected_service} | Available services: {len(self.discovered_services)}"
        
        # Search control buttons
        @self.app.callback(
            Output('search-state', 'children'),
            [Input('search-button', 'n_clicks'),
             Input('stop-button', 'n_clicks')],
            [State('service-dropdown', 'value'),
             State('data-sources', 'value')]
        )
        def handle_search_control(search_clicks, stop_clicks, selected_service, data_sources):
            """Handle search start/stop buttons"""
            ctx = callback_context
            if not ctx.triggered:
                return ""
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'search-button' and search_clicks and selected_service:
                self.start_background_search(selected_service, data_sources or [])
                return f"Search started for {selected_service}"
            elif button_id == 'stop-button' and stop_clicks:
                self.stop_background_search()
                return "Search stopped"
            
            return ""
        
        # Automatic search when service is selected or typed
        @self.app.callback(
            Output('search-state', 'children', allow_duplicate=True),
            [Input('service-dropdown', 'value')],
            [State('data-sources', 'value')],
            prevent_initial_call=True
        )
        def auto_search_on_service_change(selected_service, data_sources):
            """Automatically start search when service is selected"""
            if selected_service:
                self.start_background_search(selected_service, data_sources or ['log', 'dlt', 'pcap', 'other'])
                return f"Auto-search started for {selected_service}"
            return ""
        
        # Log messages window with search animation
        @self.app.callback(
            [Output('log-messages-table', 'data'),
             Output('log-message-count', 'children'),
             Output('log-search-indicator', 'children'),
             Output('log-progress-bar', 'children')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_log_window(n, selected_service):
            """Update log messages window with search animations"""
            if not selected_service:
                return [], "No service selected", html.Div(), html.Div()
            
            status = self.processing_status['log']
            
            # Search indicator
            search_indicator = self.create_search_indicator(status['searching'], status['progress'])
            
            # Progress bar
            progress_bar = self.create_progress_bar(status['progress'], status['searching'])
            
            # Message count and status
            if status['searching']:
                count_text = f"🔍 {status['message']}"
            else:
                count_text = f"📄 {status['count']} log messages for {selected_service}"
                if os.path.exists(self.log_file):
                    count_text += " (from real file)"
                else:
                    count_text += " (sample data)"
            
            # Data
            data = self.log_data.get(selected_service, [])
            
            return data, count_text, search_indicator, progress_bar
        
        # DLT messages window with search animation
        @self.app.callback(
            [Output('dlt-messages-table', 'data'),
             Output('dlt-message-count', 'children'),
             Output('dlt-search-indicator', 'children'),
             Output('dlt-progress-bar', 'children')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_dlt_window(n, selected_service):
            """Update DLT messages window with search animations"""
            if not selected_service:
                return [], "No service selected", html.Div(), html.Div()
            
            status = self.processing_status['dlt']
            
            # Search indicator
            search_indicator = self.create_search_indicator(status['searching'], status['progress'])
            
            # Progress bar
            progress_bar = self.create_progress_bar(status['progress'], status['searching'])
            
            # Message count and status
            if status['searching']:
                count_text = f"🔍 {status['message']}"
            else:
                count_text = f"🔍 {status['count']} DLT messages for {selected_service}"
                if os.path.exists(self.dlt_file):
                    count_text += " (from real file)"
                else:
                    count_text += " (sample data)"
            
            # Data
            data = self.dlt_data.get(selected_service, [])
            
            return data, count_text, search_indicator, progress_bar
        
        # PCAP messages window with search animation
        @self.app.callback(
            [Output('pcap-messages-table', 'data'),
             Output('pcap-message-count', 'children'),
             Output('pcap-search-indicator', 'children'),
             Output('pcap-progress-bar', 'children')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_pcap_window(n, selected_service):
            """Update PCAP messages window with search animations"""
            if not selected_service:
                return [], "No service selected", html.Div(), html.Div()
            
            status = self.processing_status['pcap']
            
            # Search indicator
            search_indicator = self.create_search_indicator(status['searching'], status['progress'])
            
            # Progress bar
            progress_bar = self.create_progress_bar(status['progress'], status['searching'])
            
            # Message count and status
            if status['searching']:
                count_text = f"🔍 {status['message']}"
            else:
                count_text = f"🌐 {status['count']} SOME/IP messages for {selected_service}"
                if os.path.exists(self.pcap_json_file):
                    count_text += " (from real file)"
                else:
                    count_text += " (sample data)"
            
            # Data
            data = self.pcap_data.get(selected_service, [])
            
            return data, count_text, search_indicator, progress_bar
        
        # Other logs window with search animation
        @self.app.callback(
            [Output('other-messages-table', 'data'),
             Output('other-message-count', 'children'),
             Output('other-search-indicator', 'children'),
             Output('other-progress-bar', 'children')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_other_window(n, selected_service):
            """Update other logs window with search animations"""
            if not selected_service:
                return [], "No service selected", html.Div(), html.Div()
            
            status = self.processing_status['other']
            
            # Search indicator
            search_indicator = self.create_search_indicator(status['searching'], status['progress'])
            
            # Progress bar
            progress_bar = self.create_progress_bar(status['progress'], status['searching'])
            
            # Message count and status
            if status['searching']:
                count_text = f"🔍 {status['message']}"
            else:
                count_text = f"📋 {status['count']} other messages"
            
            # Data
            data = self.other_logs.get(selected_service, [])
            
            return data, count_text, search_indicator, progress_bar
  
    def run(self, debug=False, host='0.0.0.0', port=8050):
        """Run the professional dashboard"""
        # Add CSS for animations
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        print("🏆 Professional ServiceId Analyzer Dashboard")
        print("=" * 50)
        print(f"🌐 Access: http://localhost:{port}")
        print("✨ Features:")
        print("  📊 Full log messages in all windows")
        print("  ⏰ Advanced timestamp correlation")
        print("  🔗 Cross-source event correlation")
        print("  📈 Professional analytics")
        print("  🏗️ Architecture visualization")
        print("  📋 Comprehensive reporting")
        
        self.app.run(debug=debug, host=host, port=port)

def main():
    """Main function"""
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    dashboard = ProfessionalDashboard(data_dir)
    dashboard.run()

if __name__ == "__main__":
    main()

