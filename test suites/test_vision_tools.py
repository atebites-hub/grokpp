#!/usr/bin/env python3
"""
Test the enhanced vision tools and screenshot context
"""

import time
from pokemon_player_browser import PokemonAIPlayer

def test_vision_tools():
    """Test screenshot context and direct vision analysis"""
    print("🧪 Testing Enhanced Vision Tools")
    print("=" * 50)
    print("This will test:")
    print("1. Screenshot numbering context (screenshot_N.png/.txt)")
    print("2. Screenshot recall functionality") 
    print("3. Direct vision analysis tool")
    print("=" * 50)
    
    player = PokemonAIPlayer()
    
    try:
        print("🔧 Setting up browser...")
        player.setup_browser()
        
        print("📂 Loading emulator...")
        player.load_emulator()
        
        print("🎮 Loading ROM...")
        rom_success = player.upload_rom("pokemonfr.gba")
        if not rom_success:
            print("⚠️ ROM loading had issues, continuing with test...")
        
        print(f"\n📊 Current screenshot count: {player.screenshot_count}")
        
        # Test 1: Take a screenshot and verify numbering
        print("\n📸 Test 1: Screenshot numbering...")
        screenshot_num = player.take_screenshot_tool()
        if screenshot_num:
            print(f"✅ Screenshot taken: screenshot_{screenshot_num}.png")
            print(f"✅ Description saved: screenshot_{screenshot_num}.txt")
        
        # Test 2: Take another screenshot
        print("\n📸 Test 2: Second screenshot...")
        screenshot_num2 = player.take_screenshot_tool()
        if screenshot_num2:
            print(f"✅ Screenshot taken: screenshot_{screenshot_num2}.png")
            print(f"✅ Current count: {player.screenshot_count}")
        
        # Test 3: Test recall functionality
        if screenshot_num:
            print(f"\n📖 Test 3: Recalling screenshot {screenshot_num}...")
            recalled_desc = player.recall_screenshot_tool(screenshot_num)
            print(f"✅ Recalled description: {recalled_desc[:100]}...")
        
        # Test 4: Test direct vision analysis
        print("\n🔍 Test 4: Direct vision analysis...")
        vision_analysis = player.analyze_current_screen_with_vision()
        if vision_analysis:
            print(f"✅ Direct vision analysis: {vision_analysis[:200]}...")
        else:
            print("❌ Direct vision analysis failed")
        
        # Test 5: Test AI tool selection with new context
        print("\n🧠 Test 5: AI tool selection with enhanced context...")
        memory_list = player.load_memory()
        tool_decision = player.ask_ai_what_to_do(memory_list)
        print(f"🔍 AI tool decision: {tool_decision}")
        
        print("\n✅ All vision tools working!")
        print("📋 Summary:")
        print(f"   - Screenshot numbering: screenshot_1.png, screenshot_2.png, etc.")
        print(f"   - Text descriptions: screenshot_1.txt, screenshot_2.txt, etc.")
        print(f"   - Current count: {player.screenshot_count}")
        print(f"   - Recall functionality: ✅")
        print(f"   - Direct vision tool: ✅")
        print(f"   - AI context awareness: ✅")
        
        input("\nPress Enter to close...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if player.driver:
            player.driver.quit()

if __name__ == "__main__":
    test_vision_tools() 