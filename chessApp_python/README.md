
#Prepare environment
python3 -m venv venv_brain
source venv_brain/bin/activate
pip install -r requirements.txt


#install new packages
source venv_brain/bin/activate
pip install pyserial #any package to be added to the installation
pip freeze > requirements.txt


#How to run it
source venv_brain/bin/activate
python ChessApp/ChessApp.py --token <aToken>


#TEST

#initial position
echo -e BOARD:FF-FF-00-00-00-00-FF-FFn > /dev/ttyV0 
