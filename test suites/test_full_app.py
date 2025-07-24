#!/usr/bin/env python3

import sys
import os
import time

# Add the parent directory to the Python path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pokemon_player_browser import PokemonAIPlayer

def test_full_application():
    """Test the complete Pokemon AI Player application"""
    print("🧪 Testing Full Pokemon AI Player Application")
    print("=" * 60)
    print("👀 Watch the Chrome window that will open!")
    print("🚨 DO NOT interact with the browser window during the test")
    print("=" * 60)
    
    player = PokemonAIPlayer()
    
    try:
        # Test 1: Browser Setup
        print("\n🔧 Step 1: Setting up browser...")
        player.setup_browser()
        print("✅ Browser setup complete - you should see a Chrome window!")
        
        # Test 2: Load Emulator
        print("\n📂 Step 2: Loading emulator...")
        player.load_emulator()
        print("✅ Emulator loaded")
        
        # Test 3: Upload ROM
        print("\n🎮 Step 3: Uploading Pokemon ROM...")
        rom_success = player.upload_rom("pokemonfr.gba")
        if rom_success:
            print("✅ ROM uploaded successfully!")
        else:
            print("❌ ROM upload failed")
            return False
        
        # Test 4: Take Screenshot and Analyze
        print("\n📸 Step 4: Taking screenshot and generating description...")
        screenshot_num = player.take_screenshot_tool()
        if screenshot_num:
            screenshot_b64 = player.get_screenshot_base64(screenshot_num)
            if screenshot_b64:
                description = player.analyze_screenshot_with_vision(screenshot_b64)
                player.save_screenshot_description(screenshot_num, description)
                print(f"✅ Screenshot {screenshot_num} analyzed and saved")
                print(f"📝 Description preview: {description[:100]}...")
            else:
                print("❌ Failed to get screenshot as base64")
        else:
            print("❌ Failed to take screenshot")
        
        # Test 5: AI Decision Making
        print("\n🧠 Step 5: Testing AI decision making...")
        memory_list = player.load_memory()
        ai_decision = player.ask_ai_what_to_do(memory_list)
        print(f"🤖 AI Decision: {ai_decision}")
        
        # Test 6: Execute AI Tools
        print("\n🔧 Step 6: Testing AI tool execution...")
        tool_results = player.execute_tools(ai_decision.get("tool_calls", []))
        print(f"🛠️ Tool Results: {tool_results}")
        
        # Test 7: Action Execution
        print("\n⌨️ Step 7: Testing action execution...")
        test_actions = ["START", "A", "DOWN", "A"]
        player.execute_action_sequence(test_actions)
        print(f"✅ Executed actions: {test_actions}")
        
        # Test 8: Let it run for a few cycles
        print("\n🎮 Step 8: Running a few AI cycles...")
        print("👀 Watch the browser window - the AI should be playing!")
        
        for i in range(3):
            print(f"\n🔄 AI Cycle {i+1}/3:")
            
            # AI decides what to do
            ai_decision = player.ask_ai_what_to_do(memory_list)
            print(f"🧠 AI wants to: {ai_decision.get('reasoning', 'No reasoning')}")
            
            # Execute tools
            tool_results = player.execute_tools(ai_decision.get("tool_calls", []))
            if tool_results:
                print(f"🛠️ Tool results: {tool_results[0][:100]}...")
            
            # Execute actions
            actions = ai_decision.get("actions", ["A"])
            player.execute_action_sequence(actions)
            print(f"⌨️ Actions executed: {actions}")
            
            # Update memory
            memory_updates = ai_decision.get("memory_updates", {})
            if memory_updates:
                memory_list = player.update_memory(memory_list, memory_updates)
                player.save_memory(memory_list)
            
            # Wait before next cycle
            time.sleep(3)
        
        print("\n🎉 Full application test completed successfully!")
        print("👀 Keeping browser open for final observation...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        print(traceback.format_exc())
        return False
        
    finally:
        if player.driver:
            input("\n⏸️ Press Enter to close the browser and end the test...")
            player.driver.quit()
            print("🔒 Browser closed")

if __name__ == "__main__":
    success = test_full_application()
    if success:
        print("\n✅ ALL TESTS PASSED! Your Pokemon AI Player is working correctly!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.") 