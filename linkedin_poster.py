"""
Module to automate LinkedIn posting using Selenium
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import config


class LinkedInPoster:
    """Handles automated posting to LinkedIn"""
    
    def __init__(self):
        self.email = config.LINKEDIN_EMAIL
        self.password = config.LINKEDIN_PASSWORD
        self.driver = None
        self.timeout = config.BROWSER_TIMEOUT
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        
        if config.HEADLESS_MODE:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()
    
    def login(self) -> bool:
        """Login to LinkedIn"""
        try:
            if not self.email or not self.password:
                print("❌ LinkedIn credentials not configured. Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file")
                return False
            
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Enter email
            email_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.send_keys(self.email)
            
            # Enter password
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(self.password)
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "linkedin.com/in/" in self.driver.current_url:
                print("✅ Successfully logged in to LinkedIn")
                return True
            else:
                print("❌ Login failed. Please check your credentials.")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
    
    def post_content(self, content: str) -> bool:
        """Post content to LinkedIn"""
        try:
            # Navigate to LinkedIn feed
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Find the post input box (LinkedIn uses "Start a post" button)
            try:
                # Try to find the "Start a post" button
                start_post_button = WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Start a post')] | //div[contains(@aria-label, 'Start a post')]"))
                )
                start_post_button.click()
                time.sleep(2)
            except:
                # Alternative: Look for the post textarea directly
                post_box = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox']"))
                )
                post_box.click()
                time.sleep(1)
            
            # Find the text area/div
            post_textarea = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox'] | //div[@aria-label='Write a post']"))
            )
            
            # Clear and enter content using JavaScript to avoid BMP character issues
            post_textarea.click()
            time.sleep(1)
            
            # Use JavaScript to set content (handles emojis and special characters)
            # This method properly handles contenteditable divs and triggers all necessary events
            # Replace newlines with a placeholder that we'll convert to <br> tags
            content_with_placeholders = content.replace('\n', '|||NEWLINE|||')
            
            self.driver.execute_script("""
                var element = arguments[0];
                var text = arguments[1];
                
                // Clear existing content
                element.focus();
                element.innerHTML = '';
                
                // Split by placeholder and create proper formatting
                var lines = text.split('|||NEWLINE|||');
                for (var i = 0; i < lines.length; i++) {
                    if (i > 0) {
                        // Add line break
                        var br = document.createElement('br');
                        element.appendChild(br);
                    }
                    // Add text node (handles emojis and special characters)
                    if (lines[i]) {
                        var textNode = document.createTextNode(lines[i]);
                        element.appendChild(textNode);
                    }
                }
                
                // Set cursor to end
                var range = document.createRange();
                range.selectNodeContents(element);
                range.collapse(false);
                var selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                
                // Trigger input event to notify LinkedIn's JavaScript
                var inputEvent = new Event('input', { bubbles: true, cancelable: true });
                element.dispatchEvent(inputEvent);
                
                // Trigger other events that LinkedIn might be listening to
                var changeEvent = new Event('change', { bubbles: true, cancelable: true });
                element.dispatchEvent(changeEvent);
                
                // Also trigger keyup event
                var keyupEvent = new Event('keyup', { bubbles: true, cancelable: true });
                element.dispatchEvent(keyupEvent);
            """, post_textarea, content_with_placeholders)
            
            time.sleep(2)
            
            # Find and click the Post button
            post_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Post')] | //button[@aria-label='Post']"))
            )
            post_button.click()
            
            time.sleep(config.POSTING_DELAY)
            
            print("✅ Post published successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            print("💡 Tip: LinkedIn's interface may have changed. You may need to post manually.")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

