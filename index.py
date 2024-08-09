import discord
from discord.ext import commands
from discord.ui import Button, View

# Substitua pelo seu token
TOKEN = 'TOKEN'

# Defina os intents para o bot
intents = discord.Intents.default()
intents.message_content = True

# Prefixo para os comandos
bot = commands.Bot(command_prefix='!', intents=intents)

# Evento que ocorre quando o bot está pronto
@bot.event
async def on_ready():
    print(f'{bot.user} está online!')

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
    view.add_item(Button(style=discord.ButtonStyle.success, label="Produto 1", custom_id="produto_1"))
    view.add_item(Button(style=discord.ButtonStyle.primary, label="Produto 2", custom_id="produto_2"))
    view.add_item(Button(style=discord.ButtonStyle.danger, label="Produto 3", custom_id="produto_3"))

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

# Inicializa o bot
bot.run(TOKEN)
