#!/usr/bin/env python3
"""
Test script to demonstrate batching and memory features
"""

import time
from pokemon_player_browser import PokemonAIPlayer

def test_batching_and_memory():
    """Test batching actions and memory system"""
    print("🧪 Testing Batching & Memory System")
    print("=" * 40)
    
    player = PokemonAIPlayer()
    
    try:
        print("🔧 Setting up browser...")
        player.setup_browser()
        
        print("📂 Loading emulator...")
        player.load_emulator()
        
        print("🧠 Testing memory system...")
        memory = player.load_memory()
        print("📋 Current memory:")
        for i, mem in enumerate(memory, 1):
            print(f"   {i}. {mem}")
        
        print("\n⚡ Testing batched actions...")
        
        # Test different batching scenarios
        batch_tests = [
            (["UP", "UP", "UP"], "Moving up 3 spaces quickly"),
            (["A", "A", "A"], "Advancing through multiple text boxes"),
            (["LEFT", "LEFT", "DOWN", "DOWN"], "Moving left 2, down 2"),
            (["RIGHT", "A"], "Move right then interact"),
            (["B", "B"], "Cancel twice to go back")
        ]
        
        for actions, description in batch_tests:
            print(f"\n🎮 {description}")
            print(f"⌨️ Actions: {actions}")
            
            # Send AI thought about what we're testing
            player.send_ai_thought(
                f"Testing batched movement: {description}",
                f"Executing sequence: {actions}",
                str(actions)
            )
            
            # Execute the batched actions
            player.execute_action_sequence(actions)
            print(f"✅ Completed batch with 0.75s delays")
            time.sleep(2)  # Pause between tests
        
        print("\n📝 Testing memory update...")
        
        # Test memory updates
        test_memory_updates = {
            "add": ["Tested batching system - works great!", "Can move efficiently with batched commands"],
            "update": {}
        }
        
        updated_memory = player.update_memory(memory, test_memory_updates)
        player.save_memory(updated_memory)
        
        print("📋 Updated memory:")
        for i, mem in enumerate(updated_memory, 1):
            print(f"   {i}. {mem}")
        
        print("\n✅ Batching and memory test completed!")
        print("👀 Check the browser for AI thoughts and action execution")
        input("Press Enter to close...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        if player.driver:
            player.driver.quit()

if __name__ == "__main__":
    test_batching_and_memory() 