from discord.ext import commands
import discord

class Help(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=0x47A7FF)
        prefix = self.context.clean_prefix
        embed.description = f"Do `{prefix}help <command>` for more help of the command.\nFor example: `{prefix}help play`\n\nCapitalizations are ignored.\n"
        for cog, commands in mapping.items():
            command_signatures = []

            for c in commands:
                signature = f'{prefix}`' + self.get_command_signature(c)[1:].replace(" ", '` ', 1)
                command_signatures.append(signature)

            cog_name = getattr(cog, "qualified_name", "No Category")
            embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        embed.set_footer(text='[argument] are optional, <argument> are required', icon_url = self.context.bot.user.display_avatar.url)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command) , color=0x47A7FF)
        if command.description:
            embed.description = command.description
        if alias := command.aliases:
            alias = '`' + "`, `".join(alias) + '`'
            embed.add_field(name="Aliases", value=alias, inline=False)

        embed.set_footer(text='[argument] are optional, <argument> are required', icon_url = self.context.bot.user.display_avatar.url)
        channel = self.get_destination()
        await channel.send(embed=embed)