from discord.ext import commands


class BotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = self.bot.settings(self)
        super().__init__()
