#!/usr/bin/env python3

import os
import time
import base64
import json
import requests
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import re
from PIL import Image

# Load environment variables
load_dotenv()

class PokemonAIPlayer:
    def __init__(self):
        self.driver = None
        self.api_key = os.getenv('XAI_API_KEY')
        self.memory_file = "memory.txt"
        self.frame_count = 0
        self.screenshot_count = 0
        self.screenshots_folder = "screenshots"
        
        # Ensure screenshots folder exists
        os.makedirs(self.screenshots_folder, exist_ok=True)
        
        # Game controls mapping (synchronized with JavaScript keyMappings)
        self.controls = {
            'A': 'z',           # KeyZ, keyCode: 90
            'B': 'x',           # KeyX, keyCode: 88
            'START': 'Enter',   # Enter, keyCode: 13 (FIXED: was 'Return')
            'SELECT': 'Shift',  # ShiftLeft, keyCode: 16
            'UP': 'ArrowUp',    # ArrowUp, keyCode: 38
            'DOWN': 'ArrowDown', # ArrowDown, keyCode: 40
            'LEFT': 'ArrowLeft', # ArrowLeft, keyCode: 37
            'RIGHT': 'ArrowRight', # ArrowRight, keyCode: 39
            'L': 'a',           # KeyA, keyCode: 65
            'R': 's'            # KeyS, keyCode: 83
        }
        
        if not self.api_key:
            raise ValueError("❌ XAI_API_KEY not found in environment variables")
        
        print("🎮 Advanced Pokemon Fire Red AI Player with Grok-4")
        print("=" * 56)
        print(f"🔑 Using API key: {self.api_key[:10]}...{self.api_key[-4:]}")

    def log(self, message):
        """Log message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def load_memory(self):
        """Load AI memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    memory = f.read().strip()
                    if memory:
                        return memory.split('\n')
            return [
                "GOAL: Complete Pokemon Fire Red - beat Elite 4, become Champion, catch Mewtwo",
                "CURRENT PROGRESS: Just started - need to get through intro and choose starter",
                "STRATEGY: Build balanced team, learn type advantages, train consistently",
                "EFFICIENCY: Use batched moves like ['UP','UP','UP'] and ['A','A','A'] for speed",
                "MEMORY: Track important NPCs, locations, and story progress in this scratchpad"
            ]
        except Exception as e:
            self.log(f"⚠️ Error loading memory: {e}")
            return ["Fresh start - beginning Pokemon Fire Red adventure"]

    def save_memory(self, memory_list):
        """Save AI memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                f.write('\n'.join(memory_list))
        except Exception as e:
            self.log(f"⚠️ Error saving memory: {e}")

    def cleanup_memory_with_ai(self):
        """Use AI to clean up, summarize, and reorganize memory"""
        try:
            self.log("🧠 Starting intelligent memory cleanup...")
            
            memory_list = self.load_memory()
            if len(memory_list) < 50:  # Only cleanup if there's substantial memory
                return memory_list
            
            # Join all memories for AI analysis
            current_memory = "\n".join([f"{i+1}. {memory}" for i, memory in enumerate(memory_list)])
            
            cleanup_prompt = [{
                "role": "system", 
                "content": f"""You are an AI memory management system for a Pokemon Fire Red gameplay session. 

CURRENT MEMORY (320 entries max):
{current_memory}

Your task: Clean up, summarize, and reorganize this memory for optimal gameplay context.

CLEANUP RULES:
1. **Remove Duplicates**: Merge repetitive "CURRENT PROGRESS" entries
2. **Summarize Sequences**: Condense long intro sequences into key milestones
3. **Detect Loops**: Identify and flag repetitive action patterns
4. **Prioritize Recent**: Keep recent events detailed, summarize older events
5. **Maintain Structure**: Keep the natural progression flow
6. **Flag Inconsistencies**: Note any contradictory information
7. **Preserve Screenshot Links**: Maintain SCREENSHOTS: [X,Y] associations for visual context

OUTPUT FORMAT - Return cleaned memory as a JSON list:
{{
    "cleaned_memory": [
        "SCREENSHOTS: [1-20] | SUMMARY: Completed Professor Oak's introduction sequence (selected male character, advanced through tutorials)",
        "SCREENSHOTS: [21] | CURRENT LOCATION: [Current area]",
        "SCREENSHOTS: [21] | RECENT ACTION: [Last meaningful action]",
        "SCREENSHOTS: [N/A] | TEAM STATUS: [Pokemon team if any]",
        "SCREENSHOTS: [N/A] | OBJECTIVE: [Next goal]",
        "SCREENSHOTS: [N/A] | FLAGS: [Any issues detected: loops, inconsistencies, etc.]"
    ],
    "cleanup_notes": "Summary of changes made",
    "issues_detected": ["list of any problems found"]
}}

