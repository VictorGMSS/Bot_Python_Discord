import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('streamers.db')
cursor = conn.cursor()

# Executar uma consulta para visualizar os dados
cursor.execute("SELECT * FROM streamers")
rows = cursor.fetchall()

# Exibir os dados
for row in rows:
    print(row)

# Fechar a conexão
conn.close()
