import zipfile
import os
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth Extension",
        "permissions": ["proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
        }}
    }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_user}",
                    password: "{proxy_pass}"
                }}
            }};
        }},
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """

    pluginfile = "proxy_auth_plugin.zip"
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return pluginfile

def scrape_website(website):
    proxy_host = "brd.superproxy.io"
    proxy_port = 33335
    proxy_user = "brd-customer-hl_2d101aa5-zone-ai_scraper"
    proxy_pass = "05yb57u8vz65"

    proxy_extension = create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass)

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")
    options.add_extension(proxy_extension)

    driver = uc.Chrome(options=options)

    try:
        driver.get(website)
        
        return driver.page_source
    except Exception as e:
        return f"<b>Error loading page:</b> {str(e)}"
    finally:
        driver.quit()
        os.remove(proxy_extension)  # Clean up the extension zip


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def cleaned_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    
    for script_or_style in soup(["script", 'style']):
        script_or_style.extract()


    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()          
    )

    return cleaned_content


def split_dom_content(dom_content, max_length = 6000):
    return [
        dom_content[i:i + max_length] for i in range(0, len(dom_content), max_length)
    ]
