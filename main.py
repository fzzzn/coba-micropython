from wifi import wifi_connect
from ping import test_ping
from dht22 import DHT22Sensor
import socket
from machine import Pin
import gc

# Setup built-in LED (GPIO2 for most ESP32 boards)
led = Pin(2, Pin.OUT)
led.value(0)  # Start with LED off

# Setup DHT22 sensor 
sensor = DHT22Sensor(pin=4)
# sensor = None  # Disabled 

# HTML template as const to save memory
HTML_TEMPLATE = '''<!DOCTYPE html><html><head><title>ESP32 Dashboard</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:Arial;text-align:center;margin:50px;background:#f0f0f0}.container{background:#fff;padding:30px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,.1);max-width:400px;margin:0 auto}h1{color:#333;margin-bottom:10px}h2{color:#666;font-size:18px;margin-top:30px;margin-bottom:15px}.status{font-size:24px;margin:20px 0;padding:15px;border-radius:5px;transition:all .3s}.sensor{display:flex;justify-content:space-around;margin:20px 0}.sensor-box{flex:1;padding:15px;margin:0 5px;background:#e8f4f8;border-radius:5px}.sensor-label{font-size:12px;color:#666;text-transform:uppercase}.sensor-value{font-size:28px;font-weight:bold;color:#333;margin:10px 0}.sensor-unit{font-size:14px;color:#999}.button{padding:20px 40px;font-size:20px;color:#fff;border:none;border-radius:5px;cursor:pointer;transition:all .3s;font-weight:bold}.button:hover{opacity:.8;transform:scale(1.05)}</style></head><body><div class="container"><h1>ESP32 Dashboard</h1><h2>Sensor Data</h2><div class="sensor"><div class="sensor-box"><div class="sensor-label">Temperature</div><div class="sensor-value" id="temp">--</div><div class="sensor-unit">C</div></div><div class="sensor-box"><div class="sensor-label">Humidity</div><div class="sensor-value" id="humidity">--</div><div class="sensor-unit">%</div></div></div><h2>LED Control</h2><div class="status" id="status">LED: <strong id="state">...</strong></div><button class="button" id="toggleBtn" onclick="toggle()">Toggle</button></div><script>function toggle(){fetch('/toggle').then(r=>r.json()).then(updateUI)}function updateUI(d){let st=d.state;document.getElementById('state').textContent=st?'ON':'OFF';document.getElementById('status').style.background=st?'#d4edda':'#f8d7da';let btn=document.getElementById('toggleBtn');btn.textContent=st?'Turn OFF':'Turn ON';btn.style.background=st?'#dc3545':'#28a745';if(d.temp!==null)document.getElementById('temp').textContent=d.temp.toFixed(1);if(d.humidity!==null)document.getElementById('humidity').textContent=d.humidity.toFixed(1)}function poll(){fetch('/status').then(r=>r.json()).then(updateUI).catch(e=>console.log(e))}setInterval(poll,2000);poll()</script></body></html>'''


def get_json_status():
    """Return LED status and sensor data as JSON"""
    # Try to read sensor data
    temp = None
    humidity = None
    if sensor:  # Only read if sensor is enabled
        try:
            if sensor.read():
                temp = sensor.last_temp
                humidity = sensor.last_humidity
        except:
            pass
    
    return '{"state":%s,"temp":%s,"humidity":%s}' % (
        'true' if led.value() else 'false',
        temp if temp is not None else 'null',
        humidity if humidity is not None else 'null'
    )


def start_web_server():
    """Start web server on port 80"""
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print('Web server listening on port 80')

    while True:
        cl = None
        try:
            cl, addr = s.accept()
            cl.settimeout(3.0)

            # Read request efficiently
            request = cl.recv(512).decode('utf-8', 'ignore')

            # Parse and handle request
            if 'GET /toggle' in request:
                led.value(not led.value())
                response = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n' + get_json_status()
            elif 'GET /status' in request:
                response = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n' + get_json_status()
            else:
                # Serve main HTML page
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n' + HTML_TEMPLATE
            
            cl.sendall(response)

        except OSError:
            pass  # Timeout or connection error
        finally:
            if cl:
                try:
                    cl.close()
                except:
                    pass
            gc.collect()  # Free memory after each request


# Main execution
gc.collect()
print("Starting ESP32 LED Web Server...")
wlan = wifi_connect(retries=5, reboot_on_fail=True)

if wlan and wlan.isconnected():
    test_ping()
    ip = wlan.ifconfig()[0]
    print("\n" + "="*40)
    print("Web interface: http://{}".format(ip))
    print("="*40 + "\n")
    start_web_server()
else:
    print("Failed to connect. Cannot start server.")
