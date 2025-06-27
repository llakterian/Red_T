import json
import os
import logging
from typing import Dict, List, Optional

class VulnerabilityAssessor:
    def __init__(self):
        self.logger = logging.getLogger('Red_T.vulnerabilities')
        self.vulnerability_db = self._load_vulnerability_db()
        self.exploit_db = self._load_exploit_db()
        
    def _load_vulnerability_db(self) -> Dict:
        """Load vulnerability database from file"""
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'vulnerabilities.json')
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load vulnerability DB: {str(e)}")
            return {
                "classic": {},
                "ble": {},
                "platforms": {
                    "android": {},
                    "ios": {},
                    "windows": {},
                    "linux": {}
                }
            }
            
    def _load_exploit_db(self) -> Dict:
        """Load exploit database from file"""
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'exploits.json')
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load exploit DB: {str(e)}")
            return {
                "zero_click": {},
                "ble": {},
                "classic": {},
                "platform_specific": {
                    "android": {},
                    "ios": {},
                    "windows": {},
                    "linux": {}
                }
            }
            
    def check_classic_vulnerabilities(self, device_address: str, device_info: Optional[Dict] = None) -> List[str]:
        """Check for known classic Bluetooth vulnerabilities"""
        vulns = []
        
        # Check against known vulnerable devices
        for vuln_device, vuln_info in self.vulnerability_db.get('classic', {}).items():
            if vuln_device.lower() in device_address.lower():
                vulns.extend(vuln_info['vulnerabilities'])
                
        # Check against device class patterns
        if device_info and 'class' in device_info:
            device_class = device_info['class']
            for pattern, vuln_info in self.vulnerability_db.get('class_patterns', {}).items():
                if pattern in device_class:
                    vulns.extend(vuln_info['vulnerabilities'])
                    
        return list(set(vulns))  # Remove duplicates
        
    def check_ble_vulnerabilities(self, device_address: str, advertisement_data: Optional[Dict] = None) -> List[str]:
        """Check for known BLE vulnerabilities"""
        vulns = []
        
        # Check against known vulnerable devices
        for vuln_device, vuln_info in self.vulnerability_db.get('ble', {}).items():
            if vuln_device.lower() in device_address.lower():
                vulns.extend(vuln_info['vulnerabilities'])
                
        # Check advertisement data for vulnerable patterns
        if advertisement_data:
            # Check manufacturer data
            for manufacturer_id, data in advertisement_data.get('manufacturer_data', {}).items():
                hex_id = f"{manufacturer_id:04x}"
                for pattern, vuln_info in self.vulnerability_db.get('ble_manufacturer', {}).items():
                    if pattern in hex_id:
                        vulns.extend(vuln_info['vulnerabilities'])
                        
            # Check service UUIDs
            for service_uuid in advertisement_data.get('services', []):
                for pattern, vuln_info in self.vulnerability_db.get('ble_services', {}).items():
                    if pattern.lower() in service_uuid.lower():
                        vulns.extend(vuln_info['vulnerabilities'])
                        
        return list(set(vulns))
        
    def check_platform_vulnerabilities(self, platform: str, version: str) -> List[str]:
        """Check for platform-specific vulnerabilities"""
        platform = platform.lower()
        vulns = []
        
        if platform in self.vulnerability_db.get('platforms', {}):
            for version_pattern, vuln_info in self.vulnerability_db['platforms'][platform].items():
                if version_pattern in version:
                    vulns.extend(vuln_info['vulnerabilities'])
                    
        return list(set(vulns))
        
    def check_exploit_compatibility(self, device_address: str, exploit_name: str) -> List[str]:
        """Check if a device is vulnerable to a specific exploit"""
        # First check if we have direct mapping for this device
        for device_pattern, exploits in self.exploit_db.get('device_exploits', {}).items():
            if device_pattern.lower() in device_address.lower():
                if exploit_name in exploits:
                    return [exploit_name]
                    
        # Check general exploit compatibility
        exploit_info = self.exploit_db.get('exploits', {}).get(exploit_name, {})
        if not exploit_info:
            return []
            
        # Check required characteristics
        required = exploit_info.get('requires', [])
        if not required:
            return [exploit_name]  # No specific requirements
            
        # For now, we'll assume compatibility if the exploit exists
        # In real implementation, we'd check device characteristics
        return [exploit_name]
        
    def get_exploit_info(self, exploit_name: str) -> Dict:
        """Get detailed information about an exploit"""
        return self.exploit_db.get('exploits', {}).get(exploit_name, {})
        
    def get_zero_click_exploits(self, platform: Optional[str] = None) -> List[Dict]:
        """Get list of available zero-click exploits"""
        if platform:
            return self.exploit_db.get('platform_specific', {}).get(platform.lower(), {}).get('zero_click', [])
        return self.exploit_db.get('zero_click', [])
        
    def get_ble_exploits(self) -> List[Dict]:
        """Get list of available BLE exploits"""
        return self.exploit_db.get('ble', [])
        
    def get_mitm_techniques(self) -> List[Dict]:
        """Get available MITM techniques"""
        return self.exploit_db.get('mitm', [])