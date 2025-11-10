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
    
    def prepare_post_for_manual_confirmation(self, content: str) -> bool:
        """Prepare LinkedIn post with content pre-filled, wait for manual confirmation"""
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
                try:
                    post_box = WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox']"))
                    )
                    post_box.click()
                    time.sleep(1)
                except:
                    print("⚠️ Could not find post input. Please start a post manually.")
                    return False
            
            # Find the text area/div
            post_textarea = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox'] | //div[@aria-label='Write a post']"))
            )
            
            # Clear and enter content using JavaScript to avoid BMP character issues
            post_textarea.click()
            time.sleep(1)
            
            # Set content using JavaScript - handles emojis and special characters
            self.driver.execute_script("""
                var element = arguments[0];
                var text = arguments[1];
                
                // Focus the element first
                element.focus();
                
                // Clear existing content
                element.innerHTML = '';
                element.innerText = '';
                
                // Set text using innerText (preserves formatting and handles emojis)
                element.innerText = text;
                
                // Create a proper InputEvent
                var inputEvent = new InputEvent('input', {
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: text
                });
                element.dispatchEvent(inputEvent);
                
                // Trigger beforeinput event
                var beforeInputEvent = new InputEvent('beforeinput', {
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: text
                });
                element.dispatchEvent(beforeInputEvent);
                
                // Trigger change event
                var changeEvent = new Event('change', { bubbles: true, cancelable: true });
                element.dispatchEvent(changeEvent);
                
                // Set cursor to end
                var range = document.createRange();
                var selection = window.getSelection();
                range.selectNodeContents(element);
                range.collapse(false);
                selection.removeAllRanges();
                selection.addRange(range);
                
                // Focus the element
                element.focus();
            """, post_textarea, content)
            
            # Wait for content to be set
            time.sleep(2)
            
            # Verify content was set
            actual_content = post_textarea.text
            if actual_content and len(actual_content.strip()) > 10:
                print("✅ Post content pre-filled successfully!")
                print("📝 Please review the post in the browser and click 'Post' manually when ready.")
                print("💡 The browser will remain open for you to complete the posting.")
                return True
            else:
                print("⚠️ Content may not have been set properly.")
                print("💡 You can manually copy and paste the post content.")
                return False
            
        except Exception as e:
            print(f"❌ Error preparing post: {e}")
            return False
    
    def post_content(self, content: str) -> bool:
        """Post content to LinkedIn - Manual confirmation approach"""
        try:
            # Prepare the post (pre-fill content)
            if not self.prepare_post_for_manual_confirmation(content):
                return False
            
            # Keep browser open and wait for user to manually post
            print("\n" + "="*60)
            print("⏳ Waiting for manual confirmation...")
            print("="*60)
            print("📋 Instructions:")
            print("   1. Review the pre-filled post in the browser")
            print("   2. Make any final edits if needed")
            print("   3. Click the 'Post' button in LinkedIn")
            print("   4. Come back here and confirm when done")
            print("="*60 + "\n")
            
            # Don't close the browser - let user complete manually
            # The browser will stay open until user closes it or the script ends
            return True
            
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