Be thorough but preserve important game state information."""
            }, {
                "role": "user",
                "content": "Please analyze and clean up this Pokemon Fire Red memory log. Focus on removing redundancy while preserving all important game state information."
            }]
            
            # Use robust API call for memory cleanup
            content = self.robust_api_call(cleanup_prompt, max_tokens=32000, temperature=0.3, function_name="Memory Cleanup")
            
            if content:
                cleanup_result = self.parse_json_with_fallback(content, "Memory Cleanup", "")
                
                if "cleaned_memory" in cleanup_result:
                    cleaned_memory = cleanup_result["cleaned_memory"]
                    self.log(f"✅ Memory cleanup successful: {len(memory_list)} → {len(cleaned_memory)} entries")
                    
                    if "cleanup_notes" in cleanup_result:
                        self.log(f"📝 Cleanup notes: {cleanup_result['cleanup_notes']}")
                    
                    if "issues_detected" in cleanup_result and cleanup_result["issues_detected"]:
                        self.log(f"⚠️ Issues detected: {', '.join(cleanup_result['issues_detected'])}")
                    
                    return cleaned_memory
                else:
                    self.log("❌ Memory cleanup failed - invalid response format")
                    return memory_list
            else:
                self.log("❌ Memory cleanup failed - no response")
                return memory_list
                
        except Exception as e:
            self.log(f"❌ Memory cleanup error: {e}")
            return memory_list

    def setup_browser(self):
        """Setup Chrome browser with local emulator - OPTIMIZED for speed"""
        self.log("🔧 Setting up Chrome browser...")
        
        # SPEED OPTIMIZATION: Kill any lingering chromedriver processes
        try:
            import subprocess
            import platform
            if platform.system() == "Darwin":  # macOS
                subprocess.run(['pkill', '-f', 'chromedriver'], capture_output=True, timeout=2)
            elif platform.system() == "Linux":
                subprocess.run(['pkill', '-f', 'chromedriver'], capture_output=True, timeout=2)
        except:
            pass  # Don't let cleanup failures block startup
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--allow-file-access-from-files")
        chrome_options.add_argument("--allow-file-access")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--start-maximized")
        
        # SPEED OPTIMIZATION: Disable unnecessary features
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Speed up page loading
        chrome_options.add_argument("--disable-javascript-harmony-shipping")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Critical: Enable file access
        chrome_options.add_argument("--allow-file-access")
        chrome_options.add_argument("--allow-file-access-from-files")
        chrome_options.add_argument("--disable-web-security")
        
        # Use unique user data directory to avoid conflicts
        import tempfile
        import uuid
        unique_dir = os.path.join(tempfile.gettempdir(), f"chrome_pokemon_ai_{uuid.uuid4().hex[:8]}")
        chrome_options.add_argument(f"--user-data-dir={unique_dir}")
        
        # Remove automation detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("detach", True)
        
        # Set Chrome binary for macOS
        import platform
        if platform.system() == "Darwin":
            chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        try:
            # SPEED OPTIMIZATION: Go directly to the working method (skip service management)
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(1400, 800)
            self.driver.set_window_position(100, 100)
            
            self.log("✅ Browser setup complete!")
            self.log("👀 You should now see a Chrome window open!")
            
        except Exception as e:
            self.log(f"❌ Browser setup failed: {e}")
            raise

    def load_emulator(self):
        """Load the local GBA emulator - OPTIMIZED for speed"""
        emulator_path = os.path.abspath("local_emulator.html")
        self.log(f"📂 Loading emulator from: {emulator_path}")
        
        if not os.path.exists("local_emulator.html"):
            raise FileNotFoundError("local_emulator.html not found!")
        
        try:
            # Close any extra windows
            if len(self.driver.window_handles) > 1:
                for handle in self.driver.window_handles[1:]:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            
            # Navigate to emulator with proper file URL
            file_url = f"file://{emulator_path}"
            self.log(f"🌐 Navigating to: {file_url}")
            self.driver.get(file_url)
            
            # SPEED OPTIMIZATION: Quick page load verification (no unnecessary waits)
            wait = WebDriverWait(self.driver, 5)  # Reduced from 15 to 5
            game_div = wait.until(EC.presence_of_element_located((By.ID, "game")))
            
            self.log("✅ Emulator page loaded!")
            
            # SPEED OPTIMIZATION: Quick setup (no activation delays)
            self.ensure_ai_overlay_functions()
            self.send_ai_thought("Emulator ready", "Loading ROM...", "Starting soon")
            
            self.log("✅ Emulator ready!")
            
        except Exception as e:
            self.log(f"❌ Failed to load emulator: {e}")
            raise

    def dismiss_any_popups(self):
        """Simple popup dismissal for any unexpected dialogs (not netplay specific)"""
        try:
            dismiss_js = """
            // Simple check for any modal dialogs and close buttons
            const closeButtons = document.querySelectorAll('button, [role="button"]');
            let dismissed = false;
            
            closeButtons.forEach(btn => {
                const text = (btn.textContent || '').toLowerCase();
                if (text.includes('close') || text.includes('ok') || text.includes('×')) {
                    try {
                        btn.click();
                        dismissed = true;
                    } catch (e) {}
                }
            });
            
            return dismissed;
            """
            
            dismissed = self.driver.execute_script(dismiss_js)
            if dismissed:
                self.log("✅ Dismissed unexpected popup")
            return dismissed
            
        except Exception as e:
            self.log(f"⚠️ Error checking for popups: {e}")
            return False

    def upload_rom(self, rom_filename="roms/pokemonfr.gba"):
        """Upload ROM to emulator via the web interface - OPTIMIZED for speed"""
        self.log(f"⬆️ Uploading ROM: {rom_filename}")
        
        if not os.path.exists(rom_filename):
            self.log(f"❌ ROM file {rom_filename} not found!")
            return False
        
        try:
            # Read ROM file as base64
            with open(rom_filename, 'rb') as f:
                rom_data = f.read()
            
            # Convert to base64 for JavaScript transfer
            import base64
            rom_base64 = base64.b64encode(rom_data).decode('utf-8')
            
            self.log(f"📁 ROM loaded: {len(rom_data):,} bytes ({len(rom_data)/1024/1024:.1f} MB)")
            
            # Use JavaScript to create file and load ROM
            js_script = f"""
            try {{
                // Convert base64 back to binary data
                const romData = atob('{rom_base64}');
                const romBytes = new Uint8Array(romData.length);
                for (let i = 0; i < romData.length; i++) {{
                    romBytes[i] = romData.charCodeAt(i);
                }}
                
                // Create a proper File object
                const romFile = new File([romBytes], '{rom_filename}', {{
                    type: 'application/octet-stream'
                }});
                
                console.log('📁 Created ROM file:', romFile.name, romFile.size, 'bytes');
                
                // Store the ROM file for potential reloading
                window.lastRomFile = romFile;
                
                // Load the ROM using the existing function
                if (window.loadROM && typeof window.loadROM === 'function') {{
                    window.loadROM(romFile);
                    return 'ROM_UPLOAD_SUCCESS';
                }} else {{
                    return 'ERROR: loadROM function not found';
                }}
                
            }} catch (error) {{
                return 'ERROR: ' + error.message;
            }}
            """
            
            result = self.driver.execute_script(js_script)
            self.log(f"📤 ROM upload result: {result}")
            
            if 'SUCCESS' in result:
                self.log("✅ ROM uploaded successfully!")
                
                # SPEED OPTIMIZATION: Quick ROM loading check  
                self.log("⏳ Quick ROM loading check...")
                
                for i in range(8):  # Reduced from 30 to 8 (4 seconds max)
                    try:
                        status_js = """
                        // Quick status check
                        const canvas = document.querySelector('#game canvas');
                        if (!canvas) return 'NO_CANVAS';
                        if (window.gameLoaded === true) return 'GAME_FULLY_LOADED';
                        if (window.EJS && window.EJS.started === true) return 'EMULATOR_STARTED';
                        if (canvas.width > 200 && canvas.height > 100) return 'CANVAS_READY';
                        return 'LOADING';
                        """
                        
                        status = self.driver.execute_script(status_js)
                        
                        if status in ['GAME_FULLY_LOADED', 'EMULATOR_STARTED']:
                            self.log("✅ Game ready!")
                            return True
                        elif status == 'CANVAS_READY':
                            # After 3 seconds, assume it's working
                            if i > 5:
                                self.log("🚀 Canvas ready - starting gameplay!")
                                return True
                        
                        time.sleep(0.5)  # Quick checks every 0.5 seconds
                        
                    except Exception as e:
                        time.sleep(0.5)
                
                self.log("🚀 Quick start mode - proceeding with gameplay!")
                return True
            else:
                self.log(f"❌ ROM upload failed: {result}")
                return False
            
        except Exception as e:
            self.log(f"❌ ROM upload failed: {e}")
            return False

    def take_screenshot_tool(self, game_only=True):
        """Tool: Take screenshot and return the screenshot number
        Args:
            game_only (bool): If True, capture only the game canvas. If False, capture full browser.
        """
        try:
            self.screenshot_count += 1
            filename = f"screenshot_{self.screenshot_count}.png"
            filepath = os.path.join(self.screenshots_folder, filename)
            
            if game_only:
                # Try to capture just the game canvas
                screenshot_data = self.capture_game_canvas()
                if screenshot_data:
                    with open(filepath, 'wb') as f:
                        f.write(screenshot_data)
                    self.log(f"📸 Game canvas screenshot saved: {filename}")
                    return self.screenshot_count
                else:
                    self.log("⚠️ Game canvas capture failed, falling back to full browser screenshot")
            
            # Fallback: Take full browser screenshot
            screenshot = self.driver.get_screenshot_as_png()
            
            # Save to file
            with open(filepath, 'wb') as f:
                f.write(screenshot)
            
            self.log(f"📸 {'Full browser' if not game_only else 'Fallback'} screenshot saved: {filename}")
            return self.screenshot_count
            
        except Exception as e:
            self.log(f"❌ Screenshot failed: {e}")
            return None

    def capture_game_canvas(self):
        """Capture just the game canvas by cropping the full browser screenshot"""
        try:
            self.log("🎮 Capturing game area from browser screenshot...")
            
            # First, get the full browser screenshot
            full_screenshot = self.driver.get_screenshot_as_png()
            
            # Get the position and size of the game canvas
            canvas_info_js = """
            try {
                const gameDiv = document.getElementById('game');
                if (!gameDiv) return { error: 'No game div found' };
                
                const canvas = gameDiv.querySelector('canvas');
                if (!canvas) return { error: 'No canvas found' };
                
                // Get the canvas position and size relative to the viewport
                const rect = canvas.getBoundingClientRect();
                const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
                const scrollY = window.pageYOffset || document.documentElement.scrollTop;
                
                return {
                    success: true,
                    x: Math.round(rect.left + scrollX),
                    y: Math.round(rect.top + scrollY),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight,
                    devicePixelRatio: window.devicePixelRatio || 1
                };
                
            } catch (error) {
                return { error: error.message };
            }
            """
            
            canvas_info = self.driver.execute_script(canvas_info_js)
            
            if isinstance(canvas_info, dict) and canvas_info.get('error'):
                self.log(f"❌ Canvas position detection failed: {canvas_info['error']}")
                return None
            elif not isinstance(canvas_info, dict) or not canvas_info.get('success'):
                self.log(f"❌ Unexpected canvas info result: {canvas_info}")
                return None
            
            # Extract canvas position and dimensions
            canvas_x = canvas_info['x']
            canvas_y = canvas_info['y'] 
            canvas_width = canvas_info['width']
            canvas_height = canvas_info['height']
            pixel_ratio = canvas_info['devicePixelRatio']
            
            self.log(f"📐 Canvas detected at ({canvas_x}, {canvas_y}) size {canvas_width}x{canvas_height}, pixel ratio: {pixel_ratio}")
            
            # Validate canvas dimensions
            if canvas_width < 100 or canvas_height < 100:
                self.log(f"⚠️ Canvas too small: {canvas_width}x{canvas_height}")
                return None
            
            # Use PIL to crop the screenshot
            from PIL import Image
            import io
            
            # Open the full screenshot
            full_image = Image.open(io.BytesIO(full_screenshot))
            
            # Account for device pixel ratio (retina displays)
            crop_x = int(canvas_x * pixel_ratio)
            crop_y = int(canvas_y * pixel_ratio)
            crop_width = int(canvas_width * pixel_ratio)
            crop_height = int(canvas_height * pixel_ratio)
            
            # Ensure crop coordinates are within image bounds
            img_width, img_height = full_image.size
            crop_x = max(0, min(crop_x, img_width - 10))
            crop_y = max(0, min(crop_y, img_height - 10))
            crop_width = min(crop_width, img_width - crop_x)
            crop_height = min(crop_height, img_height - crop_y)
            
            self.log(f"🔪 Cropping area: ({crop_x}, {crop_y}) to ({crop_x + crop_width}, {crop_y + crop_height})")
            
            # Crop the image
            game_image = full_image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
            
            # Convert back to PNG bytes
            output_buffer = io.BytesIO()
            game_image.save(output_buffer, format='PNG')
            game_image_bytes = output_buffer.getvalue()
            
            # Quick content check
            if len(game_image_bytes) < 1000:
                self.log(f"⚠️ Cropped image seems too small: {len(game_image_bytes)} bytes")
                return None
            
            self.log(f"✅ Game area cropped successfully: {len(game_image_bytes):,} bytes")
            self.log(f"📐 Final game image size: {game_image.size}")
            
            return game_image_bytes
            
        except Exception as e:
            self.log(f"❌ Game area crop failed: {e}")
            import traceback
            self.log(f"❌ Full error: {traceback.format_exc()}")
            return None
    
    def save_screenshot_description(self, screenshot_number, description):
        """Save screenshot description to .txt file"""
        try:
            desc_filename = f"screenshot_{screenshot_number}.txt"
            desc_filepath = os.path.join(self.screenshots_folder, desc_filename)
            
            self.log(f"🔍 DEBUG: Saving to {desc_filepath}")
            self.log(f"🔍 DEBUG: Description length: {len(description) if description else 0}")
            self.log(f"🔍 DEBUG: Description preview: {description[:100] if description else 'EMPTY'}...")
            
            with open(desc_filepath, 'w', encoding='utf-8') as f:
                f.write(description or "No description provided")
            
            # Verify the file was written
            if os.path.exists(desc_filepath):
                with open(desc_filepath, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                    self.log(f"✅ Verified saved content length: {len(saved_content)}")
            
            self.log(f"📝 Description saved: {desc_filename}")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to save description: {e}")
            import traceback
            self.log(f"❌ Full error: {traceback.format_exc()}")
            return False
    
    def recall_screenshot_tool(self, screenshot_number):
        """Tool: Recall screenshot description by number"""
        try:
            desc_filename = f"screenshot_{screenshot_number}.txt"
            desc_filepath = os.path.join(self.screenshots_folder, desc_filename)
            
            if os.path.exists(desc_filepath):
                with open(desc_filepath, 'r', encoding='utf-8') as f:
                    description = f.read()
                    self.log(f"📖 Retrieved description: {desc_filename}")
                    return description
            else:
                self.log(f"❌ Description not found: {desc_filename}")
                return f"No description found for screenshot {screenshot_number}"
                
        except Exception as e:
            self.log(f"❌ Error retrieving description: {e}")
            return f"Error retrieving description for screenshot {screenshot_number}"

    def analyze_current_screen_with_vision(self):
        """Direct vision analysis of current screen - fallback when text descriptions aren't sufficient"""
        try:
            self.log("📸 Taking direct vision screenshot...")
            
            # Get current screenshot as base64
            screenshot_data = self.capture_game_canvas()
            if not screenshot_data:
                self.log("❌ Failed to capture game canvas for vision analysis")
                return None
            
            screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')
            
            # Load current memory for context
            memory_list = self.load_memory()
            memory_context = "\n".join([f"- {memory}" for memory in memory_list])
            
            self.log("🧠 Sending direct vision analysis to Grok-4...")
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an AI playing Pokemon Fire Red. Analyze this screenshot and provide detailed gameplay guidance.

