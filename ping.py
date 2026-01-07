import socket
import time

def test_ping(host="8.8.8.8", port=53, timeout=2):
    s = None
    try:
        addr = socket.getaddrinfo(host, port)[0][-1]
        s = socket.socket()
        s.settimeout(timeout)
        start = time.ticks_ms()
        s.connect(addr)
        rtt = time.ticks_diff(time.ticks_ms(), start)
        print("Ping OK ({}ms)".format(rtt))
        return True
    except Exception as e:
        print("Ping failed:", e)
        return False
    finally:
        if s:
            s.close()
