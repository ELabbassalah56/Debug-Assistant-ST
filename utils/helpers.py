"""
Helper utilities for the Debug Assistant application.
"""

import re
import os
import threading
from datetime import datetime
from typing import Dict, List, Set, Optional, Any


class ServiceDiscovery:
    """Service discovery utility for finding ServiceIds in various data sources."""
    
    def __init__(self):
        self.discovered_services: Set[str] = set()
    
    def discover_from_log(self, log_file: str, line_limit: int = 200000) -> Set[str]:
        """Discover services from log file."""
        services = set()
        try:
            if not os.path.exists(log_file):
                return services
                
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i > line_limit:
                        break
                    service_match = re.search(r'ServiceId:\s*(0x[0-9a-fA-F]+)', line)
                    if service_match:
                        services.add(service_match.group(1))
        except Exception as e:
            print(f"⚠️ Error discovering services from log: {e}")
        
        return services
    
    def discover_from_dlt(self, dlt_file: str, byte_limit: int = 10000) -> Set[str]:
        """Discover services from DLT file."""
        services = set()
        try:
            if not os.path.exists(dlt_file):
                return services
                
            with open(dlt_file, 'rb') as f:
                content = f.read(byte_limit)
                text_content = content.decode('utf-8', errors='ignore')
                service_matches = re.findall(r'0x[0-9a-fA-F]{4}', text_content)
                for match in service_matches[:10]:  # Limit results
                    services.add(match)
        except Exception as e:
            print(f"⚠️ Error discovering services from DLT: {e}")
        
        return services
    
    def discover_from_pcap_json(self, pcap_file: str, line_limit: int = 100) -> Set[str]:
        """Discover services from PCAP JSON file."""
        services = set()
        try:
            if not os.path.exists(pcap_file):
                return services
                
            with open(pcap_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i > line_limit:
                        break
                    try:
                        import json
                        data = json.loads(line)
                        if 'service_id' in data:
                            services.add(data['service_id'])
                        # Look for service patterns in the data
                        line_str = str(data)
                        service_matches = re.findall(r'0x[0-9a-fA-F]{4}', line_str)
                        for match in service_matches[:5]:
                            services.add(match)
                    except:
                        continue
        except Exception as e:
            print(f"⚠️ Error discovering services from PCAP: {e}")
        
        return services
    
    def discover_all(self, data_files: Dict[str, str]) -> Set[str]:
        """Discover services from all data sources."""
        all_services = set()
        
        # Discover from each source
        all_services.update(self.discover_from_log(data_files.get('log_file', '')))
        all_services.update(self.discover_from_dlt(data_files.get('dlt_file', '')))
        all_services.update(self.discover_from_pcap_json(data_files.get('pcap_json_file', '')))
        
        self.discovered_services = all_services
        return all_services


class ProcessingStatus:
    """Thread-safe processing status manager."""
    
    def __init__(self):
        self._status = {
            'log': {'status': 'ready', 'progress': 0, 'message': 'Ready', 'count': 0, 'searching': False},
            'dlt': {'status': 'ready', 'progress': 0, 'message': 'Ready', 'count': 0, 'searching': False},
            'pcap': {'status': 'ready', 'progress': 0, 'message': 'Ready', 'count': 0, 'searching': False},
            'other': {'status': 'ready', 'progress': 0, 'message': 'Ready', 'count': 0, 'searching': False}
        }
        self._lock = threading.Lock()
    
    def get_status(self, source: str) -> Dict[str, Any]:
        """Get status for a specific source."""
        with self._lock:
            return self._status.get(source, {}).copy()
    
    def update_status(self, source: str, **kwargs) -> None:
        """Update status for a specific source."""
        with self._lock:
            if source in self._status:
                self._status[source].update(kwargs)
    
    def reset_status(self, source: str) -> None:
        """Reset status for a specific source."""
        with self._lock:
            if source in self._status:
                self._status[source] = {
                    'status': 'ready', 
                    'progress': 0, 
                    'message': 'Ready', 
                    'count': 0, 
                    'searching': False
                }
    
    def reset_all(self) -> None:
        """Reset all statuses."""
        with self._lock:
            for source in self._status:
                self.reset_status(source)


class TimestampParser:
    """Utility for parsing and formatting timestamps."""
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        try:
            # Try different timestamp formats
            formats = [
                '%Y-%m-%d %H:%M:%S.%f',
                '%H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
            
            # Try parsing as Unix timestamp
            try:
                ts_int = int(timestamp_str)
                return datetime.fromtimestamp(ts_int / 1000000)  # Assume microseconds
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Error parsing timestamp '{timestamp_str}': {e}")
        
        return None
    
    @staticmethod
    def format_timestamp(dt: datetime, format_str: str = '%H:%M:%S.%f') -> str:
        """Format datetime object to string."""
        try:
            formatted = dt.strftime(format_str)
            if format_str.endswith('.%f'):
                return formatted[:-3]  # Remove last 3 digits from microseconds
            return formatted
        except Exception as e:
            print(f"⚠️ Error formatting timestamp: {e}")
            return str(dt)


def check_data_files(data_files: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """Check if data files exist and provide status information."""
    file_status = {}
    
    for file_type, file_path in data_files.items():
        exists = os.path.exists(file_path)
        size_mb = 0
        
        if exists:
            try:
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
            except:
                size_mb = 0
        
        file_status[file_type] = {
            'path': file_path,
            'exists': exists,
            'size_mb': size_mb
        }
    
    return file_status


def create_sample_data_files(data_dir: str) -> None:
    """Create sample data files for demonstration."""
    os.makedirs(data_dir, exist_ok=True)
    
    # Create sample log file
    log_file = os.path.join(data_dir, 'adaptive.log')
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            for i in range(50):
                timestamp = 1234567890000000 + i * 1000000
                service_id = f"0x{1234 + (i % 4):04X}"
                level = ['INFO', 'WARN', 'ERROR', 'DEBUG'][i % 4]
                f.write(f"[{timestamp}][{level}] ServiceManager ServiceId: {service_id} Sample log message {i+1}\n")
    
    print(f"✅ Sample data files created in {data_dir}")

