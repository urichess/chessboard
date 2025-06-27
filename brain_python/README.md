
#Prepare environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


#install new packages
source venv/bin/activate
pip install pyserial #any package to be added to the installation
pip freeze > requirements.txt


#How to run it
source venv/bin/activate
python python_client.py -p /dev/ttyUSB0 -b 115200
