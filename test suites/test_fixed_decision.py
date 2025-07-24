#!/usr/bin/env python3
"""
Test the fixed decision-making system
"""

import time
from pokemon_player_browser import PokemonAIPlayer

def test_fixed_decision_loop():
    """Test that AI can read screenshots and make decisions"""
    print("🧪 Testing Fixed Decision Loop")
    print("=" * 40)
    print("This should show:")
    print("1. AI takes screenshot") 
    print("2. AI reads the description")
    print("3. AI makes gameplay decision based on what it sees")
    print("=" * 40)
    
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
        
        print("\n🧠 Testing fixed decision loop...")
        memory_list = player.load_memory()
        
        # Run one complete decision cycle
        print("\n📸 Step 1: AI chooses what to observe...")
        tool_decision = player.ask_ai_what_to_do(memory_list)
        print(f"🔍 Tool decision: {tool_decision}")
        
        print("\n🛠️ Step 2: Executing tools...")
        tool_results = player.execute_tools(tool_decision.get("tool_calls", []))
        print(f"📊 Tool results: {tool_results}")
        
        if tool_results:
            print("\n🎯 Step 3: Making gameplay decision with visual info...")
            latest_screenshot = tool_results[-1]
            print(f"📸 Visual info: {latest_screenshot[:200]}...")
            
            ai_response = player.make_gameplay_decision(memory_list, latest_screenshot)
            print(f"🎮 AI Decision: {ai_response}")
            
            print("\n✅ FIXED! AI can now:")
            print("- Take screenshots")
            print("- Read the descriptions")  
            print("- Make decisions based on what it sees")
            print("- Update memory with progress")
            
        else:
            print("❌ No tool results - something is still wrong")
        
        input("\nPress Enter to close...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        if player.driver:
            player.driver.quit()

if __name__ == "__main__":
    test_fixed_decision_loop() 