CURRENT MEMORY CONTEXT:
{memory_context}

Your task: Look at the screenshot and provide:
1. **Scene Description**: What type of location is this? (overworld, cave, building, menu, battle, etc.)
2. **Player Position**: Where is the player character located on screen?
3. **Interactive Elements**: NPCs, items, doors, ladders, signs, Pokemon, etc.
4. **Navigation Instructions**: If this is a navigable area (overworld/cave/building), provide SPECIFIC movement directions

FOR NAVIGATION AREAS (overworld, caves, buildings):
- Give precise movement instructions like "move UP 3 spaces then LEFT 2 spaces to reach the Pokemon Center"
- Count grid spaces/tiles when possible
- Identify key destinations: Pokemon Centers, Gyms, shops, exits, ladders, doors
- Note obstacles: trees, rocks, water, walls, trainers
- Suggest efficient pathing to objectives

FOR BATTLES/MENUS:
- Describe available options and recommend selections
- Explain battle strategies and type advantages

FOR DIALOGUE/TEXT:
- Summarize the conversation and recommend responses
- Note important story information

MOVEMENT BATCHING: Always suggest batched movement for efficiency:
- "[UP, UP, UP, LEFT, LEFT]" instead of individual moves
- Chain movements with interactions: "[RIGHT, RIGHT, A]" to move then talk to NPC

Be specific about game elements: coordinates, distances, exact button sequences needed."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this Pokemon Fire Red screenshot and tell me what I should do next. Be specific about what you see and what actions to take."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_b64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Use robust API call instead of direct requests
            content = self.robust_api_call(messages, max_tokens=32000, temperature=0.3, function_name="Direct Vision")
            
            if content:
                self.log(f"✅ Direct vision analysis complete: {content[:100]}...")
                return content
            else:
                self.log("❌ Direct vision analysis failed")
                return None
                
        except Exception as e:
            self.log(f"❌ Direct vision analysis error: {e}")
            return None

    def ask_ai_what_to_do(self, memory_list):
        """Ask AI what tools to use and actions to take"""
        try:
            memory_context = "\n".join([f"- {memory}" for memory in memory_list])
            
            messages = [{
                "role": "system",
                "content": f"""You're playing Pokemon Fire Red. Frame {self.frame_count}.

MEMORY: {memory_context}

Tools available:
- analyze_with_vision() - Direct AI vision analysis, this is the preferred way to see the game.
- take_screenshot() - See current game state (saves as screenshot_N.png + description as screenshot_N.txt)
- recall_screenshot(N) - View previous screenshot N description (reads screenshot_N.txt)


Respond with JSON (ONLY choose tools, no actions):
{{
  "tool_calls": [{{"tool": "take_screenshot"}}],
  "reasoning": "why you want to see this visual information"
}}

Examples:
- {{"tool_calls": [{{"tool": "take_screenshot"}}], "reasoning": "need to see current screen"}}
- {{"tool_calls": [{{"tool": "recall_screenshot", "number": 3}}], "reasoning": "need to remember what screen 3 looked like"}}
- {{"tool_calls": [{{"tool": "analyze_with_vision"}}], "reasoning": "text description unclear, need direct vision analysis"}}

SCREENSHOT SYSTEM:
- Screenshots saved as: screenshot_1.png, screenshot_2.png, etc.
- Descriptions saved as: screenshot_1.txt, screenshot_2.txt, etc.
- Current screenshot count: {self.screenshot_count}

STRATEGY:
- Usually use analyze_with_vision() to see current state
- Use recall_screenshot(N) to remember past locations/screens (reads screenshot_N.txt)
- Use take_screenshot() when you need detailed text descriptions of the viewport
- You'll make gameplay decisions AFTER seeing the visual info

Focus: Choose the right tool to get visual information you need."""
            }, {
                "role": "user",
                "content": f"Frame {self.frame_count}: What should you do? Use tools to see the game."
            }]
            
            # Use robust API call
            content = self.robust_api_call(messages, max_tokens=32000, temperature=0.7, function_name="Tool Selection")
            
            if content:
                result = self.parse_json_with_fallback(content, "Tool Selection")
                
                # Ensure we always have tool_calls
                if "tool_calls" not in result:
                    result["tool_calls"] = [{"tool": "analyze_with_vision"}]
                if "reasoning" not in result:
                    result["reasoning"] = "Default reasoning"
                    
                return result
            else:
                return {
                    "tool_calls": [{"tool": "analyze_with_vision"}],
                    "reasoning": "API failed, taking screenshot"
                }
                
        except Exception as e:
            self.log(f"❌ AI query error: {e}")
            return {
                "tool_calls": [{"tool": "analyze_with_vision"}],
                "reasoning": f"Error: {e}",
                "actions": ["START"]
            }

    def execute_tools(self, tool_calls):
        """Execute the AI's tool calls"""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            
            if tool_name == "take_screenshot":
                screenshot_num = self.take_screenshot_tool()  # Uses game_only=True by default
                if screenshot_num:
                    # Get screenshot and analyze it
                    screenshot_b64 = self.get_screenshot_base64(screenshot_num)
                    if screenshot_b64:
                        # Get vision analysis
                        self.log("🧠 Analyzing screenshot with Grok-4 Vision...")
                        description = self.analyze_screenshot_with_vision(screenshot_b64)
                        # Save description
                        self.save_screenshot_description(screenshot_num, description)
                        results.append(f"Screenshot {screenshot_num}: {description}")
                        self.log(f"📸 Screenshot {screenshot_num} analyzed and saved")
                    else:
                        results.append(f"Screenshot {screenshot_num} failed to load")
                        self.log(f"❌ Screenshot {screenshot_num} failed to load")
                else:
                    results.append("Failed to take screenshot")
                    self.log("❌ Failed to take screenshot")
                    
            elif tool_name == "recall_screenshot":
                # Get number from different possible locations
                number = tool_call.get("number") or tool_call.get("screenshot_number") or tool_call.get("N")
                if number:
                    description = self.recall_screenshot_tool(number)
                    results.append(f"Screenshot {number}: {description}")
                    self.log(f"📖 Recalled screenshot {number}")
                else:
                    results.append("No screenshot number provided for recall")
                    self.log("❌ No screenshot number provided for recall")
                    
            elif tool_name == "analyze_with_vision":
                self.log("🔍 Using direct vision analysis...")
                vision_analysis = self.analyze_current_screen_with_vision()
                if vision_analysis:
                    results.append(f"Direct Vision Analysis: {vision_analysis}")
                    self.log("✅ Direct vision analysis completed")
                else:
                    results.append("Direct vision analysis failed")
                    self.log("❌ Direct vision analysis failed")
                    
            elif tool_name == "cleanup_memory":
                self.log("🧠 Manual memory cleanup requested...")
                memory_list = self.load_memory()
                cleaned_memory = self.cleanup_memory_with_ai()
                if cleaned_memory and len(cleaned_memory) != len(memory_list):
                    self.save_memory(cleaned_memory)
                    results.append(f"Memory cleanup completed: {len(memory_list)} → {len(cleaned_memory)} entries")
                    self.log(f"✅ Manual memory cleanup successful: {len(memory_list)} → {len(cleaned_memory)}")
                else:
                    results.append("Memory cleanup completed - no changes needed")
                    self.log("✅ Memory cleanup completed - no changes needed")
        
        return results
    
    def get_screenshot_base64(self, screenshot_number):
        """Get a previous screenshot by number and return as base64"""
        try:
            filename = f"screenshot_{screenshot_number}.png"
            filepath = os.path.join(self.screenshots_folder, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    image_data = f.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    self.log(f"📷 Retrieved screenshot: {filename}")
                    return base64_data
            else:
                self.log(f"❌ Screenshot not found: {filename}")
                return None
                
        except Exception as e:
            self.log(f"❌ Error retrieving screenshot: {e}")
            return None
    
    def get_canvas_screenshot_base64(self):
        """Get current canvas screenshot as base64 for AI analysis"""
        try:
            # Take screenshot of just the game canvas
            canvas_screenshot_js = """
            const canvas = document.querySelector('#game canvas');
            if (canvas && canvas.width > 0 && canvas.height > 0) {
                // Convert canvas to base64 image
                return canvas.toDataURL('image/png').split(',')[1];
            }
            return null;
            """
            
            canvas_b64 = self.driver.execute_script(canvas_screenshot_js)
            
            if canvas_b64:
                return canvas_b64
            else:
                # Fallback: take full screenshot and return base64
                self.log("⚠️ Canvas screenshot failed, using full browser screenshot")
                screenshot = self.driver.get_screenshot_as_png()
                return base64.b64encode(screenshot).decode('utf-8')
                
        except Exception as e:
            self.log(f"❌ Canvas screenshot error: {e}")
            return None

    def analyze_screenshot_with_vision(self, image_base64):
        """Analyze a screenshot with Grok-4 Vision and return description"""
        try:
            self.log(f"🔍 Starting vision analysis (image size: {len(image_base64)} chars)")
            
            # Optimize image size if it's too large
            optimized_image_b64 = self.optimize_image_for_vision(image_base64)
            if len(optimized_image_b64) < len(image_base64):
                self.log(f"📸 Image optimized: {len(image_base64)} -> {len(optimized_image_b64)} chars")
                image_base64 = optimized_image_b64
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this Pokemon Fire Red screenshot briefly: what you see, menus, characters, dialog, battles."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Use robust API call for vision analysis
            content = self.robust_api_call(messages, max_tokens=32000, temperature=0.3, function_name="Vision Analysis")
            
            if content and len(content.strip()) > 0:
                self.log(f"✅ Vision analysis complete: {content[:100]}...")
                return content
            else:
                self.log("❌ Vision analysis failed or returned empty content")
                return "Vision analysis failed"
            
        except Exception as e:
            error_msg = f"Vision analysis error: {e}"
            self.log(f"❌ {error_msg}")
            return error_msg

    def optimize_image_for_vision(self, image_base64):
        """Optimize image size for vision analysis if needed"""
        try:
            # Only optimize if image is very large (>500KB base64)
            if len(image_base64) < 500000:
                return image_base64
            
            self.log("📸 Optimizing large image for vision analysis...")
            
            import base64
            from PIL import Image
            import io
            
            # Decode base64 to image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Get original size
            original_size = image.size
            self.log(f"📐 Original image size: {original_size}")
            
            # Resize if too large (keep aspect ratio)
            max_dimension = 1200
            if max(original_size) > max_dimension:
                ratio = max_dimension / max(original_size)
                new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                self.log(f"📐 Resized to: {new_size}")
            
            # Save as PNG with optimization
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='PNG', optimize=True)
            optimized_data = output_buffer.getvalue()
            
            # Convert back to base64
            optimized_b64 = base64.b64encode(optimized_data).decode('utf-8')
            
            self.log(f"📸 Optimization result: {len(image_base64)} -> {len(optimized_b64)} chars")
            return optimized_b64
            
        except Exception as e:
            self.log(f"⚠️ Image optimization failed: {e}, using original")
            return image_base64

    def query_grok4_simple(self, memory_list, vision_description, screenshot_num):
        """Simple query to Grok-4 with vision description"""
        try:
            memory_context = "\n".join([f"- {memory}" for memory in memory_list])
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are playing Pokemon Fire Red. You can see the game through screenshot descriptions.

