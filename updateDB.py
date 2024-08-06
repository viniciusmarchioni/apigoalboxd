import requests
from datetime import datetime
import mysql.connector


# Configurações de conexão
config = {
    'user': 'root',
    'password': 'vinicius15',
    'host': '127.0.0.1',
    'database': 'db_footapp'
}

def close_db_connection(conn, cursor):
    cursor.close()
    conn.close()

# Sua chave de API
api_key = 'd5606e44fd4ef56705bd2b46414ee781'

# Cabeçalhos da requisição
headers = {
    'x-apisports-key': api_key
}
# URL para obter os jogos da liga
fixtures_url = f'https://v3.football.api-sports.io/fixtures'

fixtures_params = {
    'league': 71, #brasileirão 71, euro copa 4, Argentina 5942, premiere league 39, la liga 140, serie b 72, CDB 73, serie A italiana 135, Bundesliga 78
    'season': 2024,
    #'status': 'FT',  # Filtra apenas os jogos que já foram finalizados
    'timezone':'America/Sao_Paulo',
    'from':'2024-07-01',
    'to':'2024-08-25'
}
   
fixtures_response = requests.get(fixtures_url, headers=headers, params=fixtures_params)
fixtures = fixtures_response.json()
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

#Jogos de liga

for fixture in fixtures['response']:
    championship = fixture['league']['name']
    country = fixture['league']['country']
    gamedate = fixture['fixture']['date']
    team1 = fixture['teams']['home']['name']
    team1image = fixture['teams']['home']['logo']
    team2 = fixture['teams']['away']['name']
    team2image = fixture['teams']['away']['logo']
    score1 = fixture['goals']['home']
    score2 = fixture['goals']['away']
    cursor = conn.cursor()
    cursor.execute("INSERT INTO teste(team1,team2,score1,score2,championship,country1,country2,gamedate,type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,'futebol') ON DUPLICATE KEY UPDATE gamedate = VALUES(gamedate),country1 = values(country1),country2= values(country2), score1 = VALUES(score1), score2 = VALUES(score2);", (team1,team2,score1,score2,championship,country[0:3].upper(),country[0:3].upper(),gamedate))
    conn.commit()
    print('Atualizado jogo de',team1,'e', team2)
    cursor.execute("INSERT IGNORE INTO teams(name,url_image,color,country) values(%s,%s,'white',%s);", (team1,team1image,country[0:3].upper()))
    conn.commit()
    print('Atualizado',team1)
    cursor.execute("INSERT IGNORE INTO teams(name,url_image,color,country) values(%s,%s,'white',%s);", (team2,team2image,country[0:3].upper()))
    conn.commit()
    print('Atualizado',team2)



#tentativa falha da copa do brasil
'''
for fixture in fixtures['response']:
    championship = fixture['league']['name']
    country = fixture['league']['country']
    gamedate = fixture['fixture']['date']
    team1 = fixture['teams']['home']['name']
    team1image = fixture['teams']['home']['logo']
    team2 = fixture['teams']['away']['name']
    team2image = fixture['teams']['away']['logo']
    score1 = fixture['goals']['home']
    score2 = fixture['goals']['away']
    print(f'Pais:{country}\nteam1:{team1}\nteam2:{team2}\nscore1:{score1}\nscore2:{score2}\nChampionship:{championship}\n########################################')

'''

close_db_connection(conn, cursor)
