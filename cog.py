from discord.ext import commands

from api.bot import PluginBot

class BotCog(commands.Cog):
    def __init__(self, bot: PluginBot):
        self.bot = bot
        self.settings: dict = self.bot.settings(self)
        super().__init__()
