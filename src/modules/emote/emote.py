from io import BytesIO
import nextcord
from nextcord.ext import commands
from PIL import Image


class EmoteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="emote", description="Enlarges the specified custom server emoji.")
    async def emote(self, interaction: nextcord.Interaction, emoji_name):
        all_emoji = await interaction.guild.fetch_emojis()
        emoji_url = ""
        for emoji in all_emoji:
            if emoji.name.replace(":", "").lower() == emoji_name.lower():
                emoji_url = emoji.url
        if not emoji_url:
            await interaction.send(
                "This server doesn't have an emoji called `" + str(emoji_name) + "`.",
                ephemeral=True,
            )
            return
        async with self.bot.aiohttp_session.get(emoji_url) as resp:
            if resp.status != 200:
                await interaction.send(
                    "Sorry, something went wrong while retrieving the custom emoji.", ephemeral=True
                )
                return
            image = Image.open(BytesIO(await resp.read()))
        new_size = (int(image.width * 3), int(image.height * 3))
        image = image.resize(new_size, resample=Image.LANCZOS)
        with BytesIO() as image_binary:
            image.save(image_binary, "PNG")
            image_binary.seek(0)
            await interaction.response.send_message(
                file=nextcord.File(fp=image_binary, filename="lemote.png")
            )

    @emote.on_autocomplete("emoji_name")
    async def autocomplete_emote(self, interaction: nextcord.Interaction, emoji_name):
        all_emoji = await interaction.guild.fetch_emojis()
        emoji_names = []
        for emoji in all_emoji:
            emoji_names.append(emoji.name.replace(":", "").lower())
        if not emoji_name:
            await interaction.response.send_autocomplete(emoji_names[0:24])
            return
        matching_emoji = []
        for emoji in all_emoji:
            if (emoji.name.replace(":", "").lower()).startswith(emoji_name):
                matching_emoji.append(emoji.name.replace(":", "").lower())
        await interaction.response.send_autocomplete(matching_emoji[0:24])


def setup(bot):
    bot.add_cog(EmoteCog(bot))
