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

with open ('././config/config.json', 'r') as f:
	topgg_data = json.load(f)
	topgg_botid = topgg_data["topgg_botid"]
	togg_token = topgg_data["topgg_token"]

def accountData(name, tagline):
		
	r  = requests.get(f'https://api.henrikdev.xyz/valorant/v1/account/{name}/{tagline}', headers=headers)
	data = r.json()


	puuid = data['data']['puuid']
	region = data['data']['region']
	username = data['data']['name']
	tag = data['data']['tag']

	return puuid, region, username, tag

def voteCheck(userId):
	Authorization = {
		"Authorization" : togg_token
	}
	r = requests.get(f"https://top.gg/api/bots/{topgg_botid}/check?userId={userId}", headers=Authorization)
	data = r.json()
	print(data)
	voteData = data["voted"]

	if voteData == 0:
		return False
	else:
		return True
	
class slash_acclink(commands.Cog):
	def __init__(self, bot):
			self.bot = bot

	@commands.slash_command(description="Link to your Valorant account")
	async def link(
		self,
		ctx,
		username: Option(str, "Enter your ingame username", required=True),
		tagline: Option(str, "Enter your ingame tag", required=True),
	):
		await ctx.response.defer()

		voted = voteCheck(ctx.author.id)
		
		if voted == True:
			try:

				author_id = str(ctx.author.id)
				user = await self.bot.pg_con.fetchrow("SELECT * FROM acclink WHERE userid = $1", author_id)
				if not user:
					
					puuid , region, user_id, tag = accountData(username, tagline)
					

					await self.bot.pg_con.execute("INSERT INTO acclink (userid, name, tagline, puuid, region) VALUES ($1, $2, $3, $4, $5)", author_id, user_id, tag, str(puuid), str(region))
					embed = discord.Embed(
						color = discord.Color.random(),
						description="Successfully linked"
					)
					await ctx.respond(embed=embed)

				if user:
						
					puuid , region, user_id, tag = accountData(username, tagline)
					await self.bot.pg_con.execute("UPDATE acclink SET name = $1, tagline = $2, puuid=$3, region=$4  WHERE userid = $5",user_id, tag,str(puuid), str(region), author_id)
					embed = discord.Embed(
						color = discord.Color.random(),
						description="Successfully linked"
					)
					await ctx.respond(embed=embed)

			except:

				view = discord.ui.View()
				view.add_item(discord.ui.Button(label='Support Server', url='https://discord.gg/m5mSyTV7RR', style=discord.ButtonStyle.url))
				view.add_item(discord.ui.Button(label='Vote', url='https://top.gg/bot/864451929346539530/vote', style=discord.ButtonStyle.url))
				
				embed = discord.Embed(
					color = discord.Color.red(),
					description="Some error occured"
				)
				await ctx.respond(
					embed=embed,
					view=view
				)

		else:
			embed = discord.Embed(
				color = discord.Color.red(),
			)
			embed.add_field(name="🔒 Command Locked", value="> Vote for the BOT to unlock this command! Just click the BIG BUTTON below")
			view = discord.ui.View()
			view.add_item(discord.ui.Button(label='Vote', url='https://top.gg/bot/864451929346539530/vote', style=discord.ButtonStyle.url, emoji=emojidata["vote"]))
			await ctx.respond(embed=embed, view=view)
	
	
	@commands.slash_command(description="UnLink to your Valorant account")
	async def unlink(
		self,
		ctx,
	):
		await ctx.response.defer()
		author_id = str(ctx.author.id)
		user = await self.bot.pg_con.fetchrow("SELECT * FROM acclink WHERE userid = $1", author_id)
		
		try: 
			if not user:
				embed = discord.Embed(
					color = discord.Colour.random(),
					description = f"""
					You have not linked your account yet. 
					please link your account first to unlink it.
					user `/link` to do it now. 
					"""
				)
				await ctx.respond(embed=embed)

			if user:
				await self.bot.pg_con.fetchval(
					"DELETE FROM acclink WHERE userid = $1", 
					author_id
				)
				embed = discord.Embed(
						color = discord.Colour.random(),
						description="Successfully unlinked"
				)
				await ctx.respond(embed=embed)
		except:
			embed = discord.Embed(
				color = discord.Color.red(),
				description="Some error occured"
			)
			await ctx.respond(embed=embed)


def setup(bot):
	bot.add_cog(slash_acclink(bot))