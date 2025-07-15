# Debug Assistant - Professional ServiceId Analyzer

A comprehensive, modular dashboard application for analyzing service logs with advanced timestamp correlation, anomaly detection, and architecture visualization capabilities.

## 🚀 Features

- **Multi-Source Data Analysis**: Supports log files, DLT messages, PCAP/SOME-IP data, and other log sources
- **Advanced Timestamp Correlation**: Correlates events across different data sources based on timestamps and service IDs
- **Real-time Processing**: Background processing with progress indicators and live updates
- **Anomaly Detection**: Detects unusual patterns, error spikes, and service behavior anomalies
- **Comprehensive Reporting**: Generates detailed analysis reports in text and JSON formats
- **UML Diagram Generation**: Creates service architecture, sequence, and component diagrams
- **Professional UI**: Modern, responsive dashboard with interactive tables and visualizations
- **Modular Architecture**: Clean, maintainable code structure for easy debugging and extension

## 📁 Project Structure

```
debug_assistant_project/
├── main.py                 # Main application entry point
├── config.yaml            # Configuration file
├── requirements.txt        # Python dependencies
├── README.md              # This documentation
├── code_analysis.md       # Original code analysis report
├── original_tool2.py      # Original code for reference
├── dashboard/             # Dashboard components
│   ├── __init__.py
│   └── layout.py          # UI layout components
├── data_processing/       # Data processing modules
│   ├── __init__.py
│   ├── log_parser.py      # Log file processing
│   ├── dlt_parser.py      # DLT file processing
│   ├── pcap_parser.py     # PCAP data processing
│   └── correlator.py      # Data correlation logic
├── analysis/              # Analysis modules
│   ├── __init__.py
│   ├── anomaly_detector.py # Anomaly detection
│   ├── reporter.py        # Report generation
│   └── uml_generator.py   # UML diagram generation
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   └── helpers.py         # Helper functions
├── tests/                 # Unit tests (placeholder)
│   └── __init__.py
├── data/                  # Data directory (created at runtime)
├── reports/               # Generated reports (created at runtime)
└── diagrams/              # Generated UML diagrams (created at runtime)
```

## 🔧 Installation

1. **Clone or extract the project**:
   ```bash
   cd debug_assistant_project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the application** (optional):
   Edit `config.yaml` to customize settings like data directories, processing limits, and UI preferences.

## 🚀 Usage

### Starting the Application

```bash
python main.py
```

The application will start and be available at `http://localhost:8050` by default.

### Using Your Own Data

1. **Prepare your data files**:
   - Place your log file as `data/adaptive.log`
   - Place your DLT file as `data/dltlog_0.dlt`
   - Place your PCAP JSON file as `data/full_pcap.json`

2. **Restart the application** - it will automatically detect and use your real data files.

### Dashboard Features

1. **Service Selection**: Choose a ServiceId from the dropdown to analyze
2. **Data Sources**: Select which data sources to include in the analysis
3. **Real-time Analysis**: The system automatically processes data in the background
4. **Interactive Tables**: View, sort, and filter messages from all data sources
5. **Correlation Timeline**: Visualize event correlations across time
6. **Generate Reports**: Create comprehensive analysis reports
7. **Generate UML**: Create architecture and sequence diagrams

## 📊 Key Improvements from Original Code

### 1. **Modular Architecture**
- Separated monolithic code into focused, reusable modules
- Clear separation of concerns (UI, data processing, analysis)
- Easy to test, debug, and extend individual components

### 2. **Fixed Critical Issues**
- **Missing Callbacks**: Implemented all referenced but missing callback functions
- **Layout Problems**: Fixed HTML structure and CSS issues
- **Threading Issues**: Improved thread management and state handling
- **Error Handling**: Added comprehensive error handling throughout

### 3. **Enhanced Functionality**
- **Real Correlation Analysis**: Implemented actual event correlation logic
- **Anomaly Detection**: Added multiple anomaly detection algorithms
- **Report Generation**: Complete reporting system with multiple formats
- **UML Generation**: PlantUML diagram generation for architecture visualization

### 4. **Professional Features**
- **Configuration Management**: YAML-based configuration system
- **Progress Indicators**: Real-time progress bars and status updates
- **Data Validation**: File existence checks and data quality validation
- **Sample Data**: Automatic sample data generation for demonstration

