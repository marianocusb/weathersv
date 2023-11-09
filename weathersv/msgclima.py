import datetime

import pandas as pd
import requests
from tqdm import tqdm
from twilio.rest import Client

from configccl import *

query = 'Bogotá'
api_key = API_KEY_WAPI

url_clima = 'http://api.weatherapi.com/v1/forecast.json?key=' + api_key + '&q=' + query + '&days=1&aqi=no&alerts=no'
response = requests.get(url_clima).json()


def get_forecast(response, i):
    fecha = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hora = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    condicion = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    temp = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    prob_rain = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    humidity = response['forecast']['forecastday'][0]['hour'][i]['humidity']
    return fecha, hora, condicion, float(temp), rain, float(prob_rain), humidity

def get_message(df_rain):
    body = 'Hola! \n\n\n El pronostico del clima hoy ' + df['Fecha'][0] + ' en ' + query + ' es : \n\n\nHora 🕒  Temperatura 🌡️' + '\n'+str(df_rain['Temperatura'].apply(lambda x: f'{x}°C 🌡️')) + '\n\n\nHora  🕒   Probabilidad de lluvia  🌧️' + '\n' + str(df_rain['prob_lluvia'].apply(lambda x: f'{x}% 🌧️'))
    df_rain = df_rain.sort_values(by='Hora', ascending=True)
    body += body.replace("Name: prob_lluvia, dtype: object", "")
    body += body.replace("Name: Temperatura, dtype: object", "")
    return body

datos = []
for i in tqdm(range(len(response['forecast']['forecastday'][0]['hour'])), colour='green'):
    datos.append(get_forecast(response, i))
col = ['Fecha', 'Hora', 'Condici'
                        'on', 'Temperatura', 'Lluvia', 'prob_lluvia', 'Humedad']
df = pd.DataFrame(datos, columns=col)
df_rain = df[(df['Lluvia'] == 1) & (df['Hora'] > 6) & (df['Hora'] < 22)]
df_rain = df_rain[['Hora', 'Condicion', 'Temperatura', 'prob_lluvia']]
df_rain.set_index('Hora', inplace=False)
df_rain['Temperatura'] = df_rain['Temperatura'].astype('float')
df_rain['prob_lluvia'] = df_rain['prob_lluvia'].astype('float')


account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)
message = client.messages \
    .create(
    body=get_message(df_rain),
    from_=PHONE_NUMBER,
    to=number
)
print('Mensaje Enviado ' + message.sid)
message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=get_message(df_rain),
    to='whatsapp:+573046781698'
)
print('Whatsapp Enviado ' + message.sid)
