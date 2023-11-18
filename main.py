import asyncio
from datetime import datetime, timedelta
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


def generate_incrementing_times(start_time: str):
    """Generates a list of incrementing times.
    Args:
    start_time: The start time.
    Returns:
    A list of incrementing times.
    """
    times = []
    current_time = datetime.strptime(start_time, "%H:%M")
    while len(times) < 7:
        times.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=10)
    return times


async def main(comp_id, tee_time):
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

    await page.goto(
        f"https://www.stannesoldlinks.com/competition2.php?tab=details&compid={comp_id}"
    )
    signUp_btn = await wait_for_element_reload(page, ".comp-signup-button")
    await signUp_btn.click()
    # btn = await page.waitForXPath('//*[@id="onlineSignupContainer"]/div[3]/a[1]')
    # await page.waitFor(2000)
    # await btn.click()
    await page.waitFor(2000)

    tds = await page.querySelectorAll("td")
    for td in tds:
        text_handle = await td.getProperty("textContent")
        text = await text_handle.jsonValue()
        print(text)
        if text == f"{tee_time}":
            nextElementSibling = await td.getProperty("nextElementSibling")
            link = await nextElementSibling.querySelector("a")
            await link.click()

            break
        else:
            print("not found")

    await page.waitForNavigation()


competition_id = input("What is the competition ID? ")
tee_time = input("What is the earliest tee time? (hh:mm) ")
print("time list")
times_list = generate_incrementing_times(tee_time)
print(times_list)

asyncio.get_event_loop().run_until_complete(main(competition_id, tee_time))
