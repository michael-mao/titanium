# titanium

Requirements:
- Python v3.4.x
  - pygame v1.9.2
- Node v5.7.0
  - npm
  - bower

Hardware:
- Raspberry Pi
- DS18b20 digital temperature sensor
- 3.5" touchscreen

## Thermostat
In the root project directory, install the python dependencies with:
```
$ pip install -r requirements.txt
```
*NOTE: pygame needs to be manually downloaded and built from source. PyPI version is not guaranteed to work.*

Run the code with:
```
$ python main.py
```

## Webapp
Install server and front-end dependencies with the `setup.sh` bash script or manually:

**Script**
```
$ bash setup.sh
```

**Manual**
```
# in the webapp/ directory
$ npm install
```

```
# in the webapp/app/ directory
$ bower install
```

Run the server with:
```
# in the webapp/ directory
$ node server.js
```
