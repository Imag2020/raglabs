from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastmcp import FastMCP
import pyautogui
import logging
import base64
import pyperclip
import time
import os
from PIL import Image
import io
import keyboard
import json
import subprocess
import platform
import psutil
import pdfkit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modified response model without screenshot_base64
class ActionResult(BaseModel):
    status: str
    page_content: str = ""
    details: str = ""

# New model for screenshot response
class ScreenshotResult(BaseModel):
    status: str
    screenshot_base64: str
    details: str = ""

# Create FastAPI app and FastMCP instance
mcp: FastMCP = FastMCP("App")

def activate_or_launch_browser():
    system = platform.system()
    browser_commands = {
        "Windows": ["start", "chrome"],
        "Darwin": ["open", "-a", "Google Chrome"],
        "Linux": ["google-chrome"]
    }
    try:
        chrome_running = any("chrome" in p.name().lower() for p in psutil.process_iter(['name']))
        if chrome_running:
            # Try to bring Chrome to foreground
            if system == "Windows":
                subprocess.run(["powershell", "-Command", "(New-Object -ComObject WShell).SendKeys('%{Tab}')"], shell=True)
            elif system == "Darwin":
                subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
            elif system == "Linux":
                subprocess.run(["wmctrl", "-a", "Google Chrome"])
            time.sleep(1)
            pyautogui.hotkey("ctrl", "t"); time.sleep(0.5)
            return True
        else:
            command = browser_commands.get(system)
            if command:
                subprocess.run(command, shell=(system == "Windows"), check=False)
                time.sleep(3)
                return True
            else:
                raise RuntimeError(f"Unsupported platform: {system}")
    except Exception as e:
        logger.error(f"Error activating or launching browser: {e}")
        return False

@mcp.tool(description="Ouvre un navigateur sur une URL spécifiée et retourne le contenu textuel de la page.")
async def open_browser_and_capture(
    url: str = Field(..., description="L'URL complète à laquelle naviguer (ex: 'https://www.google.com').")
) -> str:
    """
    Ouvre un navigateur sur une URL et retourne le contenu textuel.
    """
    try:
        logger.info(f"Received request to navigate to: {url}")

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        if not activate_or_launch_browser():
            raise RuntimeError("Failed to activate or launch browser")

        pyautogui.hotkey("ctrl", "t"); time.sleep(1)
        pyautogui.write(url); pyautogui.press("enter")
        logger.info(f"Navigated to {url}"); time.sleep(5)

        page_content = ""
        try:
            pyautogui.hotkey("ctrl", "a"); time.sleep(0.5)
            pyautogui.hotkey("ctrl", "c"); time.sleep(0.5)
            page_content = pyperclip.paste()
            pyautogui.click(x=50, y=50); time.sleep(0.5)
        except Exception as e:
            logger.warning(f"Failed to extract page content: {e}")

        result = ActionResult(
            status="success",
            page_content=page_content,
            details=f"Navigated to {url}"
        )
        return result.model_dump_json()

    except Exception as e:
        logger.error(f"Error processing {url}: {e}")
        result = ActionResult(status="error", page_content="", details=str(e))
        return result.model_dump_json()

@mcp.tool(description="Clique à des coordonnées spécifiées ou sur un bouton identifié par une image.")
async def click_on_screen(
    x: float | None = Field(default=None, description="Coordonnée X (horizontale) pour le clic."),
    y: float | None = Field(default=None, description="Coordonnée Y (verticale) pour le clic."),
    image_name: str | None = Field(default=None, description="Nom du fichier image à trouver sur l'écran pour cliquer dessus (ex: 'bouton_accepter.png').")
) -> str:
    """
    Clique sur l'écran à des coordonnées ou sur une image.
    """
    try:
        logger.info(f"Received click request with x={x}, y={y}, image_name='{image_name}'")

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

        details = ""
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y)
            details = f"Clicked at coordinates ({x}, {y})"
        elif image_name:
            button_location = pyautogui.locateOnScreen(image_name, confidence=0.8)
            if button_location:
                pyautogui.click(button_location)
                details = f"Clicked on button from image {image_name}"
            else:
                raise ValueError(f"Button image '{image_name}' not found on screen")
        else:
            raise ValueError("Click request must provide either coordinates (x, y) ou une image_name")
        logger.info(details)

        time.sleep(1)
        result = ActionResult(status="success", details=details)
        return result.model_dump_json()

    except Exception as e:
        logger.error(f"Error during click action: {e}")
        result = ActionResult(status="error", details=str(e))
        return result.model_dump_json()

@mcp.tool(description="Génère un PDF de la fenêtre active du navigateur.")
async def save_as_pdf(
    output_path: str = Field(..., description="Chemin du fichier où sauvegarder le PDF (ex: 'output.pdf').")
) -> str:
    """
    Génère un PDF de la fenêtre active du navigateur.
    """
    try:
        logger.info(f"Received request to save PDF to: {output_path}")

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

        if not activate_or_launch_browser():
            raise RuntimeError("Failed to activate or launch browser")

        # Ensure browser is in focus
        system = platform.system()
        if system == "Windows":
            subprocess.run(["powershell", "-Command", "(New-Object -ComObject WShell).SendKeys('%{Tab}')"], shell=True)
        elif system == "Darwin":
            subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
        elif system == "Linux":
            subprocess.run(["wmctrl", "-a", "Google Chrome"])
        time.sleep(1)

        # Click in a safe area to ensure focus
        pyautogui.click(x=50, y=50)
        time.sleep(0.5)

        # Open print dialog
        if system == "Darwin":
            pyautogui.hotkey("command", "p")
        else:
            pyautogui.hotkey("ctrl", "p")
        time.sleep(2)

        # Handle print dialog
        pyautogui.write(output_path)
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(2)

        # Verify if file was created
        if os.path.exists(output_path):
            result = ActionResult(
                status="success",
                details=f"PDF saved to {output_path}"
            )
        else:
            raise RuntimeError("PDF file was not created")

        return result.model_dump_json()

    except Exception as e:
        logger.error(f"Error saving PDF: {e}")
        result = ActionResult(status="error", details=str(e))
        return result.model_dump_json()

@mcp.tool(description="Prend une capture d'écran de la fenêtre active et retourne l'image en base64.")
async def screenshot() -> str:
    """
    Prend une capture d'écran et retourne l'image en base64.
    """
    try:
        logger.info("Received request to take screenshot")

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

        screenshot = pyautogui.screenshot()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        screenshot_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        result = ScreenshotResult(
            status="success",
            screenshot_base64=screenshot_base64,
            details="Screenshot captured successfully"
        )
        return result.model_dump_json()

    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}")
        result = ScreenshotResult(status="error", screenshot_base64="", details=str(e))
        return result.model_dump_json()

app = FastAPI()
app.mount("/", mcp.sse_app())