# database_streamers_def.py
import sqlite3
import requests

# Configurações da Twitch
TWITCH_CLIENT_ID = 'eihdbw6tvicumxjm2j7czflxgrmu6n'
TWITCH_CLIENT_SECRET = '49awu3axiwkmiy5h5fo91go5dwed3y'

# Função para conectar ao banco de dados SQLite
def connect_db():
    return sqlite3.connect('streamers.db')

# Função para obter a lista de streamers do banco de dados
def get_streamers():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM streamers')
    streamers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return streamers

# Função para adicionar um streamer ao banco de dados
def add_streamer_to_db(streamer_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO streamers (name) VALUES (?)', (streamer_name,))
    conn.commit()
    conn.close()

# Função para verificar se um streamer já está no banco de dados
def is_streamer_in_db(streamer_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM streamers WHERE name = ?', (streamer_name,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Função para validar se o streamer realmente existe na Twitch
def validate_streamer_exists(oauth_token, streamer_name):
    url = f'https://api.twitch.tv/helix/users?login={streamer_name}'
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {oauth_token}'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return bool(data['data'])