Current screenshot #{screenshot_num}: {vision_description}

Previous memories:
{memory_context}

Respond with JSON:
{{
    "reasoning": "what you see and plan",
    "actions": ["list of actions like A, B, UP, DOWN, LEFT, RIGHT, START, SELECT"],
    "memory_updates": {{"add": [], "remove": [], "update": {{"key": "value"}}}}
}}

Key controls:
- A: Confirm/interact/advance text (USE THIS MOST)
- B: Cancel/back  
- Arrow keys: Navigate menus/movement
- START: ONLY for title screen or opening main menu
- SELECT: Special functions

IMPORTANT: 
- Use A to advance dialogue and interact with NPCs/objects
- Use arrows to move around - batch them for efficiency (["UP", "UP", "UP"])
- Only use START if you see a title screen or need the main menu
- Use buttons appropriately based on context
- Use memory.txt to track your progress and plan ahead (320 entries, ~100 tokens each)
- Include rich detail: locations, Pokemon, battles, story progress, items, NPCs
- Always associate memories with screenshot numbers: "SCREENSHOTS: [X,Y] | LOCATION: ..."
- 🚀 BATCH ACTIONS AGGRESSIVELY: For intro/tutorial text, send ["A","A","A","A","A"] to blast through dialogue
- Only take individual actions when making choices or entering text

START BUTTON USAGE:
- Use START to access in-game menus and pause screens
- Use A button for dialogue, tutorials, and most navigation
- If START doesn't work on a screen, try A instead
- Both START and A are valid - choose based on context"""
                },
                {
                    "role": "user",
                    "content": f"Screenshot {screenshot_num} shows: {vision_description}. What should I do next?"
                }
            ]
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-4",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500  # Increased from 300 to 500
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                try:
                    ai_response = json.loads(content)
                    ai_response["image_description"] = vision_description
                    return ai_response
                except json.JSONDecodeError:
                    self.log("⚠️ JSON parse failed, using simple fallback")
                    return {
                        "reasoning": "JSON parse failed, pressing START to progress",
                        "actions": ["START"],
                        "memory_updates": {"add": [f"Screenshot {screenshot_num}: {vision_description}"]},
                        "image_description": vision_description
                    }
            else:
                self.log(f"❌ API request failed: {response.status_code}")
                return {
                    "reasoning": "API failed, trying START",
                    "actions": ["START"],
                    "memory_updates": {},
                    "image_description": vision_description
                }
                
        except Exception as e:
            self.log(f"❌ Simple query error: {e}")
            return {
                "reasoning": f"Error occurred: {e}",
                "actions": ["START"],
                "memory_updates": {},
                "image_description": vision_description
            }

    def query_grok4_with_vision(self, memory_list, image_base64):
        """Query Grok-4 with vision capabilities for both image analysis and decision making"""
        try:
            # Format memory context
            memory_context = "//MEMORY//\n" + "\n".join([f"{i+1}. {mem}" for i, mem in enumerate(memory_list)]) + "\n//END MEMORY//\n\n"
            
            # Add control hints
            controls_hint = """//KEYBOARD CONTROLS//
A Button (z key): Interact/Confirm - Use to talk to NPCs, select menu options, advance dialogue
B Button (x key): Cancel/Back - Use to go back in menus, cancel actions
START (Enter): Start/Menu - Opens the main menu, confirms on title screen  
SELECT (Shift): Select/Options - Special functions, item shortcuts
Arrow Keys: Move character Up/Down/Left/Right in overworld
L/R Shoulder (a/s keys): Quick actions, menu shortcuts
//END CONTROLS//

"""
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "grok-4",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an AI playing Pokemon Fire Red. You can see the game screen and must decide what actions to take.

Respond with JSON containing:
{
  "image_description": "detailed description of what you see in the game",
  "reasoning": "your strategy and why you chose these actions",
  "actions": ["ACTION1", "ACTION2", ...],
  "memory_updates": {
    "add": ["new memory to add"],
    "remove": [1, 3],
    "update": {"index": 2, "content": "updated memory"}
  }
}

Available actions: A, B, START, SELECT, UP, DOWN, LEFT, RIGHT, L, R

🚀 AGGRESSIVE BATCHING REQUIRED: You can and SHOULD send multiple actions in sequence:
- ["UP", "UP", "UP"] to move up 3 spaces quickly
- ["LEFT", "LEFT", "A"] to move left twice then interact
- ["A", "A", "A", "A", "A"] to RAPIDLY advance through intro/tutorial dialogue
- ["A", "A", "A", "A"] for repetitive menu navigation
- Each action has 0.75s delay, so batch aggressively for speed

⚡ INTRO/TUTORIAL EFFICIENCY: For obvious dialogue sequences (Professor Oak intro, controls tutorial, story exposition):
- Use ["A", "A", "A", "A", "A"] to blast through 5+ dialogue boxes at once
- Only take individual actions when you need to make a choice or enter text
- Don't waste time taking screenshots between every single text advance
- Be AGGRESSIVE about batching during repetitive sequences

🎯 SPECIFIC SITUATIONS REQUIRING BATCHING:
- Professor Oak intro dialogue: ["A", "A", "A", "A", "A"] 
- Controls tutorial pages: ["A", "A", "A", "A"]
- Story exposition with Pikachu: ["A", "A", "A", "A"]
- Any "red arrow" dialogue sequences: BATCH MULTIPLE A's!
- Only use single ["A"] when you see actual choices or text input

MEMORY SYSTEM: Use your memory.txt scratchpad for:
- Long-term planning and objectives
- Pokemon team composition and levels  
- Important locations and NPCs
- Battle strategies and type matchups
- Progress tracking through the story

Key strategies:
- Use A for most navigation, START for menus and pause screens
- Use A to advance dialogue and interact with NPCs/objects
- Use B to go back in menus  
- Use arrow keys to move around the overworld
- Read all text carefully and make strategic decisions
- Progress through the tutorial to start your Pokemon journey

Memory management (memory.txt is your massive persistent scratchpad - 320 entries!):
- Each memory entry should be ~100 tokens (75-100 words) with rich detail
- Format: "LOCATION: [place] | ACTION: [what you did] | RESULT: [outcome] | POKEMON: [team status] | NEXT: [plan]"
- Track: story progress, Pokemon caught/trained, battles won/lost, items found, NPCs met
- Include: levels, movesets, type advantages learned, gym strategies, important locations
- Update CURRENT PROGRESS with detailed status and immediate goals
- Plan long-term strategies: gym order, team building, story objectives
- Track exploration: routes visited, areas unlocked, secrets found

Examples of good memory entries:
- "SCREENSHOTS: [15,16,17] | ROUTE 1: Caught Pidgey Lv4 (Tackle/Sand Attack), fought 3 trainers, gained 200 exp, learned type advantages. Rattata weak to Fighting moves. NEXT: Train team to Lv8 before Brock"
- "SCREENSHOTS: [23,24] | VIRIDIAN CITY: Visited Pokemon Center (healed team), bought 5 Pokeballs, 3 Potions. Gym Leader absent. Old man taught catching demo. NEXT: Explore Route 2, find Viridian Forest"

REMEMBER: You have MASSIVE memory capacity - use detailed, structured entries!
🚀 BATCH ACTIONS AGGRESSIVELY: Chain movements and interactions for maximum efficiency with 0.75s delays.
⚡ SPEED RULE: For intro sequences, tutorials, and repetitive dialogue - BATCH 4-5 A's at once! Don't be cautious!"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{memory_context}{controls_hint}Please analyze this Pokemon Fire Red game screenshot and decide what actions to take next."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content']
                
                try:
                    # Try to parse JSON response
                    json_response = json.loads(response_text)
                    return json_response
                except json.JSONDecodeError:
                    # Fallback for non-JSON responses
                    self.log("⚠️ Non-JSON response from Grok-4, parsing manually")
                    return {
                        "image_description": "Unable to parse image description",
                        "reasoning": response_text,
                        "actions": ["A"],
                        "memory_updates": {"add": [], "remove": [], "update": {}}
                    }
                    
            else:
                self.log(f"❌ Grok-4 Vision API Error: {response.status_code} - {response.text}")
                return {
                    "image_description": "API error occurred",
                    "reasoning": "API error, defaulting to A button",
                    "actions": ["A"],
                    "memory_updates": {"add": [], "remove": [], "update": {}}
                }
                
        except Exception as e:
            self.log(f"❌ Grok-4 Vision error: {e}")
            return {
                "image_description": "Error analyzing image",
                "reasoning": "Error occurred, defaulting to A button",
                "actions": ["A"], 
                "memory_updates": {"add": [], "remove": [], "update": {}}
            }

    def update_memory(self, memory_list, updates):
        """Update memory based on AI instructions"""
        try:
            new_memory = memory_list.copy()
            
            # Remove items (in reverse order to maintain indices)
            if "remove" in updates and updates["remove"]:
                for index in sorted(updates["remove"], reverse=True):
                    if 0 <= index - 1 < len(new_memory):
                        removed = new_memory.pop(index - 1)
                        self.log(f"🧠 Removed memory: {removed}")
            
            # Update items
            if "update" in updates and updates["update"]:
                update_info = updates["update"]
                if "index" in update_info and "content" in update_info:
                    index = update_info["index"] - 1
                    if 0 <= index < len(new_memory):
                        old_content = new_memory[index]
                        new_memory[index] = update_info["content"]
                        self.log(f"🧠 Updated memory {index+1}: {old_content} → {update_info['content']}")
            
            # Add new items
            if "add" in updates and updates["add"]:
                for new_mem in updates["add"]:
                    new_memory.append(new_mem)
                    self.log(f"🧠 Added memory: {new_mem}")
            
            # Keep memory size manageable (massive limit with 32K tokens)
            if len(new_memory) > 320:
                new_memory = new_memory[-320:]
                self.log("🧠 Trimmed memory to last 320 items")
            
            # Trigger intelligent cleanup if memory is getting repetitive
            elif len(new_memory) > 100 and len(new_memory) % 50 == 0:  # Every 50 entries after 100
                self.log("🧠 Memory checkpoint reached - checking for cleanup needs...")
                
                # Quick analysis for repetitive patterns
                recent_entries = new_memory[-20:]  # Last 20 entries
                if len(set(recent_entries)) < len(recent_entries) * 0.5:  # If >50% are duplicates
                    self.log("🔄 Repetitive memory detected - triggering AI cleanup...")
                    cleaned_memory = self.cleanup_memory_with_ai()
                    if cleaned_memory and len(cleaned_memory) < len(new_memory):
                        new_memory = cleaned_memory
                        self.log(f"✅ Memory optimized via AI cleanup")
            
            return new_memory
            
        except Exception as e:
            self.log(f"⚠️ Memory update error: {e}")
            return memory_list

    def analyze_current_screen_with_vision(self):
        """Direct vision analysis when text descriptions aren't sufficient"""
        try:
            self.log("🔍 Taking current screenshot for direct vision analysis...")
            
            # Take a fresh screenshot
            canvas_screenshot_data = self.capture_game_canvas()
            if not canvas_screenshot_data:
                self.log("❌ Failed to capture game canvas for vision analysis")
                return None
            
            # Convert to base64
            canvas_b64 = base64.b64encode(canvas_screenshot_data).decode('utf-8')
            
            # Optimize if needed
            optimized_b64 = self.optimize_image_for_vision(canvas_b64)
            
            self.log("🧠 Performing direct vision analysis with context...")
            
            # Load memory for context
            memory_list = self.load_memory()
            memory_context = "\n".join([f"- {memory}" for memory in memory_list])
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an AI playing Pokemon Fire Red. You have been asked to analyze the current screen directly because text descriptions were insufficient.

