#!/usr/bin/env python3
"""
Debug Assistant - Main Application
Advanced analytics dashboard for ServiceId analysis with timestamp correlation and comprehensive reporting.
"""

import os
import sys
import threading
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash
from dash import Input, Output, State, callback_context
import plotly.graph_objs as go

# Import our modules
from utils.config import config
from utils.helpers import ServiceDiscovery, ProcessingStatus, check_data_files, create_sample_data_files
from data_processing.log_parser import LogParser
from data_processing.dlt_parser import DLTParser
from data_processing.pcap_parser import PCAPParser
from data_processing.correlator import EventCorrelator
from analysis.anomaly_detector import AnomalyDetector
from analysis.reporter import ReportGenerator
from analysis.uml_generator import UMLGenerator
from dashboard.layout import create_main_layout


class DebugAssistantApp:
    """Main Debug Assistant application class."""
    
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.app.title = config.get('app.title', 'Debug Assistant')
        
        # Initialize components
        self.status_manager = ProcessingStatus()
        self.service_discovery = ServiceDiscovery()
        self.log_parser = LogParser(self.status_manager)
        self.dlt_parser = DLTParser(self.status_manager)
        self.pcap_parser = PCAPParser(self.status_manager)
        self.correlator = EventCorrelator()
        self.anomaly_detector = AnomalyDetector()
        self.report_generator = ReportGenerator()
        self.uml_generator = UMLGenerator()
        
        # Data storage
        self.data_cache = {
            'log': {},
            'dlt': {},
            'pcap': {},
            'other': {}
        }
        
        # Threading control
        self.processing_threads = {}
        self.stop_event = threading.Event()
        
        # Initialize data files and discover services
        self.initialize_data()
        
        # Setup layout and callbacks
        self.setup_layout()
        self.setup_callbacks()
    
    def initialize_data(self):
        """Initialize data files and discover services."""
        print("🔍 Initializing Debug Assistant...")
        
        # Get data file paths
        data_files = config.get_data_files()
        
        # Check data files
        file_status = check_data_files(data_files)
        
        print("📁 Data file status:")
        for file_type, status in file_status.items():
            if status['exists']:
                print(f"  ✅ {file_type}: {status['path']} ({status['size_mb']:.1f} MB)")
            else:
                print(f"  ❌ {file_type}: {status['path']} (NOT FOUND)")
        
        # Create sample data if no real data exists
        missing_files = [status['path'] for status in file_status.values() if not status['exists']]
        if missing_files:
            print("📋 Creating sample data files for demonstration...")
            create_sample_data_files(config.get('data.directory'))
        
        # Discover services
        print("🔍 Discovering services...")
        discovered_services = self.service_discovery.discover_all(data_files)
        print(f"✅ Discovered {len(discovered_services)} services: {sorted(list(discovered_services))}")
    
    def setup_layout(self):
        """Setup the dashboard layout."""
        self.app.layout = create_main_layout()
        
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
    
    def setup_callbacks(self):
        """Setup all dashboard callbacks."""
        
        # Service dropdown population
        @self.app.callback(
            [Output('service-dropdown', 'options'),
             Output('service-dropdown', 'value')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_service_dropdown(n, current_value):
            """Update service dropdown with discovered services."""
            services = self.service_discovery.discovered_services
            options = [{'label': f'ServiceId: {s}', 'value': s} for s in sorted(services)]
            
            if current_value and current_value in services:
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
            """Update service status information."""
            if not selected_service:
                return "No service selected"
            
            services_count = len(self.service_discovery.discovered_services)
            return f"Selected: {selected_service} | Available services: {services_count}"
        
        # Run analysis button
        @self.app.callback(
            Output('search-state', 'children'),
            [Input('run-button', 'n_clicks'),
             Input('stop-button', 'n_clicks')],
            [State('service-dropdown', 'value'),
             State('data-sources', 'value')]
        )
        def handle_analysis_control(run_clicks, stop_clicks, selected_service, data_sources):
            """Handle run/stop analysis buttons."""
            ctx = callback_context
            if not ctx.triggered:
                return ""
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'run-button' and run_clicks and selected_service:
                self.start_analysis(selected_service, data_sources or [])
                return f"Analysis started for {selected_service}"
            elif button_id == 'stop-button' and stop_clicks:
                self.stop_analysis()
                return "Analysis stopped"
            
            return ""
        
        # Auto-search when service is selected
        @self.app.callback(
            Output('search-state', 'children', allow_duplicate=True),
            [Input('service-dropdown', 'value')],
            [State('data-sources', 'value')],
            prevent_initial_call=True
        )
        def auto_search_on_service_change(selected_service, data_sources):
            """Automatically start analysis when service is selected."""
            if selected_service and config.get('processing.auto_search_on_selection', True):
                self.start_analysis(selected_service, data_sources or ['log', 'dlt', 'pcap', 'other'])
                return f"Auto-analysis started for {selected_service}"
            return ""
        
        # Data table updates
        self.setup_data_table_callbacks()
        
        # Analysis results callbacks
        self.setup_analysis_callbacks()
        
        # Report and UML generation callbacks
        self.setup_generation_callbacks()
    
    def setup_data_table_callbacks(self):
        """Setup callbacks for data tables."""
        
        # Log messages table
        @self.app.callback(
            [Output('log-messages-table', 'data'),
             Output('log-messages-message-count', 'children'),
             Output('log-messages-search-indicator', 'children'),
             Output('log-messages-progress-bar', 'children')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_log_table(n, selected_service):
            """Update log messages table."""
            return self.update_data_table('log', selected_service)
        
        # DLT messages table
        @self.app.callback(
            [Output('dlt-messages-table', 'data'),
             Output('dlt-messages-message-count', 'children'),
             Output('dlt-messages-search-indicator', 'children'),
             Output('dlt-messages-progress-bar', 'children')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_dlt_table(n, selected_service):
            """Update DLT messages table."""
            return self.update_data_table('dlt', selected_service)
        
        # PCAP messages table
        @self.app.callback(
            [Output('pcap-messages-table', 'data'),
             Output('pcap-messages-message-count', 'children'),
             Output('pcap-messages-search-indicator', 'children'),
             Output('pcap-messages-progress-bar', 'children')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_pcap_table(n, selected_service):
            """Update PCAP messages table."""
            return self.update_data_table('pcap', selected_service)
        
        # Other messages table
        @self.app.callback(
            [Output('other-messages-table', 'data'),
             Output('other-messages-message-count', 'children'),
             Output('other-messages-search-indicator', 'children'),
             Output('other-messages-progress-bar', 'children')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_other_table(n, selected_service):
            """Update other messages table."""
            return self.update_data_table('other', selected_service)
    
    def setup_analysis_callbacks(self):
        """Setup callbacks for analysis results."""
        
        @self.app.callback(
            [Output('correlation-report', 'children'),
             Output('anomaly-report', 'children'),
             Output('correlation-timeline', 'figure')],
            [Input('interval-component', 'n_intervals')],
            [State('service-dropdown', 'value')]
        )
        def update_analysis_results(n, selected_service):
            """Update analysis results."""
            if not selected_service:
                return "No service selected", "No service selected", {'data': [], 'layout': {}}
            
            # Get cached data
            log_data = self.data_cache['log'].get(selected_service, [])
            dlt_data = self.data_cache['dlt'].get(selected_service, [])
            pcap_data = self.data_cache['pcap'].get(selected_service, [])
            other_data = self.data_cache['other'].get(selected_service, [])
            
            if not any([log_data, dlt_data, pcap_data, other_data]):
                return "No data available", "No data available", {'data': [], 'layout': {}}
            
            # Run correlation analysis
            correlation_results = self.correlator.correlate_events(log_data, dlt_data, pcap_data, other_data)
            
            # Run anomaly detection
            anomaly_results = self.anomaly_detector.detect_anomalies(log_data, dlt_data, pcap_data, other_data)
            
            # Generate reports
            correlation_report = self.format_correlation_report(correlation_results)
            anomaly_report = self.format_anomaly_report(anomaly_results)
            
            # Generate timeline figure
            timeline_figure = self.create_timeline_figure(correlation_results)
            
            return correlation_report, anomaly_report, timeline_figure
    
    def setup_generation_callbacks(self):
        """Setup callbacks for report and UML generation."""
        
        @self.app.callback(
            Output('architecture-status', 'children'),
            [Input('report-button', 'n_clicks'),
             Input('uml-button', 'n_clicks')],
            [State('service-dropdown', 'value')]
        )
        def handle_generation_buttons(report_clicks, uml_clicks, selected_service):
            """Handle report and UML generation buttons."""
            ctx = callback_context
            if not ctx.triggered or not selected_service:
                return "Select a service and click Generate Report or Generate UML"
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'report-button' and report_clicks:
                return self.generate_report(selected_service)
            elif button_id == 'uml-button' and uml_clicks:
                return self.generate_uml(selected_service)
            
            return "Ready for report or UML generation"
    
    def start_analysis(self, service_id: str, data_sources: list):
        """Start analysis for the selected service."""
        print(f"🚀 Starting analysis for service {service_id} with sources: {data_sources}")
        
        # Stop any existing analysis
        self.stop_analysis()
        
        # Get data file paths
        data_files = config.get_data_files()
        
        # Start analysis threads
        if 'log' in data_sources:
            thread = threading.Thread(
                target=self.analyze_log_data,
                args=(service_id, data_files['log_file']),
                daemon=True
            )
            thread.start()
            self.processing_threads['log'] = thread
        
        if 'dlt' in data_sources:
            thread = threading.Thread(
                target=self.analyze_dlt_data,
                args=(service_id, data_files['dlt_file']),
                daemon=True
            )
            thread.start()
            self.processing_threads['dlt'] = thread
        
        if 'pcap' in data_sources:
            thread = threading.Thread(
                target=self.analyze_pcap_data,
                args=(service_id, data_files['pcap_json_file']),
                daemon=True
            )
            thread.start()
            self.processing_threads['pcap'] = thread
        
        if 'other' in data_sources:
            thread = threading.Thread(
                target=self.analyze_other_data,
                args=(service_id,),
                daemon=True
            )
            thread.start()
            self.processing_threads['other'] = thread
    
    def stop_analysis(self):
        """Stop all analysis operations."""
        print("⏹️ Stopping analysis...")
        self.stop_event.set()
        
        # Stop parsers
        self.log_parser.stop_search()
        self.dlt_parser.stop_search()
        self.pcap_parser.stop_search()
        
        # Wait for threads to finish
        for thread in self.processing_threads.values():
            if thread.is_alive():
                thread.join(timeout=1)
        
        self.processing_threads.clear()
        self.stop_event.clear()
    
    def analyze_log_data(self, service_id: str, log_file: str):
        """Analyze log data in background thread."""
        try:
            max_messages = config.get('data.max_messages_per_source', 20000)
            messages = self.log_parser.search_log_file(log_file, service_id, max_messages)
            self.data_cache['log'][service_id] = messages
        except Exception as e:
            print(f"❌ Error analyzing log data: {e}")
    
    def analyze_dlt_data(self, service_id: str, dlt_file: str):
        """Analyze DLT data in background thread."""
        try:
            max_messages = config.get('data.max_messages_per_source', 200)
            messages = self.dlt_parser.search_dlt_file(dlt_file, service_id, max_messages)
            self.data_cache['dlt'][service_id] = messages
        except Exception as e:
            print(f"❌ Error analyzing DLT data: {e}")
    
    def analyze_pcap_data(self, service_id: str, pcap_file: str):
        """Analyze PCAP data in background thread."""
        try:
            max_messages = config.get('data.max_messages_per_source', 200)
            messages = self.pcap_parser.search_pcap_file(pcap_file, service_id, max_messages)
            self.data_cache['pcap'][service_id] = messages
        except Exception as e:
            print(f"❌ Error analyzing PCAP data: {e}")
    
    def analyze_other_data(self, service_id: str):
        """Analyze other data sources."""
        try:
            # Generate sample other data
            other_data = []
            for i in range(8):
                other_data.append({
                    'timestamp': f"12:34:{56+i:02d}.{i*250:03d}",
                    'source': ['System', 'Network', 'Security', 'Performance'][i % 4],
                    'level': ['INFO', 'WARN', 'ERROR'][i % 3],
                    'category': ['Startup', 'Runtime', 'Shutdown', 'Monitoring'][i % 4],
                    'full_message': f"System message {i+1} - {['Normal operation', 'Warning condition', 'Error detected'][i % 3]}"
                })
            
            self.data_cache['other'][service_id] = other_data
            self.status_manager.update_status('other', status='complete', count=len(other_data))
        except Exception as e:
            print(f"❌ Error analyzing other data: {e}")
    
    def update_data_table(self, source: str, selected_service: str):
        """Update data table for a specific source."""
        if not selected_service:
            return [], "No service selected", "", ""
        
        status = self.status_manager.get_status(source)
        data = self.data_cache[source].get(selected_service, [])
        
        # Create search indicator
        search_indicator = self.create_search_indicator(status.get('searching', False), status.get('progress', 0))
        
        # Create progress bar
        progress_bar = self.create_progress_bar(status.get('progress', 0), status.get('searching', False))
        
        # Create message count
        if status.get('searching', False):
            count_text = f"🔍 {status.get('message', 'Searching...')}"
        else:
            count_text = f"📊 {len(data)} messages for {selected_service}"
        
        return data, count_text, search_indicator, progress_bar
    
    def create_search_indicator(self, is_searching: bool, progress: int = 0):
        """Create search indicator component."""
        if is_searching:
            return dash.html.Div([
                dash.html.Span("🔍", style={
                    'animation': 'spin 1s linear infinite',
                    'display': 'inline-block',
                    'marginRight': '5px'
                }),
                dash.html.Span(f"Searching... {progress}%", style={'color': '#007bff', 'fontSize': '0.9em'})
            ], style={
                'display': 'inline-block',
                'padding': '2px 8px',
                'background': '#e3f2fd',
                'borderRadius': '10px',
                'border': '1px solid #2196f3'
            })
        else:
            return ""
    
    def create_progress_bar(self, progress: int, is_active: bool = False):
        """Create progress bar component."""
        if not is_active:
            return ""
        
        return dash.html.Div([
            dash.html.Div(
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
    
    def format_correlation_report(self, correlation_results: dict) -> str:
        """Format correlation results for display."""
        if not correlation_results:
            return "No correlation analysis available."
        
        stats = correlation_results.get('statistics', {})
        
        report = f"""Correlation Analysis Results:
========================

Total correlations: {stats.get('total_correlations', 0)}
Average events per correlation: {stats.get('avg_events_per_correlation', 0)}
Most active service: {stats.get('most_active_service', 'N/A')}
Time range: {stats.get('time_range', 'N/A')}
Correlation rate: {stats.get('correlation_rate', 0)}%

Sources involved: {', '.join(stats.get('sources_involved', []))}
Total events analyzed: {stats.get('total_events', 0)}
Correlated events: {stats.get('correlated_events', 0)}
"""
        
        return report
    
    def format_anomaly_report(self, anomaly_results: dict) -> str:
        """Format anomaly results for display."""
        if not anomaly_results:
            return "No anomaly analysis available."
        
        summary = anomaly_results.get('summary', {})
        
        report = f"""Anomaly Detection Results:
=========================

Total anomalies: {summary.get('total_anomalies', 0)}

By severity:
  High: {summary.get('by_severity', {}).get('high', 0)}
  Medium: {summary.get('by_severity', {}).get('medium', 0)}
  Low: {summary.get('by_severity', {}).get('low', 0)}

Recommendations:
"""
        
        for rec in summary.get('recommendations', []):
            report += f"  • {rec}\n"
        
        return report
    
    def create_timeline_figure(self, correlation_results: dict):
        """Create timeline figure for correlations."""
        if not correlation_results or not correlation_results.get('correlations'):
            return {'data': [], 'layout': {'title': 'No correlation data available'}}
        
        timeline_data = self.correlator.generate_timeline_data(correlation_results['correlations'])
        
        if not timeline_data:
            return {'data': [], 'layout': {'title': 'No timeline data available'}}
        
        # Create scatter plot
        fig = go.Figure()
        
        # Group by source for different colors
        sources = list(set(item['source'] for item in timeline_data))
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        
        for i, source in enumerate(sources):
            source_data = [item for item in timeline_data if item['source'] == source]
            
            fig.add_trace(go.Scatter(
                x=[item['x'] for item in source_data],
                y=[item['y'] for item in source_data],
                mode='markers',
                name=source,
                marker=dict(color=colors[i % len(colors)], size=8),
                text=[item['text'] for item in source_data],
                hovertext=[item['hovertext'] for item in source_data]
            ))
        
        fig.update_layout(
            title='Event Correlation Timeline',
            xaxis_title='Time',
            yaxis_title='Correlation Group',
            height=300
        )
        
        return fig
    
    def generate_report(self, service_id: str) -> str:
        """Generate comprehensive report."""
        try:
            log_data = self.data_cache['log'].get(service_id, [])
            dlt_data = self.data_cache['dlt'].get(service_id, [])
            pcap_data = self.data_cache['pcap'].get(service_id, [])
            other_data = self.data_cache['other'].get(service_id, [])
            
            # Run analysis
            correlation_results = self.correlator.correlate_events(log_data, dlt_data, pcap_data, other_data)
            anomaly_results = self.anomaly_detector.detect_anomalies(log_data, dlt_data, pcap_data, other_data)
            
            # Generate report
            report_path = self.report_generator.generate_comprehensive_report(
                service_id, log_data, dlt_data, pcap_data, other_data,
                correlation_results, anomaly_results
            )
            
            return f"✅ Report generated: {report_path}"
            
        except Exception as e:
            return f"❌ Error generating report: {str(e)}"
    
    def generate_uml(self, service_id: str) -> str:
        """Generate UML diagrams."""
        try:
            log_data = self.data_cache['log'].get(service_id, [])
            dlt_data = self.data_cache['dlt'].get(service_id, [])
            pcap_data = self.data_cache['pcap'].get(service_id, [])
            
            # Run correlation analysis for UML
            correlation_results = self.correlator.correlate_events(log_data, dlt_data, pcap_data, [])
            
            # Generate UML diagrams
            diagram_paths = self.uml_generator.generate_all_diagrams(
                service_id, log_data, dlt_data, pcap_data, correlation_results
            )
            
            if diagram_paths:
                return f"✅ UML diagrams generated:\n" + "\n".join(f"  • {path}" for path in diagram_paths)
            else:
                return "❌ No UML diagrams generated"
                
        except Exception as e:
            return f"❌ Error generating UML: {str(e)}"
    
    def run(self):
        """Run the Debug Assistant application."""
        host = config.get('app.host', '0.0.0.0')
        port = config.get('app.port', 8050)
        debug = config.get('app.debug', False)
        
        print("🏆 Debug Assistant - Professional ServiceId Analyzer")
        print("=" * 60)
        print(f"🌐 Access: http://localhost:{port}")
        print("✨ Features:")
        print("  📊 Full log messages in all windows")
        print("  ⏰ Advanced timestamp correlation")
        print("  🔗 Cross-source event correlation")
        print("  📈 Professional analytics")
        print("  🏗️ Architecture visualization")
        print("  📋 Comprehensive reporting")
        print("=" * 60)
        
        try:
            self.app.run(debug=debug, host=host, port=port)
        except KeyboardInterrupt:
            print("\n👋 Shutting down Debug Assistant...")
            self.stop_analysis()
        except Exception as e:
            print(f"❌ Error running application: {e}")


def main():
    """Main function."""
    try:
        app = DebugAssistantApp()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start Debug Assistant: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

