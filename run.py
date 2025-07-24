#!/usr/bin/env python3
"""
🎮 GROK PLAYS POKEMON - PRODUCTION VERSION
=========================================
Watch Grok-4 Vision AI autonomously play Pokemon Fire Red
and attempt to beat the game and catch Mewtwo!

Author: AI-Powered Pokemon Player
Version: 1.0 Production
"""

import time
import sys
import os
from pokemon_player_browser import PokemonAIPlayer

def print_banner():
    """Display the production banner"""
    print("=" * 60)
    print("🎮 GROK PLAYS POKEMON - COMPLETE ADVENTURE")
    print("=" * 60)
    print("🤖 Grok-4 Vision AI will autonomously play Pokemon Fire Red")
    print("🏆 Goal: Beat the game and catch Mewtwo!")
    print("👀 Watch the AI make strategic decisions in real-time")
    print("🧠 AI thoughts appear in the browser overlay")
    print("=" * 60)
    print()

def check_prerequisites():
    """Check all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check ROM file
    if not os.path.exists("roms/pokemonfr.gba"):
        print("❌ Pokemon Fire Red ROM not found!")
        print("📁 Please place Pokemon Fire Red ROM as 'roms/pokemonfr.gba'")
        print("🔧 Run ./setup.sh to download automatically")
        return False
    
    # Check API key
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("🔑 Please create .env with your XAI_API_KEY")
        return False
    
    print("✅ All prerequisites met!")
    return True

def production_run():
    """Run the production Pokemon AI player"""
    try:
        print_banner()
        
        if not check_prerequisites():
            return False
        
        print("🚀 Initializing Grok Pokemon AI Player...")
        player = PokemonAIPlayer()
        
        print("\n🔧 Setting up browser environment...")
        player.setup_browser()
        print("✅ Browser ready!")
        
        print("\n📂 Loading Pokemon Fire Red emulator...")
        player.load_emulator()
        print("✅ Emulator loaded!")
        
        print("\n🎮 Loading Pokemon Fire Red ROM...")
        rom_success = player.upload_rom("roms/pokemonfr.gba")
        
        if not rom_success:
            print("❌ ROM loading failed!")
            print("🔧 Please manually click the emulator if you see a play button")
            print("⏳ Waiting for manual intervention...")
        
        print("\n🏆 POKEMON ADVENTURE BEGINS!")
        print("👀 Watch Grok-4 Vision AI play Pokemon Fire Red")
        print("🧠 AI strategy and thoughts will appear in browser")
        print("⚨ AI can batch actions like ['UP','UP','UP'] for efficiency")
        print("📝 AI uses memory.txt as persistent scratchpad for planning")
        print("📸 AI can recall past screenshots and use direct vision analysis")
        print("⌨️ AI has full control - DO NOT touch the browser!")
        print("🎯 Goal: Complete the game and catch Mewtwo!")
        print()
        print("🛑 Press Ctrl+C to stop the AI at any time")
        print("=" * 60)
        print()
        
        # Start the AI gameplay loop
        player.play_game()
        
    except KeyboardInterrupt:
        print("\n🛑 Pokemon adventure stopped by user")
        print("🎮 Thanks for watching Grok play Pokemon!")
        return True
        
    except Exception as e:
        print(f"\n💥 Error during Pokemon adventure: {e}")
        print("🔧 Try restarting or check the logs above")
        return False
        
    finally:
        if 'player' in locals() and player.driver:
            input("\n⏸️ Press Enter to close browser and exit...")
            player.driver.quit()
            print("🔒 Browser closed - Adventure complete!")

def main():
    """Main entry point"""
    print("🎮 Welcome to GROK PLAYS POKEMON!")
    print("🏆 Ready to watch AI complete Pokemon Fire Red?")
    
    while True:
        choice = input("\n[S]tart Adventure, [Q]uit: ").upper().strip()
        
        if choice == 'S':
            success = production_run()
            if success:
                print("\n🎉 Pokemon adventure session completed!")
            else:
                print("\n⚠️ Adventure encountered issues")
            break
        elif choice == 'Q':
            print("👋 Maybe next time! Goodbye!")
            break
        else:
            print("❓ Please enter 'S' to start or 'Q' to quit")

if __name__ == "__main__":
    main() 