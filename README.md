# 🔍 Peekachu

A Discord bot that allows you to **search recent messages across all channels** in your server, with pagination and clickable "Jump to Message" links.  

It also logs **execution time** and **memory usage** to the console for better debugging and monitoring.

---

## ✨ Features

- `/search <word> [limit]` slash command to search messages  
  - `word`: keyword to search for  
  - `limit`: minimum message length (default: 80 chars)  
- Searches up to the **last 500 messages per channel**  
- Results are shown in a **paginated embed** (with "Previous" / "Next" buttons)  
- Each result includes:  
  - Author’s display name  
  - Channel name  
  - Preview of the message  
  - "Jump to Message" link (opens the original message in Discord)

<br>
<p align="center">
  <img width="271" height="343" alt="Screenshot" src="https://github.com/user-attachments/assets/7dbe6852-5442-41b1-9076-e5cca3cc45ed" />
  <br>
  <em>Example search results with pagination</em>
</p>
<br>
  
- Console logs show:  
  - Search start/end  
  - **Time taken**  
  - **Memory usage** (`psutil`)

<br>
<p align="center">
  <img width="578" height="165" alt="Screenshot from 2025-08-24 17-21-17" src="https://github.com/user-attachments/assets/b51edfe9-27fd-4fe6-8ad4-0354d69be3b0" />
  <br>
  <em>Example bot logs</em>
</p>
<br>

---

## ⚙️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/git-pixel22/peekachu.git
cd peekachu
```

### 2. Create and activate a virtual environment
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file
Add your bot token inside a `.env` file in the project root:

```
DISCORD_TOKEN=your-bot-token-here
```

### 5. Run the bot
```bash
python bot.py
```

---

## 📋 Requirements

- Python 3.9+  
- A Discord application & bot token ([Create one here](https://discord.com/developers/applications))  
- Dependencies listed in `requirements.txt` (mainly `discord.py`, `python-dotenv`, `psutil`)

---

## 📝 Example Command

```
/search hello 20
```

This will search for the keyword **hello** in all messages (≥ 20 characters long) across all channels.

---

## 📊 Logging Example

The bot logs each event with a timestamp, memory usage, and execution time:

```
[12:34:56] 🔎 User Pixel triggered /search for 'hello' (≥ 20 chars) | 🧠 45.23 MB
[12:34:58] ✅ Found 10 results for 'hello' (requested by Pixel) in 2.15s | 🧠 47.01 MB
```

---
