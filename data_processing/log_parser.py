"""
Log file parser for the Debug Assistant application.
"""

import os
import re
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable

from utils.helpers import ProcessingStatus, TimestampParser


class LogParser:
    """Parser for log files with ServiceId information."""
    
    def __init__(self, status_manager: ProcessingStatus):
        self.status_manager = status_manager
        self.stop_event = threading.Event()
    
    def parse_log_line(self, line: str, line_num: int) -> Optional[Dict]:
        """Parse a single log line and extract relevant information."""
        line = line.strip()
        if not line:
            return None
        
        # Extract ServiceId
        service_match = re.search(r'ServiceId:\s*(0x[0-9a-fA-F]+)', line)
        service_id = service_match.group(1) if service_match else None
        
        if not service_id:
            return None
        
        # Extract timestamp
        timestamp_match = re.search(r'\[(\d+)\]', line)
        timestamp = timestamp_match.group(1) if timestamp_match else str(line_num)
        
        # Extract log level
        level_match = re.search(r'\]\[([A-Z]+)\]\s', line)
        level = level_match.group(1) if level_match else 'INFO'
        
        # Extract component
        component_match = re.search(r'\]([^[]+)\]\[', line)
        component = component_match.group(1) if component_match else 'Unknown'
        
        # Format timestamp
        try:
            ts_int = int(timestamp)
            dt = datetime.fromtimestamp(ts_int / 1000000)
            formatted_time = TimestampParser.format_timestamp(dt)
        except:
            formatted_time = timestamp
        
        return {
            'timestamp': formatted_time,
            'service_id': service_id,
            'level': level,
            'component': component.strip(),
            'full_message': line,
            'raw_timestamp': timestamp,
            'line_number': line_num
        }
    
    def search_log_file(self, log_file: str, service_id: Optional[str] = None, 
                       max_messages: int = 20000, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Search log file for messages matching the service ID."""
        messages = []
        
        try:
            self.status_manager.update_status('log', 
                                            status='searching', 
                                            progress=0, 
                                            message='Starting log search...',
                                            searching=True)
            
            if not os.path.exists(log_file):
                # Generate sample data
                messages = self._generate_sample_log_data(service_id, max_messages, progress_callback)
            else:
                # Process real file
                messages = self._process_real_log_file(log_file, service_id, max_messages, progress_callback)
            
            self.status_manager.update_status('log',
                                            status='complete',
                                            progress=100,
                                            message=f'Found {len(messages)} messages',
                                            count=len(messages),
                                            searching=False)
            
        except Exception as e:
            self.status_manager.update_status('log',
                                            status='error',
                                            message=f'Error: {str(e)}',
                                            searching=False)
            print(f"❌ Error in log search: {e}")
        
        return messages
    
    def _process_real_log_file(self, log_file: str, service_id: Optional[str], 
                              max_messages: int, progress_callback: Optional[Callable]) -> List[Dict]:
        """Process real log file."""
        messages = []
        
        # Count total lines for progress
        total_lines = sum(1 for _ in open(log_file, 'r', encoding='utf-8', errors='ignore'))
        processed_lines = 0
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                if self.stop_event.is_set():
                    break
                
                processed_lines += 1
                
                # Update progress every 100 lines
                if processed_lines % 100 == 0:
                    progress = min((processed_lines / total_lines) * 100, 100)
                    self.status_manager.update_status('log',
                                                    progress=int(progress),
                                                    message=f'Processing line {processed_lines}/{total_lines}...')
                    if progress_callback:
                        progress_callback('log', int(progress))
                
                # Parse line
                parsed_line = self.parse_log_line(line, line_num)
                if not parsed_line:
                    continue
                
                # Filter by service ID if specified
                if service_id and parsed_line['service_id'].upper() != service_id.upper():
                    continue
                
                messages.append(parsed_line)
                
                # Limit number of messages for performance
                if len(messages) >= max_messages:
                    break
        
        return messages
    
    def _generate_sample_log_data(self, service_id: Optional[str], max_messages: int, 
                                 progress_callback: Optional[Callable]) -> List[Dict]:
        """Generate sample log data for demonstration."""
        messages = []
        
        for i in range(min(max_messages, 15)):
            if self.stop_event.is_set():
                break
            
            time.sleep(0.1)  # Simulate processing time
            progress = ((i + 1) / 15) * 100
            
            self.status_manager.update_status('log',
                                            progress=int(progress),
                                            message=f'Generating sample data... {int(progress)}%')
            
            if progress_callback:
                progress_callback('log', int(progress))
            
            timestamp = datetime.now().replace(second=56+i, microsecond=i*100000)
            formatted_time = TimestampParser.format_timestamp(timestamp)
            
            messages.append({
                'timestamp': formatted_time,
                'service_id': service_id or '0x1234',
                'level': ['INFO', 'WARN', 'ERROR', 'DEBUG'][i % 4],
                'component': ['ServiceManager', 'NetworkHandler', 'DataProcessor', 'EventDispatcher'][i % 4],
                'full_message': f"[{int(timestamp.timestamp()*1000000)}][{['INFO', 'WARN', 'ERROR', 'DEBUG'][i % 4]}] Sample log message {i+1} for service {service_id or '0x1234'}",
                'raw_timestamp': str(int(timestamp.timestamp()*1000000)),
                'line_number': i + 1
            })
        
        return messages
    
    def stop_search(self):
        """Stop the current search operation."""
        self.stop_event.set()
        self.status_manager.update_status('log',
                                        status='stopped',
                                        message='Search stopped',
                                        searching=False)
    
    def reset(self):
        """Reset the parser state."""
        self.stop_event.clear()
        self.status_manager.reset_status('log')

