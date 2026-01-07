import network
import time
import machine
import gc

SSID = "SIJA-WAN"
PASSWORD = "12345678"

def wifi_connect(timeout_s=15, retries=3, reboot_on_fail=False):
    wlan = network.WLAN(network.STA_IF)

    for attempt in range(1, retries + 1):
        try:
            # Reset Wi-Fi state
            wlan.active(False)
            time.sleep(0.3)
            gc.collect()

            wlan.active(True)
            time.sleep(0.3)

            # Check if already connected
            if wlan.isconnected():
                print("Already connected. IP:", wlan.ifconfig()[0])
                return wlan

            print("Connecting... (attempt {}/{})".format(attempt, retries))
            wlan.connect(SSID, PASSWORD)

            # Wait for connection
            start = time.ticks_ms()
            while not wlan.isconnected():
                if time.ticks_diff(time.ticks_ms(), start) > (timeout_s * 1000):
                    print("Timeout")
                    break
                time.sleep(0.1)

            if wlan.isconnected():
                print("Connected. IP:", wlan.ifconfig()[0])
                return wlan

        except OSError as e:
            print("OSError:", e)
            time.sleep(0.5)

    print("Failed after {} retries".format(retries))
    if reboot_on_fail:
        print("Rebooting...")
        time.sleep(1)
        machine.reset()
    return None