MEMORY CONTEXT:
{memory_context}

SCREENSHOT COUNT: {self.screenshot_count}
FILES: Screenshots saved as screenshot_1.png, screenshot_2.png, etc. with descriptions in screenshot_1.txt, screenshot_2.txt, etc.

Provide detailed analysis focusing on:
- **Scene Type**: Overworld, cave, building, battle, menu, dialogue, etc.
- **Player Position**: Exact location of player character on the grid/screen
- **Interactive Elements**: NPCs, items, Pokemon, doors, ladders, signs, trainers
- **Navigation Instructions**: For movement areas, provide SPECIFIC directions

FOR OVERWORLD/CAVES/BUILDINGS (when player can move):
- Count exact tile distances: "Pokemon Center is 3 tiles UP, 2 tiles LEFT from player"
- Identify pathways: "Clear path available" or "blocked by trainer/obstacle"
- Suggest efficient batched movements: "[UP, UP, UP, LEFT, LEFT, A]"
- Note all destinations: Pokemon Centers, Gyms, shops, exits, doors, ladders
- Identify obstacles: trees, water, rocks, walls, NPCs, trainers

FOR BATTLES/MENUS:
- Describe options and recommend selections
- Battle strategy and type advantages

🚀 AGGRESSIVE EFFICIENCY REQUIRED: Always suggest batched actions for maximum speed.
⚡ DIALOGUE RULE: For story/tutorial text, use ["A","A","A","A","A"] to advance 5 dialogue boxes at once!
🎯 MOVEMENT RULE: Instead of "move up then left", say "[UP, UP, LEFT, LEFT]"
⏱️ SPEED PRIORITY: Don't waste time with single actions during obvious repetitive sequences!

Be specific about visual details and provide actionable navigation guidance."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "I need direct vision analysis of this Pokemon Fire Red screen. Text descriptions weren't clear enough for navigation/decision making. What exactly do you see and what should I do?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{optimized_b64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Use robust API call instead of direct requests
            content = self.robust_api_call(messages, max_tokens=32000, temperature=0.3, function_name="Direct Vision")
            
            if content:
                self.log(f"✅ Direct vision analysis complete: {content[:100]}...")
                return content
            else:
                self.log("❌ Direct vision analysis failed")
                return None
                
        except Exception as e:
            self.log(f"❌ Direct vision analysis error: {e}")
            return None

    def make_gameplay_decision(self, memory_list, screenshot_info):
        """Make gameplay decisions based on memory and current screenshot"""
        try:
            memory_context = "\n".join([f"- {memory}" for memory in memory_list])
            
            # Extract screenshot description from the info
            if "Screenshot" in screenshot_info and ":" in screenshot_info:
                screenshot_desc = screenshot_info.split(":", 1)[1].strip()
            else:
                screenshot_desc = screenshot_info
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are playing Pokemon Fire Red. You have memory context and current visual information.

MEMORY (your persistent scratchpad - up to 320 entries):
{memory_context}

CURRENT VISUAL: {screenshot_desc}
CURRENT SCREENSHOT: This is screenshot #{self.screenshot_count} - reference this number in your memory entries

BUTTON SELECTION STRATEGY:
- A button: Primary for dialogue, tutorials, confirmations, and most navigation
- START button: For accessing in-game menus, pause screens, and game options
- If unsure which to use, A is usually the safer choice for progression
- Try START if you need to access menus or pause the game

MEMORY GUIDELINES:
- You have room for 320 memory entries (massive context!)
- Make each memory entry ~100 tokens (about 75-100 words)
- Include rich detail: locations, Pokemon encountered, battle outcomes, story progress
- Use structured format: "LOCATION: Pallet Town | ACTION: Talked to Mom | RESULT: Got running shoes | NEXT: Visit Oak's lab"
- **ASSOCIATE WITH SCREENSHOTS**: Link memories to relevant screenshot files for reference

MEMORY-SCREENSHOT LINKING:
- Format: "SCREENSHOTS: [1,2,3] | LOCATION: Pallet Town | ACTION: Talked to Mom..."
- Always reference which screenshot numbers are relevant to each memory
- This helps you recall visual context and verify memory accuracy
- You can use recall_screenshot(N) to review linked screenshots later

MEMORY SELF-MONITORING:
- If you notice repetitive or contradictory entries, flag them for cleanup
- If stuck in loops (same actions repeatedly), recognize this and try different approaches
- Periodically assess if your memory accurately reflects game state
- You can use the analyze_with_vision() tool to verify current situation vs memory
- Use screenshot associations to cross-reference visual evidence with memories

Respond with JSON:
{{
    "reasoning": "what you see and your strategy",
    "actions": ["A", "B", "UP", "DOWN", "LEFT", "RIGHT", "START", "SELECT"],
    "memory_updates": {{"add": [], "remove": [], "update": {{"index": 1, "content": "new content"}}}}
}}

CONTROLS:
- A: Interact/advance text/confirm (USE MOST)
- B: Cancel/back
- UP/DOWN/LEFT/RIGHT: Move (batch them: ["UP","UP","UP"])
- START: ONLY for title screen or main menu
- SELECT: Special functions

BUTTON TROUBLESHOOTING:
- If START button doesn't respond on title screens, try A button instead
- If you pressed START recently and nothing happened, use A to proceed
- Some screens accept both START and A - A is more reliable
- If stuck on a screen after pressing START, try A to advance

BATCHING: Use efficient sequences like ["UP","UP","A"] or ["A","A","A"]
MEMORY: Update your progress with rich detail (~100 tokens per entry, up to 320 entries)
- Include: locations, Pokemon encounters, battle results, story progress, NPCs met
- Format: "SCREENSHOTS: [X,Y] | LOCATION: Route 1 | POKEMON: Caught Pidgey Lv3 | MOVES: Tackle, Sand Attack | NEXT: Head to Viridian City"
- Always link memories to relevant screenshot numbers for visual reference
TOOLS: You can use recall_screenshot(N), analyze_with_vision(), or cleanup_memory() if needed

MEMORY MANAGEMENT TOOLS:
- cleanup_memory(): Use if you notice repetitive or contradictory memory entries
- This will intelligently reorganize and summarize your memory for better context
- Useful when stuck in loops or when memory seems inconsistent with current state

