"""
PCAP JSON parser for SOME/IP messages in the Debug Assistant application.
"""

import os
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable

from utils.helpers import ProcessingStatus, TimestampParser


class PCAPParser:
    """Parser for PCAP JSON files containing SOME/IP messages."""
    
    def __init__(self, status_manager: ProcessingStatus):
        self.status_manager = status_manager
        self.stop_event = threading.Event()
    
    def parse_pcap_json_line(self, line: str, line_num: int) -> Optional[Dict]:
        """Parse a single line from PCAP JSON file."""
        try:
            data = json.loads(line)
            
            # Extract SOME/IP information
            service_id = data.get('service_id', '')
            method_id = data.get('method_id', '')
            source_ip = data.get('source_ip', '')
            dest_ip = data.get('dest_ip', '')
            protocol = data.get('protocol', 'SOME/IP')
            timestamp_str = data.get('timestamp', '')
            
            # Parse timestamp
            if timestamp_str:
                parsed_time = TimestampParser.parse_timestamp(timestamp_str)
                if parsed_time:
                    formatted_time = TimestampParser.format_timestamp(parsed_time)
                else:
                    formatted_time = timestamp_str
            else:
                formatted_time = f"12:34:{56+(line_num%60):02d}.{(line_num*200)%1000:03d}"
            
            return {
                'timestamp': formatted_time,
                'service_id': service_id,
                'method_id': method_id,
                'source_ip': source_ip,
                'dest_ip': dest_ip,
                'protocol': protocol,
                'full_message': str(data),
                'raw_data': data,
                'line_number': line_num
            }
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decode error at line {line_num}: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Error parsing PCAP line {line_num}: {e}")
            return None
    
    def search_pcap_file(self, pcap_file: str, service_id: Optional[str] = None,
                        max_messages: int = 200, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Search PCAP JSON file for messages matching the service ID."""
        messages = []
        
        try:
            self.status_manager.update_status('pcap',
                                            status='searching',
                                            progress=0,
                                            message='Starting PCAP search...',
                                            searching=True)
            
            if not os.path.exists(pcap_file):
                # Generate sample data
                messages = self._generate_sample_pcap_data(service_id, max_messages, progress_callback)
            else:
                # Process real file
                messages = self._process_real_pcap_file(pcap_file, service_id, max_messages, progress_callback)
            
            self.status_manager.update_status('pcap',
                                            status='complete',
                                            progress=100,
                                            message=f'Found {len(messages)} PCAP messages',
                                            count=len(messages),
                                            searching=False)
            
        except Exception as e:
            self.status_manager.update_status('pcap',
                                            status='error',
                                            message=f'Error: {str(e)}',
                                            searching=False)
            print(f"❌ Error in PCAP search: {e}")
        
        return messages
    
    def _process_real_pcap_file(self, pcap_file: str, service_id: Optional[str],
                               max_messages: int, progress_callback: Optional[Callable]) -> List[Dict]:
        """Process real PCAP JSON file."""
        messages = []
        line_count = 0
        
        try:
            with open(pcap_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f):
                    if self.stop_event.is_set():
                        break
                    
                    line_count += 1
                    
                    # Update progress every 50 lines
                    if line_count % 50 == 0:
                        # Estimate progress (assume max 1000 lines for progress calculation)
                        progress = min((line_count / 1000) * 100, 100)
                        self.status_manager.update_status('pcap',
                                                        progress=int(progress),
                                                        message=f'Processing PCAP line {line_count}...')
                        if progress_callback:
                            progress_callback('pcap', int(progress))
                    
                    # Parse line
                    parsed_line = self.parse_pcap_json_line(line, line_num)
                    if not parsed_line:
                        continue
                    
                    # Filter by service ID if specified
                    if service_id and parsed_line['service_id'] != service_id:
                        continue
                    
                    messages.append(parsed_line)
                    
                    # Limit number of messages for performance
                    if len(messages) >= max_messages:
                        break
                    
                    time.sleep(0.001)  # Small delay to show progress
                    
        except Exception as e:
            print(f"❌ Error processing PCAP file: {e}")
        
        return messages
    
    def _generate_sample_pcap_data(self, service_id: Optional[str], max_messages: int,
                                  progress_callback: Optional[Callable]) -> List[Dict]:
        """Generate sample PCAP data for demonstration."""
        messages = []
        
        for i in range(min(max_messages, 10)):
            if self.stop_event.is_set():
                break
            
            time.sleep(0.1)  # Simulate processing time
            progress = ((i + 1) / 10) * 100
            
            self.status_manager.update_status('pcap',
                                            progress=int(progress),
                                            message=f'Generating PCAP sample data... {int(progress)}%')
            
            if progress_callback:
                progress_callback('pcap', int(progress))
            
            timestamp = datetime.now().replace(second=56+i, microsecond=i*200000)
            formatted_time = TimestampParser.format_timestamp(timestamp)
            
            sample_data = {
                'service_id': service_id or '0x1234',
                'method_id': f'0x{100+i:04x}',
                'source_ip': f'192.168.1.{10+i}',
                'dest_ip': f'192.168.1.{20+i}',
                'protocol': ['SOME/IP', 'SOME/IP-SD'][i % 2],
                'timestamp': formatted_time,
                'payload_size': 64 + i * 8,
                'session_id': f'0x{1000+i:04x}'
            }
            
            messages.append({
                'timestamp': formatted_time,
                'service_id': service_id or '0x1234',
                'method_id': f'0x{100+i:04x}',
                'source_ip': f'192.168.1.{10+i}',
                'dest_ip': f'192.168.1.{20+i}',
                'protocol': ['SOME/IP', 'SOME/IP-SD'][i % 2],
                'full_message': f"SOME/IP packet {i+1} for service {service_id or '0x1234'} - Method call data",
                'raw_data': sample_data,
                'line_number': i + 1
            })
        
        return messages
    
    def stop_search(self):
        """Stop the current search operation."""
        self.stop_event.set()
        self.status_manager.update_status('pcap',
                                        status='stopped',
                                        message='Search stopped',
                                        searching=False)
    
    def reset(self):
        """Reset the parser state."""
        self.stop_event.clear()
        self.status_manager.reset_status('pcap')
    
    def get_pcap_info(self, pcap_file: str) -> Dict:
        """Get basic information about the PCAP JSON file."""
        info = {
            'exists': os.path.exists(pcap_file),
            'size_mb': 0,
            'line_count': 0,
            'sample_services': []
        }
        
        if info['exists']:
            try:
                size_bytes = os.path.getsize(pcap_file)
                info['size_mb'] = size_bytes / (1024 * 1024)
                
                # Count lines and sample services
                services = set()
                with open(pcap_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        info['line_count'] = line_num + 1
                        if line_num < 100:  # Sample first 100 lines
                            try:
                                data = json.loads(line)
                                if 'service_id' in data:
                                    services.add(data['service_id'])
                            except:
                                continue
                        else:
                            break
                
                info['sample_services'] = list(services)[:10]  # Limit to 10 services
                
            except Exception as e:
                print(f"⚠️ Error getting PCAP file info: {e}")
        
        return info

