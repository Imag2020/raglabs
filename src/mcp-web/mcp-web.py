"""MCP SSE Server Example with FastAPI"""
from pydantic import BaseModel
from fastapi import FastAPI
from fastmcp import FastMCP
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import logging
import time
import random
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modèle pour la requête structurée
class NavigationRequest(BaseModel):
    url: str
    action: str = None  # "navigate", "type", "click", "scroll"
    selector: str = None  # CSS selector for actions
    value: str = None  # Value for type or scroll distance

# Modèle pour la réponse
class NavigationResult(BaseModel):
    title: str
    content_snippet: str
    url: str
    status: str

mcp: FastMCP = FastMCP("App")

# Gestion de l'instance Selenium
driver = None
driver_lock = Lock()

# Initialiser le driver
def initialize_driver():
    global driver
    if driver is None:
        hub_url = "http://magroune.net:4444/wd/hub"
        firefox_options = Options()
        firefox_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0")
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        try:
            driver = webdriver.Remote(command_executor=hub_url, options=firefox_options)
            driver.creation_time = time.time()  # Pour suivre l'inactivité
            logger.info("Selenium driver initialized successfully")
        except WebDriverException as e:
            logger.error(f"Failed to initialize driver: {e}")
            raise
    return driver

# Fermer le driver
def cleanup_driver():
    global driver
    with driver_lock:
        if driver:
            driver.quit()
            driver = None
            logger.info("Selenium driver closed")

# Navigate to url or perform actions
@mcp.tool()
async def navigate_to_url(input_data: str | dict) -> str:
    global driver
    with driver_lock:
        try:
            # Convertir l'entrée en NavigationRequest
            if isinstance(input_data, str):
                request = NavigationRequest(url=input_data)
            elif isinstance(input_data, dict):
                request = NavigationRequest(**input_data)
            else:
                raise ValueError("Input must be a string (URL) or a dictionary with 'url', 'action', etc.")

            logger.info(f"Received request: {request}")

            # Initialiser le driver si nécessaire
            if driver is None:
                initialize_driver()

            # Exécuter l'action demandée
            if request.action == "navigate" or request.action is None:
                driver.get(request.url)
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                logger.info(f"Navigated to {request.url}")
                # Simuler un comportement humain
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(random.uniform(1, 3))
                driver.execute_script("window.scrollBy(0, -200);")
                time.sleep(random.uniform(0.5, 2))

            # Détecter et gérer le CAPTCHA
            try:
                captcha = driver.find_element(By.ID, "recaptcha")
                logger.warning("CAPTCHA detected, waiting for manual resolution via VNC")
                time.sleep(30)  # Attendre l'intervention humaine
                WebDriverWait(driver, 60).until_not(
                    EC.presence_of_element_located((By.ID, "recaptcha"))
                )
                logger.info("CAPTCHA resolved, continuing")
            except NoSuchElementException:
                logger.info("No CAPTCHA detected")

            # Gérer les actions supplémentaires
            if request.action == "type":
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, request.selector)))
                element.clear()
                element.send_keys(request.value)
                logger.info(f"Typed '{request.value}' into {request.selector}")
            elif request.action == "click":
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, request.selector)))
                element.click()
                logger.info(f"Clicked on {request.selector}")
            elif request.action == "scroll":
                driver.execute_script(f"window.scrollBy(0, {request.value});")
                logger.info(f"Scrolled by {request.value} pixels")

            # Attendre le rendu
            time.sleep(5)

            # Gérer les pop-ups de cookies
            try:
                cookie_buttons = [
                    'button[id*="accept"], button[class*="accept"], button[id*="consent"], button[class*="consent"]',
                    'button[id*="agree"], button[class*="agree"]',
                    'button[id*="ok"], button[class*="ok"]',
                    'button[id*="autoriser"], button[class*="autoriser"]',
                    'button[id*="accepter"], button[class*="accepter"]',
                    'button:contains("Accept"), button:contains("Agree"), button:contains("OK"), button:contains("Consent"), button:contains("Accepter"), button:contains("J\'accepte"), button:contains("Autoriser")',
                    '[role="button"][aria-label*="accept"], [role="button"][aria-label*="consent"]'
                ]
                for selector in cookie_buttons:
                    try:
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                        for button in buttons:
                            if button.is_displayed():
                                text = button.text.lower()
                                if any(keyword in text for keyword in ['accept', 'agree', 'ok', 'consent', 'accepter', 'autoriser']):
                                    button.click()
                                    logger.info(f"Clicked cookie pop-up button: {text}")
                                    time.sleep(1.5)
                                    break
                        else:
                            continue
                        break
                    except NoSuchElementException:
                        continue
                else:
                    logger.info("No cookie pop-up detected")
            except Exception as e:
                logger.info(f"Error handling cookie pop-up: {e}")

            # Extraire le contenu
            title = driver.title
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            for element in soup(['script', 'style', 'iframe', 'nav', 'footer', 'aside', '[class*="ad"], [id*="ad"]']):
                element.decompose()
            content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'div', 'span', 'li', 'article', 'section'],
                                          class_=lambda x: x and not any(keyword in x.lower() for keyword in ['ad', 'advert', 'banner', 'promo']))
            text_parts = [element.get_text(separator=' ', strip=True) for element in content_elements if element.get_text(strip=True) and len(element.get_text().split()) > 5]
            content = ' '.join(text_parts) if text_parts else soup.get_text(separator=' ', strip=True)
            content = ' '.join(content.split())
            if "unusual traffic" in content.lower():
                logger.warning("Page blocked by CAPTCHA or traffic detection")
                return f"Failed to extract content due to CAPTCHA or traffic block\nURL: {request.url}"

            logger.info(f"Extracted content length: {len(content)} characters")
            driver.save_screenshot("/home/seluser/output/screenshot.png")
            logger.info("Screenshot saved to /home/seluser/output/screenshot.png")

            result = NavigationResult(title=title, content_snippet=content, url=request.url, status="success")
            return f"Page Title: {result.title}\nContent: {result.content_snippet}\nURL: {result.url}\nStatus: {result.status}"

        except Exception as e:
            logger.error(f"Error processing {request.url}: {e}")
            result = NavigationResult(title="", content_snippet="", url=request.url, status="error")
            return f"Failed to process {request.url}: {str(e)}\nStatus: {result.status}"

        finally:
            pass

# Outil pour fermer le navigateur manuellement
@mcp.tool()
async def close_browser() -> str:
    global driver
    with driver_lock:
        cleanup_driver()
        return "Browser closed successfully"

# Create FastAPI app and mount the SSE MCP server
app = FastAPI()
app.mount("/", mcp.sse_app())

