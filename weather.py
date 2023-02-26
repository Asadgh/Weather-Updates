import requests
import json
from datetime import datetime
from my_scripts import kmh_to_ms, format_date
import pytz
from os import path


with open("app_defaults.json", "r") as fileh:
    app_json = json.load(fileh)

APIKEY = app_json['APIKEY']
NESTS = app_json['NESTS']
BASE = 'weather_info'


def jobber():
    LASTDATE = app_json['LASTDATE']
    # Get the current time in GMT
    tz = pytz.timezone('GMT')
    now = datetime.now(tz)
    if str(now.date()) != LASTDATE:
        if now.hour >= 6 and now.minute >= 00:
            fetch_weather()

            app_json['LASTDATE'] = str(now.date())
            with open("app_defaults.json", "w") as fileh:
                json.dump(app_json, fileh)

def fetch_weather():
    for nest in NESTS.keys():
        LOCATIONKEY = NESTS[nest][1]
        
        daily_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{LOCATIONKEY}?apikey={APIKEY}&details=true&metric=true"
        hourly_url = f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{LOCATIONKEY}?apikey={APIKEY}&details=true&metric=true"

        daily_response = requests.get(daily_url)
        daily_response_json = json.loads(daily_response.content)

        with open(path.join(BASE, f"{nest}_Daily.json"), "w") as outfile:
            json.dump(daily_response_json, outfile)

        hourly_response = requests.get(hourly_url)
        hourly_response_json = json.loads(hourly_response.content)

        with open(path.join(BASE, f"{nest}_Hourly.json"), "w") as outfile:
            json.dump(hourly_response_json, outfile)


