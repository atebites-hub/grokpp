#!/bin/bash

echo "🎮 GROK PLAYS POKEMON - PRODUCTION SETUP"
echo "========================================"
echo "🤖 Setting up everything you need to watch AI play Pokemon!"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    echo "🔗 Download from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p roms
mkdir -p screenshots
echo "✅ Directories created: roms/, screenshots/"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️ Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "✅ All dependencies installed!"

# Create .env file with placeholder
echo "🔑 Creating .env file with API key placeholder..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# xAI API Key for Grok-4 Vision
# Get your API key from: https://console.x.ai/
XAI_API_KEY=your_xai_api_key_here
EOF
    echo "✅ .env file created with placeholder"
else
    echo "⚠️ .env file already exists, skipping..."
fi

# Create memory.txt file
echo "🧠 Creating AI memory scratchpad..."
if [ ! -f "memory.txt" ]; then
    cat > memory.txt << 'EOF'
GOAL: Complete Pokemon Fire Red - beat Elite 4, become Champion, catch Mewtwo
CURRENT PROGRESS: Fresh start - need to get through intro and choose starter
STRATEGY: Build balanced team, learn type advantages, train consistently
EFFICIENCY: Use batched moves like ['UP','UP','UP'] and ['A','A','A'] for speed
MEMORY: Track important NPCs, locations, and story progress in this scratchpad
EOF
    echo "✅ memory.txt created with initial goals"
else
    echo "⚠️ memory.txt already exists, skipping..."
fi

# Download Pokemon Fire Red ROM
echo "🎮 Setting up Pokemon Fire Red ROM..."
ROM_PATH="roms/pokemonfr.gba"

if [ -f "$ROM_PATH" ]; then
    echo "✅ Pokemon Fire Red ROM already exists"
else
    echo "📥 Downloading Pokemon Fire Red ROM..."
    echo "🔗 Note: Using a publicly available ROM for educational purposes"
    
    # Try multiple ROM sources
    ROM_DOWNLOADED=false
    
    # Source 1: Archive.org (legal ROM dumps)
    echo "🌐 Attempting download from archive.org..."
    if command -v curl &> /dev/null; then
        curl -L -o "$ROM_PATH" "https://archive.org/download/PokemonFireRedVersion/Pokemon%20-%20Fire%20Red%20Version%20%28U%29%20%28V1.1%29.gba" 2>/dev/null
        if [ -f "$ROM_PATH" ] && [ -s "$ROM_PATH" ]; then
            # Verify it's actually a GBA file (should start with certain bytes)
            if file "$ROM_PATH" | grep -q "Game Boy Advance"; then
                ROM_DOWNLOADED=true
                echo "✅ Pokemon Fire Red ROM downloaded successfully!"
            else
                echo "⚠️ Downloaded file doesn't appear to be a valid GBA ROM"
                rm -f "$ROM_PATH"
            fi
        fi
    fi
    
    # If download failed, provide instructions
    if [ "$ROM_DOWNLOADED" = false ]; then
        echo "❌ Automatic ROM download failed"
        echo ""
        echo "📋 MANUAL ROM SETUP REQUIRED:"
        echo "🔗 Please download Pokemon Fire Red ROM manually:"
        echo "   1. Visit: https://archive.org/details/PokemonFireRedVersion"
        echo "   2. Download: 'Pokemon - Fire Red Version (U) (V1.1).gba'"
        echo "   3. Save it as: $ROM_PATH"
        echo "   4. Or place any Pokemon Fire Red ROM in roms/ and rename to pokemonfr.gba"
        echo ""
        echo "⚖️  Legal note: Only use ROM dumps of games you legally own"
        echo ""
        
        # Create placeholder file
        touch "$ROM_PATH"
        echo "📝 Created placeholder ROM file - replace with actual ROM"
    fi
fi

# Final status check
echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""

# Check what still needs to be done
NEEDS_API_KEY=false
NEEDS_ROM=false

if grep -q "your_xai_api_key_here" .env 2>/dev/null; then
    NEEDS_API_KEY=true
fi

if [ ! -s "$ROM_PATH" ]; then
    NEEDS_ROM=true
fi

if [ "$NEEDS_API_KEY" = true ] || [ "$NEEDS_ROM" = true ]; then
    echo "📋 FINAL STEPS REQUIRED:"
    echo ""
    
    if [ "$NEEDS_API_KEY" = true ]; then
        echo "🔑 1. Add your xAI API key:"
        echo "   - Get key from: https://console.x.ai/"
        echo "   - Edit .env file and replace 'your_xai_api_key_here' with your actual key"
        echo ""
    fi
    
    if [ "$NEEDS_ROM" = true ]; then
        echo "🎮 2. Add Pokemon Fire Red ROM:"
        echo "   - Download from: https://archive.org/details/PokemonFireRedVersion"
        echo "   - Save as: roms/pokemonfr.gba"
        echo "   - Or use any Pokemon Fire Red ROM you legally own"
        echo ""
    fi
    
    echo "✅ Then run: source venv/bin/activate && python run.py"
else
    echo "🚀 Everything is ready! Run the AI player with:"
    echo "   source venv/bin/activate && python run.py"
fi

echo ""
echo "🎮 Get ready to watch Grok-4 Vision AI beat Pokemon Fire Red!"
echo "🏆 Goal: Complete the game and catch Mewtwo!"
echo ""
echo "⚠️  Remember: Don't interact with the browser during gameplay!"
echo "🤖 Look for 'Chrome is being controlled by automated test software' message" 