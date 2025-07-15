"""
Anomaly detection module for the Debug Assistant application.
Detects unusual patterns in log data and service behavior.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter, defaultdict
import re


class AnomalyDetector:
    """Detects anomalies in log data and service behavior."""
    
    def __init__(self):
        self.anomalies = []
        self.thresholds = {
            'error_rate': 0.1,  # 10% error rate threshold
            'message_frequency': 100,  # Messages per minute threshold
            'service_silence': 300,  # Seconds of silence threshold
            'duplicate_messages': 10  # Duplicate message threshold
        }
    
    def detect_anomalies(self, log_data: List[Dict], dlt_data: List[Dict], 
                        pcap_data: List[Dict], other_data: List[Dict]) -> Dict[str, Any]:
        """Detect anomalies across all data sources."""
        
        self.anomalies = []
        
        # Combine all data
        all_data = {
            'log': log_data,
            'dlt': dlt_data,
            'pcap': pcap_data,
            'other': other_data
        }
        
        # Run different anomaly detection algorithms
        self._detect_error_spikes(all_data)
        self._detect_message_frequency_anomalies(all_data)
        self._detect_service_silence(all_data)
        self._detect_duplicate_messages(all_data)
        self._detect_unusual_patterns(all_data)
        
        # Generate summary
        summary = self._generate_anomaly_summary()
        
        return {
            'anomalies': self.anomalies,
            'summary': summary,
            'total_anomalies': len(self.anomalies)
        }
    
    def _detect_error_spikes(self, all_data: Dict[str, List[Dict]]):
        """Detect spikes in error messages."""
        for source, data in all_data.items():
            if not data:
                continue
            
            # Count errors by time window (1-minute windows)
            error_counts = defaultdict(int)
            total_counts = defaultdict(int)
            
            for item in data:
                level = item.get('level') or item.get('log_level', 'INFO')
                timestamp_str = item.get('timestamp', '')
                
                # Extract minute from timestamp
                try:
                    # Simple minute extraction (assumes HH:MM:SS format)
                    minute_key = timestamp_str[:5] if len(timestamp_str) >= 5 else 'unknown'
                    
                    total_counts[minute_key] += 1
                    if level in ['ERROR', 'FATAL']:
                        error_counts[minute_key] += 1
                except:
                    continue
            
            # Check for error rate spikes
            for minute, total in total_counts.items():
                if total > 0:
                    error_rate = error_counts[minute] / total
                    if error_rate > self.thresholds['error_rate']:
                        self.anomalies.append({
                            'type': 'error_spike',
                            'severity': 'high' if error_rate > 0.3 else 'medium',
                            'source': source,
                            'time_window': minute,
                            'error_rate': round(error_rate * 100, 2),
                            'error_count': error_counts[minute],
                            'total_count': total,
                            'description': f'High error rate ({error_rate*100:.1f}%) detected in {source} at {minute}'
                        })
    
    def _detect_message_frequency_anomalies(self, all_data: Dict[str, List[Dict]]):
        """Detect unusual message frequency patterns."""
        for source, data in all_data.items():
            if not data:
                continue
            
            # Count messages by service and time
            service_counts = defaultdict(lambda: defaultdict(int))
            
            for item in data:
                service_id = item.get('service_id', 'unknown')
                timestamp_str = item.get('timestamp', '')
                
                # Extract minute from timestamp
                try:
                    minute_key = timestamp_str[:5] if len(timestamp_str) >= 5 else 'unknown'
                    service_counts[service_id][minute_key] += 1
                except:
                    continue
            
            # Check for frequency anomalies
            for service_id, time_counts in service_counts.items():
                counts = list(time_counts.values())
                if len(counts) > 1:
                    avg_count = sum(counts) / len(counts)
                    max_count = max(counts)
                    
                    # Detect spikes (more than 3x average)
                    if max_count > avg_count * 3 and max_count > 20:
                        max_time = max(time_counts.items(), key=lambda x: x[1])[0]
                        self.anomalies.append({
                            'type': 'frequency_spike',
                            'severity': 'medium',
                            'source': source,
                            'service_id': service_id,
                            'time_window': max_time,
                            'message_count': max_count,
                            'average_count': round(avg_count, 2),
                            'description': f'Message frequency spike for {service_id} in {source}: {max_count} messages (avg: {avg_count:.1f})'
                        })
    
    def _detect_service_silence(self, all_data: Dict[str, List[Dict]]):
        """Detect services that have gone silent."""
        # This is a simplified implementation
        # In a real system, you'd track historical patterns
        
        for source, data in all_data.items():
            if not data:
                continue
            
            # Group by service
            service_data = defaultdict(list)
            for item in data:
                service_id = item.get('service_id')
                if service_id:
                    service_data[service_id].append(item)
            
            # Check for services with very few messages
            for service_id, messages in service_data.items():
                if len(messages) < 3:  # Very few messages might indicate silence
                    self.anomalies.append({
                        'type': 'service_silence',
                        'severity': 'low',
                        'source': source,
                        'service_id': service_id,
                        'message_count': len(messages),
                        'description': f'Service {service_id} in {source} has very few messages ({len(messages)})'
                    })
    
    def _detect_duplicate_messages(self, all_data: Dict[str, List[Dict]]):
        """Detect duplicate or repeated messages."""
        for source, data in all_data.items():
            if not data:
                continue
            
            # Count identical messages
            message_counts = Counter()
            
            for item in data:
                # Use a simplified message signature
                message = item.get('full_message', '')
                if message:
                    # Remove timestamps and variable parts for comparison
                    normalized_msg = re.sub(r'\d{2}:\d{2}:\d{2}', 'TIME', message)
                    normalized_msg = re.sub(r'\[\d+\]', '[NUM]', normalized_msg)
                    message_counts[normalized_msg] += 1
            
            # Check for excessive duplicates
            for message, count in message_counts.items():
                if count > self.thresholds['duplicate_messages']:
                    self.anomalies.append({
                        'type': 'duplicate_messages',
                        'severity': 'low' if count < 20 else 'medium',
                        'source': source,
                        'message_pattern': message[:100] + '...' if len(message) > 100 else message,
                        'count': count,
                        'description': f'Duplicate message pattern repeated {count} times in {source}'
                    })
    
    def _detect_unusual_patterns(self, all_data: Dict[str, List[Dict]]):
        """Detect unusual patterns in messages."""
        suspicious_patterns = [
            (r'failed|failure|error|exception', 'error_pattern'),
            (r'timeout|timed out', 'timeout_pattern'),
            (r'connection.*lost|disconnected', 'connection_issue'),
            (r'memory|out of memory|oom', 'memory_issue'),
            (r'crash|crashed|segfault', 'crash_pattern')
        ]
        
        for source, data in all_data.items():
            if not data:
                continue
            
            pattern_counts = defaultdict(int)
            
            for item in data:
                message = item.get('full_message', '').lower()
                
                for pattern, pattern_type in suspicious_patterns:
                    if re.search(pattern, message):
                        pattern_counts[pattern_type] += 1
            
            # Report patterns that appear frequently
            for pattern_type, count in pattern_counts.items():
                if count > 5:  # Threshold for suspicious patterns
                    self.anomalies.append({
                        'type': 'suspicious_pattern',
                        'severity': 'medium' if count > 10 else 'low',
                        'source': source,
                        'pattern_type': pattern_type,
                        'count': count,
                        'description': f'Suspicious pattern "{pattern_type}" found {count} times in {source}'
                    })
    
    def _generate_anomaly_summary(self) -> Dict[str, Any]:
        """Generate summary of detected anomalies."""
        if not self.anomalies:
            return {
                'total_anomalies': 0,
                'by_severity': {'high': 0, 'medium': 0, 'low': 0},
                'by_type': {},
                'by_source': {},
                'recommendations': ['No anomalies detected. System appears to be operating normally.']
            }
        
        # Count by severity
        severity_counts = Counter(a['severity'] for a in self.anomalies)
        
        # Count by type
        type_counts = Counter(a['type'] for a in self.anomalies)
        
        # Count by source
        source_counts = Counter(a['source'] for a in self.anomalies)
        
        # Generate recommendations
        recommendations = []
        
        if severity_counts['high'] > 0:
            recommendations.append('⚠️ High severity anomalies detected - immediate attention required')
        
        if type_counts['error_spike'] > 0:
            recommendations.append('🔍 Investigate error spikes - check system logs and service health')
        
        if type_counts['frequency_spike'] > 0:
            recommendations.append('📊 Monitor message frequency patterns - possible performance issues')
        
        if type_counts['service_silence'] > 0:
            recommendations.append('🔇 Check silent services - they may have stopped or crashed')
        
        if not recommendations:
            recommendations.append('✅ Minor anomalies detected - monitor for trends')
        
        return {
            'total_anomalies': len(self.anomalies),
            'by_severity': dict(severity_counts),
            'by_type': dict(type_counts),
            'by_source': dict(source_counts),
            'recommendations': recommendations
        }
    
    def get_anomaly_report(self) -> str:
        """Generate a formatted anomaly report."""
        if not self.anomalies:
            return "No anomalies detected."
        
        report = f"ANOMALY DETECTION REPORT\n"
        report += f"========================\n\n"
        report += f"Total anomalies detected: {len(self.anomalies)}\n\n"
        
        # Group by severity
        by_severity = defaultdict(list)
        for anomaly in self.anomalies:
            by_severity[anomaly['severity']].append(anomaly)
        
        for severity in ['high', 'medium', 'low']:
            if severity in by_severity:
                report += f"{severity.upper()} SEVERITY ({len(by_severity[severity])} items):\n"
                report += "-" * 40 + "\n"
                
                for anomaly in by_severity[severity]:
                    report += f"• {anomaly['description']}\n"
                
                report += "\n"
        
        return report

