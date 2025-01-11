import json
import  requests

URL = "https://api.openweathermap.org/data/2.5/weather"

def current_weather(city_name, KEY, df):
    mean = df[(df.city == city_name) & (df.season == "winter")].average_season_temperature.values[0]
    std= df[(df.city == city_name) & (df.season == "winter")].season_temperature_std.values[0]

    payload = {
    "q": city_name,
    "appid": KEY,
    "units": "metric"
    }
    resp = requests.get(url=URL, params=payload)
    if resp.status_code != 200:
        return resp.text, None
    curr_temp = json.loads(resp.text)['main']['temp']
    return curr_temp, abs(curr_temp) > (mean + 2*std)

def get_season_stats(df, city):
    store = {}
    for name, frame in df[df.city==city].groupby(['season', 'city']):
        store[name[0]] = {"mean": frame.temperature.mean(), "std": frame.temperature.std()}
    return store


def prepare_dataframe(df):
    df['moving_average'] = df.temperature.rolling(30).mean()
    df['moving_average_std'] = df.temperature.rolling(30).std()
    df['average_season_temperature'] = df.groupby(['season', 'city']).temperature.transform("mean")
    df['season_temperature_std'] = df.groupby(['season', 'city']).temperature.transform("std")
    df['upper_boundary'] = df['average_season_temperature'] + 2*df['season_temperature_std']
    df['lower_boundary'] =  df['average_season_temperature'] - 2*df['season_temperature_std']
    df['is_anomaly'] = (df.temperature > (df.moving_average+2*df.moving_average_std)) | (df.temperature < (df.moving_average-2*df.moving_average_std))
    return df