import asyncio
import time
from bleak import BleakClient, BleakError
import bluetooth
from bluetooth.ble import DiscoveryService
import logging
from core.stealth import StealthManager
from core.vulnerabilities import VulnerabilityAssessor

class BluetoothConnector:
    def __init__(self, stealth_level=1):
        self.stealth_manager = StealthManager(stealth_level)
        self.vuln_assessor = VulnerabilityAssessor()
        self.logger = logging.getLogger('Red_T.connector')
        self.active_connections = {}
        
    async def connect_classic(self, target_address, port=1):
        """Establish classic Bluetooth connection with stealth"""
        try:
            self.logger.info(f"Attempting classic connection to {target_address}")
            
            # Apply stealth timing
            await self.stealth_manager.random_delay()
            
            # Check for known vulnerabilities first
            vulns = self.vuln_assessor.check_classic_vulnerabilities(target_address)
            if vulns:
                self.logger.info(f"Found vulnerabilities for {target_address}: {vulns}")
                
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            
            # Apply connection timing pattern
            await self.stealth_manager.connection_pattern()
            
            sock.connect((target_address, port))
            self.logger.info(f"Established classic connection to {target_address}")
            
            self.active_connections[target_address] = {
                'type': 'classic',
                'socket': sock,
                'connected_at': time.time(),
                'vulnerabilities': vulns
            }
            
            return sock
            
        except Exception as e:
            self.logger.error(f"Classic connection failed to {target_address}: {str(e)}")
            raise

    async def connect_ble(self, target_address, service_uuid=None):
        """Establish BLE connection with stealth techniques"""
        try:
            self.logger.info(f"Attempting BLE connection to {target_address}")
            
            # Check for BLE vulnerabilities
            vulns = self.vuln_assessor.check_ble_vulnerabilities(target_address)
            if vulns:
                self.logger.info(f"Found BLE vulnerabilities for {target_address}: {vulns}")
            
            # Apply random delay before connection
            await self.stealth_manager.random_delay()
            
            client = BleakClient(target_address)
            
            # Use stealth connection pattern
            await self.stealth_manager.connection_pattern()
            
            connected = await client.connect()
            if connected:
                self.logger.info(f"Established BLE connection to {target_address}")
                
                self.active_connections[target_address] = {
                    'type': 'BLE',
                    'client': client,
                    'connected_at': time.time(),
                    'vulnerabilities': vulns,
                    'services': await client.get_services()
                }
                
                return client
            else:
                raise Exception("Failed to connect to BLE device")
                
        except Exception as e:
            self.logger.error(f"BLE connection failed to {target_address}: {str(e)}")
            raise

    async def disconnect(self, target_address):
        """Disconnect from a device with stealthy timing"""
        if target_address not in self.active_connections:
            self.logger.warning(f"No active connection for {target_address}")
            return False
            
        conn = self.active_connections[target_address]
        
        try:
            # Apply random delay before disconnection
            await self.stealth_manager.random_delay()
            
            if conn['type'] == 'classic':
                conn['socket'].close()
            elif conn['type'] == 'BLE':
                await conn['client'].disconnect()
                
            del self.active_connections[target_address]
            self.logger.info(f"Disconnected from {target_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"Disconnection failed for {target_address}: {str(e)}")
            return False

    async def send_data(self, target_address, data):
        """Send data through an established connection"""
        if target_address not in self.active_connections:
            raise Exception("No active connection for this device")
            
        conn = self.active_connections[target_address]
        
        try:
            # Apply timing pattern to data transmission
            await self.stealth_manager.transmission_pattern(len(data))
            
            if conn['type'] == 'classic':
                conn['socket'].send(data)
            elif conn['type'] == 'BLE':
                # This is simplified - actual BLE would need service/characteristic
                await conn['client'].write_gatt_char(
                    "0000ffe1-0000-1000-8000-00805f9b34fb",  # Example characteristic
                    bytearray(data),
                    response=True
                )
                
            self.logger.debug(f"Sent {len(data)} bytes to {target_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"Data transmission failed to {target_address}: {str(e)}")
            raise

    async def mitm_proxy(self, target1, target2):
        """Establish man-in-the-middle between two devices"""
        self.logger.info(f"Attempting MITM between {target1} and {target2}")
        
        # This is a conceptual implementation - actual MITM would be more complex
        try:
            # Connect to both devices
            conn1 = await self.connect_classic(target1) if ':' not in target1 else await self.connect_ble(target1)
            conn2 = await self.connect_classic(target2) if ':' not in target2 else await self.connect_ble(target2)
            
            # Create proxy loop
            while True:
                # Proxy data between devices with stealth timing
                await self.stealth_manager.random_delay()
                
                # This would need actual implementation for each protocol
                # For demonstration, we just log the concept
                self.logger.debug("Proxying data between devices...")
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"MITM proxy failed: {str(e)}")
            await self.disconnect(target1)
            await self.disconnect(target2)
            raise