
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


#CREATE ANDROID APP

#sudo apt install -y python3-pip python3-setuptools python3-venv git zip unzip openjdk-17-jdk

cd folder_with_main.py
buildozer init
#condigure buildozer.spec
buildozer -v android debug
buildozer android deploy run
