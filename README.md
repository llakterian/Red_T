Red_T - Advanced Bluetooth Exploitation Framework
Red_T is a powerful Bluetooth security assessment and exploitation framework designed for penetration testers and red teams. It provides capabilities for device discovery, vulnerability assessment, stealthy connections, and remote control across multiple platforms (Android, iOS, Windows, Linux).

📌 Features
✅ Multi-Platform Support – Works with Android, iOS, Windows, and Linux
✅ Stealth Mode – Implements timing attacks to avoid detection
✅ Vulnerability Scanner – Detects known Bluetooth exploits automatically
✅ Remote Control – Execute commands and control target devices
✅ Web-Based UI – Control the framework from any browser
✅ Advanced Exploits – BLE attacks, MITM, firmware flashing, zero-click exploits

⚙️ Installation
1. Clone the Repository
bash
git clone https://github.com/llakterian/Red_T.git
cd Red_T
2. Set Up Python Virtual Environment
bash
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Configure Bluetooth Permissions
bash
sudo apt install libbluetooth-dev python3-dev
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(which python3)
5. Start the Server
bash
python web_ui/server.py
Access the UI at: http://localhost:5000

🚀 Usage
Basic Workflow
Scan for Devices – Discover nearby Bluetooth devices

Select Target – Choose a device from the list

Connect – Establish a stealthy connection

Execute Commands – Open apps, extract data, run exploits

Advanced Features
Zero-Click Exploits – Target devices without user interaction

MITM Attacks – Intercept Bluetooth communications

Firmware Flashing – Upload custom firmware to vulnerable devices

Keylogger – Capture keystrokes from compromised devices

🔧 Troubleshooting
Issue	Solution
Bluetooth not detected	Run sudo hciconfig hci0 up
Web UI not loading	Check firewall settings (port 5000)
No devices found	Ensure targets are in discoverable mode
Permission errors	Run with sudo or check setcap permissions
🤝 Contribute & Support
We welcome contributions! If you want to improve Red_T, feel free to:
🔹 Submit Pull Requests
🔹 Report Issues
🔹 Request Features

📧 Contact for Collaboration: llakterian@gmail.com

💖 Support the Project:
https://img.shields.io/badge/Donate-PayPal-blue
PayPal: cherusambu@gmail.com

⚠️ Legal & Ethical Use
This tool is for authorized security testing only. Unauthorized use against systems you don’t own is illegal.

📜 License: MIT

📌 Credits
Developed by Llakterian

🚀 Happy Hacking! 🚀

📌 Quick Start Command
bash
git clone https://github.com/llakterian/Red_T.git && cd Red_T && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python web_ui/server.py
Now open http://localhost:5000 in your browser! 🎉

