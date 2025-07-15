#!/usr/bin/env python3
"""
Test script for Debug Assistant application.
Validates basic functionality without starting the full web server.
"""

import sys
import os
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing imports...")
    
    try:
        from utils.config import config
        from utils.helpers import ServiceDiscovery, ProcessingStatus
        from data_processing.log_parser import LogParser
        from data_processing.dlt_parser import DLTParser
        from data_processing.pcap_parser import PCAPParser
        from data_processing.correlator import EventCorrelator
        from analysis.anomaly_detector import AnomalyDetector
        from analysis.reporter import ReportGenerator
        from analysis.uml_generator import UMLGenerator
        from dashboard.layout import create_main_layout
        
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("🧪 Testing configuration...")
    
    try:
        from utils.config import config
        
        # Test basic config access
        title = config.get('app.title', 'Default Title')
        port = config.get('app.port', 8050)
        data_dir = config.get('data.directory', './data')
        
        print(f"  ✅ Config loaded: title='{title}', port={port}, data_dir='{data_dir}'")
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_service_discovery():
    """Test service discovery functionality."""
    print("🧪 Testing service discovery...")
    
    try:
        from utils.helpers import ServiceDiscovery
        
        discovery = ServiceDiscovery()
        
        # Test with empty files (should not crash)
        services = discovery.discover_all({
            'log_file': 'nonexistent.log',
            'dlt_file': 'nonexistent.dlt',
            'pcap_json_file': 'nonexistent.json'
        })
        
        print(f"  ✅ Service discovery completed: found {len(services)} services")
        return True
    except Exception as e:
        print(f"  ❌ Service discovery test failed: {e}")
        return False

def test_data_parsers():
    """Test data parser functionality."""
    print("🧪 Testing data parsers...")
    
    try:
        from utils.helpers import ProcessingStatus
        from data_processing.log_parser import LogParser
        from data_processing.dlt_parser import DLTParser
        from data_processing.pcap_parser import PCAPParser
        
        status_manager = ProcessingStatus()
        
        # Test parsers with non-existent files (should generate sample data)
        log_parser = LogParser(status_manager)
        dlt_parser = DLTParser(status_manager)
        pcap_parser = PCAPParser(status_manager)
        
        # Test sample data generation
        log_data = log_parser.search_log_file('nonexistent.log', '0x1234', 5)
        dlt_data = dlt_parser.search_dlt_file('nonexistent.dlt', '0x1234', 5)
        pcap_data = pcap_parser.search_pcap_file('nonexistent.json', '0x1234', 5)
        
        print(f"  ✅ Parsers working: log={len(log_data)}, dlt={len(dlt_data)}, pcap={len(pcap_data)} messages")
        return True
    except Exception as e:
        print(f"  ❌ Data parser test failed: {e}")
        return False

def test_analysis_modules():
    """Test analysis modules."""
    print("🧪 Testing analysis modules...")
    
    try:
        from data_processing.correlator import EventCorrelator
        from analysis.anomaly_detector import AnomalyDetector
        from analysis.reporter import ReportGenerator
        from analysis.uml_generator import UMLGenerator
        
        # Create sample data
        sample_log = [{'timestamp': '12:34:56.123', 'service_id': '0x1234', 'level': 'INFO', 'component': 'Test', 'full_message': 'Test message'}]
        sample_dlt = [{'timestamp': '12:34:56.124', 'service_id': '0x1234', 'app_id': 'APP1', 'context_id': 'CTX1', 'log_level': 'INFO', 'full_message': 'DLT test'}]
        sample_pcap = [{'timestamp': '12:34:56.125', 'service_id': '0x1234', 'method_id': '0x0100', 'source_ip': '192.168.1.1', 'dest_ip': '192.168.1.2', 'protocol': 'SOME/IP', 'full_message': 'PCAP test'}]
        sample_other = [{'timestamp': '12:34:56.126', 'source': 'System', 'level': 'INFO', 'category': 'Test', 'full_message': 'Other test'}]
        
        # Test correlator
        correlator = EventCorrelator()
        correlation_results = correlator.correlate_events(sample_log, sample_dlt, sample_pcap, sample_other)
        
        # Test anomaly detector
        anomaly_detector = AnomalyDetector()
        anomaly_results = anomaly_detector.detect_anomalies(sample_log, sample_dlt, sample_pcap, sample_other)
        
        # Test report generator (with temp directory)
        with tempfile.TemporaryDirectory() as temp_dir:
            report_generator = ReportGenerator(temp_dir)
            report_path = report_generator.generate_comprehensive_report(
                '0x1234', sample_log, sample_dlt, sample_pcap, sample_other,
                correlation_results, anomaly_results
            )
            
            # Test UML generator
            uml_generator = UMLGenerator(temp_dir)
            uml_paths = uml_generator.generate_all_diagrams('0x1234', sample_log, sample_dlt, sample_pcap, correlation_results)
        
        print(f"  ✅ Analysis modules working: correlations={correlation_results.get('total_correlations', 0)}, anomalies={anomaly_results.get('total_anomalies', 0)}")
        print(f"      Report generated: {os.path.basename(report_path)}")
        print(f"      UML diagrams: {len(uml_paths)} files")
        return True
    except Exception as e:
        print(f"  ❌ Analysis modules test failed: {e}")
        return False

def test_dashboard_layout():
    """Test dashboard layout generation."""
    print("🧪 Testing dashboard layout...")
    
    try:
        from dashboard.layout import create_main_layout
        
        layout = create_main_layout()
        
        # Basic validation that layout is created
        if layout and hasattr(layout, 'children'):
            print("  ✅ Dashboard layout created successfully")
            return True
        else:
            print("  ❌ Dashboard layout is invalid")
            return False
    except Exception as e:
        print(f"  ❌ Dashboard layout test failed: {e}")
        return False

def test_main_app_creation():
    """Test main application creation (without running)."""
    print("🧪 Testing main application creation...")
    
    try:
        # Import main app class
        from main import DebugAssistantApp
        
        # Create app instance (this will initialize everything)
        app = DebugAssistantApp()
        
        # Basic validation
        if app and app.app and app.status_manager:
            print("  ✅ Main application created successfully")
            return True
        else:
            print("  ❌ Main application creation failed")
            return False
    except Exception as e:
        print(f"  ❌ Main application test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Debug Assistant - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_service_discovery,
        test_data_parsers,
        test_analysis_modules,
        test_dashboard_layout,
        test_main_app_creation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The application is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

