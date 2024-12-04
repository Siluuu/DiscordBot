clear

echo "Updating repository from GitHub..."
git pull origin main
if [ $? -ne 0 ]; then
    echo "Failed to pull the latest changes from GitHub."
    exit 1
fi

VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv $VENV_DIR

    echo "Activating virtual environment and installing requirements..."
    source $VENV_DIR/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Virtual environment already exists."
fi

source $VENV_DIR/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate the virtual environment."
    exit 1
fi

clear

python run_discord.py &
python run_twitch.py &

read -p "Press Enter to exit..."
