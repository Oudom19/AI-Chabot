1️⃣ Clone the Repository 
git clone <your-repo-url>
cd <your-project-folder>

2️⃣ Create a Virtual Environment (Recommended)
To keep dependencies isolated, create a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows

3️⃣ Install Dependencies
Install all required Python packages:
pip install -r requirements.txt
pip install -r requirements-actions.txt
💡 Tip: You can combine requirements-actions.txt into requirements.txt to simplify installation.

4️⃣ Install and Configure ngrok
Download and install ngrok:
pip install pyngrok
Authenticate ngrok with your auth token:
ngrok authtoken <your-ngrok-auth-token>
Then, configure ngrok in credentials.yml.

5️⃣ Setup Telegram Bot
Install Telegram dependencies:
pip install aiogram
Add your Telegram bot token and bot name in credentials.yml.

6️⃣ MySQL Database Configuration
Ensure MySQL is installed and running.

Update actions.py to match your database connection settings.

7️⃣ Training the Rasa Model
rasa train

8️⃣ Start the Services
Run ngrok:
ngrok http 5005 or ngrok http --url=morally-wired-dassie.ngrok-free.app 5005 (For Static Domain)
Start MySQL.

Run Rasa:
rasa run

Run Rasa actions:
rasa run actions

Run Telegram bot:
python telegram_bot.py