def get_daily_weather(nest):
    with open(path.join(BASE, f'{nest}_Daily.json'), "r") as fileh:
        response_json = json.load(fileh)

    daily_weather_info = {}

    daily_weather_info["text"] = response_json["Headline"]["Text"]
    daily_weather_info["date"] = format_date(str(datetime.fromisoformat(response_json["DailyForecasts"][0]["Date"]).date()))
    daily_weather_info["category"] = response_json["Headline"]["Category"]
    daily_weather_info["max_temp"] = response_json["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
    daily_weather_info["max_real_feel"] = response_json["DailyForecasts"][0]["RealFeelTemperature"]["Maximum"]["Value"]
    daily_weather_info["min_temp"] = response_json["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
    daily_weather_info["min_real_feel"] = response_json["DailyForecasts"][0]["RealFeelTemperature"]["Minimum"]["Value"]
    daily_weather_info["real_feel_phrase"] = response_json["DailyForecasts"][0]["RealFeelTemperature"]["Maximum"]["Phrase"]
    daily_weather_info["uv_index"] = response_json["DailyForecasts"][0]["AirAndPollen"][5]["Value"]
    daily_weather_info["uv_index_cat"] = response_json["DailyForecasts"][0]["AirAndPollen"][5]["Category"]

    icon = str(response_json["DailyForecasts"][0]["Day"]["Icon"])
    daily_weather_info["icon"] = icon if len(icon) > 1 else '0' + icon
    daily_weather_info["has_precipitation"] = response_json["DailyForecasts"][0]["Day"]["HasPrecipitation"]
    daily_weather_info["short_phrase"] = response_json["DailyForecasts"][0]["Day"]["ShortPhrase"]
    daily_weather_info["long_phrase"] = response_json["DailyForecasts"][0]["Day"]["LongPhrase"]

    daily_weather_info["precipitation_probability"] = response_json["DailyForecasts"][0]["Day"]["PrecipitationProbability"]
    daily_weather_info["thunderstorm_probability"] = response_json["DailyForecasts"][0]["Day"]["ThunderstormProbability"]
    daily_weather_info["rain_probability"] = response_json["DailyForecasts"][0]["Day"]["RainProbability"]
    daily_weather_info["snow_probability"] = response_json["DailyForecasts"][0]["Day"]["SnowProbability"]

    daily_weather_info["wind_speed"] = kmh_to_ms(response_json["DailyForecasts"][0]["Day"]["Wind"]["Speed"]["Value"])
    daily_weather_info["wind_dir_deg"] = response_json["DailyForecasts"][0]["Day"]["Wind"]["Direction"]["Degrees"]
    daily_weather_info["wind_dir"] = response_json["DailyForecasts"][0]["Day"]["Wind"]["Direction"]["Localized"]

    daily_weather_info["wind_gust_speed"] = kmh_to_ms(response_json["DailyForecasts"][0]["Day"]["WindGust"]["Speed"]["Value"])
    daily_weather_info["wind_gust_dir_deg"] = response_json["DailyForecasts"][0]["Day"]["WindGust"]["Direction"]["Degrees"]
    daily_weather_info["wind_gust_dir"] = response_json["DailyForecasts"][0]["Day"]["WindGust"]["Direction"]["Localized"]

    daily_weather_info["link"] = response_json["DailyForecasts"][0]["Link"]

    return daily_weather_info



def get_hourly_weather(nest):

    with open(path.join(BASE, f'{nest}_Hourly.json'), "r") as fileh:
        response_json = json.load(fileh)

    hourly_weather_info = {
        "date": None,

        "min_temp": None,
        "min_temp_hr": None,
        "min_temp_icon": None,
        "min_temp_hp": None,
        "min_temp_rf": None,

        "min_wind": None,
        "min_wind_hr": None,
        "min_wind_deg": None,
        "min_wind_dir": None,

        "min_wind_gust": None,
        "min_wind_gust_hr": None,

        "min_rel_humidity": None,
        "min_rel_humidity_hr": None,

        "min_uv_index": None,
        "min_uv_index_hr": None,
        "min_uv_index_text": None,
        
        "max_temp": None,
        "max_temp_hr": None,
        "max_temp_icon": None,
        "max_temp_hp": None,
        "max_temp_rf": None,

        "max_wind": None,
        "max_wind_hr": None,
        "max_wind_deg": None,
        "max_wind_dir": None,

        "max_wind_gust": None,
        "max_wind_gust_hr": None,

        "max_rel_humidity": None,
        "max_rel_humidity_hr": None,

        "max_uv_index": None,
        "max_uv_index_hr": None,
        "max_uv_index_text": None,
    }

    for hour in range(len(response_json)):
        hourly_info = response_json[hour]
        if hour == 0:
            hourly_weather_info["date"] = format_date(str(datetime.fromisoformat(hourly_info['DateTime']).date()))
            
            hourly_weather_info["max_temp"] = hourly_info['Temperature']['Value']
            hourly_weather_info["max_temp_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["max_temp_icon"] = hourly_info['WeatherIcon']
            hourly_weather_info["max_temp_hp"] = hourly_info['HasPrecipitation']
            hourly_weather_info["max_temp_rf"] = hourly_info['RealFeelTemperature']['Value']
            
            hourly_weather_info["max_wind"] = kmh_to_ms(hourly_info['Wind']['Speed']['Value'])
            hourly_weather_info["max_wind_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["max_wind_deg"] = hourly_info['Wind']['Direction']['Degrees']
            hourly_weather_info["max_wind_dir"] = hourly_info['Wind']['Direction']['Localized']

            hourly_weather_info["max_wind_gust"] = kmh_to_ms(hourly_info['WindGust']['Speed']['Value'])
            hourly_weather_info["max_wind_gust_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour

            hourly_weather_info["max_rel_humidity"] = hourly_info['RelativeHumidity']
            hourly_weather_info["max_rel_humidity_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour

            hourly_weather_info["max_uv_index"] = hourly_info['UVIndex']
            hourly_weather_info["max_uv_index_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["max_uv_index_text"] = hourly_info['UVIndexText']

            hourly_weather_info["min_temp"] = hourly_info['Temperature']['Value']
            hourly_weather_info["min_temp_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["min_temp_icon"] = hourly_info['WeatherIcon']
            hourly_weather_info["min_temp_hp"] = hourly_info['HasPrecipitation']
            hourly_weather_info["min_temp_rf"] = hourly_info['RealFeelTemperature']['Value']
            
            hourly_weather_info["min_wind"] = kmh_to_ms(hourly_info['Wind']['Speed']['Value'])
            hourly_weather_info["min_wind_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["min_wind_deg"] = hourly_info['Wind']['Direction']['Degrees']
            hourly_weather_info["min_wind_dir"] = hourly_info['Wind']['Direction']['Localized']

            hourly_weather_info["min_wind_gust"] = kmh_to_ms(hourly_info['WindGust']['Speed']['Value'])
            hourly_weather_info["min_wind_gust_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour

            hourly_weather_info["min_rel_humidity"] = hourly_info['RelativeHumidity']
            hourly_weather_info["min_rel_humidity_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour

            hourly_weather_info["min_uv_index"] = hourly_info['UVIndex']
            hourly_weather_info["min_uv_index_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["min_uv_index_text"] = hourly_info['UVIndexText']

            continue

        if hourly_info['Temperature']['Value'] > hourly_weather_info["max_temp"]:
            hourly_weather_info["max_temp"] = hourly_info['Temperature']['Value']
            hourly_weather_info["max_temp_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["max_temp_icon"] = hourly_info['WeatherIcon']
            hourly_weather_info["max_temp_hp"] = hourly_info['HasPrecipitation']
            hourly_weather_info["max_temp_rf"] = hourly_info['RealFeelTemperature']['Value']
        elif hourly_info['Temperature']['Value'] == hourly_weather_info["max_temp"]:
            hourly_weather_info["max_temp_hr"] = str(hourly_weather_info["max_temp_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)
            

        if hourly_info['Temperature']['Value'] < hourly_weather_info["min_temp"]:
            hourly_weather_info["min_temp"] = hourly_info['Temperature']['Value']
            hourly_weather_info["min_temp_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["min_temp_icon"] = hourly_info['WeatherIcon']
            hourly_weather_info["min_temp_hp"] = hourly_info['HasPrecipitation']
            hourly_weather_info["min_temp_rf"] = hourly_info['RealFeelTemperature']['Value']
        elif hourly_info['Temperature']['Value'] == hourly_weather_info["min_temp"]:
            hourly_weather_info["min_temp_hr"] = str(hourly_weather_info["min_temp_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)
            
        if hourly_info['Wind']['Speed']['Value'] > hourly_weather_info["max_wind"]:
            hourly_weather_info["max_wind"] = hourly_info['Wind']['Speed']['Value']
            hourly_weather_info["max_wind_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["max_wind_deg"] = hourly_info['Wind']['Direction']['Degrees']
            hourly_weather_info["max_wind_dir"] = hourly_info['Wind']['Direction']['Localized']
        elif hourly_info['Wind']['Speed']['Value'] == hourly_weather_info["max_wind"]:
            hourly_weather_info["max_wind_hr"] = str(hourly_weather_info["max_wind_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)

        if hourly_info['Wind']['Speed']['Value'] < hourly_weather_info["min_wind"]:
            hourly_weather_info["min_wind"] = hourly_info['Wind']['Speed']['Value']
            hourly_weather_info["min_wind_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["min_wind_deg"] = hourly_info['Wind']['Direction']['Degrees']
            hourly_weather_info["min_wind_dir"] = hourly_info['Wind']['Direction']['Localized']
        elif hourly_info['Wind']['Speed']['Value'] == hourly_weather_info["min_wind"]:
            hourly_weather_info["min_wind_hr"] = str(hourly_weather_info["min_wind_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)
            
        if hourly_info['WindGust']['Speed']['Value'] > hourly_weather_info["max_wind_gust"]:
            hourly_weather_info["max_wind_gust"] = hourly_info['WindGust']['Speed']['Value']
            hourly_weather_info["max_wind_gust_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
        elif hourly_weather_info["max_wind_gust"] == hourly_info['WindGust']['Speed']['Value']:
            hourly_weather_info["max_wind_gust_hr"] = str(hourly_weather_info["max_wind_gust_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)

        if hourly_info['WindGust']['Speed']['Value'] < hourly_weather_info["min_wind_gust"]:
            hourly_weather_info["min_wind_gust"] = hourly_info['WindGust']['Speed']['Value']
            hourly_weather_info["min_wind_gust_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
        elif hourly_weather_info["min_wind_gust"] == hourly_info['WindGust']['Speed']['Value']:
            hourly_weather_info["min_wind_gust_hr"] = str(hourly_weather_info["min_wind_gust_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)

        if hourly_info['RelativeHumidity'] > hourly_weather_info["max_rel_humidity"]:
            hourly_weather_info["max_rel_humidity"] = hourly_info['RelativeHumidity']
            hourly_weather_info["max_rel_humidity_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
        elif hourly_info['RelativeHumidity'] == hourly_weather_info["max_rel_humidity"]:
            hourly_weather_info["max_rel_humidity_hr"] = str(hourly_weather_info["max_rel_humidity_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)

        if hourly_info['RelativeHumidity'] < hourly_weather_info["min_rel_humidity"]:
            hourly_weather_info["min_rel_humidity"] = hourly_info['RelativeHumidity']
            hourly_weather_info["min_rel_humidity_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
        elif hourly_info['RelativeHumidity'] == hourly_weather_info["min_rel_humidity"]:
            hourly_weather_info["min_rel_humidity_hr"] = str(hourly_weather_info["min_rel_humidity_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)

        if hourly_info['UVIndex'] > hourly_weather_info["max_uv_index"]:
            hourly_weather_info["max_uv_index"] = hourly_info['UVIndex']
            hourly_weather_info["max_uv_index_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["max_uv_index_text"] = hourly_info['UVIndexText']
        elif hourly_info['UVIndex'] == hourly_weather_info["max_uv_index"]:
            hourly_weather_info["max_uv_index_hr"] = str(hourly_weather_info["max_uv_index_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)

        if hourly_info['UVIndex'] < hourly_weather_info["min_uv_index"]:
            hourly_weather_info["min_uv_index"] = hourly_info['UVIndex']
            hourly_weather_info["min_uv_index_hr"] = datetime.fromisoformat(hourly_info['DateTime']).time().hour
            hourly_weather_info["min_uv_index_text"] = hourly_info['UVIndexText']
        elif hourly_info['UVIndex'] == hourly_weather_info["min_uv_index"]:
            hourly_weather_info["min_uv_index_hr"] = str(hourly_weather_info["min_uv_index_hr"]) + ', ' +\
                 str(datetime.fromisoformat(hourly_info['DateTime']).time().hour)

    hourly_weather_info["max_wind"] = kmh_to_ms(hourly_weather_info["max_wind"])
    hourly_weather_info["max_wind_gust"] = kmh_to_ms(hourly_weather_info["max_wind_gust"])
    return hourly_weather_info


# APIKEY = 'G3z85PdZaboaBGmZy4Ri7Q4PqJa7z6ny'
# LOCATIONKEY = '180265'

# import pprint
# pprint.pprint(get_hourly_weather(LOCATIONKEY, APIKEY))