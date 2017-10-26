"""
Read LICENSE file
"""
import logging
from discord.ext import commands
import discord
from .config import initConfig
import os

class CustomContext(commands.Context):
	async def send_help(self):
		command = self.invoked_subcommand or self.command
		pages = await self.bot.formatter.format_help_for(self, command)
		ret = []
		for page in pages:
			ret.append(await self.send(page))
		return ret

# I'll just make it an auto sharded bot, in case someone is stupid enough to add this bot to 2500 servers
class Bot(commands.AutoShardedBot):
	def __init__(self, *args, **kwargs):
		self.config = initConfig()
		self.logger = logging.getLogger("PartnersBot")
		super(Bot, self).__init__(command_prefix=self.config.get('command_prefix'), *args, **kwargs)
		self.description = "An instance of JustMaffie's Partnerships Discord Bot"

	async def get_context(self, message, *, cls=CustomContext):
		return await super().get_context(message, cls=cls)

	def load_extension(self, name):
		self.logger.info(f'LOADING EXTENSION {name}')
		if not name.startswith("modules."):
			name = f"modules.{name}"
		return super().load_extension(name)

	def unload_extension(self, name):
		self.logger.info(f'UNLOADING EXTENSION {name}')
		if not name.startswith("modules."):
			name = f"modules.{name}"
		return super().unload_extension(name)

	def load_all_extensions(self):
		_modules = [os.path.splitext(x)[0] for x in os.listdir("modules")]
		modules = []
		for module in _modules:
			if not module in ['__pycache__', '__init__']:
				if not module.startswith("_"):
					modules.append(f"modules.{module}")

		for module in modules:
			self.load_extension(module)

	def run(self):
		super().run(self.config.get("token"))

def make_bot(*args, **kwargs):
	bot = Bot(*args, **kwargs)
	bot.load_all_extensions()

	@bot.event
	async def on_command_error(ctx, error):
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send_help()
		elif isinstance(error, commands.BadArgument):
			await ctx.send_help()
		elif isinstance(error, commands.CommandInvokeError):
			message = f"Error in command '{ctx.command.qualified_name}'.\n{error}"
			await ctx.send(f"```{message}```")
		elif isinstance(error, commands.CommandNotFound):
			pass
		elif isinstance(error, commands.CheckFailure):
			pass
		elif isinstance(error, commands.NoPrivateMessage):
			pass
		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send("This command is on cooldown. "
						   "Try again in {:.2f}s"
						   "".format(error.retry_after))
		else:
			log.exception(type(error).__name__, exc_info=error)

	return bot