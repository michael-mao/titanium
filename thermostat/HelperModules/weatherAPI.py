import pyowm
import time

#Pass in the city, returns current humidity and temp
def getCurrentWeather(city):
	#API Key
	owm = pyowm.OWM('bf301adce702f7ed7a91b92a0861a56e')

	#Get observation for the city
	observation = owm.weather_at_place( city + ',Canada')

	#Get Weather at this time
	w = observation.get_weather()

	#Parse and print
	print "Humidty is: " + str(w.get_humidity())              # 87
	print "Avg Temp is: " + str(w.get_temperature('celsius')['temp']) 

	#Return humidity and temp
	return (w.get_humidity(), w.get_temperature('celsius')['temp'])

#Pass in the city, prints 3 hourly temperature
#Return method customizable, list? Dictionary? Let me know
def get3hourWeather(city):
	owm = pyowm.OWM('bf301adce702f7ed7a91b92a0861a56e')
	fc = owm.three_hours_forecast(city + ',Canada')
	f = fc.get_forecast()
	for weather in f:
		print "Temp at " + str(weather.get_reference_time('iso')) + " is " + str(weather.get_temperature('celsius')['temp'])


#Uncomment following to run the script to test the above subroutines
#nb = raw_input('Please enter Canadian city:')
#getCurrentWeather(nb)
#get3hourWeather(nb)

