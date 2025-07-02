
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
python python_client.py -p /dev/ttyUSB0 -b 115200
python python_client.py -p /dev/ttyUSB1 -b 115200
python wait_for_initial_position_poo.py -p /dev/ttyV1 -b 115200



#TEST

#initial position
echo -e BOARD:FF-FF-00-00-00-00-EF-FFn > /dev/ttyV0 
