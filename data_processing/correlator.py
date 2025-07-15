"""
Data correlation module for the Debug Assistant application.
Correlates events across different data sources based on timestamps and service IDs.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import re

from utils.helpers import TimestampParser


class EventCorrelator:
    """Correlates events across different data sources."""
    
    def __init__(self, time_window_ms: int = 1000):
        self.time_window_ms = time_window_ms
        self.correlation_results = {}
    
    def correlate_events(self, log_data: List[Dict], dlt_data: List[Dict], 
                        pcap_data: List[Dict], other_data: List[Dict]) -> Dict[str, Any]:
        """Correlate events across all data sources."""
        
        # Normalize timestamps for all data sources
        normalized_log = self._normalize_timestamps(log_data, 'log')
        normalized_dlt = self._normalize_timestamps(dlt_data, 'dlt')
        normalized_pcap = self._normalize_timestamps(pcap_data, 'pcap')
        normalized_other = self._normalize_timestamps(other_data, 'other')
        
        # Combine all events
        all_events = normalized_log + normalized_dlt + normalized_pcap + normalized_other
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x['parsed_timestamp'] or datetime.min)
        
        # Find correlations
        correlations = self._find_correlations(all_events)
        
        # Generate correlation statistics
        stats = self._generate_correlation_stats(correlations, all_events)
        
        return {
            'correlations': correlations,
            'statistics': stats,
            'timeline': all_events,
            'total_events': len(all_events)
        }
    
    def _normalize_timestamps(self, data: List[Dict], source: str) -> List[Dict]:
        """Normalize timestamps and add source information."""
        normalized = []
        
        for item in data:
            timestamp_str = item.get('timestamp', '')
            parsed_time = TimestampParser.parse_timestamp(timestamp_str)
            
            normalized_item = item.copy()
            normalized_item.update({
                'source': source,
                'parsed_timestamp': parsed_time,
                'timestamp_str': timestamp_str
            })
            
            normalized.append(normalized_item)
        
        return normalized
    
    def _find_correlations(self, events: List[Dict]) -> List[Dict]:
        """Find correlated events within the time window."""
        correlations = []
        
        for i, event in enumerate(events):
            if not event['parsed_timestamp']:
                continue
            
            correlated_events = [event]
            
            # Look for events within the time window
            for j, other_event in enumerate(events[i+1:], i+1):
                if not other_event['parsed_timestamp']:
                    continue
                
                time_diff = abs((other_event['parsed_timestamp'] - event['parsed_timestamp']).total_seconds() * 1000)
                
                if time_diff <= self.time_window_ms:
                    # Check if they're related (same service_id or similar content)
                    if self._are_events_related(event, other_event):
                        correlated_events.append(other_event)
                else:
                    break  # Events are sorted, so no need to check further
            
            if len(correlated_events) > 1:
                correlation = {
                    'id': len(correlations) + 1,
                    'events': correlated_events,
                    'time_span_ms': self._calculate_time_span(correlated_events),
                    'sources': list(set(e['source'] for e in correlated_events)),
                    'service_ids': list(set(e.get('service_id', 'N/A') for e in correlated_events if e.get('service_id'))),
                    'correlation_strength': self._calculate_correlation_strength(correlated_events)
                }
                correlations.append(correlation)
        
        return correlations
    
    def _are_events_related(self, event1: Dict, event2: Dict) -> bool:
        """Check if two events are related."""
        # Same service ID
        if event1.get('service_id') and event2.get('service_id'):
            if event1['service_id'] == event2['service_id']:
                return True
        
        # Similar message content
        msg1 = event1.get('full_message', '').lower()
        msg2 = event2.get('full_message', '').lower()
        
        if msg1 and msg2:
            # Check for common keywords
            keywords1 = set(re.findall(r'\b\w+\b', msg1))
            keywords2 = set(re.findall(r'\b\w+\b', msg2))
            
            common_keywords = keywords1.intersection(keywords2)
            if len(common_keywords) >= 2:  # At least 2 common words
                return True
        
        # Same component or context
        if event1.get('component') and event2.get('component'):
            if event1['component'] == event2['component']:
                return True
        
        if event1.get('app_id') and event2.get('app_id'):
            if event1['app_id'] == event2['app_id']:
                return True
        
        return False
    
    def _calculate_time_span(self, events: List[Dict]) -> float:
        """Calculate time span of correlated events in milliseconds."""
        timestamps = [e['parsed_timestamp'] for e in events if e['parsed_timestamp']]
        if len(timestamps) < 2:
            return 0.0
        
        min_time = min(timestamps)
        max_time = max(timestamps)
        return (max_time - min_time).total_seconds() * 1000
    
    def _calculate_correlation_strength(self, events: List[Dict]) -> float:
        """Calculate correlation strength (0.0 to 1.0)."""
        if len(events) < 2:
            return 0.0
        
        strength = 0.0
        
        # More events = higher strength
        strength += min(len(events) / 5.0, 0.4)
        
        # Multiple sources = higher strength
        sources = set(e['source'] for e in events)
        strength += min(len(sources) / 4.0, 0.3)
        
        # Same service IDs = higher strength
        service_ids = [e.get('service_id') for e in events if e.get('service_id')]
        if service_ids and len(set(service_ids)) == 1:
            strength += 0.3
        
        return min(strength, 1.0)
    
    def _generate_correlation_stats(self, correlations: List[Dict], all_events: List[Dict]) -> Dict:
        """Generate correlation statistics."""
        if not correlations:
            return {
                'total_correlations': 0,
                'avg_events_per_correlation': 0,
                'most_active_service': 'N/A',
                'time_range': 'N/A',
                'sources_involved': []
            }
        
        # Calculate statistics
        total_correlations = len(correlations)
        total_correlated_events = sum(len(c['events']) for c in correlations)
        avg_events_per_correlation = total_correlated_events / total_correlations if total_correlations > 0 else 0
        
        # Find most active service
        service_counts = {}
        for correlation in correlations:
            for service_id in correlation['service_ids']:
                service_counts[service_id] = service_counts.get(service_id, 0) + 1
        
        most_active_service = max(service_counts.items(), key=lambda x: x[1])[0] if service_counts else 'N/A'
        
        # Calculate time range
        timestamps = [e['parsed_timestamp'] for e in all_events if e['parsed_timestamp']]
        if timestamps:
            min_time = min(timestamps)
            max_time = max(timestamps)
            time_range = f"{TimestampParser.format_timestamp(min_time)} - {TimestampParser.format_timestamp(max_time)}"
        else:
            time_range = 'N/A'
        
        # Sources involved
        sources_involved = list(set(e['source'] for e in all_events))
        
        return {
            'total_correlations': total_correlations,
            'avg_events_per_correlation': round(avg_events_per_correlation, 2),
            'most_active_service': most_active_service,
            'time_range': time_range,
            'sources_involved': sources_involved,
            'total_events': len(all_events),
            'correlated_events': total_correlated_events,
            'correlation_rate': round((total_correlated_events / len(all_events)) * 100, 2) if all_events else 0
        }
    
    def generate_timeline_data(self, correlations: List[Dict]) -> List[Dict]:
        """Generate timeline data for visualization."""
        timeline_data = []
        
        for i, correlation in enumerate(correlations):
            for j, event in enumerate(correlation['events']):
                if event['parsed_timestamp']:
                    timeline_data.append({
                        'x': event['parsed_timestamp'].isoformat(),
                        'y': i,
                        'text': f"{event['source']}: {event.get('service_id', 'N/A')}",
                        'hovertext': event.get('full_message', '')[:100] + '...',
                        'source': event['source'],
                        'service_id': event.get('service_id', 'N/A'),
                        'correlation_id': correlation['id']
                    })
        
        return timeline_data

