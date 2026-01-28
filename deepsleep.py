import machine
import esp32
import time

class DeepSleepManager:
    """Deep Sleep Manager for ESP32 power conservation"""
    
    # Wake-up reasons
    WAKE_REASONS = {
        machine.DEEPSLEEP_RESET: "Deep Sleep",
        machine.SOFT_RESET: "Soft Reset", 
        machine.PWRON_RESET: "Power On",
        machine.HARD_RESET: "Hard Reset",
        machine.WDT_RESET: "Watchdog",
        machine.DEEPSLEEP: "Deep Sleep Timer"
    }
    
    def __init__(self, wake_pin=None):
        """
        Initialize Deep Sleep Manager
        
        Args:
            wake_pin: Optional GPIO pin number for external wake-up (e.g., button)
        """
        self.wake_pin = wake_pin
        
    def get_wake_reason(self):
        """Get the reason for the last wake-up"""
        reason = machine.reset_cause()
        return self.WAKE_REASONS.get(reason, "Unknown ({})".format(reason))
    
    def was_deep_sleep_wake(self):
        """Check if device woke from deep sleep"""
        return machine.reset_cause() == machine.DEEPSLEEP_RESET
    
    def configure_timer_wake(self, sleep_ms):
        """
        Configure timer-based wake-up
        
        Args:
            sleep_ms: Sleep duration in milliseconds
        """
        self.sleep_duration = sleep_ms
        
    def configure_ext_wake(self, pin, level=esp32.WAKEUP_ANY_HIGH):
        """
        Configure external pin wake-up
        
        Args:
            pin: GPIO pin number (must be RTC GPIO: 0,2,4,12-15,25-27,32-39)
            level: esp32.WAKEUP_ANY_HIGH or esp32.WAKEUP_ALL_LOW
        """
        self.wake_pin = pin
        wake_pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN)
        esp32.wake_on_ext0(wake_pin, level)
        print("External wake configured on GPIO{}".format(pin))
    
    def sleep_ms(self, duration_ms):
        """
        Enter deep sleep for specified milliseconds
        
        Args:
            duration_ms: Sleep duration in milliseconds (1000ms = 1 second)
        """
        print("Entering deep sleep for {}ms...".format(duration_ms))
        time.sleep(0.1)  # Allow print to complete
        machine.deepsleep(duration_ms)
    
    def sleep_seconds(self, duration_s):
        """
        Enter deep sleep for specified seconds
        
        Args:
            duration_s: Sleep duration in seconds
        """
        self.sleep_ms(duration_s * 1000)
    
    def sleep_minutes(self, duration_min):
        """
        Enter deep sleep for specified minutes
        
        Args:
            duration_min: Sleep duration in minutes
        """
        self.sleep_ms(duration_min * 60 * 1000)
    
    def sleep_until_ext_wake(self):
        """Enter deep sleep until external pin triggers wake-up"""
        if self.wake_pin is None:
            print("Error: No wake pin configured. Use configure_ext_wake() first.")
            return
        print("Entering deep sleep until GPIO{} triggers...".format(self.wake_pin))
        time.sleep(0.1)
        machine.deepsleep()
    
    def light_sleep_ms(self, duration_ms):
        """
        Enter light sleep (faster wake-up, slightly higher power than deep sleep)
        
        Args:
            duration_ms: Sleep duration in milliseconds
        """
        print("Entering light sleep for {}ms...".format(duration_ms))
        time.sleep(0.1)
        machine.lightsleep(duration_ms)
        print("Woke from light sleep")


def print_wake_info():
    """Print information about the wake-up reason"""
    dsm = DeepSleepManager()
    print("Wake reason:", dsm.get_wake_reason())
    if dsm.was_deep_sleep_wake():
        print("Device woke from deep sleep")


def test_deep_sleep(sleep_seconds=10):
    """Test deep sleep functionality"""
    print("\n=== Deep Sleep Test ===")
    print_wake_info()
    
    print("\nWill enter deep sleep for {} seconds...".format(sleep_seconds))
    print("Device will restart after wake-up.")
    time.sleep(2)
    
    dsm = DeepSleepManager()
    dsm.sleep_seconds(sleep_seconds)


def sleep_after_reading(sensor, sleep_minutes=5):
    """
    Take a sensor reading then enter deep sleep
    Useful for battery-powered sensor nodes
    
    Args:
        sensor: DHT22Sensor instance
        sleep_minutes: Minutes to sleep between readings
    """
    print("\n=== Low Power Sensor Mode ===")
    
    dsm = DeepSleepManager()
    print("Wake reason:", dsm.get_wake_reason())
    
    # Take reading
    if sensor:
        print("\nReading sensor...")
        data = sensor.get_readings()
        if data:
            print("Temperature: {:.1f}°C".format(data['temperature']))
            print("Humidity: {:.1f}%".format(data['humidity']))
            # Here you could send data via WiFi, MQTT, etc.
        else:
            print("Sensor read failed")
    
    # Sleep
    print("\nSleeping for {} minutes...".format(sleep_minutes))
    dsm.sleep_minutes(sleep_minutes)
