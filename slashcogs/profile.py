from distutils import errors
import json
import discord
from discord.ext import commands
from discord.commands import Option, slash_command
import requests
import json

with open ('././extension/emoji.json', 'r') as f:
	emojidata = json.load(f)

with open ('././config/api.json', 'r') as f:
	api_heads = json.load(f)
	headers = api_heads["user_agent"]

def profile_info(username, tagline):
		
	
	api_Req = requests.get(f"https://api.henrikdev.xyz/valorant/v1/account/{username}/{tagline}", headers=headers)
	data = api_Req.json()

	VALUE = {}

	VALUE["puuid"] = data["data"]["puuid"]
	VALUE["region"] = data["data"]["region"]
	VALUE["account_level"] = data["data"]["account_level"]
	VALUE["name"] = data["data"]["name"]
	VALUE["tag"] = data["data"]["tag"]
	VALUE["thumbnail"] = data["data"]["thumbnail"] = data["data"]["card"]["small"]
	VALUE["image"] = data["data"]["card"]["wide"]

	return VALUE

def getRank(region, puuid):
	req_data = requests.get(f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{region}/{puuid}", headers=headers) 
	whole_data = req_data.json()
		
	currenttier =  whole_data['data']['current_data']['currenttier']


	return currenttier
	
class slash_profile(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.slash_command( description="Info about your valorant account")
	async def profile(
			self,
			ctx
		):
			
			REPLY_EMOTE = emojidata["reply"] # there is a reason why i did this ;-;
			

			await ctx.response.defer()
			author_id = str(ctx.author.id)
			
			try:
				user = await self.bot.pg_con.fetchrow("SELECT * FROM acclink WHERE userid = $1", author_id)
				user_name = user['name']
				tagline = user['tagline']

				data = profile_info(user_name, tagline)
				rank = getRank(data['region'], data['puuid'])

				embed = discord.Embed(
					color = discord.Colour.random(),
					timestamp=discord.utils.utcnow()
				)
				embed.add_field(name ="Region", value=f'{REPLY_EMOTE}{data["region"]}', inline=False)
				embed.add_field(name ="Account Level", value=f'{REPLY_EMOTE}{data["account_level"]}', inline=False)
				embed.add_field(name ="Name", value=f'{REPLY_EMOTE}{data["name"]}', inline=False)
				embed.add_field(name ="Tag", value=f'{REPLY_EMOTE}{data["tag"]}')
				embed.add_field(name ="PUUID", value=f'{REPLY_EMOTE}{data["puuid"]}', inline=False)

				embed.set_footer(text="🟢 Linked")
				embed.set_image(url=data["image"])
				embed.set_author(name=data["name"],icon_url=data["thumbnail"])
				embed.set_thumbnail(url=f"https://raw.githubusercontent.com/typhonshambo/Valorant-server-stat-bot/main/assets/valorantRankImg/{rank}.png")
				
				view = discord.ui.View()
				view.add_item(discord.ui.Button(label='Support Server', url='https://discord.gg/m5mSyTV7RR', style=discord.ButtonStyle.url, emoji=emojidata["support"]))
				view.add_item(discord.ui.Button(label='Vote', url='https://top.gg/bot/864451929346539530/vote', style=discord.ButtonStyle.url, emoji=emojidata["vote"]))
				
				await ctx.respond(embed=embed, view=view)
			
			
			
			except:

				embed = discord.Embed(
					color = discord.Colour.random(),
					description = f"""
					You have not linked your account yet. 
					please link your account first to unlink it.
					user `/link` to do it now.
					"""
				)
				await ctx.respond(embed=embed)

def setup(bot):
	bot.add_cog(slash_profile(bot))