import socket
import concurrent.futures
from services import COMMON_PORTS

class PortScanner:
    def __init__(self, target, ports, timeout=1.0, threads=100):
        self.target = target
        self.ports = ports
        self.timeout = timeout
        self.threads = threads
        self.results = []
        self.target_ip = None
        try:
            self.target_ip = socket.gethostbyname(target)
        except socket.gaierror:
            self.target_ip = None

    def scan_port(self, port):
        service = COMMON_PORTS.get(port, "Unknown")
        status = "FILTERED"
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.target_ip, port))
                
                if result == 0:
                    status = "OPEN"
                elif result in (10061, 111, 61):  # Common connection refused codes across OS
                    status = "CLOSED"
                else:
                    # Treat other error codes as filtered/closed depending on OS behaviour
                    status = "CLOSED" if result != 0 else "OPEN"
        except socket.timeout:
            status = "FILTERED"
        except Exception:
            status = "FILTERED"
            
        return {'port': port, 'status': status, 'service': service}

    def run(self, progress_callback=None):
        if not self.target_ip:
            return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_port = {executor.submit(self.scan_port, port): port for port in self.ports}
            for future in concurrent.futures.as_completed(future_to_port):
                res = future.result()
                self.results.append(res)
                if progress_callback:
                    progress_callback()
                    
        # Sort results by port number
        self.results.sort(key=lambda x: x['port'])
        return True
