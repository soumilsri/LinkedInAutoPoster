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
            
            # Clear and enter content - use a more LinkedIn-compatible approach
            post_textarea.click()
            time.sleep(1)
            
            # Try to clear using keyboard shortcuts (more natural)
            try:
                post_textarea.send_keys(Keys.CONTROL + "a")
                time.sleep(0.3)
                post_textarea.send_keys(Keys.DELETE)
                time.sleep(0.5)
            except:
                # Fallback to JavaScript clear
                self.driver.execute_script("arguments[0].innerHTML = ''; arguments[0].innerText = '';", post_textarea)
                time.sleep(0.5)
            
            # Set content using a hybrid approach: type first part, then use JS for rest
            # This makes it more human-like while handling emojis
            try:
                # Try typing first 200 characters (if no emojis) to trigger LinkedIn's validation
                safe_chars = content[:200]
                # Check if safe_chars contains only ASCII/BMP characters
                try:
                    safe_chars.encode('ascii')
                    # All ASCII - safe to type
                    post_textarea.send_keys(safe_chars)
                    time.sleep(1)
                    remaining = content[200:]
                except UnicodeEncodeError:
                    # Contains non-ASCII - use JS for everything
                    safe_chars = ""
                    remaining = content
                
                # Use JavaScript for the rest (handles emojis and special chars)
                if remaining:
                    self.driver.execute_script("""
                        var element = arguments[0];
                        var text = arguments[1];
                        
                        // Append text
                        var currentText = element.innerText || element.textContent || '';
                        element.innerText = currentText + text;
                        
                        // Trigger all necessary events
                        var inputEvent = new InputEvent('input', {
                            bubbles: true,
                            cancelable: true,
                            inputType: 'insertText',
                            data: text
                        });
                        element.dispatchEvent(inputEvent);
                        
                        var changeEvent = new Event('change', { bubbles: true, cancelable: true });
                        element.dispatchEvent(changeEvent);
                        
                        // Also trigger keyup for LinkedIn
                        var keyupEvent = new KeyboardEvent('keyup', { 
                            bubbles: true, 
                            cancelable: true,
                            key: 'Enter'
                        });
                        element.dispatchEvent(keyupEvent);
                    """, post_textarea, remaining)
                    time.sleep(1)
            except Exception as e:
                print(f"⚠️ Hybrid approach failed, using pure JavaScript: {e}")
                # Fallback to pure JavaScript
                self.driver.execute_script("""
                    var element = arguments[0];
                    var text = arguments[1];
                    
                    // Focus and clear
                    element.focus();
                    element.innerHTML = '';
                    element.innerText = '';
                    
                    // Set text
                    element.innerText = text;
                    
                    // Trigger comprehensive events
                    var beforeInput = new InputEvent('beforeinput', {
                        bubbles: true,
                        cancelable: true,
                        inputType: 'insertText',
                        data: text
                    });
                    element.dispatchEvent(beforeInput);
                    
                    var inputEvent = new InputEvent('input', {
                        bubbles: true,
                        cancelable: true,
                        inputType: 'insertText',
                        data: text
                    });
                    element.dispatchEvent(inputEvent);
                    
                    var changeEvent = new Event('change', { bubbles: true, cancelable: true });
                    element.dispatchEvent(changeEvent);
                    
                    // Trigger keyboard events
                    var keydown = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, key: 'Enter' });
                    element.dispatchEvent(keydown);
                    
                    var keyup = new KeyboardEvent('keyup', { bubbles: true, cancelable: true, key: 'Enter' });
                    element.dispatchEvent(keyup);
                    
                    // Set cursor to end
                    var range = document.createRange();
                    var selection = window.getSelection();
                    range.selectNodeContents(element);
                    range.collapse(false);
                    selection.removeAllRanges();
                    selection.addRange(range);
                    
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
            
            # Trigger one more input event to ensure LinkedIn recognizes the content
            post_textarea.click()
            time.sleep(0.5)
            self.driver.execute_script("""
                var element = arguments[0];
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('blur', { bubbles: true }));
                element.focus();
            """, post_textarea)
            time.sleep(1)
            
            # Wait for Post button to be enabled - LinkedIn needs time to validate
            # Wait up to 10 seconds for the button to become enabled
            print("⏳ Waiting for Post button to be enabled...")
            post_button = None
            selectors = [
                "//button[contains(., 'Post') and not(contains(@class, 'disabled')) and not(@disabled)]",
                "//button[@aria-label='Post' and not(@disabled)]",
                "//button[contains(@class, 'share-actions__primary-action') and not(@disabled)]",
                "//button[contains(text(), 'Post') and not(@disabled)]",
                "//span[contains(text(), 'Post')]/ancestor::button[not(@disabled)]",
                "//button[@data-control-name='share.post' and not(@disabled)]",
                "//button[contains(@class, 'share-box__post-button')]",
                "//button[contains(@class, 'share-actions__primary-action')]"
            ]
            
            # Wait for button to be enabled (not just clickable)
            for wait_time in range(10):  # Wait up to 10 seconds
                for selector in selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, selector)
                        for btn in buttons:
                            if btn.is_displayed():
                                # Check multiple conditions
                                is_enabled = btn.is_enabled()
                                disabled_attr = btn.get_attribute('disabled')
                                button_class = btn.get_attribute('class') or ''
                                aria_disabled = btn.get_attribute('aria-disabled')
                                
                                # Button is truly enabled if:
                                # - is_enabled() returns True
                                # - disabled attribute is None
                                # - class doesn't contain 'disabled'
                                # - aria-disabled is not 'true'
                                if (is_enabled and 
                                    disabled_attr is None and 
                                    'disabled' not in button_class.lower() and
                                    aria_disabled != 'true'):
                                    post_button = btn
                                    print(f"✅ Found enabled Post button! (waited {wait_time + 1}s)")
                                    break
                        if post_button:
                            break
                    except:
                        continue
                
                if post_button:
                    break
                
                time.sleep(1)
            
            if not post_button:
                print("❌ Could not find enabled Post button after waiting")
                # Debug: Show what buttons are available
                try:
                    all_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Post')]")
                    print(f"   Found {len(all_buttons)} buttons with 'Post' text:")
                    for i, btn in enumerate(all_buttons[:5]):
                        try:
                            print(f"   Button {i+1}: Enabled={btn.is_enabled()}, Disabled attr={btn.get_attribute('disabled')}, Class={btn.get_attribute('class')[:50]}")
                        except:
                            pass
                except:
                    pass
                return False
            
            # Scroll button into view and wait
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", post_button)
            time.sleep(1)
            
            # Double-check button is still enabled before clicking
            if not post_button.is_enabled() or post_button.get_attribute('disabled') is not None:
                print("⚠️ Post button became disabled before clicking. Retrying...")
                time.sleep(2)
                # Try to find it again
                for selector in selectors[:3]:  # Try top 3 selectors
                    try:
                        btn = self.driver.find_element(By.XPATH, selector)
                        if btn.is_enabled() and btn.get_attribute('disabled') is None:
                            post_button = btn
                            break
                    except:
                        continue
                
                if not post_button.is_enabled():
                    print("❌ Post button is disabled and cannot be clicked")
                    return False
            
            # Click the Post button with multiple strategies
            clicked = False
            click_method = None
            
            # Strategy 1: Move to element first, then click (more human-like)
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(post_button).pause(0.2).click().perform()
                clicked = True
                click_method = "ActionChains"
                print("✅ Post button clicked (ActionChains)!")
            except Exception as e1:
                print(f"⚠️ ActionChains click failed: {e1}")
                try:
                    # Strategy 2: Regular click
                    post_button.click()
                    clicked = True
                    click_method = "regular"
                    print("✅ Post button clicked (regular click)!")
                except Exception as e2:
                    print(f"⚠️ Regular click failed: {e2}")
                    try:
                        # Strategy 3: JavaScript click with mouse events
                        self.driver.execute_script("""
                            var btn = arguments[0];
                            // Simulate mouse events
                            var mouseDown = new MouseEvent('mousedown', { bubbles: true, cancelable: true });
                            var mouseUp = new MouseEvent('mouseup', { bubbles: true, cancelable: true });
                            var clickEvent = new MouseEvent('click', { bubbles: true, cancelable: true });
                            btn.dispatchEvent(mouseDown);
                            btn.dispatchEvent(mouseUp);
                            btn.dispatchEvent(clickEvent);
                            btn.click();
                        """, post_button)
                        clicked = True
                        click_method = "JavaScript"
                        print("✅ Post button clicked (JavaScript with events)!")
                    except Exception as e3:
                        print(f"❌ All click strategies failed: {e3}")
                        return False
            
            if not clicked:
                return False
            
            # Wait a moment to see if click registered
            time.sleep(1)
            
            # Verify the click actually did something - check if button state changed or modal started closing
            try:
                # Check if button became disabled (indicates click was registered)
                if post_button.get_attribute('disabled') is not None or 'disabled' in (post_button.get_attribute('class') or '').lower():
                    print("✅ Button state changed - click registered!")
            except:
                pass
            
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

