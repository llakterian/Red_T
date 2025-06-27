from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import asyncio
import json
import logging
from threading import Thread
from core.scanner import BluetoothScanner
from core.connector import BluetoothConnector
from core.controller import DeviceController
from modules.android import AndroidController
from modules.ios import IOSController
from modules.windows import WindowsController
from modules.linux import LinuxController

app = Flask(__name__)
app.config['SECRET_KEY'] = 'redteam_secret'
socketio = SocketIO(app, async_mode='threading')

# Global variables
scanner = None
connector = None
controllers = {}
active_connections = {}
scan_thread = None
stealth_level = 2  # Default stealth level

def get_controller(target_address, platform=None):
    """Get appropriate controller for device"""
    if not platform:
        # Try to detect platform from address or other means
        # This is simplified - real implementation would need proper detection
        if target_address.startswith("AA:BB:CC"):  # Example Android pattern
            platform = "android"
        elif target_address.startswith("DD:EE:FF"):  # Example iOS pattern
            platform = "ios"
        else:
            platform = "unknown"
    
    if platform not in controllers:
        if platform == "android":
            controllers[platform] = AndroidController(connector, stealth_level)
        elif platform == "ios":
            controllers[platform] = IOSController(connector, stealth_level)
        elif platform == "windows":
            controllers[platform] = WindowsController(connector, stealth_level)
        elif platform == "linux":
            controllers[platform] = LinuxController(connector, stealth_level)
        else:
            controllers[platform] = DeviceController(connector, stealth_level)
    
    return controllers[platform]

def background_scan():
    """Background scanning thread"""
    global scanner, connector
    scanner = BluetoothScanner(stealth_level=stealth_level)
    connector = BluetoothConnector(stealth_level=stealth_level)
    
    while True:
        try:
            # Run persistent scan
            discovered = asyncio.run(scanner.persistent_scan(interval=30, max_duration=3600))
            
            # Emit results to all clients
            socketio.emit('scan_results', {
                'devices': discovered,
                'count': len(discovered)
            })
            
        except Exception as e:
            logging.error(f"Scanning error: {str(e)}")
            socketio.emit('scan_error', {'message': str(e)})

@app.route('/')
def index():
    """Main UI page"""
    return render_template('index.html')

@app.route('/api/start_scan', methods=['POST'])
def start_scan():
    """API endpoint to start scanning"""
    global scan_thread
    
    if scan_thread is None or not scan_thread.is_alive():
        scan_thread = Thread(target=background_scan)
        scan_thread.daemon = True
        scan_thread.start()
        return jsonify({'status': 'success', 'message': 'Scanning started'})
    else:
        return jsonify({'status': 'error', 'message': 'Scan already in progress'})

@app.route('/api/stop_scan', methods=['POST'])
def stop_scan():
    """API endpoint to stop scanning"""
    global scanner
    
    if scanner:
        scanner.stop_scan()
        return jsonify({'status': 'success', 'message': 'Scanning stopped'})
    else:
        return jsonify({'status': 'error', 'message': 'No active scanner'})

@app.route('/api/connect', methods=['POST'])
def connect_device():
    """API endpoint to connect to a device"""
    data = request.json
    target_address = data.get('address')
    platform = data.get('platform')
    
    if not target_address:
        return jsonify({'status': 'error', 'message': 'No target address provided'})
    
    try:
        # Get appropriate controller
        controller = get_controller(target_address, platform)
        
        # Connect based on device type (simplified)
        if ":" in target_address:  # BLE device
            asyncio.run(connector.connect_ble(target_address))
        else:  # Classic Bluetooth
            asyncio.run(connector.connect_classic(target_address))
            
        active_connections[target_address] = {
            'controller': controller,
            'platform': platform or 'unknown'
        }
        
        return jsonify({
            'status': 'success',
            'message': f'Connected to {target_address}',
            'platform': platform
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/command', methods=['POST'])
def send_command():
    """API endpoint to send command to device"""
    data = request.json
    target_address = data.get('address')
    command = data.get('command')
    args = data.get('args', [])
    
    if not target_address or not command:
        return jsonify({'status': 'error', 'message': 'Missing parameters'})
    
    if target_address not in active_connections:
        return jsonify({'status': 'error', 'message': 'No active connection to this device'})
    
    try:
        controller = active_connections[target_address]['controller']
        result = asyncio.run(controller.execute_command(target_address, command, *args))
        
        return jsonify({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connections"""
    logging.info('Client connected')
    socketio.emit('status', {'message': 'Connected to Red_T server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnections"""
    logging.info('Client disconnected')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)