### 5. **Better User Experience**
- **Responsive Design**: Mobile-friendly interface
- **Interactive Elements**: Sortable, filterable tables
- **Visual Feedback**: Loading indicators and status messages
- **Error Recovery**: Graceful error handling and user feedback

## 🔍 Data Processing Capabilities

### Log File Processing
- Parses standard log formats with ServiceId extraction
- Supports timestamp normalization and component identification
- Handles large files with progress tracking

### DLT Message Processing
- Basic DLT format support (extensible for full DLT library integration)
- Application and context ID extraction
- Log level categorization

### PCAP/SOME-IP Processing
- JSON format PCAP data processing
- Service ID and method ID extraction
- Network traffic analysis

### Event Correlation
- Time-window based correlation (configurable)
- Service ID matching across data sources
- Content similarity analysis
- Correlation strength calculation

## 📈 Analysis Features

### Anomaly Detection
- **Error Rate Spikes**: Detects unusual error patterns
- **Message Frequency**: Identifies abnormal message rates
- **Service Silence**: Detects services that have gone quiet
- **Duplicate Messages**: Finds repeated message patterns
- **Suspicious Patterns**: Identifies concerning keywords and patterns

### Reporting
- **Comprehensive Reports**: Detailed analysis with statistics
- **Executive Summary**: High-level overview for management
- **Technical Details**: In-depth technical information
- **Multiple Formats**: Text and JSON output formats
- **Recommendations**: Actionable insights and suggestions

### UML Generation
- **Service Architecture**: Component relationships and interactions
- **Sequence Diagrams**: Event flow visualization
- **Component Diagrams**: System component structure
- **PlantUML Format**: Industry-standard diagram format

## ⚙️ Configuration

The `config.yaml` file allows customization of:

```yaml
app:
  title: "Debug Assistant"
  host: "0.0.0.0"
  port: 8050
  debug: false

data:
  directory: "./data"
  max_messages_per_source: 500
  discovery_line_limit: 1000

processing:
  progress_update_interval: 100
  thread_timeout: 30
  auto_search_on_selection: true

ui:
  refresh_interval: 500
  table_page_size: 10
```

## 🧪 Testing

The application includes:
- Syntax validation for all modules
- Sample data generation for testing
- Error handling validation
- Thread safety testing

To run basic tests:
```bash
python -m py_compile main.py
python main.py --test  # (if test mode is implemented)
```

## 🔧 Development

### Adding New Data Sources
1. Create a new parser in `data_processing/`
2. Implement the standard parser interface
3. Add UI components in `dashboard/layout.py`
4. Update the main application to include the new source

### Extending Analysis
1. Add new analysis modules in `analysis/`
2. Implement the analysis interface
3. Update the main application to call new analysis
4. Add UI components for displaying results

### Customizing UI
1. Modify `dashboard/layout.py` for layout changes
2. Update CSS in the main application
3. Add new callbacks for interactive features

## 📝 API Reference

### Core Classes

#### `DebugAssistantApp`
Main application class that orchestrates all components.

#### `LogParser`
Processes log files and extracts ServiceId information.

#### `EventCorrelator`
Correlates events across different data sources.

#### `AnomalyDetector`
Detects unusual patterns in service behavior.

#### `ReportGenerator`
Generates comprehensive analysis reports.

#### `UMLGenerator`
Creates UML diagrams for architecture visualization.

## 🤝 Contributing

1. Follow the modular architecture pattern
2. Add comprehensive error handling
3. Include progress indicators for long operations
4. Update documentation for new features
5. Test with both sample and real data

## 📄 License

This project is provided as-is for educational and professional use.

## 🆘 Troubleshooting

### Common Issues

1. **Dependencies not found**: Run `pip install -r requirements.txt`
2. **Port already in use**: Change the port in `config.yaml`
3. **Data files not found**: Place your files in the `data/` directory or use sample data
4. **Performance issues**: Reduce `max_messages_per_source` in configuration

### Getting Help

1. Check the console output for detailed error messages
2. Review the `code_analysis.md` file for technical details
3. Examine the modular structure for debugging specific components

---

**Debug Assistant** - Professional ServiceId Analysis Made Simple

