import sqlite3

# Nome do arquivo do banco de dados
DATABASE = 'streamers.db'

# Conectar ao banco de dados (será criado se não existir)
conn = sqlite3.connect(DATABASE)

# Criar um cursor para executar comandos SQL
cursor = conn.cursor()

# Criar a tabela "streamers" se ela não existir
cursor.execute('''
CREATE TABLE IF NOT EXISTS streamers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

# Inserir alguns streamers de exemplo
streamers = ['alanzoka', 'coreano', 'tck10']
cursor.executemany('INSERT INTO streamers (name) VALUES (?)', [(name,) for name in streamers])

# Salvar as mudanças e fechar a conexão
conn.commit()
conn.close()

print("Banco de dados e tabela 'streamers' criados com sucesso!")
