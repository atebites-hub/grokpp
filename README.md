# 🎮 Grok Plays Pokemon

**Watch Grok-4 Vision AI autonomously play Pokemon Fire Red and attempt to beat the entire game!**

An AI-powered Pokemon player that uses advanced computer vision to analyze the game screen and make strategic decisions to complete Pokemon Fire Red, beat the Elite 4, and catch Mewtwo.

## ✨ Features

- 🤖 **AI-Powered Gameplay**: Uses Grok-4 Vision to analyze screenshots and make intelligent decisions
- 🎯 **Complete Game Goal**: Aims to beat the entire game including Elite 4 and catch Mewtwo
- 🎮 **Browser-Based Emulation**: Runs Pokemon Fire Red in a web browser using EmulatorJS
- ⚡ **Real-Time Analysis**: Takes screenshots and decides actions every 0.5 seconds
- 🧠 **AI Thoughts Display**: See the AI's reasoning in real-time in the browser overlay
- 🔧 **Production Ready**: Optimized for reliability and speed

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome browser
- Pokemon Fire Red ROM file (`pokemonfr.gba`)
- xAI API key (get from [x.ai](https://x.ai))

### Installation

1. **Clone and setup**
   ```bash
   git clone <repo-url>
   cd grokpp
   ./setup.sh
   ```

2. **Add your API key**
   ```bash
   echo 'XAI_API_KEY=your_actual_api_key_here' > .env
   ```

3. **Add your Pokemon ROM**
   - Place your Pokemon Fire Red ROM in the project directory
   - Name it exactly: `pokemonfr.gba`

### Usage

**Run the AI Pokemon Player:**
```bash
source venv/bin/activate
python run.py
```

**Or use the main launcher:**
```bash
python grok_plays_pokemon.py
```

## 🎮 How It Works

1. **Screenshot Analysis**: AI captures and analyzes the game screen
2. **Strategic Decision Making**: Grok-4 Vision determines the best action
3. **Action Execution**: Converts AI decisions into keyboard inputs
4. **Continuous Learning**: Updates memory and strategy as it progresses

## ⚠️ Important Rules

- **NEVER interact with the browser window** - this will crash the automation
- **Let the AI play completely autonomously** - just watch and enjoy
- **The AI will handle everything** - battles, navigation, catching Pokemon
- **Watch the AI thoughts** in the right panel of the browser

## 🎯 AI Objectives

The AI is programmed with these goals:
- Complete the Pokemon Fire Red storyline
- Train and evolve Pokemon strategically  
- Beat all Gym Leaders and the Elite 4
- Become the Pokemon Champion
- Catch legendary Pokemon including Mewtwo
- Make strategic battle decisions using type advantages

## 🛠️ Technical Details

- **Frontend**: HTML5 with EmulatorJS for GBA emulation
- **Backend**: Python with Selenium for browser automation
- **AI Model**: Grok-4 Vision via xAI API
- **Input Method**: JavaScript keyboard simulation
- **Analysis Frequency**: Every 0.5 seconds for fast gameplay

## 📁 Project Structure

```
grokpp/
├── run.py                      # Simple launcher script
├── grok_plays_pokemon.py       # Main production launcher
├── pokemon_player_browser.py   # Core AI player logic
├── local_emulator.html         # GBA emulator interface
├── requirements.txt            # Python dependencies
├── setup.sh                   # Automated setup script
├── .env                       # API key configuration
└── pokemonfr.gba              # Pokemon ROM (not included)
```

## 🔧 Configuration

- ROM loading with automatic retry and manual fallback
- Optimized for speed with 0.5s decision cycles
- Enhanced game state detection and validation
- Production-ready error handling and logging

## 🎉 Watch the Magic

Once started, you'll see:
- 🖥️ **Chrome browser** with Pokemon Fire Red running
- 🧠 **AI thoughts panel** showing real-time decision making
- ⌨️ **Automatic gameplay** with no human intervention needed
- 📊 **Progress updates** in the terminal

---

**Sit back and watch Grok-4 Vision master Pokemon Fire Red! 🎮🤖** 