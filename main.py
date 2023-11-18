import asyncio
import re
import os
import logging

from pyppeteer import launch
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USER")
PIN = os.getenv("PIN")

if not USERNAME or not PIN:
    raise ValueError("Environment variables USER and PIN must be set")

logging.basicConfig(level=logging.INFO)


async def wait_for_element_reload(page, element: str):
    """Waits for element to appear.
    Args:
        page: the page in which element will appear
        element: class for the element being looked for
    Returns:
        The element
    """
    button = None

    while not button:
        await page.reload()
        button = await page.querySelector(element)

    return button


async def main(comp_id, tee_time):
    """
    This function automates the process of signing up for a golf competition on the St. Annes Old Links website.

    Parameters:
    comp_id (str): The ID of the competition.
    tee_time (str): The desired tee time for signing up.

    Returns:
    None
    """
    browser = await launch({"headless": False})
    page = await browser.newPage()
    await page.goto("https://www.stannesoldlinks.com/login.php")

    # find and enter username
    username = await page.querySelector("#memberid")
    await username.type(USERNAME)

    # find and enter pin number
    pin = await page.querySelector("#pin")
    await pin.type(PIN)
    await page.keyboard.press("Enter")

    # Navigate to competition page
    await page.goto(
        f"https://www.stannesoldlinks.com/competition2.php?tab=details&compid={comp_id}"
    )
    signUp_btn = await wait_for_element_reload(page, ".comp-signup-button")
    print("Sign up button found")
    await signUp_btn.click()
    print("Sign up button clicked")

    await page.waitFor(1000)

    tds = await page.querySelectorAll("td")
    for td in tds:
        text_handle = await td.getProperty("textContent")
        text = await text_handle.jsonValue()
        print(text)
        if text == f"{tee_time}":
            nextElementSibling = await td.getProperty("nextElementSibling")
            link = await nextElementSibling.querySelector("a")
            await link.click()
            print(
                "Tee time selected, now please login, navigate to competition and add playing partners"
            )
            break
        else:
            print("not found")

    await page.waitForNavigation()


competition_id = input("What is the competition ID? ")

while not re.match(r"^\d{5}$", competition_id):
    print("Invalid input. The competition ID should be exactly 5 digits.")
    competition_id = input("What is the competition ID? ")

tee_time = input("What is the earliest tee time? (hh:mm) ")

while not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", tee_time):
    print("Invalid time format. Please enter time in 'hh:mm' format.")
    tee_time = input("What is the earliest tee time? (hh:mm) ")

asyncio.get_event_loop().run_until_complete(main(competition_id, tee_time))
