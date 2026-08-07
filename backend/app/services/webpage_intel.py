import logging
import urllib.parse
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import tldextract
import socket
import ssl

logger = logging.getLogger("app.services.webpage_intel")

class WebpageIntelService:
    def is_external(self, target_url: str, base_domain: str) -> bool:
        """
        Check if a link/resource is external relative to base_domain.
        Relative URLs are assumed internal.
        """
        if not target_url:
            return False
        trimmed = target_url.strip()
        if not trimmed.startswith(("http://", "https://", "//")):
            # Relative path implies internal
            return False
        
        try:
            full_url = trimmed
            if trimmed.startswith("//"):
                full_url = "https:" + trimmed
            
            extracted = tldextract.extract(full_url)
            target_domain = f"{extracted.domain}.{extracted.suffix}"
            
            return target_domain.lower() != base_domain.lower()
        except Exception:
            return True

    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from the given URL. Handles timeouts and non-200 responses safely.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            # verify=False is needed to bypass SSL failures on untrusted threat sites
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to fetch webpage content for {url}: Status code {response.status_code}")
                return None
        except (Exception, requests.RequestException, socket.error, ssl.SSLError) as e:
            logger.warning(f"Failed to fetch webpage content for {url}: {e}")
            return None

    def extract_webpage_intelligence(self, url: str) -> Dict[str, Any]:
        """
        Extract page characteristics: metadata, form structure, resources, and links.
        """
        data = {
            "metadata": {
                "title": None,
                "meta_description": None,
                "meta_keywords": None,
                "language": None,
                "favicon_url": None,
                "canonical_url": None,
                "og_metadata": {}
            },
            "structure": {
                "total_forms": 0,
                "has_password_field": False,
                "is_login_form_detected": False
            },
            "resources": {
                "js_count": 0,
                "css_count": 0,
                "images_count": 0,
                "external_resources": 0,
                "internal_resources": 0
            },
            "links": {
                "external_links": 0,
                "internal_links": 0
            }
        }

        try:
            html = self.fetch_html(url)
            if not html:
                data["status"] = "unreachable"
                data["error"] = "Failed to fetch HTML content (host offline or request timeout)"
                return data

            soup = BeautifulSoup(html, "html.parser")
            
            # Base domain for internal/external comparison
            extracted_base = tldextract.extract(url)
            base_domain = f"{extracted_base.domain}.{extracted_base.suffix}"


            # 1. Metadata extraction
            if soup.title:
                data["metadata"]["title"] = soup.title.get_text(strip=True)

            html_tag = soup.find("html")
            if html_tag and html_tag.has_attr("lang"):
                data["metadata"]["language"] = html_tag["lang"]

            for meta in soup.find_all("meta"):
                # Meta description & keywords
                name = meta.get("name", "").lower()
                content = meta.get("content")
                if content:
                    if name == "description":
                        data["metadata"]["meta_description"] = content
                    elif name == "keywords":
                        data["metadata"]["meta_keywords"] = content
                
                # Open Graph meta tags
                property_attr = meta.get("property", "").lower()
                if property_attr.startswith("og:") and content:
                    data["metadata"]["og_metadata"][property_attr] = content

            # Canonical link
            canonical = soup.find("link", rel="canonical")
            if canonical and canonical.has_attr("href"):
                data["metadata"]["canonical_url"] = canonical["href"]

            # Favicon url
            favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
            if favicon and favicon.has_attr("href"):
                fav_href = favicon["href"]
                # Resolve favicon url if relative
                data["metadata"]["favicon_url"] = urllib.parse.urljoin(url, fav_href)

            # 2. Form structures
            forms = soup.find_all("form")
            data["structure"]["total_forms"] = len(forms)
            
            for form in forms:
                # Presence of password fields
                pwd_input = form.find("input", type="password")
                if pwd_input:
                    data["structure"]["has_password_field"] = True
                
                # Login form detection heuristic check
                form_action = form.get("action", "").lower()
                form_class = " ".join(form.get("class", [])).lower()
                form_id = form.get("id", "").lower()
                
                # Input field names check
                input_indicators = False
                for inp in form.find_all("input"):
                    inp_name = inp.get("name", "").lower()
                    inp_id = inp.get("id", "").lower()
                    if any(term in inp_name or term in inp_id for term in ["username", "email", "login", "password", "signin"]):
                        input_indicators = True

                form_indicators = any(
                    term in form_action or term in form_class or term in form_id
                    for term in ["login", "signin", "auth", "session"]
                )

                if form_indicators or (pwd_input and input_indicators):
                    data["structure"]["is_login_form_detected"] = True

            # 3. Resources extraction
            # JS Scripts
            scripts = soup.find_all("script")
            js_src_list = [s["src"] for s in scripts if s.has_attr("src")]
            data["resources"]["js_count"] = len(js_src_list)

            # CSS Styles
            css_links = soup.find_all("link", rel=lambda x: x and "stylesheet" in x.lower())
            css_href_list = [c["href"] for c in css_links if c.has_attr("href")]
            data["resources"]["css_count"] = len(css_href_list)

            # Images
            imgs = soup.find_all("img")
            img_src_list = [i["src"] for i in imgs if i.has_attr("src")]
            data["resources"]["images_count"] = len(img_src_list)

            # Classify resources as internal/external
            all_resources = js_src_list + css_href_list + img_src_list
            for res in all_resources:
                if self.is_external(res, base_domain):
                    data["resources"]["external_resources"] += 1
                else:
                    data["resources"]["internal_resources"] += 1

            # 4. Links extraction
            anchors = soup.find_all("a")
            for a in anchors:
                href = a.get("href")
                if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    if self.is_external(href, base_domain):
                        data["links"]["external_links"] += 1
                    else:
                        data["links"]["internal_links"] += 1

        except (Exception, requests.RequestException, socket.error, ssl.SSLError) as e:
            logger.error(f"HTML parsing failed for {url}: {e}")
            data["status"] = "unreachable"
            data["error"] = str(e)

        return data
