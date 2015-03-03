#LYS Media Server
Basic README for LYS Media Server side.

Involved technologies:

1. **Bottle.py**
2. **Redis**

##How to test locally

*Install and run Redis*
		
		sudo apt-get install redis-server
		redis-server

*Create a virtual enviroment, clone the repo, install requirements*

		virtualenv -p /usr/bin/python3.2 lys-ms
		cd lys-ms
		source bin/activate
		git clone https://github.com/brunifrancesco/lys-ms.git
		pip install -r requirements.txt

*Run the server*
		
		python ms.py

*Run the tests*
	
		 python -m unittest discover

##Exposed enpoints

1. **POST** <localhost:8080/recordStream>; 
		
		Body (JSON): port, filename
		returns (JSON) {details:"details"}

2. **POST** <localhost:8080/writeSdp>;
	
		Body (JSON) port, sdp_content
		returns (JSON) {details:details}

		
3. **DELETE** <localhost:8080/writeSdp>;

	
		Body (JSON): pid
		returns (JSON) {details:"details"}

4. **GET** <localhost:8080/currentStreams>; 
	
	
		returns (JSON) {data:[pid1, pid2, pid3]}
