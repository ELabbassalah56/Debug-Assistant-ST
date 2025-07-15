"""
UML diagram generation module for the Debug Assistant application.
Generates UML diagrams showing service architecture and interactions.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict


class UMLGenerator:
    """Generates UML diagrams for service architecture visualization."""
    
    def __init__(self, output_dir: str = "./diagrams"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_service_architecture_diagram(self, log_data: List[Dict], dlt_data: List[Dict], 
                                            pcap_data: List[Dict], correlation_results: Dict) -> str:
        """Generate a service architecture diagram in PlantUML format."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        diagram_filename = f"service_architecture_{timestamp}.puml"
        diagram_path = os.path.join(self.output_dir, diagram_filename)
        
        # Extract service information
        services = self._extract_services(log_data, dlt_data, pcap_data)
        interactions = self._extract_interactions(pcap_data, correlation_results)
        components = self._extract_components(log_data, dlt_data)
        
        # Generate PlantUML content
        puml_content = self._generate_plantuml_content(services, interactions, components)
        
        with open(diagram_path, 'w') as f:
            f.write(puml_content)
        
        return diagram_path
    
    def generate_sequence_diagram(self, correlation_results: Dict, service_id: str) -> str:
        """Generate a sequence diagram showing event flow."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        diagram_filename = f"sequence_diagram_{service_id}_{timestamp}.puml"
        diagram_path = os.path.join(self.output_dir, diagram_filename)
        
        # Generate sequence diagram content
        puml_content = self._generate_sequence_diagram_content(correlation_results, service_id)
        
        with open(diagram_path, 'w') as f:
            f.write(puml_content)
        
        return diagram_path
    
    def generate_component_diagram(self, log_data: List[Dict], dlt_data: List[Dict]) -> str:
        """Generate a component diagram showing system components."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        diagram_filename = f"component_diagram_{timestamp}.puml"
        diagram_path = os.path.join(self.output_dir, diagram_filename)
        
        # Extract component information
        components = self._extract_detailed_components(log_data, dlt_data)
        
        # Generate component diagram content
        puml_content = self._generate_component_diagram_content(components)
        
        with open(diagram_path, 'w') as f:
            f.write(puml_content)
        
        return diagram_path
    
    def _extract_services(self, log_data: List[Dict], dlt_data: List[Dict], 
                         pcap_data: List[Dict]) -> Dict[str, Dict]:
        """Extract service information from all data sources."""
        services = {}
        
        # Extract from log data
        for entry in log_data:
            service_id = entry.get('service_id')
            if service_id:
                if service_id not in services:
                    services[service_id] = {
                        'id': service_id,
                        'name': f"Service_{service_id}",
                        'components': set(),
                        'log_levels': set(),
                        'message_count': 0,
                        'sources': set()
                    }
                
                services[service_id]['components'].add(entry.get('component', 'Unknown'))
                services[service_id]['log_levels'].add(entry.get('level', 'INFO'))
                services[service_id]['message_count'] += 1
                services[service_id]['sources'].add('log')
        
        # Extract from DLT data
        for entry in dlt_data:
            service_id = entry.get('service_id')
            if service_id:
                if service_id not in services:
                    services[service_id] = {
                        'id': service_id,
                        'name': f"Service_{service_id}",
                        'components': set(),
                        'log_levels': set(),
                        'message_count': 0,
                        'sources': set()
                    }
                
                services[service_id]['components'].add(entry.get('app_id', 'Unknown'))
                services[service_id]['log_levels'].add(entry.get('log_level', 'INFO'))
                services[service_id]['message_count'] += 1
                services[service_id]['sources'].add('dlt')
        
        # Extract from PCAP data
        for entry in pcap_data:
            service_id = entry.get('service_id')
            if service_id:
                if service_id not in services:
                    services[service_id] = {
                        'id': service_id,
                        'name': f"Service_{service_id}",
                        'components': set(),
                        'log_levels': set(),
                        'message_count': 0,
                        'sources': set()
                    }
                
                services[service_id]['components'].add(entry.get('protocol', 'SOME/IP'))
                services[service_id]['message_count'] += 1
                services[service_id]['sources'].add('pcap')
        
        return services
    
    def _extract_interactions(self, pcap_data: List[Dict], correlation_results: Dict) -> List[Dict]:
        """Extract service interactions from PCAP data and correlations."""
        interactions = []
        
        # Extract from PCAP data (network interactions)
        ip_to_service = {}
        for entry in pcap_data:
            service_id = entry.get('service_id')
            source_ip = entry.get('source_ip')
            dest_ip = entry.get('dest_ip')
            
            if service_id and source_ip:
                ip_to_service[source_ip] = service_id
            if service_id and dest_ip:
                ip_to_service[dest_ip] = service_id
        
        # Create interactions from network traffic
        for entry in pcap_data:
            source_ip = entry.get('source_ip')
            dest_ip = entry.get('dest_ip')
            method_id = entry.get('method_id')
            protocol = entry.get('protocol', 'SOME/IP')
            
            if source_ip in ip_to_service and dest_ip in ip_to_service:
                source_service = ip_to_service[source_ip]
                dest_service = ip_to_service[dest_ip]
                
                if source_service != dest_service:
                    interactions.append({
                        'from': source_service,
                        'to': dest_service,
                        'method': method_id,
                        'protocol': protocol,
                        'type': 'network'
                    })
        
        # Extract from correlation results
        if correlation_results and 'correlations' in correlation_results:
            for correlation in correlation_results['correlations']:
                services_in_correlation = correlation.get('service_ids', [])
                if len(services_in_correlation) > 1:
                    # Create interactions between correlated services
                    for i, service1 in enumerate(services_in_correlation):
                        for service2 in services_in_correlation[i+1:]:
                            interactions.append({
                                'from': service1,
                                'to': service2,
                                'method': 'correlated_event',
                                'protocol': 'correlation',
                                'type': 'correlation'
                            })
        
        return interactions
    
    def _extract_components(self, log_data: List[Dict], dlt_data: List[Dict]) -> Dict[str, Set[str]]:
        """Extract component information."""
        components = defaultdict(set)
        
        # From log data
        for entry in log_data:
            service_id = entry.get('service_id')
            component = entry.get('component')
            if service_id and component:
                components[service_id].add(component)
        
        # From DLT data
        for entry in dlt_data:
            service_id = entry.get('service_id')
            app_id = entry.get('app_id')
            context_id = entry.get('context_id')
            if service_id:
                if app_id:
                    components[service_id].add(f"App:{app_id}")
                if context_id:
                    components[service_id].add(f"Ctx:{context_id}")
        
        return dict(components)
    
    def _extract_detailed_components(self, log_data: List[Dict], dlt_data: List[Dict]) -> Dict:
        """Extract detailed component information for component diagram."""
        components = {}
        
        # Analyze log data for components
        component_stats = defaultdict(lambda: {'services': set(), 'levels': set(), 'count': 0})
        
        for entry in log_data:
            component = entry.get('component', 'Unknown')
            service_id = entry.get('service_id')
            level = entry.get('level', 'INFO')
            
            component_stats[component]['services'].add(service_id)
            component_stats[component]['levels'].add(level)
            component_stats[component]['count'] += 1
        
        # Convert to component structure
        for component, stats in component_stats.items():
            components[component] = {
                'name': component,
                'services': list(stats['services']),
                'log_levels': list(stats['levels']),
                'message_count': stats['count'],
                'type': 'component'
            }
        
        # Add DLT applications as components
        app_stats = defaultdict(lambda: {'contexts': set(), 'services': set(), 'count': 0})
        
        for entry in dlt_data:
            app_id = entry.get('app_id')
            context_id = entry.get('context_id')
            service_id = entry.get('service_id')
            
            if app_id:
                app_stats[app_id]['contexts'].add(context_id)
                app_stats[app_id]['services'].add(service_id)
                app_stats[app_id]['count'] += 1
        
        for app_id, stats in app_stats.items():
            components[f"DLT_{app_id}"] = {
                'name': f"DLT Application {app_id}",
                'contexts': list(stats['contexts']),
                'services': list(stats['services']),
                'message_count': stats['count'],
                'type': 'dlt_application'
            }
        
        return components
    
    def _generate_plantuml_content(self, services: Dict, interactions: List[Dict], 
                                  components: Dict) -> str:
        """Generate PlantUML content for service architecture diagram."""
        
        puml = []
        puml.append("@startuml")
        puml.append("!theme plain")
        puml.append("title Service Architecture Diagram")
        puml.append("")
        
        # Define services as components
        for service_id, service_info in services.items():
            service_name = service_info['name']
            message_count = service_info['message_count']
            sources = ', '.join(service_info['sources'])
            
            puml.append(f"component \"{service_name}\" as {service_id.replace('0x', 'S')} {{")
            puml.append(f"  [Messages: {message_count}]")
            puml.append(f"  [Sources: {sources}]")
            
            # Add components within service
            if service_id in components:
                for component in list(components[service_id])[:3]:  # Limit to 3 components
                    puml.append(f"  [{component}]")
            
            puml.append("}")
            puml.append("")
        
        # Add interactions
        interaction_counts = defaultdict(int)
        for interaction in interactions:
            from_service = interaction['from'].replace('0x', 'S')
            to_service = interaction['to'].replace('0x', 'S')
            interaction_type = interaction['type']
            
            key = (from_service, to_service)
            interaction_counts[key] += 1
        
        # Draw connections
        for (from_service, to_service), count in interaction_counts.items():
            if count > 1:
                puml.append(f"{from_service} --> {to_service} : {count} interactions")
            else:
                puml.append(f"{from_service} --> {to_service}")
        
        # Add legend
        puml.append("")
        puml.append("legend right")
        puml.append("  Service Architecture")
        puml.append("  Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        puml.append("endlegend")
        
        puml.append("@enduml")
        
        return "\n".join(puml)
    
    def _generate_sequence_diagram_content(self, correlation_results: Dict, service_id: str) -> str:
        """Generate PlantUML content for sequence diagram."""
        
        puml = []
        puml.append("@startuml")
        puml.append("!theme plain")
        puml.append(f"title Event Sequence for Service {service_id}")
        puml.append("")
        
        if not correlation_results or 'correlations' not in correlation_results:
            puml.append("note over User : No correlation data available")
            puml.append("@enduml")
            return "\n".join(puml)
        
        # Extract participants from correlations
        participants = set()
        relevant_correlations = []
        
        for correlation in correlation_results['correlations']:
            if service_id in correlation.get('service_ids', []):
                relevant_correlations.append(correlation)
                for event in correlation['events']:
                    participants.add(event['source'])
        
        # Define participants
        for participant in sorted(participants):
            puml.append(f"participant {participant}")
        
        puml.append("")
        
        # Generate sequence for relevant correlations
        for i, correlation in enumerate(relevant_correlations[:5]):  # Limit to 5 correlations
            puml.append(f"group Correlation {correlation['id']}")
            
            events = sorted(correlation['events'], 
                          key=lambda x: x.get('parsed_timestamp') or datetime.min)
            
            for j, event in enumerate(events):
                source = event['source']
                message = event.get('full_message', 'Event')[:50] + '...'
                
                if j == 0:
                    puml.append(f"activate {source}")
                
                puml.append(f"{source} -> {source} : {message}")
                
                if j == len(events) - 1:
                    puml.append(f"deactivate {source}")
            
            puml.append("end")
            puml.append("")
        
        puml.append("@enduml")
        
        return "\n".join(puml)
    
    def _generate_component_diagram_content(self, components: Dict) -> str:
        """Generate PlantUML content for component diagram."""
        
        puml = []
        puml.append("@startuml")
        puml.append("!theme plain")
        puml.append("title System Component Diagram")
        puml.append("")
        
        # Group components by type
        log_components = {k: v for k, v in components.items() if v.get('type') == 'component'}
        dlt_components = {k: v for k, v in components.items() if v.get('type') == 'dlt_application'}
        
        # Log components package
        if log_components:
            puml.append("package \"Log Components\" {")
            for comp_name, comp_info in log_components.items():
                safe_name = comp_name.replace(' ', '_').replace('-', '_')
                puml.append(f"  component [{comp_info['name']}] as {safe_name}")
            puml.append("}")
            puml.append("")
        
        # DLT components package
        if dlt_components:
            puml.append("package \"DLT Applications\" {")
            for comp_name, comp_info in dlt_components.items():
                safe_name = comp_name.replace(' ', '_').replace('-', '_')
                puml.append(f"  component [{comp_info['name']}] as {safe_name}")
            puml.append("}")
            puml.append("")
        
        # Add some connections based on shared services
        connections_added = set()
        for comp1_name, comp1_info in components.items():
            for comp2_name, comp2_info in components.items():
                if comp1_name != comp2_name:
                    # Check if they share services
                    services1 = set(comp1_info.get('services', []))
                    services2 = set(comp2_info.get('services', []))
                    
                    if services1.intersection(services2):
                        safe_name1 = comp1_name.replace(' ', '_').replace('-', '_')
                        safe_name2 = comp2_name.replace(' ', '_').replace('-', '_')
                        
                        connection = tuple(sorted([safe_name1, safe_name2]))
                        if connection not in connections_added:
                            puml.append(f"{safe_name1} --> {safe_name2} : shared services")
                            connections_added.add(connection)
        
        # Add legend
        puml.append("")
        puml.append("legend right")
        puml.append("  Component Relationships")
        puml.append("  Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        puml.append("endlegend")
        
        puml.append("@enduml")
        
        return "\n".join(puml)
    
    def generate_all_diagrams(self, service_id: str, log_data: List[Dict], 
                            dlt_data: List[Dict], pcap_data: List[Dict], 
                            correlation_results: Dict) -> List[str]:
        """Generate all types of UML diagrams."""
        
        diagram_paths = []
        
        try:
            # Service architecture diagram
            arch_path = self.generate_service_architecture_diagram(log_data, dlt_data, pcap_data, correlation_results)
            diagram_paths.append(arch_path)
            
            # Sequence diagram
            seq_path = self.generate_sequence_diagram(correlation_results, service_id)
            diagram_paths.append(seq_path)
            
            # Component diagram
            comp_path = self.generate_component_diagram(log_data, dlt_data)
            diagram_paths.append(comp_path)
            
        except Exception as e:
            print(f"❌ Error generating UML diagrams: {e}")
        
        return diagram_paths
    
    def get_diagram_status(self) -> str:
        """Get status of generated diagrams."""
        if not os.path.exists(self.output_dir):
            return "No diagrams generated yet."
        
        files = [f for f in os.listdir(self.output_dir) if f.endswith('.puml')]
        
        if not files:
            return "No diagrams generated yet."
        
        status = f"Generated {len(files)} UML diagrams:\n"
        for file in sorted(files):
            file_path = os.path.join(self.output_dir, file)
            size = os.path.getsize(file_path)
            status += f"  • {file} ({size} bytes)\n"
        
        status += f"\nTo render diagrams, use PlantUML or online tools like:\n"
        status += f"  • http://www.plantuml.com/plantuml/uml/\n"
        status += f"  • VS Code PlantUML extension\n"
        
        return status

