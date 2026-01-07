import dht
from machine import Pin
import time

class DHT22Sensor:
    """DHT22 Temperature and Humidity Sensor Reader"""
    
    def __init__(self, pin=4):
        """Initialize DHT22 sensor on specified GPIO pin (default: GPIO4)"""
        self.sensor = dht.DHT22(Pin(pin))
        self.last_temp = None
        self.last_humidity = None
        self.last_read_time = 0
        
    def read(self):
        """Read temperature and humidity from sensor"""
        try:
            self.sensor.measure()
            self.last_temp = self.sensor.temperature()
            self.last_humidity = self.sensor.humidity()
            self.last_read_time = time.ticks_ms()
            return True
        except OSError as e:
            print("DHT22 read error:", e)
            return False
    
    def get_temperature(self, unit='C'):
        """Get temperature in Celsius or Fahrenheit"""
        if self.last_temp is None:
            if not self.read():
                return None
        
        if unit == 'F':
            return (self.last_temp * 9/5) + 32
        return self.last_temp
    
    def get_humidity(self):
        """Get relative humidity percentage"""
        if self.last_humidity is None:
            if not self.read():
                return None
        return self.last_humidity
    
    def get_readings(self):
        """Get both temperature and humidity as dictionary"""
        if self.read():
            return {
                'temperature': self.last_temp,
                'humidity': self.last_humidity,
                'timestamp': self.last_read_time
            }
        return None
    
    def print_readings(self):
        """Print current sensor readings"""
        data = self.get_readings()
        if data:
            print("Temperature: {:.1f}°C".format(data['temperature']))
            print("Humidity: {:.1f}%".format(data['humidity']))
        else:
            print("Failed to read sensor")


def test_sensor(pin=4, interval=2, count=5):
    """Test DHT22 sensor by reading multiple times"""
    print("Testing DHT22 sensor on GPIO{}".format(pin))
    sensor = DHT22Sensor(pin)
    
    for i in range(count):
        print("\nReading {}/{}:".format(i+1, count))
        sensor.print_readings()
        if i < count - 1:
            time.sleep(interval)
    
    print("\nTest complete!")
