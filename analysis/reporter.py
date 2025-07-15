"""
Report generation module for the Debug Assistant application.
Generates comprehensive analysis reports in various formats.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


class ReportGenerator:
    """Generates comprehensive analysis reports."""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_comprehensive_report(self, service_id: str, log_data: List[Dict], 
                                    dlt_data: List[Dict], pcap_data: List[Dict], 
                                    other_data: List[Dict], correlation_results: Dict,
                                    anomaly_results: Dict) -> str:
        """Generate a comprehensive analysis report."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"debug_report_{service_id}_{timestamp}.txt"
        report_path = os.path.join(self.output_dir, report_filename)
        
        with open(report_path, 'w') as f:
            f.write(self._generate_report_content(service_id, log_data, dlt_data, 
                                                pcap_data, other_data, correlation_results, 
                                                anomaly_results))
        
        return report_path
    
    def _generate_report_content(self, service_id: str, log_data: List[Dict], 
                               dlt_data: List[Dict], pcap_data: List[Dict], 
                               other_data: List[Dict], correlation_results: Dict,
                               anomaly_results: Dict) -> str:
        """Generate the actual report content."""
        
        report = []
        
        # Header
        report.append("=" * 80)
        report.append("DEBUG ASSISTANT - COMPREHENSIVE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Service ID: {service_id}")
        report.append("=" * 80)
        report.append("")
        
        # Executive Summary
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 40)
        report.append(self._generate_executive_summary(log_data, dlt_data, pcap_data, 
                                                     other_data, correlation_results, 
                                                     anomaly_results))
        report.append("")
        
        # Data Sources Overview
        report.append("DATA SOURCES OVERVIEW")
        report.append("-" * 40)
        report.append(self._generate_data_sources_overview(log_data, dlt_data, pcap_data, other_data))
        report.append("")
        
        # Log Analysis
        if log_data:
            report.append("LOG FILE ANALYSIS")
            report.append("-" * 40)
            report.append(self._analyze_log_data(log_data))
            report.append("")
        
        # DLT Analysis
        if dlt_data:
            report.append("DLT MESSAGE ANALYSIS")
            report.append("-" * 40)
            report.append(self._analyze_dlt_data(dlt_data))
            report.append("")
        
        # PCAP Analysis
        if pcap_data:
            report.append("SOME/IP NETWORK ANALYSIS")
            report.append("-" * 40)
            report.append(self._analyze_pcap_data(pcap_data))
            report.append("")
        
        # Correlation Analysis
        if correlation_results:
            report.append("EVENT CORRELATION ANALYSIS")
            report.append("-" * 40)
            report.append(self._generate_correlation_report(correlation_results))
            report.append("")
        
        # Anomaly Detection
        if anomaly_results:
            report.append("ANOMALY DETECTION RESULTS")
            report.append("-" * 40)
            report.append(self._generate_anomaly_report(anomaly_results))
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 40)
        report.append(self._generate_recommendations(log_data, dlt_data, pcap_data, 
                                                   other_data, correlation_results, 
                                                   anomaly_results))
        report.append("")
        
        # Technical Details
        report.append("TECHNICAL DETAILS")
        report.append("-" * 40)
        report.append(self._generate_technical_details(log_data, dlt_data, pcap_data, other_data))
        report.append("")
        
        return "\n".join(report)
    
    def _generate_executive_summary(self, log_data: List[Dict], dlt_data: List[Dict], 
                                  pcap_data: List[Dict], other_data: List[Dict],
                                  correlation_results: Dict, anomaly_results: Dict) -> str:
        """Generate executive summary."""
        summary = []
        
        total_events = len(log_data) + len(dlt_data) + len(pcap_data) + len(other_data)
        summary.append(f"• Total events analyzed: {total_events}")
        
        if correlation_results:
            correlations = correlation_results.get('statistics', {}).get('total_correlations', 0)
            summary.append(f"• Event correlations found: {correlations}")
        
        if anomaly_results:
            anomalies = anomaly_results.get('total_anomalies', 0)
            summary.append(f"• Anomalies detected: {anomalies}")
        
        # Data source breakdown
        sources = []
        if log_data:
            sources.append(f"Log files ({len(log_data)} entries)")
        if dlt_data:
            sources.append(f"DLT messages ({len(dlt_data)} entries)")
        if pcap_data:
            sources.append(f"SOME/IP packets ({len(pcap_data)} entries)")
        if other_data:
            sources.append(f"Other logs ({len(other_data)} entries)")
        
        summary.append(f"• Data sources: {', '.join(sources)}")
        
        # Overall health assessment
        if anomaly_results and anomaly_results.get('total_anomalies', 0) > 0:
            high_severity = anomaly_results.get('summary', {}).get('by_severity', {}).get('high', 0)
            if high_severity > 0:
                summary.append("• System health: ⚠️ ATTENTION REQUIRED (High severity issues detected)")
            else:
                summary.append("• System health: ⚡ MONITORING RECOMMENDED (Anomalies detected)")
        else:
            summary.append("• System health: ✅ NORMAL (No significant issues detected)")
        
        return "\n".join(summary)
    
    def _generate_data_sources_overview(self, log_data: List[Dict], dlt_data: List[Dict], 
                                      pcap_data: List[Dict], other_data: List[Dict]) -> str:
        """Generate data sources overview."""
        overview = []
        
        overview.append(f"Log Files:        {len(log_data):>6} entries")
        overview.append(f"DLT Messages:     {len(dlt_data):>6} entries")
        overview.append(f"SOME/IP Packets:  {len(pcap_data):>6} entries")
        overview.append(f"Other Logs:       {len(other_data):>6} entries")
        overview.append(f"{'':>20} ------")
        overview.append(f"Total:            {len(log_data) + len(dlt_data) + len(pcap_data) + len(other_data):>6} entries")
        
        return "\n".join(overview)
    
    def _analyze_log_data(self, log_data: List[Dict]) -> str:
        """Analyze log data and generate report section."""
        if not log_data:
            return "No log data available."
        
        analysis = []
        
        # Level distribution
        levels = {}
        components = {}
        
        for entry in log_data:
            level = entry.get('level', 'UNKNOWN')
            component = entry.get('component', 'UNKNOWN')
            
            levels[level] = levels.get(level, 0) + 1
            components[component] = components.get(component, 0) + 1
        
        analysis.append("Log Level Distribution:")
        for level, count in sorted(levels.items()):
            percentage = (count / len(log_data)) * 100
            analysis.append(f"  {level:>8}: {count:>4} ({percentage:>5.1f}%)")
        
        analysis.append("")
        analysis.append("Top Components:")
        sorted_components = sorted(components.items(), key=lambda x: x[1], reverse=True)[:5]
        for component, count in sorted_components:
            percentage = (count / len(log_data)) * 100
            analysis.append(f"  {component:>20}: {count:>4} ({percentage:>5.1f}%)")
        
        # Error analysis
        errors = [entry for entry in log_data if entry.get('level') == 'ERROR']
        if errors:
            analysis.append("")
            analysis.append(f"Error Analysis ({len(errors)} errors):")
            analysis.append("Recent errors:")
            for error in errors[-3:]:  # Show last 3 errors
                analysis.append(f"  • {error.get('timestamp', 'N/A')}: {error.get('full_message', 'N/A')[:80]}...")
        
        return "\n".join(analysis)
    
    def _analyze_dlt_data(self, dlt_data: List[Dict]) -> str:
        """Analyze DLT data and generate report section."""
        if not dlt_data:
            return "No DLT data available."
        
        analysis = []
        
        # App ID distribution
        app_ids = {}
        context_ids = {}
        log_levels = {}
        
        for entry in dlt_data:
            app_id = entry.get('app_id', 'UNKNOWN')
            context_id = entry.get('context_id', 'UNKNOWN')
            log_level = entry.get('log_level', 'UNKNOWN')
            
            app_ids[app_id] = app_ids.get(app_id, 0) + 1
            context_ids[context_id] = context_ids.get(context_id, 0) + 1
            log_levels[log_level] = log_levels.get(log_level, 0) + 1
        
        analysis.append("Application ID Distribution:")
        for app_id, count in sorted(app_ids.items()):
            percentage = (count / len(dlt_data)) * 100
            analysis.append(f"  {app_id:>8}: {count:>4} ({percentage:>5.1f}%)")
        
        analysis.append("")
        analysis.append("Context ID Distribution:")
        for context_id, count in sorted(context_ids.items()):
            percentage = (count / len(dlt_data)) * 100
            analysis.append(f"  {context_id:>8}: {count:>4} ({percentage:>5.1f}%)")
        
        analysis.append("")
        analysis.append("Log Level Distribution:")
        for level, count in sorted(log_levels.items()):
            percentage = (count / len(dlt_data)) * 100
            analysis.append(f"  {level:>8}: {count:>4} ({percentage:>5.1f}%)")
        
        return "\n".join(analysis)
    
    def _analyze_pcap_data(self, pcap_data: List[Dict]) -> str:
        """Analyze PCAP data and generate report section."""
        if not pcap_data:
            return "No SOME/IP data available."
        
        analysis = []
        
        # Protocol distribution
        protocols = {}
        method_ids = {}
        source_ips = {}
        
        for entry in pcap_data:
            protocol = entry.get('protocol', 'UNKNOWN')
            method_id = entry.get('method_id', 'UNKNOWN')
            source_ip = entry.get('source_ip', 'UNKNOWN')
            
            protocols[protocol] = protocols.get(protocol, 0) + 1
            method_ids[method_id] = method_ids.get(method_id, 0) + 1
            source_ips[source_ip] = source_ips.get(source_ip, 0) + 1
        
        analysis.append("Protocol Distribution:")
        for protocol, count in sorted(protocols.items()):
            percentage = (count / len(pcap_data)) * 100
            analysis.append(f"  {protocol:>12}: {count:>4} ({percentage:>5.1f}%)")
        
        analysis.append("")
        analysis.append("Top Method IDs:")
        sorted_methods = sorted(method_ids.items(), key=lambda x: x[1], reverse=True)[:5]
        for method_id, count in sorted_methods:
            percentage = (count / len(pcap_data)) * 100
            analysis.append(f"  {method_id:>12}: {count:>4} ({percentage:>5.1f}%)")
        
        analysis.append("")
        analysis.append("Top Source IPs:")
        sorted_ips = sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:5]
        for source_ip, count in sorted_ips:
            percentage = (count / len(pcap_data)) * 100
            analysis.append(f"  {source_ip:>15}: {count:>4} ({percentage:>5.1f}%)")
        
        return "\n".join(analysis)
    
    def _generate_correlation_report(self, correlation_results: Dict) -> str:
        """Generate correlation analysis report."""
        if not correlation_results:
            return "No correlation data available."
        
        stats = correlation_results.get('statistics', {})
        correlations = correlation_results.get('correlations', [])
        
        report = []
        
        report.append(f"Total correlations found: {stats.get('total_correlations', 0)}")
        report.append(f"Average events per correlation: {stats.get('avg_events_per_correlation', 0)}")
        report.append(f"Most active service: {stats.get('most_active_service', 'N/A')}")
        report.append(f"Time range: {stats.get('time_range', 'N/A')}")
        report.append(f"Correlation rate: {stats.get('correlation_rate', 0)}%")
        
        if correlations:
            report.append("")
            report.append("Top Correlations:")
            for i, correlation in enumerate(correlations[:3]):  # Show top 3
                report.append(f"  {i+1}. Correlation ID {correlation['id']}:")
                report.append(f"     Events: {len(correlation['events'])}")
                report.append(f"     Sources: {', '.join(correlation['sources'])}")
                report.append(f"     Services: {', '.join(correlation['service_ids'])}")
                report.append(f"     Time span: {correlation['time_span_ms']:.1f}ms")
                report.append(f"     Strength: {correlation['correlation_strength']:.2f}")
        
        return "\n".join(report)
    
    def _generate_anomaly_report(self, anomaly_results: Dict) -> str:
        """Generate anomaly detection report."""
        if not anomaly_results:
            return "No anomaly data available."
        
        summary = anomaly_results.get('summary', {})
        anomalies = anomaly_results.get('anomalies', [])
        
        report = []
        
        report.append(f"Total anomalies detected: {summary.get('total_anomalies', 0)}")
        
        by_severity = summary.get('by_severity', {})
        report.append(f"By severity: High={by_severity.get('high', 0)}, Medium={by_severity.get('medium', 0)}, Low={by_severity.get('low', 0)}")
        
        by_type = summary.get('by_type', {})
        if by_type:
            report.append("By type:")
            for anomaly_type, count in by_type.items():
                report.append(f"  {anomaly_type}: {count}")
        
        recommendations = summary.get('recommendations', [])
        if recommendations:
            report.append("")
            report.append("Recommendations:")
            for rec in recommendations:
                report.append(f"  • {rec}")
        
        # Show some example anomalies
        if anomalies:
            report.append("")
            report.append("Example Anomalies:")
            for anomaly in anomalies[:5]:  # Show first 5
                report.append(f"  • [{anomaly['severity'].upper()}] {anomaly['description']}")
        
        return "\n".join(report)
    
    def _generate_recommendations(self, log_data: List[Dict], dlt_data: List[Dict], 
                                pcap_data: List[Dict], other_data: List[Dict],
                                correlation_results: Dict, anomaly_results: Dict) -> str:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Data quality recommendations
        total_events = len(log_data) + len(dlt_data) + len(pcap_data) + len(other_data)
        if total_events < 10:
            recommendations.append("• Increase data collection period for more comprehensive analysis")
        
        # Error rate recommendations
        if log_data:
            error_count = len([e for e in log_data if e.get('level') == 'ERROR'])
            error_rate = (error_count / len(log_data)) * 100
            if error_rate > 10:
                recommendations.append(f"• High error rate ({error_rate:.1f}%) - investigate root causes")
            elif error_rate > 5:
                recommendations.append(f"• Moderate error rate ({error_rate:.1f}%) - monitor trends")
        
        # Correlation recommendations
        if correlation_results:
            correlation_rate = correlation_results.get('statistics', {}).get('correlation_rate', 0)
            if correlation_rate < 20:
                recommendations.append("• Low event correlation - consider adjusting time windows or correlation criteria")
        
        # Anomaly recommendations
        if anomaly_results:
            high_severity = anomaly_results.get('summary', {}).get('by_severity', {}).get('high', 0)
            if high_severity > 0:
                recommendations.append("• Address high-severity anomalies immediately")
        
        # General recommendations
        recommendations.extend([
            "• Set up automated monitoring for detected patterns",
            "• Consider implementing alerting for anomaly detection",
            "• Regular analysis recommended for trend identification",
            "• Archive analysis results for historical comparison"
        ])
        
        return "\n".join(recommendations)
    
    def _generate_technical_details(self, log_data: List[Dict], dlt_data: List[Dict], 
                                  pcap_data: List[Dict], other_data: List[Dict]) -> str:
        """Generate technical details section."""
        details = []
        
        details.append("Analysis Parameters:")
        details.append(f"  • Log entries processed: {len(log_data)}")
        details.append(f"  • DLT messages processed: {len(dlt_data)}")
        details.append(f"  • SOME/IP packets processed: {len(pcap_data)}")
        details.append(f"  • Other log entries processed: {len(other_data)}")
        
        details.append("")
        details.append("Processing Information:")
        details.append(f"  • Analysis timestamp: {datetime.now().isoformat()}")
        details.append(f"  • Report format: Text")
        details.append(f"  • Data sources: Multiple")
        
        return "\n".join(details)
    
    def generate_json_report(self, service_id: str, log_data: List[Dict], 
                           dlt_data: List[Dict], pcap_data: List[Dict], 
                           other_data: List[Dict], correlation_results: Dict,
                           anomaly_results: Dict) -> str:
        """Generate a JSON format report."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"debug_report_{service_id}_{timestamp}.json"
        report_path = os.path.join(self.output_dir, report_filename)
        
        report_data = {
            'metadata': {
                'service_id': service_id,
                'generated_at': datetime.now().isoformat(),
                'report_type': 'comprehensive_analysis'
            },
            'data_summary': {
                'log_entries': len(log_data),
                'dlt_messages': len(dlt_data),
                'pcap_packets': len(pcap_data),
                'other_entries': len(other_data),
                'total_events': len(log_data) + len(dlt_data) + len(pcap_data) + len(other_data)
            },
            'correlation_results': correlation_results,
            'anomaly_results': anomaly_results,
            'raw_data': {
                'log_data': log_data[:100],  # Limit for file size
                'dlt_data': dlt_data[:100],
                'pcap_data': pcap_data[:100],
                'other_data': other_data[:100]
            }
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return report_path

