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
        
   async def scan_classic(self, duration=12):  # Increased default duration
    """Scan for classic Bluetooth devices with enhanced reliability"""
    self.active_scan = True
    self.discovered_devices = {}  # Reset on each scan
    start_time = time.time()
    
    # Ensure Bluetooth adapter is ready
    try:
        subprocess.run(["sudo", "hciconfig", "hci0", "up"], check=True)
        subprocess.run(["sudo", "hciconfig", "hci0", "piscan"], check=True)
    except Exception as e:
        self.logger.error(f"Bluetooth init failed: {str(e)}")
        return {}

    while self.active_scan and (time.time() - start_time < duration):
        try:
            # Extended single scan instead of multiple short ones
            devices = discover_devices(
                lookup_names=True,
                duration=min(10, duration),  # Single 10s max scan
                flush_cache=True
            )
            
            current_time = time.time()
            for addr, name in devices:
                if addr not in self.discovered_devices:
                    self.discovered_devices[addr] = {
                        'name': name or 'Unknown',
                        'type': 'classic',
                        'first_seen': current_time,
                        'last_seen': current_time,
                        'rssi': 0
                    }
                    self.logger.info(f"Discovered classic device: {self.discovered_devices[addr]['name']} ({addr})")
                else:
                    self.discovered_devices[addr]['last_seen'] = current_time

            # Only sleep if we have time remaining
            remaining_time = duration - (time.time() - start_time)
            if remaining_time > 0:
                await asyncio.sleep(self.stealth_manager.get_jitter())
                
        except Exception as e:
            self.logger.error(f"Scan error: {str(e)}")
            if "Bluetooth not available" in str(e):
                break  # Don't retry if hardware failed
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