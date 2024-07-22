import pandas
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import random

def setup_driver(headers=None, user_agent=None):
    driver_path = '/Applications/chromedriver-mac-arm64/chromedriver'
    service = Service(driver_path)
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Run Chrome in headless mode (uncomment if needed)
    chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
    chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
    chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")  # Set custom User-Agent
    chrome_options.add_argument("--start-maximized")  # Open browser in maximized mode
    chrome_options.add_argument("disable-infobars")  # Disable info bars
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation controlled info
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Additional optional headers
    if user_agent:
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
    

    if headers:
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {"headers": headers})
    
    return driver

def extract_page_source(date):
    # Access date and remove unecessary characters to create base URL
    url = 'https://www.oddstrader.com/mlb/weather/?date=' + date
    print(url)

    # Launch chrome driver, go to desired url and put source code into a file for later use, quitting driver when finished
    driver_path = '/Applications/chromedriver-mac-arm64/chromedriver'
    service = Service(driver_path)
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Run Chrome in headless mode (uncomment if needed)
    chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
    chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
    chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")  # Set custom User-Agent
    chrome_options.add_argument("--start-maximized")  # Open browser in maximized mode
    chrome_options.add_argument("disable-infobars")  # Disable info bars
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation controlled info
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=service, options=chrome_options) # Create a new instance of the Chrome driver with the specified options
    # Add additional headers (Optional)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"})
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
        "headers": {
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.oddstrader.com/mlb/weather/"
        }
    })
    driver.get(url)
    time.sleep(random.uniform(10, 15)) # Wait for a few seconds to let the dynamic content load
    page_source = driver.page_source
    with open('dodgers_scrape_output.txt', 'w', encoding='utf-8') as file:
        file.write(page_source)
    dodgers_pos = page_source.find("dodgers")
    eid_pos = page_source.find("eid", dodgers_pos)
    end_pos = page_source.find('"', eid_pos)
    event_id = page_source[eid_pos:end_pos]
    if page_source[dodgers_pos + len("dodgers")] == '-':
        # Dodgers come first in the URL
        start_pos = dodgers_pos + len("dodgers") + 4
        end_pos = page_source.find("/", start_pos)
        opponent = page_source[start_pos:end_pos]
        url = 'https://www.oddstrader.com/mlb/event/los-angeles-dodgers-vs-' + opponent + '/weather/?date=' + date + '&' + event_id
        opponent = page_source[start_pos:end_pos].replace("-", " ").title()
    else:
        # Opponent comes first in the URL
        start_pos = page_source.rfind("/", 0, dodgers_pos)
        end_pos = dodgers_pos - 4
        opponent = page_source[start_pos:end_pos]
        url = 'https://www.oddstrader.com/mlb/event/' + opponent + '-vs-los-angeles-dodgers/weather/?date=' + date + '&' + event_id
        opponent = page_source[start_pos:end_pos].replace("-", " ").title()
    print(url)
    driver.get(url)
    time.sleep(random.uniform(10, 15))
    page_source = driver.page_source
    driver.quit()
    
    with open('dodgers_scrape_output.txt', 'w', encoding='utf-8') as file:
        file.write(page_source)

    return(opponent)

df = pandas.read_excel('Dodgers 2024.xlsx')

# Write opponent into dataframe
date = df.iloc[0, 0]
date = str(date).replace("-","")[:8]
#df.iat[0, 1] = extract_page_source(date)

# Read source code for information needed
with open('dodgers_scrape_output.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
for line in lines:
    if line.find("chance o") != -1:
        # Extract location
        end_index = line.find(" in")
        extracted_text = line[0:end_index].strip()
        df.iat[0, 7] = extracted_text

        # Extract weather
        start_index = line.find("\"") + 1
        end_index = line.find("\"", start_index)
        extracted_text = line[start_index:end_index]
        print(extracted_text)
        df.iat[0, 15]

    if line.find("weatherTemp") != -1:
        # Extract temperature
        start_index = line.find("weatherTemp") + len("weatherTemp") + 2
        end_index = line.find("<", start_index)
        extracted_text = line[start_index:end_index]
        df.iat[0, 8] = extracted_text + " F"

        # Extract wind speed
        start_index = line.find("weatherWind") + len("weatherWind") + 10
        end_index = line.find("-", start_index) - 1
        extracted_text = line[start_index:end_index]
        df.iat[0, 9] = extracted_text

        # Extract wind direction
        start_index = end_index + 3
        end_index = line.find("<", start_index)
        extracted_text = line[start_index:end_index]
        df.iat[0, 10] = extracted_text

        # Extract wind impact on hitter
        start_index = line.find(">", line.find("class=\"v", line.find("WIND IMPACT"))) + 1
        end_index = line.find("<", start_index)
        extracted_text = line[start_index:end_index]
        df.iat[0, 14] = extracted_text

        # Extract wind impact on pitcher
        if line[end_index + 45:end_index + 53] != "Pitching":
            print("Error: Pitching might've come before hitting in this output")
        start_index = line.find(">", line.find("class=\"v", end_index)) + 1
        end_index = line.find("<", start_index)
        extracted_text = line[start_index:end_index]
        df.iat[0, 13] = extracted_text

        # Extract temperature impact on hitter
        start_index = line.find(">", line.find("class=\"v", line.find("TEMP IMPACT"))) + 1
        end_index = line.find("<", start_index)
        extracted_text = line[start_index:end_index]
        df.iat[0, 12] = extracted_text

        # Extract wind impact on pitcher
        if line[end_index + 45:end_index + 53] != "Pitching":
            print("Error: Pitching might've come before hitting in this output")
        start_index = line.find(">", line.find("class=\"v", end_index)) + 1
        end_index = line.find("<", start_index)
        extracted_text = line[start_index:end_index]
        df.iat[0, 11] = extracted_text

    if line.find("startingPitcher") != -1:
        start_index = line.find("\"nam", line.find("startingPitcher")) + 6
        print(start_index)
        end_index = line.find("\"", start_index + 1)
        print(end_index)
        pitcher_team = line[start_index:end_index]
        print(pitcher_team)
            # Dodgers pitcher is first in page source

df.to_excel('Dodgers_2024_test.xlsx', index=False)

""" df = pandas.read_excel('Dodgers 2024.xlsx')
new_row = df.shape[0]
print(new_row)
print(datetime.now().strftime('%Y-%m-%d'))
if new_row >= df.shape[0]:
    new_row_df = pandas.DataFrame([[None] * df.shape[1]], columns=df.columns)
    # Concatenate the new row DataFrame to the original DataFrame
    df = pandas.concat([df, new_row_df], ignore_index=True)
df.at[new_row, df.columns[0]] = datetime.now().strftime('%Y-%m-%d')
df.to_excel('Dodgers 2024.xlsx', index=False) """