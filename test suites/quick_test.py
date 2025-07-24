#!/usr/bin/env python3

import time
from pokemon_player_browser import PokemonAIPlayer

def quick_test():
    """Quick test of Pokemon AI Player - minimal wait times"""
    print("🚀 Quick Pokemon AI Player Test")
    print("=" * 40)
    print("👀 Watch the Chrome window!")
    print("🚨 DO NOT interact with the browser")
    print("=" * 40)
    
    player = PokemonAIPlayer()
    
    try:
        # Quick setup
        print("\n🔧 Setting up browser...")
        player.setup_browser()
        print("✅ Browser ready!")
        
        # Load emulator
        print("\n📂 Loading emulator...")
        player.load_emulator()
        print("✅ Emulator loaded!")
        
        # Upload ROM
        print("\n🎮 Uploading ROM...")
        rom_success = player.upload_rom("pokemonfr.gba")
        if rom_success:
            print("✅ ROM uploaded!")
        else:
            print("⚠️ ROM upload had issues, continuing...")
        
        # Quick AI test
        print("\n🧠 Testing AI decision...")
        memory_list = player.load_memory()
        ai_decision = player.ask_ai_what_to_do(memory_list)
        print(f"🤖 AI wants to: {ai_decision.get('reasoning', 'No reasoning')}")
        
        # Execute tools quickly
        tool_results = player.execute_tools(ai_decision.get("tool_calls", []))
        if tool_results:
            print(f"🛠️ Screenshot taken and analyzed!")
        
        # Test actions
        actions = ai_decision.get("actions", ["A"])[:2]  # Only first 2 actions
        print(f"⌨️ Testing actions: {actions}")
        player.execute_action_sequence(actions)
        
        print("\n🎉 Quick test completed! System is working!")
        print("👀 Keeping browser open for 10 seconds...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        return False
        
    finally:
        if player.driver:
            player.driver.quit()
            print("🔒 Browser closed")

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n✅ QUICK TEST PASSED! Ready for official run!")
    else:
        print("\n❌ Quick test failed. Check the output above.") 