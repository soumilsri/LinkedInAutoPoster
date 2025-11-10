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
    
    def post_content_automated(self, content: str) -> bool:
        """Fully automated posting to LinkedIn - clicks Post button automatically"""
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
                    print("⚠️ Could not find post input.")
                    return False
            
            # Find the text area/div
            post_textarea = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@role='textbox'] | //div[@aria-label='Write a post']"))
            )
            
            # Clear and enter content using JavaScript
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
            
            # Wait for content to be set and LinkedIn to process it
            time.sleep(4)
            
            # Verify content was set - try multiple times
            actual_content = ""
            for attempt in range(3):
                actual_content = post_textarea.text
                if actual_content and len(actual_content.strip()) >= 10:
                    break
                time.sleep(2)
                # Try clicking and triggering events again
                post_textarea.click()
                self.driver.execute_script("""
                    var element = arguments[0];
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                """, post_textarea)
            
            if not actual_content or len(actual_content.strip()) < 10:
                print("⚠️ Content may not have been set properly.")
                print(f"   Content length: {len(actual_content) if actual_content else 0}")
                # Try one more time with a different approach
                try:
                    # Clear and set again
                    post_textarea.clear()
                    post_textarea.send_keys(content[:100])  # Try first 100 chars
                    time.sleep(1)
                    # Then use JS for the rest
                    if len(content) > 100:
                        self.driver.execute_script("""
                            var element = arguments[0];
                            var text = arguments[1];
                            element.innerText = element.innerText + text;
                            element.dispatchEvent(new Event('input', { bubbles: true }));
                        """, post_textarea, content[100:])
                    time.sleep(2)
                    actual_content = post_textarea.text
                except:
                    pass
            
            if not actual_content or len(actual_content.strip()) < 10:
                print("❌ Failed to set content after multiple attempts")
                return False
            
            print(f"✅ Post content set successfully! ({len(actual_content)} chars)")
            
            # Wait for Post button to be enabled - LinkedIn needs time to validate
            time.sleep(3)
            
            # Find and click the Post button - try multiple selectors
            post_button = None
            selectors = [
                "//button[contains(., 'Post') and not(contains(@class, 'disabled')) and not(@disabled)]",
                "//button[@aria-label='Post' and not(@disabled)]",
                "//button[contains(@class, 'share-actions__primary-action') and not(@disabled)]",
                "//button[contains(text(), 'Post') and not(@disabled)]",
                "//span[contains(text(), 'Post')]/ancestor::button[not(@disabled)]",
                "//button[@data-control-name='share.post' and not(@disabled)]",
                "//button[contains(@class, 'share-box__post-button')]"
            ]
            
            for selector in selectors:
                try:
                    # Wait for button to be both visible and enabled
                    post_button = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    # Double check it's enabled
                    if post_button and post_button.is_enabled():
                        # Check if button is actually clickable (not disabled by LinkedIn)
                        button_class = post_button.get_attribute('class') or ''
                        if 'disabled' not in button_class.lower():
                            print(f"✅ Found Post button using selector: {selector[:50]}...")
                            break
                        else:
                            print(f"⚠️ Post button found but appears disabled")
                            post_button = None
                except:
                    continue
            
            if not post_button:
                print("❌ Could not find enabled Post button")
                # Try to see what buttons are available
                try:
                    all_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Post')]")
                    print(f"   Found {len(all_buttons)} buttons with 'Post' text")
                    for btn in all_buttons:
                        print(f"   - Class: {btn.get_attribute('class')}, Enabled: {btn.is_enabled()}, Disabled attr: {btn.get_attribute('disabled')}")
                except:
                    pass
                return False
            
            # Scroll button into view and wait
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", post_button)
            time.sleep(2)
            
            # Click the Post button with multiple strategies
            clicked = False
            try:
                # Strategy 1: Regular click
                post_button.click()
                clicked = True
                print("✅ Post button clicked (regular click)!")
            except Exception as e1:
                print(f"⚠️ Regular click failed: {e1}")
                try:
                    # Strategy 2: JavaScript click
                    self.driver.execute_script("arguments[0].click();", post_button)
                    clicked = True
                    print("✅ Post button clicked (JavaScript)!")
                except Exception as e2:
                    print(f"⚠️ JavaScript click failed: {e2}")
                    try:
                        # Strategy 3: Action chains
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).move_to_element(post_button).click().perform()
                        clicked = True
                        print("✅ Post button clicked (ActionChains)!")
                    except Exception as e3:
                        print(f"❌ All click strategies failed: {e3}")
                        return False
            
            if not clicked:
                return False
            
            # Wait for post to be submitted - check for modal close or confirmation
            time.sleep(3)
            
            # Check for any confirmation dialogs or modals
            try:
                # Look for confirmation buttons
                confirm_selectors = [
                    "//button[contains(., 'Confirm')]",
                    "//button[contains(., 'Publish')]",
                    "//button[@aria-label='Confirm']"
                ]
                for confirm_selector in confirm_selectors:
                    try:
                        confirm_btn = self.driver.find_element(By.XPATH, confirm_selector)
                        if confirm_btn.is_displayed():
                            print("⚠️ Found confirmation dialog, clicking confirm...")
                            confirm_btn.click()
                            time.sleep(2)
                            break
                    except:
                        continue
            except:
                pass
            
            # Additional wait for LinkedIn to process
            time.sleep(4)
            
            # Verify post was submitted by checking multiple indicators
            try:
                # Wait a bit more for LinkedIn to process
                time.sleep(2)
                
                # Check if modal/post dialog is still open
                modal_open = False
                try:
                    # Look for the post modal/dialog
                    modal_selectors = [
                        "//div[contains(@class, 'share-box')]",
                        "//div[contains(@class, 'share-modal')]",
                        "//div[@role='dialog']"
                    ]
                    for modal_selector in modal_selectors:
                        try:
                            modal = self.driver.find_element(By.XPATH, modal_selector)
                            if modal.is_displayed():
                                modal_open = True
                                break
                        except:
                            continue
                except:
                    pass
                
                # Check if we're back on the feed (modal closed)
                current_url = self.driver.current_url
                on_feed = "feed" in current_url or "linkedin.com/feed" in current_url
                
                if not modal_open and on_feed:
                    print("✅ Modal closed and on feed page - post likely published!")
                    
                    # Additional wait to ensure post is processed
                    time.sleep(3)
                    
                    # Try to verify post appears in feed
                    try:
                        post_preview = content[:80].strip().lower()
                        # Get first few unique words
                        preview_words = [w for w in post_preview.split() if len(w) > 3][:5]
                        
                        feed_posts = self.driver.find_elements(By.XPATH, 
                            "//div[contains(@class, 'feed-shared-update-v2')] | //article[contains(@class, 'feed-shared-update-v2')] | //div[contains(@class, 'update-components-text')]")
                        
                        post_found = False
                        for post_element in feed_posts[:5]:  # Check first 5 posts
                            try:
                                post_text = post_element.text.lower()
                                # Check if at least 3 words from preview are in the post
                                matches = sum(1 for word in preview_words if word in post_text)
                                if matches >= 3:
                                    post_found = True
                                    print(f"✅ Post verified in feed! ({matches} words matched)")
                                    break
                            except:
                                continue
                        
                        if post_found:
                            print("✅ Post published successfully and verified in feed!")
                            return True
                        else:
                            print("⚠️ Post button was clicked and modal closed, but post not found in feed yet.")
                            print("   This might be normal - LinkedIn sometimes takes a moment to show new posts.")
                            print("   Please check your LinkedIn feed manually to confirm.")
                            return True  # Return True as button was clicked and modal closed
                    except Exception as e:
                        print(f"⚠️ Could not verify post in feed: {e}")
                        print("✅ Post button was clicked and modal closed - post likely published!")
                        return True
                elif modal_open:
                    print("⚠️ Post button was clicked but modal is still open.")
                    print("   LinkedIn might require additional confirmation or there was an error.")
                    # Try to find error messages
                    try:
                        error_elements = self.driver.find_elements(By.XPATH, 
                            "//div[contains(@class, 'error')] | //div[contains(@class, 'alert')] | //span[contains(@class, 'error')]")
                        for error_elem in error_elements:
                            if error_elem.is_displayed():
                                print(f"   Error message: {error_elem.text}")
                    except:
                        pass
                    return False
                else:
                    print("⚠️ Post button was clicked but verification unclear.")
                    print(f"   Current URL: {current_url}")
                    print("   Please check your LinkedIn feed manually.")
                    return True  # Return True as button was clicked
                    
            except Exception as e:
                print(f"⚠️ Could not verify post status: {e}")
                import traceback
                traceback.print_exc()
                print("✅ Post button was clicked. Please check your LinkedIn feed manually.")
                return True
            
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def post_content(self, content: str, automated: bool = False) -> bool:
        """Post content to LinkedIn - supports both manual and automated modes"""
        if automated:
            return self.post_content_automated(content)
        else:
            # Manual confirmation approach
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
                return True
                
            except Exception as e:
                print(f"❌ Error posting to LinkedIn: {e}")
                return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

