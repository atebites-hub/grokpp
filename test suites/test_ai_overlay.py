#!/usr/bin/env python3
"""
Quick test to verify AI overlay is working
"""

import time
from pokemon_player_browser import PokemonAIPlayer

def test_ai_overlay():
    """Test that AI thoughts are properly displayed"""
    print("🧪 Testing AI Overlay Functionality")
    print("=" * 40)
    
    player = PokemonAIPlayer()
    
    try:
        print("🔧 Setting up browser...")
        player.setup_browser()
        
        print("📂 Loading emulator...")
        player.load_emulator()
        
        print("🧠 Testing AI thoughts...")
        
        # Send test thoughts
        test_thoughts = [
            ("Pokemon Fire Red title screen detected", "I should press START to begin the game", "START"),
            ("Character selection screen", "I need to choose my starter Pokemon", "A"),
            ("Battle detected", "Time to use type advantages in this battle", "A"),
            ("Wild Pokemon appeared", "This could be a good catch", "A"),
            ("Level up screen", "My Pokemon is getting stronger", "A")
        ]
        
        for i, (vision, reasoning, action) in enumerate(test_thoughts):
            print(f"📤 Sending test thought {i+1}/5...")
            player.send_ai_thought(vision, reasoning, action)
            time.sleep(2)  # Wait to see each thought appear
        
        print("\n✅ AI overlay test completed!")
        print("👀 Check the browser - you should see AI thoughts in the right panel")
        input("Press Enter to close...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        if player.driver:
            player.driver.quit()

if __name__ == "__main__":
    test_ai_overlay() 