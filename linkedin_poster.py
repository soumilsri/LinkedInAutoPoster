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
            
            # Set content using JavaScript - LinkedIn compatible method
            # Use innerText which LinkedIn recognizes better
            content_for_linkedin = content  # Keep content as-is for innerText
            
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
                
                // Also set textContent as fallback
                element.textContent = text;
                
                // Create a proper InputEvent (more realistic)
                var inputEvent = new InputEvent('input', {
                    bubbles: true,
                    cancelable: true,
                    inputType: 'insertText',
                    data: text
                });
                element.dispatchEvent(inputEvent);
                
                // Trigger beforeinput event (LinkedIn might listen to this)
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
                
                // Trigger keyup event
                var keyupEvent = new KeyboardEvent('keyup', { 
                    bubbles: true, 
                    cancelable: true,
                    key: 'Enter',
                    code: 'Enter'
                });
                element.dispatchEvent(keyupEvent);
                
                // Set cursor to end
                var range = document.createRange();
                var selection = window.getSelection();
                range.selectNodeContents(element);
                range.collapse(false);
                selection.removeAllRanges();
                selection.addRange(range);
                
                // Force a blur and refocus to trigger LinkedIn's validation
                element.blur();
                setTimeout(function() {
                    element.focus();
                }, 100);
            """, post_textarea, content_for_linkedin)
            
            # Wait a bit for LinkedIn to process the content
            time.sleep(3)
            
            # Verify content was set
            actual_content = post_textarea.text
            if not actual_content or len(actual_content.strip()) < 10:
                print("⚠️ Content may not have been set properly. Trying alternative method...")
                # Try typing character by character for first 100 chars, then use JS for rest
                post_textarea.click()
                time.sleep(0.5)
                # Type first part normally (if no emojis)
                safe_content = content[:100] if len(content) > 100 else content
                try:
                    post_textarea.send_keys(safe_content)
                    time.sleep(1)
                    # Use JS for the rest if needed
                    if len(content) > 100:
                        remaining = content[100:]
                        self.driver.execute_script("""
                            var element = arguments[0];
                            var text = arguments[1];
                            var textNode = document.createTextNode(text);
                            element.appendChild(textNode);
                            element.dispatchEvent(new Event('input', { bubbles: true }));
                        """, post_textarea, remaining)
                except:
                    # If send_keys fails, use JS for everything
                    pass
            
            # Wait for Post button to be enabled
            time.sleep(2)
            
            # Find and click the Post button - try multiple selectors
            post_button = None
            selectors = [
                "//button[contains(., 'Post') and not(contains(@class, 'disabled'))]",
                "//button[@aria-label='Post']",
                "//button[contains(@class, 'share-actions__primary-action')]",
                "//button[contains(text(), 'Post')]",
                "//span[contains(text(), 'Post')]/ancestor::button"
            ]
            
            for selector in selectors:
                try:
                    post_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if post_button and post_button.is_enabled():
                        break
                except:
                    continue
            
            if not post_button:
                print("❌ Could not find Post button")
                return False
            
            # Scroll button into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
            time.sleep(0.5)
            
            # Click the Post button
            try:
                post_button.click()
            except:
                # Try JavaScript click as fallback
                self.driver.execute_script("arguments[0].click();", post_button)
            
            # Wait for post to be submitted
            time.sleep(5)
            
            # Verify post was submitted by checking multiple indicators
            try:
                # Check if we're back on the feed (modal closed)
                current_url = self.driver.current_url
                if "feed" not in current_url:
                    print("⚠️ Not on feed page. Post may not have been published.")
                    return False
                
                # Wait a bit more for LinkedIn to process
                time.sleep(3)
                
                # Try to verify post appears in feed by checking for the post content
                # Get first few words of the post to search for
                post_preview = content[:50].strip()
                
                # Check if post appears in feed (look for the text in recent posts)
                try:
                    # Look for the post text in the feed
                    feed_posts = self.driver.find_elements(By.XPATH, 
                        "//div[contains(@class, 'feed-shared-update-v2')] | //article[contains(@class, 'feed-shared-update-v2')]")
                    
                    # Check if any post contains our content
                    post_found = False
                    for post_element in feed_posts[:3]:  # Check first 3 posts
                        post_text = post_element.text
                        if post_preview.lower() in post_text.lower():
                            post_found = True
                            break
                    
                    if post_found:
                        print("✅ Post published successfully and verified in feed!")
                        return True
                    else:
                        print("⚠️ Post button was clicked, but post not found in feed. It may still be processing.")
                        print("💡 Please check your LinkedIn feed manually to confirm.")
                        return True  # Return True as button was clicked successfully
                        
                except Exception as e:
                    print(f"⚠️ Could not verify post in feed: {e}")
                    print("💡 Post button was clicked. Please check your LinkedIn feed manually.")
                    return True  # Assume success if button was clicked
                    
            except Exception as e:
                print(f"⚠️ Could not verify post status: {e}")
                print("💡 Post button was clicked. Please check your LinkedIn feed manually.")
                return True  # Assume success if no critical error
            
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            print("💡 Tip: LinkedIn's interface may have changed. You may need to post manually.")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

