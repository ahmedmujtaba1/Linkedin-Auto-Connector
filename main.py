from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from configparser import ConfigParser
from selenium.webdriver.common.action_chains import ActionChains
from colorama import Fore, Style, init
import time, requests
from urllib.parse import quote

# Initialize colorama
init(autoreset=True)

# Initialize config parser
config = ConfigParser()
config_file = 'setup.ini'
config.read(config_file)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--log-level=2")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    # service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome( options=chrome_options)
    return driver

def save_cookie(driver:webdriver.Chrome):
    """Save the cookie to the setup.ini file"""
    li_at_cookie = driver.get_cookie('li_at')['value']
    config.set('LinkedIn', 'li_at', li_at_cookie)
    with open(config_file, 'w') as f:
        config.write(f)

def login_with_cookie(driver:webdriver.Chrome, li_at):
    """Attempt to login with the existing 'li_at' cookie"""
    print(Fore.YELLOW + "Attempting to log in with cookie...")
    driver.get("https://www.linkedin.com")
    driver.add_cookie(
        {
            "name": "li_at",
            "value": f"{li_at}",
            "path": "/",
            "secure": True,
        }
    )
    driver.refresh()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-typeahead")))
    print(Fore.GREEN + "[INFO] Logged in with cookie successfully.")

def select_location(driver:webdriver.Chrome, location:str):
    """Select the location in the LinkedIn search filter"""
    try:
        print("Selecting location")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchFilter_geoUrn"))).click()
        time.sleep(1)
        location_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add a location']")))
        location_input.send_keys(location)
        time.sleep(2)
        driver.find_element(By.XPATH,f"//*[text()='{location.title()}']").click()
        time.sleep(1)
        driver.find_element(By.XPATH,"//button[@aria-label='Apply current filter to show results']").click()
        time.sleep(3)
    except Exception as e:
        print(Fore.RED + f"[INFO] Error selecting location: {e}")

def login_with_credentials(driver:webdriver.Chrome, email:str, password:str):
    """Login using credentials and handle verification code if required"""
    print(Fore.YELLOW + "Logging in with credentials...")
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, "global-nav-typeahead") or 
        "Enter the code" in d.page_source
    )

    if "Enter the code" in driver.page_source:
        verification_code = input("[+] Enter the verification code sent to your email: ")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "input__email_verification_pin")))
        driver.find_element(By.ID, "input__email_verification_pin").send_keys(verification_code)
        driver.find_element(By.ID, "email-pin-submit-button").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-typeahead")))
    print(Fore.GREEN + "[INFO] Logged in with credentials successfully.")
    save_cookie(driver)

def send_connection_request(driver: webdriver.Chrome, limit:str, letter:str, include_notes: bool, message_letter:str):
    """Send a connection request to the specified LinkedIn profile"""
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the page to load
        try:
            if message_letter == "":
                connect_buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='Connect']/..")))
            elif message_letter != "":
                connect_buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='Message']/..")))
            print(f"Number of connect buttons found: {len(connect_buttons)}")
        except:
            connect_buttons = [1,2,3,4,5,6,7,8,9,10,11]
            print("No connect buttons found")
            print(f"Number of connect buttons found: 0")
        actions= ActionChains(driver)
        cnt = 0
        cnt2 = 1
        for i in range(limit):
            if cnt >= limit:
                break
            # cnt2 += 1
            try:
                print("Cnt : ", cnt, cnt2)
                if message_letter == "":
                    try:
                        driver.find_element(By.XPATH, "//h2[text()='No free personalized invitations left']")
                        print(Fore.RED + "[ERROR] No free personalized invitations left.")
                        return
                    except:pass
                    try:
                        driver.find_element(By.XPATH, "//button[@aria-label='Got it']").click()
                    except:pass
                    connect_button = connect_buttons[cnt]
                    url_xpath = f'(//*[text()="Connect"]/../../../..//span[@class="entity-result__title-line entity-result__title-line--2-lines "]//a)[{cnt2}]'
                    # print(url_xpath)
                    linkedin_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, url_xpath)))
                    linkedin_url = linkedin_container.get_attribute('href')
                    name = linkedin_container.text.split(' ')[0].title()
                    # print("Connect Button : ", connect_button)
                    cnt += 1
                    actions.move_to_element(connect_button).perform()
                    time.sleep(1) 
                    connect_button.click()
                    
                    time.sleep(1)  # Adjust based on how quickly the modal appears
                    
                    if not include_notes:
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Send without a note"]'))).click()
                    else:
                        add_note_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Add a note"]')))
                        add_note_button.click()

                        message_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//textarea[@name="message"]')))
                        message_box.send_keys(letter.replace("{name}", name).replace("{fullName}",name))
                        time.sleep(1)  # Adjust based on preference
                        send_button = driver.find_element(By.XPATH, '//button[@aria-label="Send invitation"]')
                        driver.execute_script("arguments[0].click();", send_button)

                    print(Fore.GREEN + f"[INFO] Connection request sent successfully to {linkedin_url}")
                    print("---------------------------------------------------------------------------------------------------------------")
                    time.sleep(10)  # Wait for the action to complete before proceeding
                elif message_letter != "":
                    url_xpath = f'(//*[text()="Message"]/../../../../..//span[@class="entity-result__title-line entity-result__title-line--2-lines "]//a)[{cnt2}]'
                    linkedin_url = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, url_xpath))).get_attribute('href')
                    full_name = driver.find_element(By.XPATH, f'(//*[text()="Message"]/../../../../..//span[@class="entity-result__title-line entity-result__title-line--2-lines "]//a//span)[{cnt2}]').text.split(' ')[0].title().replace("view","").replace('\n','')
                    connect_button = connect_buttons[cnt]
                    cnt += 1
                    actions.move_to_element(connect_button).perform()
                    time.sleep(1) 
                    connect_button.click()
                    time.sleep(2)

                    try:
                        driver.find_element(By.XPATH, "//h2[text()='No free personalized invitations left']")
                        print(Fore.RED + "[ERROR] No free personalized invitations left.")
                        return
                    except:pass

                    message_box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']")))
                    message_box.clear()
                    message_box.send_keys(message_letter.replace("{name}", full_name).replace("{fullName}",full_name))
                    time.sleep(1)  # Adjust based on preference
                    send_button = driver.find_element(By.XPATH, '//button[text()="Send"]')
                    send_button.click()
                    # driver.execute_script("arguments[0].click();", send_button)
                    time.sleep(1)
                    driver.find_element(By.XPATH, "//button[@class='msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']").click()
                    time.sleep(2)

                    print(Fore.GREEN + f"[INFO] Connection request sent successfully to {linkedin_url}")
                    print("---------------------------------------------------------------------------------------------------------------")
                    time.sleep(10)
            except Exception as e:
                print(e)
                print(Fore.LIGHTCYAN_EX + f"[INFO] Moving towards next page...")
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for the action to complete before proceeding
                    try:
                        driver.find_element(By.XPATH, "//h2[text()='No free personalized invitations left']")
                        print(Fore.RED + "[ERROR] No free personalized invitations left.")
                        return
                    except:pass
                    driver.find_element(By.XPATH, "//button[@aria-label='Next']").click()
                    time.sleep(3.4)
                    try:
                        if message_letter == "":
                            connect_buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='Connect']/..")))
                        elif message_letter != "":
                            connect_buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[text()='Message']/..")))
                        print(f"Number of connect buttons found: {len(connect_buttons)}")
                    except:
                        connect_buttons = [1,2,3,4,5,6,7,8,9,10,11]
                        print("No connect buttons found")
                        print(f"Number of connect buttons found: 0")
                        pass
                    cnt2 = 1
                    cnt = 0
                except Exception as e:
                    print(e)
                    break
                
    except Exception as e:
        print(Fore.RED + f"[INFO] No profile found or an error occurred. Details: {e}")
        driver.quit()
      
