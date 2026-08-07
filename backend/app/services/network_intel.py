import socket
import ssl
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import urllib.parse
import requests
import urllib3
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# Disable insecure request warning logs from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("app.services.network_intel")


class NetworkIntelService:
    @staticmethod
    def extract_host(url: str) -> str:
        """
        Extract hostname from a given URL.
        """
        parsed = urllib.parse.urlparse(url)
        # If no scheme was present, urlparse might put the domain in the path
        netloc = parsed.netloc or parsed.path.split('/')[0]
        # Split port if present
        host = netloc.split(':')[0]
        return host

    def get_ip_and_dns(self, hostname: str) -> Dict[str, Any]:
        """
        Resolve IP address and perform reverse DNS lookup (PTR).
        """
        data = {
            "ip_address": None,
            "reverse_dns": None
        }
        try:
            ip = socket.gethostbyname(hostname)
            data["ip_address"] = ip
            
            # Reverse DNS lookup
            try:
                ptr = socket.gethostbyaddr(ip)[0]
                data["reverse_dns"] = ptr
            except (Exception, requests.RequestException, socket.error, ssl.SSLError) as e:
                logger.debug(f"Reverse DNS lookup failed for IP {ip}: {e}")
        except (Exception, requests.RequestException, socket.error, ssl.SSLError) as e:
            logger.warning(f"IP resolution failed for host {hostname}: {e}")
        return data

    def extract_ssl_cert(self, hostname: str) -> Dict[str, Any]:
        """
        Retrieve SSL/TLS certificate metadata connecting to port 443.
        """
        data = {
            "ssl_available": False,
            "issuer": None,
            "subject": None,
            "common_name": None,
            "sans": [],
            "valid_from": None,
            "valid_until": None,
            "days_until_expiry": None,
            "signature_algorithm": None,
            "tls_version": None,
            "cipher_suite": None
        }

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        try:
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    data["ssl_available"] = True
                    data["tls_version"] = ssock.version()
                    
                    cipher_info = ssock.cipher()
                    if cipher_info:
                        data["cipher_suite"] = cipher_info[0]

                    bin_cert = ssock.getpeercert(binary_form=True)
                    if bin_cert:
                        cert = x509.load_der_x509_certificate(bin_cert, default_backend())
                        data["subject"] = str(cert.subject)
                        data["issuer"] = str(cert.issuer)

                        # Extract Common Name (CN)
                        for attribute in cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME):
                            data["common_name"] = str(attribute.value)

                        # Extract Validity Dates & Expiry
                        try:
                            valid_from = cert.not_valid_before_utc
                            valid_until = cert.not_valid_after_utc
                        except AttributeError:
                            valid_from = cert.not_valid_before.replace(tzinfo=timezone.utc)
                            valid_until = cert.not_valid_after.replace(tzinfo=timezone.utc)

                        data["valid_from"] = valid_from.isoformat()
                        data["valid_until"] = valid_until.isoformat()
                        
                        now = datetime.now(timezone.utc)
                        days = (valid_until - now).days
                        data["days_until_expiry"] = days

                        # Signature Algorithm
                        try:
                            data["signature_algorithm"] = cert.signature_algorithm_oid.friendly_name
                        except Exception:
                            data["signature_algorithm"] = str(cert.signature_algorithm_oid)

                        # Subject Alternative Names (SANs)
                        try:
                            ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                            data["sans"] = ext.value.get_values_for_type(x509.DNSName)
                        except Exception:
                            pass
        except (Exception, requests.RequestException, socket.error, ssl.SSLError) as e:
            logger.debug(f"SSL cert extraction failed for {hostname}: {e}")
            data["status"] = "unreachable"
            data["error"] = str(e)

        return data

    def extract_http_characteristics(self, url: str) -> Dict[str, Any]:
        """
        Request HTTP headers and details to track redirects and status codes.
        """
        data = {
            "status_code": None,
            "redirect_chain": [],
            "final_url": url
        }
        try:
            # We use a standard user-agent to simulate a user request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            # verify=False is needed to query insecure or self-signed/expired targets safely
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=False)
            data["status_code"] = response.status_code
            data["final_url"] = response.url
            data["redirect_chain"] = [req.url for req in response.history]
        except (Exception, requests.RequestException, socket.error, ssl.SSLError) as e:
            logger.warning(f"HTTP GET check failed for {url}: {e}")
            data["status"] = "unreachable"
            data["error"] = str(e)
        return data

    def extract_network_intelligence(self, url: str) -> Dict[str, Any]:
        """
        Gathers IP/DNS details, SSL/TLS certificate parameters, and HTTP response headers.
        """
        try:
            hostname = self.extract_host(url)
            
            # Ensure scheme is present for http requests
            http_url = url
            if not http_url.lower().startswith(("http://", "https://")):
                http_url = f"https://{url}"

            ip_dns = self.get_ip_and_dns(hostname)
            ssl_data = self.extract_ssl_cert(hostname)
            http_data = self.extract_http_characteristics(http_url)

            return {
                "url": http_url,
                "host": hostname,
                "dns_resolution": ip_dns,
                "ssl_cert": ssl_data,
                "http_characteristics": http_data
            }
        except (Exception, requests.RequestException, socket.error, ssl.SSLError) as e:
            logger.error(f"NetworkIntelService failed for {url}: {e}")
            return {
                "url": url,
                "status": "unreachable",
                "error": str(e),
                "dns_resolution": {"ip_address": None, "reverse_dns": None},
                "ssl_cert": {
                    "ssl_available": False,
                    "issuer": None,
                    "subject": None,
                    "common_name": None,
                    "sans": [],
                    "valid_from": None,
                    "valid_until": None,
                    "days_until_expiry": None,
                    "signature_algorithm": None,
                    "tls_version": None,
                    "cipher_suite": None
                },
                "http_characteristics": {
                    "status_code": None,
                    "redirect_chain": [],
                    "final_url": url
                }
            }