Strategy: Based on what you see, decide the best actions to progress the game. If START fails, fallback to A."""
                },
                {
                    "role": "user", 
                    "content": f"Current screen: {screenshot_desc}. What should you do next?"
                }
            ]
            
            # Use robust API call with higher token limit to prevent truncation
            content = self.robust_api_call(messages, max_tokens=32000, temperature=0.7, function_name="Gameplay Decision")
             
            if content:
                decision = self.parse_json_with_fallback(content, "Gameplay Decision", "A")
                decision["image_description"] = screenshot_info
                 
                 # Ensure required fields exist
                if "reasoning" not in decision:
                     decision["reasoning"] = "AI made a decision"
                if "actions" not in decision:
                     decision["actions"] = ["A"]
                if "memory_updates" not in decision:
                     decision["memory_updates"] = {}
                     
                return decision
            else:
                return {
                     "reasoning": "API failed, using fallback",
                     "actions": ["A"],
                     "memory_updates": {},
                     "image_description": screenshot_info
                 }
                
        except Exception as e:
            self.log(f"❌ Gameplay decision error: {e}")
            return {
                "reasoning": f"Error: {e}",
                "actions": ["A"],
                "memory_updates": {},
                "image_description": screenshot_info
            }

    def send_ai_thought(self, image_desc, reasoning, action):
        """Send AI thought to the overlay"""
        try:
            # Clean up the input strings to avoid JSON issues
            image_desc_clean = str(image_desc).replace('"', "'").replace('\n', ' ') if image_desc else ""
            reasoning_clean = str(reasoning).replace('"', "'").replace('\n', ' ') if reasoning else ""
            action_clean = str(action).replace('"', "'").replace('\n', ' ') if action else ""
            
            js_script = f"""
            try {{
                // Check if the function exists
                if (typeof window.addAIThought !== 'function') {{
                    console.error('addAIThought function not found');
                    return 'NO_FUNCTION';
                }}
                
                // Check if the thoughts container exists
                const thoughtsContainer = document.getElementById('aiThoughts');
                if (!thoughtsContainer) {{
                    console.error('aiThoughts container not found');
                    return 'NO_CONTAINER';
                }}
                
                // Call the function with cleaned parameters
                window.addAIThought(
                    {json.dumps(image_desc_clean)}, 
                    {json.dumps(reasoning_clean)}, 
                    {json.dumps(action_clean)}
                );
                
                console.log('AI thought added successfully');
                return 'THOUGHT_SENT';
                
            }} catch (error) {{
                console.error('Error adding AI thought:', error);
                return 'ERROR: ' + error.message;
            }}
            """
            
            result = self.driver.execute_script(js_script)
            
            if result == 'THOUGHT_SENT':
                self.log(f"💭 AI thought sent to overlay successfully")
            elif result == 'NO_FUNCTION':
                self.log(f"⚠️ addAIThought function not found - overlay may not be loaded")
                # Try to add the function manually
                self.ensure_ai_overlay_functions()
            elif result == 'NO_CONTAINER':
                self.log(f"⚠️ AI thoughts container not found - HTML may not be loaded")
            else:
                self.log(f"⚠️ AI thought failed: {result}")
                # Try once more with fallback
                self.send_ai_thought_fallback(image_desc_clean, reasoning_clean, action_clean)
            
        except Exception as e:
            self.log(f"⚠️ Failed to send AI thought: {e}")
            # Try fallback method
            self.send_ai_thought_fallback(image_desc, reasoning, action)

    def ensure_ai_overlay_functions(self):
        """Ensure AI overlay functions are available"""
        try:
            self.log("🔧 Adding AI overlay functions...")
            setup_js = """
            // Add the addAIThought function if it doesn't exist
            if (typeof window.addAIThought !== 'function') {
                window.addAIThought = function(imageDesc, reasoning, action) {
                    const thoughtsContainer = document.getElementById('aiThoughts');
                    if (!thoughtsContainer) {
                        console.error('aiThoughts container not found');
                        return;
                    }
                    
                    const timestamp = new Date().toLocaleTimeString();
                    const entry = document.createElement('div');
                    entry.className = 'ai-entry';
                    
                    let html = '<div class="ai-timestamp">' + timestamp + '</div>';
                    
                    if (imageDesc) {
                        html += '<div class="ai-image-desc">👁️ Sees: ' + imageDesc + '</div>';
                    }
                    
                    if (reasoning) {
                        html += '<div class="ai-reasoning">🤔 Thinks: ' + reasoning + '</div>';
                    }
                    
                    if (action) {
                        html += '<div class="ai-action">⚡ Action: ' + action + '</div>';
                    }
                    
                    entry.innerHTML = html;
                    thoughtsContainer.appendChild(entry);
                    
                    // Auto-scroll to bottom
                    thoughtsContainer.scrollTop = thoughtsContainer.scrollHeight;
                    
                    // Keep only last 20 entries
                    const entries = thoughtsContainer.querySelectorAll('.ai-entry');
                    if (entries.length > 20) {
                        entries[0].remove();
                    }
                };
                
                console.log('addAIThought function added successfully');
                return 'FUNCTION_ADDED';
            }
            return 'FUNCTION_EXISTS';
            """
            
            result = self.driver.execute_script(setup_js)
            self.log(f"🔧 AI overlay setup result: {result}")
            
        except Exception as e:
            self.log(f"❌ Failed to setup AI overlay: {e}")

    def send_ai_thought_fallback(self, image_desc, reasoning, action):
        """Fallback method to send AI thoughts directly"""
        try:
            self.log("🔄 Using fallback AI thought method...")
            
            # Clean the inputs
            image_desc_clean = str(image_desc).replace('"', "'").replace('\n', ' ') if image_desc else ""
            reasoning_clean = str(reasoning).replace('"', "'").replace('\n', ' ') if reasoning else ""
            action_clean = str(action).replace('"', "'").replace('\n', ' ') if action else ""
            
            fallback_js = f"""
            try {{
                const thoughtsContainer = document.getElementById('aiThoughts');
                if (!thoughtsContainer) {{
                    console.error('No aiThoughts container found');
                    return 'NO_CONTAINER';
                }}
                
                const timestamp = new Date().toLocaleTimeString();
                const entry = document.createElement('div');
                entry.className = 'ai-entry';
                entry.style.marginBottom = '15px';
                entry.style.padding = '10px';
                entry.style.borderRadius = '5px';
                entry.style.borderLeft = '4px solid #4CAF50';
                entry.style.background = '#333';
                
                let html = '<div style="color: #888; font-size: 12px; margin-bottom: 5px;">' + timestamp + '</div>';
                
                if ({json.dumps(image_desc_clean)}) {{
                    html += '<div style="color: #87CEEB; font-style: italic; margin-bottom: 8px; padding: 5px; background: #1a1a2e; border-radius: 3px;">👁️ Sees: ' + {json.dumps(image_desc_clean)} + '</div>';
                }}
                
                if ({json.dumps(reasoning_clean)}) {{
                    html += '<div style="color: #E8F5E8; margin-bottom: 8px; line-height: 1.4;">🤔 Thinks: ' + {json.dumps(reasoning_clean)} + '</div>';
                }}
                
                if ({json.dumps(action_clean)}) {{
                    html += '<div style="color: #FFD700; font-weight: bold; font-size: 14px;">⚡ Action: ' + {json.dumps(action_clean)} + '</div>';
                }}
                
                entry.innerHTML = html;
                thoughtsContainer.appendChild(entry);
                
                // Auto-scroll to bottom
                thoughtsContainer.scrollTop = thoughtsContainer.scrollHeight;
                
                // Keep only last 20 entries
                const entries = thoughtsContainer.querySelectorAll('.ai-entry');
                if (entries.length > 20) {{
                    entries[0].remove();
                }}
                
                return 'FALLBACK_SUCCESS';
                
            }} catch (error) {{
                console.error('Fallback AI thought error:', error);
                return 'FALLBACK_ERROR: ' + error.message;
            }}
            """
            
            result = self.driver.execute_script(fallback_js)
            self.log(f"🔄 Fallback result: {result}")
            
        except Exception as e:
            self.log(f"❌ Fallback AI thought failed: {e}")

    def execute_action_sequence(self, actions):
        """Execute a sequence of actions"""
        for i, action in enumerate(actions):
            if action in self.controls:
                key = self.controls[action]
                
                try:
                    # Enhanced JavaScript input method
                    js_script = f"""
                    try {{
                        const canvas = document.querySelector('#game canvas') || document.querySelector('canvas');
                        const target = canvas || document;
                        
                        const keyMappings = {{
                            'A': {{ code: 'KeyZ', key: 'z', keyCode: 90 }},
                            'B': {{ code: 'KeyX', key: 'x', keyCode: 88 }},
                            'START': {{ code: 'Enter', key: 'Enter', keyCode: 13 }},
                            'SELECT': {{ code: 'ShiftLeft', key: 'Shift', keyCode: 16 }},
                            'UP': {{ code: 'ArrowUp', key: 'ArrowUp', keyCode: 38 }},
                            'DOWN': {{ code: 'ArrowDown', key: 'ArrowDown', keyCode: 40 }},
                            'LEFT': {{ code: 'ArrowLeft', key: 'ArrowLeft', keyCode: 37 }},
                            'RIGHT': {{ code: 'ArrowRight', key: 'ArrowRight', keyCode: 39 }},
                            'L': {{ code: 'KeyA', key: 'a', keyCode: 65 }},
                            'R': {{ code: 'KeyS', key: 's', keyCode: 83 }}
                        }};
                        
                        const mapping = keyMappings['{action}'];
                        if (!mapping) return 'NO_MAPPING';
                        
                        const eventProps = {{
                            key: mapping.key,
                            code: mapping.code,
                            keyCode: mapping.keyCode,
                            which: mapping.keyCode,
                            bubbles: true,
                            cancelable: true,
                            composed: true
                        }};
                        
                        const keyDown = new KeyboardEvent('keydown', eventProps);
                        const keyUp = new KeyboardEvent('keyup', eventProps);
                        
                        const targets = [target, document, window];
                        targets.forEach(t => {{
                            if (t && t.dispatchEvent) {{
                                t.dispatchEvent(keyDown);
                            }}
                        }});
                        
                        setTimeout(() => {{
                            targets.forEach(t => {{
                                if (t && t.dispatchEvent) {{
                                    t.dispatchEvent(keyUp);
                                }}
                            }});
                        }}, 100);
                        
                        // DEBUG: Log key press for troubleshooting
                        console.log('🎮 Key pressed:', '{action}', 'keyCode:', mapping.keyCode, 'key:', mapping.key);
                        
                        return 'SUCCESS';
                        
                    }} catch (error) {{
                        return 'ERROR: ' + error.message;
                    }}
                    """
                    
                    result = self.driver.execute_script(js_script)
                    
                    if result == 'SUCCESS':
                        self.log(f"⌨️ Action {i+1}/{len(actions)}: {action} -> {key}")
                        
                        # Track START button attempts for troubleshooting
                        if action == "START":
                            memory_list = self.load_memory()
                            memory_list.append(f"ATTEMPTED: START button pressed at frame {self.screenshot_count}")
                            # Keep memory manageable
                            if len(memory_list) > 12:
                                memory_list = memory_list[-12:]
                            self.save_memory(memory_list)
                    else:
                        self.log(f"⚠️ Action {action} failed: {result}")
                        
                    # 0.75 second delay between batched actions
                    time.sleep(0.75)
                    
                except Exception as e:
                    self.log(f"❌ Action {action} error: {e}")
            else:
                self.log(f"❌ Unknown action: {action}")
        
        # Brief delay after sequence completion
        time.sleep(0.3)

    def play_game(self):
        """Main game loop with AI decision making"""
        self.log("🎮 Starting AI Pokemon adventure!")
        self.log("👀 Watch the browser window to see Grok-4 playing!")
        self.log("")
        self.log("🚨 CRITICAL: DO NOT TOUCH THE BROWSER WINDOW!")
        self.log("🚨 Any interaction will crash the automation!")
        self.log("🚨 Just watch and enjoy the AI gameplay!")
        self.log("")
        
        memory_list = self.load_memory()
        self.log(f"🧠 Loaded {len(memory_list)} memories")
        
        try:
            while True:
                self.frame_count += 15  # Faster cycles
                self.log(f"📸 Frame {self.frame_count}: Analyzing game state...")
                
                # Let AI decide when to take screenshots
                # Step 1: AI decides what tools to use (usually take_screenshot)
                self.log("🧠 AI deciding what to observe...")
                tool_decision = self.ask_ai_what_to_do(memory_list)
                
                # Step 2: Execute tools to gather information
                tool_results = self.execute_tools(tool_decision.get("tool_calls", []))
                
                # Step 3: Now make actual gameplay decisions with the new information
                if tool_results:
                    latest_screenshot_info = tool_results[-1] if tool_results else "No visual information"
                    self.log("🎯 AI making decisions based on visual information...")
                    ai_response = self.make_gameplay_decision(memory_list, latest_screenshot_info)
                else:
                    # Fallback if no tools were used
                    ai_response = {
                        "reasoning": "No visual information available, taking conservative action",
                        "actions": ["A"],
                        "memory_updates": {},
                        "image_description": "No screenshot taken"
                    }
                
                image_desc = ai_response.get("image_description", "No image description provided")
                reasoning = ai_response.get("reasoning", "No reasoning provided")
                actions = ai_response.get("actions", ["A"])
                memory_updates = ai_response.get("memory_updates", {})
                
                self.log(f"🔍 Image: {image_desc[:100]}...")
                self.log(f"💭 AI Reasoning: {reasoning}")
                self.log(f"🎯 AI Actions: {actions}")
                
                # Send AI thoughts to the browser overlay with better formatting
                # Extract just the screenshot number and core description
                screenshot_info = "No screenshot"
                if "Screenshot" in image_desc:
                    try:
                        # Extract screenshot number and brief description
                        parts = image_desc.split(": ", 1)
                        if len(parts) > 1:
                            screenshot_info = parts[0]  # e.g., "Screenshot 5"
                            # Get the first sentence of the description
                            desc_text = parts[1]
                            first_sentence = desc_text.split('.')[0][:100] + "..."
                            image_desc_short = f"{screenshot_info}: {first_sentence}"
                        else:
                            image_desc_short = image_desc[:80] + "..."
                    except:
                        image_desc_short = image_desc[:80] + "..."
                else:
                    image_desc_short = image_desc[:80] + "..."
                
                # Send thought to overlay with cleaned up content
                self.send_ai_thought(
                    image_desc_short,
                    reasoning[:150] + "..." if len(reasoning) > 150 else reasoning,
                    str(actions)
                )
                
                # Update memory
                if memory_updates:
                    memory_list = self.update_memory(memory_list, memory_updates)
                    self.save_memory(memory_list)
                
                # Execute action sequence
                self.execute_action_sequence(actions)
                
                # Wait before next cycle (much faster)
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            self.log("🛑 Stopping AI Pokemon player...")
        except Exception as e:
            self.log(f"❌ Game loop error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.log("🔒 Browser closed")

    def run(self):
        """Main entry point"""
        try:
            self.log("")
            self.log("⚠️  IMPORTANT: DO NOT MOVE THE BROWSER WINDOW!")
            self.log("⚠️  Moving the window will crash ChromeDriver!")
            self.log("⚠️  Let the AI play - watch but don't interact!")
            self.log("")
            
            self.setup_browser()
            self.load_emulator()
            
            if self.upload_rom():
                self.log("")
                self.log("🚀 Everything ready! Starting Pokemon adventure!")
                time.sleep(1.5)
                self.play_game()
            else:
                self.log("❌ Failed to load ROM, exiting...")
                
        except Exception as e:
            self.log(f"💥 Critical error: {e}")
        finally:
            if self.driver:
                self.driver.quit()

    def take_comparison_screenshots(self):
        """Take both full browser and game-only screenshots for comparison"""
        try:
            self.log("📸 Taking comparison screenshots...")
            
            # Take game-only screenshot
            game_screenshot_num = self.take_screenshot_tool(game_only=True)
            
            # Take full browser screenshot
            browser_screenshot_num = self.take_screenshot_tool(game_only=False)
            
            if game_screenshot_num and browser_screenshot_num:
                self.log(f"✅ Comparison screenshots saved:")
                self.log(f"   🎮 Game only: screenshot_{game_screenshot_num}.png")
                self.log(f"   🌐 Full browser: screenshot_{browser_screenshot_num}.png")
                return game_screenshot_num, browser_screenshot_num
            else:
                self.log("❌ Failed to take comparison screenshots")
                return None, None
                
        except Exception as e:
            self.log(f"❌ Comparison screenshots failed: {e}")
            return None, None

    def start_emulator_properly(self):
        """Properly start the emulator after ROM is loaded"""
        try:
            self.log("🎮 Ensuring emulator starts properly...")
            
            # Step 1: Wait for emulator elements to be ready
            for attempt in range(10):
                try:
                    check_js = """
                    const gameDiv = document.getElementById('game');
                    const canvas = gameDiv ? gameDiv.querySelector('canvas') : null;
                    
                    if (!gameDiv) return 'NO_GAME_DIV';
                    if (!canvas) return 'NO_CANVAS';
                    if (canvas.width === 0 || canvas.height === 0) return 'CANVAS_NOT_READY';
                    
                    return 'ELEMENTS_READY';
                    """
                    
                    status = self.driver.execute_script(check_js)
                    self.log(f"🔍 Emulator elements check: {status}")
                    
                    if status == 'ELEMENTS_READY':
                        break
                    else:
                        time.sleep(1)
                        
                except Exception as e:
                    self.log(f"⚠️ Element check error: {e}")
                    time.sleep(1)
            
            # Step 2: Simulate user interaction to start the emulator
            self.log("🖱️ Simulating user interaction to start emulator...")
            
            # Wait 2 seconds for game to load before attempting start
            self.log("⏳ Waiting 2 seconds for game to load...")
            time.sleep(2)
            
            # Single center click to start the game (no button hunting)
            start_js = """
            try {
                const gameDiv = document.getElementById('game');
                const canvas = gameDiv.querySelector('canvas');
                
                if (canvas) {
                    console.log('🎮 Game loaded - performing single center click to start');
                    
                    // Focus the canvas first
                    canvas.focus();
                    
                    // Single click at center of emulator screen
                    const rect = canvas.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    
                    const clickEvent = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        clientX: centerX,
                        clientY: centerY
                    });
                    
                    canvas.dispatchEvent(clickEvent);
                    console.log('🎮 Single center click completed');
                    
                    return 'CENTER_CLICKED';
                } else {
                    return 'NO_CANVAS_FOUND';
                }
                
            } catch (error) {
                return 'ERROR: ' + error.message;
            }
            """
            
            interaction_result = self.driver.execute_script(start_js)
            self.log(f"🖱️ Start interaction: {interaction_result}")
            
            # Brief wait for start to register
            self.log("⏳ Waiting for game to start...")
            
            for i in range(20):  # Wait up to 40 seconds
                try:
                    game_status_js = """
                    // Check if game is actually running
                    const canvas = document.querySelector('#game canvas');
                    if (!canvas) return 'NO_CANVAS';
                    
                    // Check if EmulatorJS has started
                    if (window.EJS && window.EJS.started === true) {
                        return 'EMULATOR_RUNNING';
                    }
                    
                    // Check if gameLoaded callback was triggered
                    if (window.gameLoaded === true) {
                        return 'GAME_LOADED';
                    }
                    
                    // Check canvas size as fallback
                    if (canvas.width > 200 && canvas.height > 100) {
                        return 'CANVAS_ACTIVE';
                    }
                    
                    return 'STILL_LOADING';
                    """
                    
                    game_status = self.driver.execute_script(game_status_js)
                    self.log(f"🎮 Game status ({i+1}/20): {game_status}")
                    
                    if game_status in ['EMULATOR_RUNNING', 'GAME_LOADED']:
                        self.log("🎉 Emulator started successfully!")
                        return True
                    elif game_status == 'CANVAS_ACTIVE':
                        self.log("🎮 Canvas is active, emulator likely running")
                        return True
                    
                    time.sleep(2)
                    
                except Exception as e:
                    self.log(f"⚠️ Game status check error: {e}")
                    time.sleep(2)
            
            self.log("⚠️ Emulator start timeout - may need manual intervention")
            return False
            
        except Exception as e:
            self.log(f"❌ Emulator start failed: {e}")
            return False

    def activate_emulator(self):
        """Activate the emulator by focusing window and simulating user interaction"""
        try:
            self.log("🎮 Activating emulator...")
            
            # Method 1: Focus the browser window using Selenium
            try:
                self.driver.switch_to.window(self.driver.current_window_handle)
                self.log("✅ Switched to browser window")
            except Exception as e:
                self.log(f"⚠️ Window switch failed: {e}")
            
            # Method 2: Bring window to front using native methods
            try:
                # For macOS, try to bring Chrome to front
                import platform
                if platform.system() == "Darwin":  # macOS
                    import subprocess
                    subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to activate'], 
                                 capture_output=True, timeout=5)
                    self.log("✅ Attempted to bring Chrome to front on macOS")
            except Exception as e:
                self.log(f"⚠️ Native window activation failed: {e}")
            
            # Method 3: Multiple attempts to activate with better timing
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    self.log(f"🔄 Activation attempt {attempt + 1}/{max_attempts}")
                    
                    # Wait longer between attempts
                    time.sleep(2)
                    
                    # JavaScript to simulate user interaction with the game area
                    activation_js = """
                    try {
                        // First, try to focus the window
                        window.focus();
                        
                        // Wait for any pending operations
                        setTimeout(() => {
                            // Find the game div and canvas
                            const gameDiv = document.getElementById('game');
                            if (gameDiv) {
                                // Scroll the game div into view
                                gameDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                
                                // Try to click on the game area
                                const canvas = gameDiv.querySelector('canvas');
                                if (canvas) {
                                    // Create and dispatch click events
                                    const rect = canvas.getBoundingClientRect();
                                    const centerX = rect.left + rect.width / 2;
                                    const centerY = rect.top + rect.height / 2;
                                    
                                    // Multiple click events to ensure activation
                                    const events = ['mousedown', 'mouseup', 'click'];
                                    events.forEach((eventType, index) => {
                                        setTimeout(() => {
                                            const event = new MouseEvent(eventType, {
                                                view: window,
                                                bubbles: true,
                                                cancelable: true,
                                                clientX: centerX,
                                                clientY: centerY
                                            });
                                            canvas.dispatchEvent(event);
                                        }, index * 100);
                                    });
                                    
                                    // Also try focus events
                                    canvas.focus();
                                    gameDiv.focus();
                                    
                                    // Try to trigger any play buttons or start events
                                    if (window.EJS && window.EJS.start) {
                                        try {
                                            window.EJS.start();
                                        } catch (e) {
                                            console.log('EJS start failed:', e);
                                        }
                                    }
                                    
                                    console.log('Simulated interaction on game canvas at', centerX, centerY);
                                    return 'CANVAS_ACTIVATED';
                                } else {
                                    // No canvas yet, click on game div
                                    gameDiv.click();
                                    gameDiv.focus();
                                    
                                    // Try to trigger ROM loading if not started
                                    const uploadInput = document.querySelector('input[type="file"]');
                                    if (uploadInput && uploadInput.style.display !== 'none') {
                                        console.log('ROM upload area still visible - game may not have started');
                                    }
                                    
                                    console.log('Clicked on game div');
                                    return 'GAME_DIV_ACTIVATED';
                                }
                            } else {
                                console.log('No game div found');
                                return 'NO_GAME_DIV';
                            }
                        }, 100);
                        
                        return 'ACTIVATION_INITIATED';
                        
                    } catch (error) {
                        console.error('Activation error:', error);
                        return 'ERROR: ' + error.message;
                    }
                    """
                    
                    result = self.driver.execute_script(activation_js)
                    self.log(f"🖱️ Game interaction result: {result}")
                    
                    # Wait longer after interaction
                    time.sleep(3)
                    
                    # Check if emulator is now active
                    status_check_js = """
                    try {
                        const canvas = document.querySelector('#game canvas');
                        if (canvas && canvas.width > 0 && canvas.height > 0) {
                            // Check if the emulator is actually running
                            if (window.EJS) {
                                return `EMULATOR_READY: ${canvas.width}x${canvas.height}`;
                            } else {
                                return `CANVAS_READY_NO_EJS: ${canvas.width}x${canvas.height}`;
                            }
                        }
                        
                        // Check if game div exists
                        const gameDiv = document.getElementById('game');
                        if (gameDiv) {
                            return 'GAME_DIV_EXISTS_NO_CANVAS';
                        }
                        
                        return 'NO_EMULATOR_ELEMENTS';
                    } catch (error) {
                        return 'CHECK_ERROR: ' + error.message;
                    }
                    """
                    
                    status_result = self.driver.execute_script(status_check_js)
                    self.log(f"🔍 Emulator status: {status_result}")
                    
                    if 'EMULATOR_READY' in status_result or 'CANVAS_READY' in status_result:
                        self.log("🎉 Emulator activation successful!")
                        return True
                    elif attempt == max_attempts - 1:
                        self.log("⚠️ Emulator activation attempts completed - may need manual interaction")
                        return False
                    else:
                        self.log(f"⚠️ Attempt {attempt + 1} incomplete, retrying...")
                        
                except Exception as e:
                    self.log(f"❌ Activation attempt {attempt + 1} failed: {e}")
                    if attempt == max_attempts - 1:
                        return False
            
        except Exception as e:
            self.log(f"❌ Emulator activation failed: {e}")
            import traceback
            self.log(f"❌ Full error: {traceback.format_exc()}")
            return False

    def wait_for_manual_start(self):
        """Wait for user to manually start the emulator if auto-start fails"""
        try:
            self.log("👤 Manual intervention needed!")
            self.log("🎮 Please look at the browser window")
            self.log("🖱️ If you see a white screen or 'Play' button, click it to start")
            self.log("⏳ Waiting up to 60 seconds for game to start...")
            
            for i in range(30):  # 60 seconds total
                try:
                    # Check if game has started
                    manual_check_js = """
                    const canvas = document.querySelector('#game canvas');
                    if (!canvas) return 'NO_CANVAS';
                    
                    // Check for actual game running indicators
                    if (window.gameLoaded === true) return 'GAME_LOADED';
                    if (window.EJS && window.EJS.started === true) return 'EMULATOR_STARTED';
                    if (canvas.width > 200 && canvas.height > 100) return 'CANVAS_READY';
                    
                    return 'STILL_WAITING';
                    """
                    
                    status = self.driver.execute_script(manual_check_js)
                    self.log(f"🔍 Manual start check ({i+1}/30): {status}")
                    
                    if status in ['GAME_LOADED', 'EMULATOR_STARTED', 'CANVAS_READY']:
                        self.log("🎉 Game started successfully (manual)!")
                        return True
                    
                    time.sleep(2)
                    
                except Exception as e:
                    self.log(f"⚠️ Manual check error: {e}")
                    time.sleep(2)
            
            self.log("❌ Manual start timeout - game did not start")
            return False
            
        except Exception as e:
            self.log(f"❌ Manual start check failed: {e}")
            return False

    def robust_api_call(self, messages, max_tokens=32000, temperature=0.7, function_name="API"):
        """Robust API call with smart timeout handling and minimal retries"""
        
        # Smart timeout strategy: Start high, only retry on real failures
        if function_name == "Gameplay Decision":
            # For complex decisions: Start with very generous timeout
            initial_timeout = 180  # 3 minutes - let it think!
            max_retries = 2  # Only retry once on real failures
        else:
            # For other APIs: Still generous but faster
            initial_timeout = 120  # 2 minutes  
            max_retries = 2
        
        for attempt in range(max_retries):
            try:
                # Use the initial generous timeout for all attempts
                # Only retry on connection failures, not timeouts
                timeout = initial_timeout
                self.log(f"📡 {function_name} API call (attempt {attempt + 1}/{max_retries}, timeout: {timeout}s)")
                if function_name == "Gameplay Decision":
                    self.log(f"🧠 Waiting for strategic AI analysis... this can take 1-3 minutes for complex decisions")
                else:
                    self.log(f"⏳ Processing {function_name}... being patient with AI")
                
                # Make the API call with generous timeout
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-4",
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    self.log(f"✅ {function_name} API success")
                    return content
                elif response.status_code == 429:
                    wait_time = 5 + (attempt * 5)
                    self.log(f"⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.log(f"❌ {function_name} API error: {response.status_code}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(3)
                    continue
                    
            except requests.exceptions.Timeout:
                self.log(f"⏰ {function_name} timeout after {timeout}s - this might be normal for complex reasoning")
                if function_name == "Gameplay Decision" and attempt == 0:
                    # For gameplay decisions, one timeout might be normal - try once more with even longer timeout
                    self.log(f"🤔 Complex AI reasoning can take time, trying once more with extra patience...")
                elif attempt == max_retries - 1:
                    self.log(f"❌ {function_name} failed after {timeout}s - API might be overloaded")
                    return None
                else:
                    self.log(f"🔄 Retrying {function_name} - might be network issue...")
                time.sleep(10)  # Longer wait before retry
                
            except requests.exceptions.RequestException as e:
                self.log(f"🌐 {function_name} connection error: {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(5)
                
        return None

    def parse_json_with_fallback(self, content, function_name="API", fallback_action="A"):
        """Parse JSON with robust fallback handling"""
        if not content:
            self.log(f"⚠️ {function_name}: Empty response")
            return {
                "reasoning": f"{function_name} returned empty response",
                "actions": [fallback_action],
                "memory_updates": {}
            }
        
        # DEBUG: Log the raw response to see what we're getting
        self.log(f"🔍 DEBUG {function_name} raw response: {content[:200]}...")
        
        # Try direct JSON parse
        try:
            parsed = json.loads(content)
            self.log(f"✅ {function_name}: Direct JSON parse successful")
            return parsed
        except json.JSONDecodeError as e:
            self.log(f"❌ {function_name}: Direct JSON parse failed: {e}")
        
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                self.log(f"✅ {function_name}: Markdown JSON parse successful")
                return parsed
            except json.JSONDecodeError as e:
                self.log(f"❌ {function_name}: Markdown JSON parse failed: {e}")
        
        # Try to find JSON-like structure in the text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                self.log(f"✅ {function_name}: Regex JSON parse successful")
                return parsed
            except json.JSONDecodeError as e:
                self.log(f"❌ {function_name}: Regex JSON parse failed: {e}")
        
        # Final fallback - extract reasoning from text
        self.log(f"⚠️ {function_name}: All JSON parsing failed, using text fallback")
        self.log(f"🔍 DEBUG Full response: {content}")
        
        reasoning = content[:200] + "..." if len(content) > 200 else content
        
        # Look for action words in the response
        action = fallback_action
        action_words = ["START", "UP", "DOWN", "LEFT", "RIGHT", "A", "B", "SELECT"]
        for word in action_words:
            if word.lower() in content.lower():
                action = word
                self.log(f"🎯 Found action word '{word}' in response")
                break
        
        return {
            "reasoning": f"Parsed from text: {reasoning}",
            "actions": [action],
            "memory_updates": {"add": [f"AI response: {reasoning}"]}
        }

if __name__ == "__main__":
    player = PokemonAIPlayer()
    player.run() 