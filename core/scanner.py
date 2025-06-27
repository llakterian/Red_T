import asyncio
import time
from bleak import BleakScanner, discover
from bluetooth import discover_devices
from core.stealth import StealthManager
import logging

class BluetoothScanner:
    def __init__(self, stealth_level=1):
        self.stealth_manager = StealthManager(stealth_level)
        self.logger = logging.getLogger('Red_T.scanner')
        self.active_scan = False
        self.discovered_devices = {}
        
    async def scan_classic(self, duration=8):
        """Scan for classic Bluetooth devices with stealth timing"""
        self.active_scan = True
        start_time = time.time()
        
        while self.active_scan and (time.time() - start_time < duration):
            try:
                # Apply stealth timing
                await self.stealth_manager.random_delay()
                
                devices = discover_devices(lookup_names=True, duration=2, flush_cache=True)
                for addr, name in devices:
                    if addr not in self.discovered_devices:
                        self.discovered_devices[addr] = {
                            'name': name,
                            'type': 'classic',
                            'first_seen': time.time(),
                            'last_seen': time.time(),
                            'rssi': 0  # Classic Bluetooth doesn't provide RSSI in this method
                        }
                        self.logger.info(f"Discovered classic device: {name} ({addr})")
                    else:
                        self.discovered_devices[addr]['last_seen'] = time.time()
                
                # Apply jitter to scan duration
                await asyncio.sleep(self.stealth_manager.get_jitter())
                
            except Exception as e:
                self.logger.error(f"Classic scan error: {str(e)}")
                await asyncio.sleep(1)
                
        self.active_scan = False
        return self.discovered_devices

    async def scan_ble(self, duration=10):
        """Scan for BLE devices with stealth techniques"""
        self.active_scan = True
        start_time = time.time()
        
        def detection_callback(device, advertisement_data):
            if device.address not in self.discovered_devices:
                self.discovered_devices[device.address] = {
                    'name': device.name or 'Unknown',
                    'type': 'BLE',
                    'first_seen': time.time(),
                    'last_seen': time.time(),
                    'rssi': advertisement_data.rssi,
                    'services': list(advertisement_data.service_uuids),
                    'manufacturer_data': advertisement_data.manufacturer_data
                }
                self.logger.info(f"Discovered BLE device: {device.name} ({device.address})")
            else:
                self.discovered_devices[device.address]['last_seen'] = time.time()
                self.discovered_devices[device.address]['rssi'] = advertisement_data.rssi

        while self.active_scan and (time.time() - start_time < duration):
            try:
                scanner = BleakScanner(detection_callback=detection_callback)
                await scanner.start()
                
                # Variable scan window with jitter
                scan_time = self.stealth_manager.get_scan_window()
                await asyncio.sleep(scan_time)
                
                await scanner.stop()
                
                # Random delay between scans
                await self.stealth_manager.random_delay()
                
            except Exception as e:
                self.logger.error(f"BLE scan error: {str(e)}")
                await asyncio.sleep(1)
                
        self.active_scan = False
        return self.discovered_devices

    async def persistent_scan(self, interval=60, max_duration=3600):
        """Continuous scanning with adaptive intervals"""
        start_time = time.time()
        self.logger.info(f"Starting persistent scan for {max_duration} seconds")
        
        while time.time() - start_time < max_duration:
            scan_start = time.time()
            
            # Randomize scan type
            if self.stealth_manager.random_choice(0.7):
                await self.scan_classic(duration=self.stealth_manager.get_scan_duration())
            else:
                await self.scan_ble(duration=self.stealth_manager.get_scan_duration())
            
            elapsed = time.time() - scan_start
            sleep_time = max(0, interval - elapsed)
            
            # Add random jitter to sleep time
            sleep_time = self.stealth_manager.add_jitter(sleep_time, 0.3)
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                
        return self.discovered_devices

    def stop_scan(self):
        """Stop any ongoing scans"""
        self.active_scan = False
        self.logger.info("Scanning stopped by user request")