def main():
    print(Fore.CYAN + "[-] Please enter your search criteria:")
    message = ''
    message_letter = ''
    include_note = False
    connection_degree = input(Fore.MAGENTA + "[+] Enter the connection degree (1st, 2nd, 3rd): " + Fore.RESET)
    if connection_degree.lower() not in ['1st', '2nd', '3rd']:
        print(Fore.RED + "[ERROR] Invalid connection degree. Please enter 1st, 2nd, or 3rd.")
        connection_degree = input(Fore.MAGENTA + "[+] Enter the connection degree (1st, 2nd, 3rd): " + Fore.RESET)
    keyword = input(Fore.MAGENTA + "[+] Enter the keyword for the search: " + Fore.RESET)
    location = input(Fore.MAGENTA + "[+] Enter the location: " + Fore.RESET)
    if connection_degree.lower() == '1st':
        message_letter = input(Fore.MAGENTA + "[+] Enter the message letter for the connection request: " + Fore.RESET)
    if message_letter == "":
        include_note = input(Fore.MAGENTA + "[+] Do you want to include a note in the connection request? (y/n): " + Fore.RESET)
        if include_note.lower() == 'y':
            include_note = True
            message = input(Fore.MAGENTA + "[+] Enter the personalized message to send with connection requests: " + Fore.RESET)
        else:
            include_note = False
    limit = int(input(Fore.MAGENTA + "[+] Enter the maximum number of connection requests to send: " + Fore.RESET))
    li_at = input(Fore.MAGENTA + "[+] Enter the li_at of Linkedin: " + Fore.RESET)
    print("----------------------------------------------------------------")
    driver = setup_driver()

    try:
        login_with_cookie(driver, li_at)
    except Exception as e:
        print(Fore.RED + f"[INFO] Cookie login failed: {e}\n" + Fore.YELLOW + "Attempting login with credentials.")
        email = config.get('LinkedIn', 'email')
        password = config.get('LinkedIn', 'password')
        login_with_credentials(driver, email, password)
    
    network_mapping = {
        "1st": "%5B%22F%22%5D",  
        "2nd": "%5B%22S%22%5D",  
        "3rd": "%5B%22O%22%5D"   
    }
    network_code = network_mapping.get(connection_degree, "")

    search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword.replace(' ','%20').lower()}&locations={location.replace(' ','%20')}&network={network_code}&origin=FACETED_SEARCH"
    print(Fore.YELLOW + f"[INFO] Navigating to search URL: {search_url}")
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-typeahead")))
    if location != "":
        select_location(driver, location)
    send_connection_request(driver=driver, limit=limit, letter=message, include_notes=include_note, message_letter=message_letter)
    driver.quit()

if __name__ == "__main__":
    main()
