import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta


async def wait_for_element_reload(page, element: str):
    """Waits for element to appear.
    Args:
        page: the page which element will appear
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
    increment: The increment in minutes.
  Returns:
    A list of incrementing times.
  """
    times = []
    current_time = datetime.strptime(start_time, '%H:%M')
    while len(times) < 7:
        times.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=10)
    return times


async def main(comp_id, tee_time):
    browser = await launch({'headless': False})
    page = await browser.newPage()
    await page.goto('https://www.stannesoldlinks.com/login.php')

    # find and enter username
    username = await page.querySelector('#memberid')
    await username.type('1953')

    # find and enter pin number
    pin = await page.querySelector('#pin')
    await pin.type('2322')
    await page.keyboard.press('Enter')


    await page.goto(f'https://www.stannesoldlinks.com/competition2.php?tab=details&compid={comp_id}')
    signUp_btn = await wait_for_element_reload(page, '.comp-signup-button')
    await signUp_btn.click()
    btn = await page.waitForXPath('//*[@id="onlineSignupContainer"]/div[3]/a[1]')
    await btn.click()
    await page.waitFor(500)

    tds = await page.querySelectorAll('td')
    for td in tds:
        text_handle = await td.getProperty('textContent')
        text = await text_handle.jsonValue()
        if text == f'{tee_time}':
            nextElementSibling = await td.getProperty('nextElementSibling')
            await nextElementSibling.click()
            nextEl_handle = await nextElementSibling.getProperty('textContent')
            nextEl_text = await nextEl_handle.jsonValue()
            print(nextEl_text)
            break
        else:
            print('not found')

    await page.waitForNavigation()


id = input("What is the competition id? ")
time = input("What is the earliest tee time? (hh:mm) ")
print('time list')
times_list = generate_incrementing_times(time)
print(times_list)


asyncio.get_event_loop().run_until_complete(main(id, time))

