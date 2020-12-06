from discord.ext import commands


class BotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
