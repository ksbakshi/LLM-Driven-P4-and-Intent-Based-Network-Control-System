# P4 Code Generator using OpenAI

Hey there! This is a cool Python script that helps you generate P4 code using OpenAI's GPT-4.

## What You Need

Before you start, make sure you have:
- Python 3.x installed
- An OpenAI API key 
- A terminal to run commands (preferabily Bash)

## How to Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click on your profile icon (top right)
4. Go to "API keys"
5. Click "Create new secret key"
6. Copy your API key 

## Setting Up the Environment
I am a mac user so, it is recommended to use virtual environment to run python on mac
1. First, create a virtual environment like this:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install the required package:
```bash
pip install openai==0.28.0
```

4. Set your API key in the terminal:
```bash
export OPENAI_API_KEY='your-api-key-here'
```
(Replace 'your-api-key-here' with the key you copied)

## Running the Script

1. Make sure you're in the virtual environment (you'll see `(venv)` at the start of your terminal line)
2. Run the script:
```bash
python network_intent_to_p4.py
```
3. When prompted, describe what kind of P4 program you want (like "Create a P4 program for basic packet forwarding")
4. The script will generate the code and save it to a file

