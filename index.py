import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import random
import requests
import asyncio
from database_streamers_def import connect_db, get_streamers, add_streamer_to_db, is_streamer_in_db, validate_streamer_exists
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Substitua os tokens e IDs pelas variáveis de ambiente
TOKEN = os.getenv('DISCORD_TOKEN')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
DISCORD_CHANNEL_ID = 1271163874258980945

# Defina os intents para o bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necessário para obter a lista de membros do servidor

# Prefixo para os comandos
bot = commands.Bot(command_prefix='!', intents=intents)

# Funções da Twitch
def get_twitch_oauth_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    data = response.json()
    return data['access_token']

def get_streamer_status(oauth_token, streamer_name):
    url = f'https://api.twitch.tv/helix/streams?user_login={streamer_name}'
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {oauth_token}'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['data']

# Evento que ocorre quando o bot está pronto
@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    check_streamer_status.start()  # Inicia a tarefa de verificação

# Comando simples
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Olá, {ctx.author.name}!')

@bot.command(name='loja')
async def loja(ctx):
    # Cria uma visualização com três botões
    view = View()
    view.add_item(
        Button(style=discord.ButtonStyle.primary,
               label="Produto 1",
               custom_id="produto_1"))
    view.add_item(
        Button(style=discord.ButtonStyle.primary,
               label="Produto 2",
               custom_id="produto_2"))
    view.add_item(
        Button(style=discord.ButtonStyle.primary,
               label="Produto 3",
               custom_id="produto_3"))

    # Envia a mensagem com os botões
    await ctx.send("Escolha uma opção:", view=view)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data['custom_id'] == "produto_1":
            await interaction.response.send_message("Você escolheu o Produto 1!")
        elif interaction.data['custom_id'] == "produto_2":
            await interaction.response.send_message("Você escolheu o Produto 2!")
        elif interaction.data['custom_id'] == "produto_3":
            await interaction.response.send_message("Você escolheu o Produto 3!")

@bot.command(name='roll')
async def roll(ctx, dice: str):
    try:
        # Extrair o número de lados do dado a partir do comando
        num_sides = int(dice[1:])
        username = ctx.author.name.capitalize()
        # Gerar um número aleatório entre 1 e o número de lados
        roll_result = random.randint(1, num_sides)
        await ctx.send(f'🎲 {username}, você rolou um **{roll_result}**')
    except ValueError:
        await ctx.send('Por favor, use o formato correto, como !d20, !d6, etc.')

def generate_progress_bar(current, total, length=20):
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    return f'[{bar}] {current}/{total}'

def get_leaderboard(members, page=1, per_page=2):
    start = (page - 1) * per_page
    end = start + per_page
    leaderboard = sorted(members, key=lambda m: m.name)[start:end]
    return leaderboard

def get_page_buttons(total_pages, current_page):
    buttons = []
    for i in range(1, total_pages + 1):
        if i == current_page:
            buttons.append(
                Button(label=str(i),
                       style=discord.ButtonStyle.primary,
                       disabled=True))
        else:
            button = Button(label=str(i),
                            style=discord.ButtonStyle.secondary,
                            custom_id=f'page_{i}')
            buttons.append(button)
    return buttons

@bot.command(name='leaderboard')
async def leaderboard_command(ctx, page: int = 1):
    members = [member for member in ctx.guild.members if not member.bot]

    if not members:
        await ctx.send('Não há usuários no servidor.')
        return

    per_page = 2
    total_pages = (len(members) + per_page - 1) // per_page  # Calcula o total de páginas
    leaderboard = get_leaderboard(members, page, per_page)

    if not leaderboard:
        await ctx.send('Não há mais usuários para mostrar.')
        return

    max_points = 1000  # Valor máximo de pontos fictício
    embed = discord.Embed(
        title=f'🏆 Tabela de Liderança - Página {page}',
        description='Aqui estão os usuários mais ativos no servidor:',
        color=discord.Color.gold()  # Cor dourada para destacar a tabela
    )

    for i, member in enumerate(leaderboard):
        rank = i + 1 + (page - 1) * per_page
        points = random.randint(100, max_points)  # Pontuação aleatória
        progress_bar = generate_progress_bar(points, max_points)

        embed.add_field(name=f'**#{rank}** {member.name.capitalize()}',
                        value=f'✨ **{points}** pontos\n{progress_bar}',
                        inline=False)

    embed.set_thumbnail(url=ctx.guild.icon.url)  # Adiciona o ícone do servidor ao embed

    view = View()
    buttons = get_page_buttons(total_pages, page)

    for button in buttons:
        async def page_button_callback(interaction: discord.Interaction):
            try:
                page_number = int(interaction.data['custom_id'].split('_')[1])
                await interaction.response.defer()  # Defer a resposta
                await leaderboard_command(ctx, page=page_number)
            except Exception as e:
                print(f'Erro ao processar interação: {e}')

        button.callback = page_button_callback
        view.add_item(button)

    await ctx.send(embed=embed, view=view)

@bot.command(name='streamer')
async def add_streamer(ctx, streamer_name: str):
    oauth_token = get_twitch_oauth_token()

    if is_streamer_in_db(streamer_name):
        await ctx.send(f'O streamer `{streamer_name}` já está na lista!')
        return

    if validate_streamer_exists(oauth_token, streamer_name):
        add_streamer_to_db(streamer_name)
        await ctx.send(f'O streamer `{streamer_name}` foi adicionado com sucesso!')
    else:
        await ctx.send(f'O streamer `{streamer_name}` não foi encontrado na Twitch.')

# Tarefa para verificar o status dos streamers na Twitch
@tasks.loop(seconds=60)
async def check_streamer_status():
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print("Canal não encontrado")
        return

    oauth_token = get_twitch_oauth_token()
    streamers = get_streamers()  # Obtém a lista de streamers do banco de dados

    for streamer_name in streamers:
        status = get_streamer_status(oauth_token, streamer_name)
        is_online = bool(status)
        last_online = getattr(check_streamer_status, f"last_online_{streamer_name}", False)

        if is_online and not last_online:
            try:
                await channel.send(
                    f'{streamer_name} está ao vivo! Confira aqui: https://www.twitch.tv/{streamer_name}'
                )
                print(f"Mensagem enviada para o Discord para {streamer_name}")
            except Exception as e:
                print(f"Erro ao enviar mensagem para {streamer_name}: {e}")

        setattr(check_streamer_status, f"last_online_{streamer_name}", is_online)

# Inicializa o bot
bot.run(TOKEN)
