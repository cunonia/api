from discord.ext import commands


class BotCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings: dict = self.bot.settings(self)
        super().__init__()
