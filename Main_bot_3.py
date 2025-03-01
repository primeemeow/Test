# COPYRIGHT (c) TheHolyOneZ 2025
#
# IMPORTANT: This copyright notice and all associated text must remain intact.
# It is strictly prohibited to:
# - Remove this notice
# - Modify this notice
# - Edit this notice
# - Obfuscate this notice
# - Delete any part of this notice
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.




from discord import ButtonStyle
from datetime import datetime, timedelta, timezone
import sqlite3
from typing import Optional, Dict, List, Tuple
import io
import platform
import discord
from discord.ext import commands
import asyncio
import random
import time
import logging
import os
from dotenv import load_dotenv
import json
import aiohttp
import copy

load_dotenv()
ZygnalBot_Version = "V7.3.4 | BETA"
class ZygnalBot(commands.Bot):
    def __init__(self):
        command_prefix = os.getenv('CMD_PREFIX', '!')
        
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.all(),
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="⚡ Server Protection"
            ),
            help_command=None
        )
        self.webhook_logger = None
        self.ticket_counter = 0
        self.start_time = time.time()
        self.mod_logs = {}
        self.warning_system = {}
        self._cached_messages = {}
        self.auto_mod_config = {
            'caps_threshold': 0.7,
            'spam_threshold': 5,
            'spam_interval': 5,
            'banned_words': set(),
            'link_whitelist': set()
        }

    async def setup_cogs(self):
        await self.add_cog(CommandErrorHandler(self))
        await self.add_cog(ModerationCommands(self))
        await self.add_cog(TicketSystem(self))
        await self.add_cog(ServerManagement(self))
        await self.add_cog(ServerInfo(self))
        await self.add_cog(HelpSystem(self))
        await self.add_cog(AutoMod(self))
        await self.add_cog(WelcomeSystem(self))
        await self.add_cog(RoleManager(self))
        await self.add_cog(UserTracker(self))
        await self.add_cog(BackupSystem(self))
        await self.add_cog(Config(self))
        await self.add_cog(OwnerOnly(self))
        await self.add_cog(MinigamesCog(self))
        await self.add_cog(Analytics(self))
        await self.add_cog(AdvancedInviteTracker(self))
        await self.add_cog(Snipe(self))
        await self.add_cog(ReminderSystem(self))
        await self.add_cog(MessagePurge(self))
        await self.add_cog(CustomLogging(self))
        await self.add_cog(LevelingSystem(self))
        await self.add_cog(MuteSystem(self))
        await self.add_cog(VerificationSystem(self))
        await self.add_cog(BotVerificationSystem(self))
        await self.add_cog(RatingSystem(self))


    async def setup_hook(self):
        await self.setup_cogs()
        await self.tree.sync()

    async def on_ready(self):
        self.webhook_logger = WebhookLogger(self)
        print(f'🚀 {self.user} The Owl is Online!')
        await self.setup_status_task()

    async def setup_status_task(self):
        while True:
            animations = [
                ("watching", "⚡ Protection 🔒"),
                ("watching", "Get ZygnalBot discord.me/thezbot"),
                ("watching", "⚡ Protection ⚡"),

            ]
            
            for activity_type, message in animations:
                activity = discord.Activity(
                    type=getattr(discord.ActivityType, activity_type),
                    name=message
                )
                await self.change_presence(activity=activity)
                await asyncio.sleep(0.5)
                
            stats_messages = [
                ("playing", f"protecting {len(self.guilds)} servers ⚡"),
                ("listening", "Get ZygnalBot discord.me/thezbot"),
                ("watching", f"{sum(g.member_count for g in self.guilds)} members 👥"),
                ("watching", "⚡ 24/7 Protection Active 🔒")
            ]
            
            for activity_type, message in stats_messages:
                activity = discord.Activity(
                    type=getattr(discord.ActivityType, activity_type),
                    name=message
                )
                await self.change_presence(activity=activity)
                await asyncio.sleep(5)

    async def on_message(self, message):
        if self.webhook_logger:
            await self.webhook_logger.log_message(message)
        await self.process_commands(message)

    async def on_command(self, ctx):
        if self.webhook_logger:
            await self.webhook_logger.log_command(ctx)

bot = ZygnalBot()


class RatingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ratings_data = {}  
        self.load_ratings()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def exportrating(self, ctx):
        await ctx.message.delete()
        try:
            export_data = json.dumps(self.ratings_data, indent=4)
            with open('rating_backup.json', 'w') as f:
                f.write(export_data)
            await ctx.send("✨ Here's your rating system backup!", file=discord.File('rating_backup.json'), ephemeral=True)
            os.remove('rating_backup.json')
        except Exception as e:
            await ctx.send(f"✨ Export failed: {str(e)}", ephemeral=True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def importrating(self, ctx):
        await ctx.message.delete()
        if not ctx.message.attachments:
            return await ctx.send("✨ Please attach a rating backup file!", ephemeral=True)
        try:
            attachment = ctx.message.attachments[0]
            if not attachment.filename.endswith('.json'):
                return await ctx.send("✨ Please provide a JSON file!", ephemeral=True)
            content = await attachment.read()
            import_data = json.loads(content)
            self.ratings_data = import_data
            self.save_ratings()
            await ctx.send("✨ Rating system data imported successfully!", ephemeral=True)
        except json.JSONDecodeError:
            await ctx.send("✨ Invalid JSON file format!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"✨ Import failed: {str(e)}", ephemeral=True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ratingsetup(self, ctx):
        """Setup a beautiful rating system"""
        button = discord.ui.Button(label="Setup Rating System", style=discord.ButtonStyle.primary, emoji="✨")
            
        async def button_callback(interaction):
            modal = self.RatingSetup(self)
            await interaction.response.send_modal(modal)
            
        button.callback = button_callback
        view = discord.ui.View()
        view.add_item(button)
            
        await ctx.message.delete()  
        await ctx.send("Click below to create your rating panel! ✨", view=view, ephemeral=True)

    def load_ratings(self):
        try:
            with open('ratings.json', 'r') as f:
                self.ratings_data = json.load(f)
        except FileNotFoundError:
            self.ratings_data = {}

    def save_ratings(self):
        with open('ratings.json', 'w') as f:
            json.dump(self.ratings_data, f, indent=4)


    class DeleteRatingModal(discord.ui.Modal):
        def __init__(self, cog):
            super().__init__(title="Delete Rating Panel")
            self.cog = cog
            self.add_item(discord.ui.TextInput(
                label="Panel ID",
                placeholder="Enter the panel ID to delete"
            ))

        async def on_submit(self, interaction):
            panel_id = self.children[0].value
            if panel_id in self.cog.ratings_data:
             
                for channel in interaction.guild.text_channels:
                    try:
                        message = await channel.fetch_message(int(panel_id))
                        if message:
                            await message.delete()
                            break
                    except:
                        continue
                        
                del self.cog.ratings_data[panel_id]
                self.cog.save_ratings()
                await interaction.response.send_message(f"✨ Rating panel {panel_id} deleted!", ephemeral=True)
            else:
                await interaction.response.send_message("✨ Panel ID not found!", ephemeral=True)

    class EditRatingModal(discord.ui.Modal):
        def __init__(self, cog):
            super().__init__(title="Edit Rating Panel")
            self.cog = cog
            self.add_item(discord.ui.TextInput(
                label="Panel ID",
                placeholder="Enter the panel ID to edit"
            ))
            self.add_item(discord.ui.TextInput(
                label="New Title",
                placeholder="Enter new title (leave empty to keep current)",
                required=False
            ))
            self.add_item(discord.ui.TextInput(
                label="New Description",
                placeholder="Enter new description (leave empty to keep current)",
                required=False
            ))

        async def on_submit(self, interaction):
            panel_id = self.children[0].value
            new_title = self.children[1].value
            new_desc = self.children[2].value

            if panel_id not in self.cog.ratings_data:
                return await interaction.response.send_message("✨ Panel ID not found!", ephemeral=True)

            try:
                channel_id = None
                message = None
                for channel in interaction.guild.text_channels:
                    try:
                        message = await channel.fetch_message(int(panel_id))
                        if message:
                            break
                    except:
                        continue

                if message:
                    embed = message.embeds[0]
                    if new_title:
                        embed.title = new_title
                    if new_desc:
                        current_desc = embed.description.split("**Stats:**")
                        embed.description = f"{new_desc}\n\n**Stats:**{current_desc[1]}"
                    
                    await message.edit(embed=embed)
                    await interaction.response.send_message("✨ Rating panel updated!", ephemeral=True)
                else:
                    await interaction.response.send_message("✨ Couldn't find the rating panel message!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"✨ Error updating panel: {str(e)}", ephemeral=True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def seerating(self, ctx):
        await ctx.message.delete()
        if not self.ratings_data:
            return await ctx.send("✨ No rating panels exist yet!", ephemeral=True)

        embed = discord.Embed(
            title="📊 Rating Panels Overview",
            color=discord.Color.blue()
        )

        for message_id, ratings in self.ratings_data.items():
            total_votes = len(ratings)
            avg_rating = sum(float(r) for r in ratings.values()) / total_votes if total_votes > 0 else 0
            embed.add_field(
                name=f"ID: {message_id}",
                value=f"Votes: {total_votes} | Average: {avg_rating:.2f}",
                inline=False
            )

        view = discord.ui.View()
        delete_btn = discord.ui.Button(label="Delete Panel", style=discord.ButtonStyle.danger, emoji="🗑️")
        edit_btn = discord.ui.Button(label="Edit Panel", style=discord.ButtonStyle.primary, emoji="✏️")
        
        async def delete_callback(interaction):
            modal = self.DeleteRatingModal(self)
            await interaction.response.send_modal(modal)
            
        async def edit_callback(interaction):
            modal = self.EditRatingModal(self)
            await interaction.response.send_modal(modal)
            
        delete_btn.callback = delete_callback
        edit_btn.callback = edit_callback
        view.add_item(delete_btn)
        view.add_item(edit_btn)
        
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ratingrefresh(self, ctx, panel_id: str):
        await ctx.message.delete()
        if panel_id not in self.ratings_data:
            return await ctx.send("✨ Rating panel not found!", ephemeral=True)

        channel_id = None
        message = None
        
        for channel in ctx.guild.text_channels:
            try:
                message = await channel.fetch_message(int(panel_id))
                if message:
                    break
            except:
                continue

        if not message:
            return await ctx.send("✨ Couldn't find the rating panel message!")

        ratings = self.ratings_data[panel_id]
        avg_rating = sum(float(r) for r in ratings.values()) / len(ratings)
        
        embed = message.embeds[0]
        embed.description = f"{embed.description.split('**Stats:**')[0]}\n\n**Stats:**\n• Average: {avg_rating:.2f}\n• Total Ratings: {len(ratings)}"
        
        await message.edit(embed=embed)
        await ctx.send("✨ Rating panel refreshed successfully!")


    class RatingView(discord.ui.View):
        def __init__(self, title, description, button_color, embed_color, rating_type, channel_id, cog):
            super().__init__(timeout=None)
            self.title = title
            self.description = description
            
            color_map = {
                'red': discord.ButtonStyle.danger,
                'green': discord.ButtonStyle.success,
                'blue': discord.ButtonStyle.primary,
                'gray': discord.ButtonStyle.secondary,
                'blurple': discord.ButtonStyle.primary,
                'danger': discord.ButtonStyle.danger,
                'success': discord.ButtonStyle.success,
                'primary': discord.ButtonStyle.primary,
                'secondary': discord.ButtonStyle.secondary
            }
            self.button_color = color_map.get(button_color.lower(), discord.ButtonStyle.secondary)
            self.embed_color = embed_color
            self.rating_type = rating_type
            self.channel_id = channel_id
            self.cog = cog

            if self.rating_type == "stars":
                star_emojis = ["⭐", "🌟", "✨", "💫", "⚡"]
                for i, emoji in enumerate(star_emojis, 1):
                    btn = discord.ui.Button(
                        label=f"{i}",
                        emoji=emoji,
                        style=self.button_color,
                        custom_id=f"rate_{i}",
                        row=0
                    )
                    btn.callback = self.rate_callback
                    self.add_item(btn)
            
            elif self.rating_type == "numbers":
                for i in range(1, 11):
                    btn = discord.ui.Button(
                        label=f"{i}",
                        style=self.button_color,
                        custom_id=f"rate_{i}",
                        row=(i-1) // 5
                    )
                    btn.callback = self.rate_callback
                    self.add_item(btn)
            
            elif self.rating_type == "percent":
                emojis = ["💔", "❤️‍🩹", "💝", "💖", "💗"]
                for p, emoji in zip([0, 25, 50, 75, 100], emojis):
                    btn = discord.ui.Button(
                        label=f"{p}%",
                        emoji=emoji,
                        style=self.button_color,
                        custom_id=f"rate_{p}",
                        row=0
                    )
                    btn.callback = self.rate_callback
                    self.add_item(btn)

            view_ratings = discord.ui.Button(
                label="Statistics",
                emoji="📊",
                style=discord.ButtonStyle.secondary,
                custom_id="view_ratings",
                row=2
            )
            view_ratings.callback = self.view_ratings_callback
            
            refresh = discord.ui.Button(
                label="Refresh",
                emoji="🔄",
                style=discord.ButtonStyle.secondary,
                custom_id="refresh",
                row=2
            )
            refresh.callback = self.refresh_callback
            
            self.add_item(view_ratings)
            self.add_item(refresh)


        async def create_stats_embed(self, ratings, title="📊 Rating Statistics"):
            avg_rating = sum(float(r) for r in ratings) / len(ratings)
            rating_counts = {}
            for r in ratings:
                rating_counts[float(r)] = rating_counts.get(float(r), 0) + 1
            
            max_count = max(rating_counts.values())
            distribution = []
            for r, count in sorted(rating_counts.items()):
                bar_length = int((count / max_count) * 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                percentage = (count/len(ratings))*100
                
                if self.rating_type == "stars":
                    rating_display = "⭐" * int(r)
                elif self.rating_type == "percent":
                    rating_display = f"{int(r)}% {'💖' if r == 100 else '💝' if r >= 75 else '❤️' if r >= 50 else '💔'}"
                else:
                    rating_display = f"Rating {r}"
                    
                distribution.append(f"{rating_display}\n`{bar}` {count} votes ({percentage:.1f}%)")

            embed = discord.Embed(
                title=title,
                description="\n\n".join(distribution),
                color=self.embed_color
            )
            embed.add_field(name="Average Rating", value=f"📊 {avg_rating:.2f}", inline=True)
            embed.add_field(name="Total Votes", value=f"📈 {len(ratings)}", inline=True)
            return embed

        async def rate_callback(self, interaction: discord.Interaction):
            rating = interaction.data['custom_id'].split("_")[1]
            message_id = str(interaction.message.id)
            user_id = str(interaction.user.id)
            
            if message_id in self.cog.ratings_data and user_id in self.cog.ratings_data[message_id]:
                return await interaction.response.send_message("You've already rated this! ✨", ephemeral=True)
            
            if message_id not in self.cog.ratings_data:
                self.cog.ratings_data[message_id] = {}
            
            self.cog.ratings_data[message_id][user_id] = rating
            self.cog.save_ratings()

            embed = discord.Embed(
                title=self.title,
                description=f"{self.description}\n\n**Stats:**",
                color=self.embed_color
            )
            
            ratings = self.cog.ratings_data[message_id].values()
            avg_rating = sum(float(r) for r in ratings) / len(ratings)
            
            rating_counts = {}
            for r in ratings:
                rating_counts[float(r)] = rating_counts.get(float(r), 0) + 1
            
            embed.add_field(name="Average Rating", value=f"📊 {avg_rating:.2f}", inline=True)
            embed.add_field(name="Total Votes", value=f"📈 {len(ratings)}", inline=True)
            
            await interaction.message.edit(embed=embed, view=self)
            
            rating_display = f"{'⭐' * int(rating)}" if self.rating_type == "stars" else f"{rating}{'%' if self.rating_type == 'percent' else ''}"
            await interaction.response.send_message(f"Rating submitted: {rating_display} ✨", ephemeral=True)


        async def view_ratings_callback(self, interaction: discord.Interaction):
            message_id = str(interaction.message.id)
            if message_id not in self.cog.ratings_data:
                return await interaction.response.send_message("No ratings yet! Be the first to rate! ✨", ephemeral=True)
            
            embed = await self.create_stats_embed(self.cog.ratings_data[message_id].values(), "📊 Detailed Rating Distribution")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        async def refresh_callback(self, interaction: discord.Interaction):
            if not interaction.user.guild_permissions.administrator:
                return await interaction.response.send_message("Only administrators can refresh! ✨", ephemeral=True)
            
            message_id = str(interaction.message.id)
            if message_id not in self.cog.ratings_data:
                return await interaction.response.send_message("No ratings to refresh! ✨", ephemeral=True)
            
            embed = await self.create_stats_embed(self.cog.ratings_data[message_id].values())
            await interaction.message.edit(embed=embed, view=self)
            await interaction.response.send_message("Rating panel refreshed! ✨", ephemeral=True)

    class RatingSetup(discord.ui.Modal):
        def __init__(self, cog, **defaults):
            super().__init__(title="✨ Rating System Setup")
            self.cog = cog
            self.add_item(discord.ui.TextInput(
                label="Title",
                placeholder="Enter your rating title",
                default=defaults.get('default_title', '')
            ))
            self.add_item(discord.ui.TextInput(
                label="Description",
                placeholder="Enter rating description",
                default=defaults.get('default_desc', '')
            ))
            self.add_item(discord.ui.TextInput(
                label="Button Color",
                placeholder="red/green/blue/blurple",
                default=defaults.get('default_color', '')
            ))
            self.add_item(discord.ui.TextInput(
                label="Embed Color (hex)",
                placeholder="#ff0000",
                default=defaults.get('default_embed', '')
            ))
            self.add_item(discord.ui.TextInput(
                label="Rating Type & Channel",
                placeholder="stars/numbers/percent #channel",
                default=f"{defaults.get('default_type', '')} {defaults.get('default_channel', '')}"
            ))

        async def on_submit(self, interaction: discord.Interaction):
            title = self.children[0].value
            description = self.children[1].value
            button_color = self.children[2].value.lower()
            embed_color = int(self.children[3].value.strip("#"), 16)
            
            rating_info = self.children[4].value.split()
            rating_type = rating_info[0].lower()
            channel_mention = rating_info[1] if len(rating_info) > 1 else None
            
            channel_id = int(channel_mention.strip('<#>')) if channel_mention else interaction.channel.id
            channel = interaction.guild.get_channel(channel_id)
            
            if not channel:
                return await interaction.response.send_message("Invalid channel! ❌", ephemeral=True)

            embed = discord.Embed(title=title, description=description, color=embed_color)
            view = self.cog.RatingView(title, description, button_color, embed_color, rating_type, channel_id, self.cog)
            
            await channel.send(embed=embed, view=view)
            if channel.id != interaction.channel.id:
                await interaction.response.send_message(f"Rating panel created in {channel.mention}! ✨", ephemeral=True)
            else:
                await interaction.response.send_message("Rating panel created! ✨", ephemeral=True)

def setup(bot):
    bot.add_cog(RatingSystem(bot))

class BotVerificationSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_whitelist = set(int(bot_id) for bot_id in os.getenv('WHITELISTED_BOTS', '').split(',') if bot_id)
        self.owner_id = int(os.getenv('BOT_OWNER_ID'))
        self.bot_log_channels = {}
        self.whitelist_attempts = {}
        self.MAX_ATTEMPTS = 5
        self.ATTEMPT_RESET = 300  # 5 minutes

    def validate_bot_id(self, bot_id: int) -> bool:
        if not (17 <= len(str(bot_id)) <= 20):
            return False
        discord_epoch = 1420070400000
        timestamp = ((bot_id >> 22) + discord_epoch) / 1000
        return discord_epoch/1000 <= timestamp <= time.time() and bot_id != 0

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot and member.id not in self.bot_whitelist:
            try:
                await member.kick(reason="Bot not in whitelist")
                
                embed = discord.Embed(
                    title="🤖 Unauthorized Bot Detected",
                    description=(
                        f"**Bot:** {member.name} (`{member.id}`)\n"
                        f"**Action:** Kicked\n"
                        f"**Reason:** Not in whitelist\n"
                        f"**Guild:** {member.guild.name}\n"
                        f"**Time:** <t:{int(time.time())}:F>"
                    ),
                    color=discord.Color.red(),
                    timestamp=datetime.now(timezone.utc)
                )
                embed.set_footer(text=f"Security Event ID: {hex(member.id)}")
                
                if str(member.guild.id) in self.bot_log_channels:
                    channel_id = self.bot_log_channels[str(member.guild.id)]
                    channel = member.guild.get_channel(channel_id)
                    if channel:
                        await channel.send(embed=embed)
                        
            except discord.Forbidden:
                if str(member.guild.id) in self.bot_log_channels:
                    channel = member.guild.get_channel(self.bot_log_channels[str(member.guild.id)])
                    if channel:
                        await channel.send(
                            embed=discord.Embed(
                                title="⚠️ Permission Error",
                                description="Failed to kick unauthorized bot due to missing permissions",
                                color=discord.Color.orange()
                            )
                        )

    @commands.command(name="whitelist_bot")
    async def whitelist_bot(self, ctx, bot_id: int):
        if ctx.author.id != self.owner_id:
            return await ctx.send(
                embed=discord.Embed(
                    title="❌ Access Denied",
                    description="Only the bot owner can use this command",
                    color=discord.Color.red()
                )
            )

        current_time = time.time()
        if ctx.author.id in self.whitelist_attempts:
            attempts, last_attempt = self.whitelist_attempts[ctx.author.id]
            if current_time - last_attempt < self.ATTEMPT_RESET:
                if attempts >= self.MAX_ATTEMPTS:
                    return await ctx.send(
                        embed=discord.Embed(
                            title="🚫 Rate Limited",
                            description=f"Please wait {int(self.ATTEMPT_RESET - (current_time - last_attempt))} seconds",
                            color=discord.Color.red()
                        )
                    )
                self.whitelist_attempts[ctx.author.id] = (attempts + 1, current_time)
            else:
                self.whitelist_attempts[ctx.author.id] = (1, current_time)
        else:
            self.whitelist_attempts[ctx.author.id] = (1, current_time)

        if not self.validate_bot_id(bot_id):
            return await ctx.send(
                embed=discord.Embed(
                    title="❌ Invalid Bot ID",
                    description="The provided ID is not a valid Discord bot ID",
                    color=discord.Color.red()
                )
            )

        try:
            bot_user = await self.bot.fetch_user(bot_id)
            if not bot_user.bot:
                raise ValueError("Provided ID belongs to a user, not a bot")
            
            self.bot_whitelist.add(bot_id)
            await ctx.send(
                embed=discord.Embed(
                    title="✅ Bot Whitelisted",
                    description=f"**Bot:** {bot_user.name}\n**ID:** `{bot_id}`\n**Added by:** {ctx.author.mention}",
                    color=discord.Color.green()
                ).set_thumbnail(url=bot_user.display_avatar.url)
            )
            
        except (discord.NotFound, discord.HTTPException, ValueError) as e:
            await ctx.send(
                embed=discord.Embed(
                    title="❌ Verification Failed",
                    description=str(e),
                    color=discord.Color.red()
                )
            )

    @commands.command(name="botlogs")
    @commands.has_permissions(administrator=True)
    async def set_bot_logs(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for unauthorized bot join logs"""
        if channel is None:
            if str(ctx.guild.id) in self.bot_log_channels:
                del self.bot_log_channels[str(ctx.guild.id)]
                embed = discord.Embed(
                    title="🤖 Bot Logs Disabled",
                    description="Bot join logging has been turned off.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="ℹ️ No Channel Set",
                    description="Please specify a channel to enable bot join logging.",
                    color=discord.Color.blue()
                )
        else:
            self.bot_log_channels[str(ctx.guild.id)] = channel.id
            embed = discord.Embed(
                title="🤖 Bot Logs Channel Set",
                description=f"Unauthorized bot joins will be logged in {channel.mention}",
                color=discord.Color.green()
            )
        
        await ctx.send(embed=embed)

    @commands.command(name="whitelisted")
    @commands.has_permissions(administrator=True)
    async def list_whitelisted(self, ctx):
        """List all whitelisted bots"""
        if not self.bot_whitelist:
            return await ctx.send(
                embed=discord.Embed(
                    title="📝 Whitelisted Bots",
                    description="No bots are currently whitelisted",
                    color=discord.Color.blue()
                )
            )

        whitelisted_bots = []
        for bot_id in self.bot_whitelist:
            try:
                bot_user = await self.bot.fetch_user(bot_id)
                whitelisted_bots.append(f"• {bot_user.name} (`{bot_id}`)")
            except:
                whitelisted_bots.append(f"• Unknown Bot (`{bot_id}`)")

        await ctx.send(
            embed=discord.Embed(
                title="📝 Whitelisted Bots",
                description="\n".join(whitelisted_bots),
                color=discord.Color.blue()
            )
        )

def setup(bot):
    bot.add_cog(BotVerificationSystem(bot))


class VerificationSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification_levels = {
            "easy": {
                "timeout": 300,
                "requirements": ["VERIFIED_EMAIL"],
                "emoji": "🟢",
                "description": "Basic security level",
                "min_account_age": 1,
                "min_avatar": False
            },
            "medium": {
                "timeout": 600,
                "requirements": ["VERIFIED_EMAIL", "VERIFIED_PHONE"],
                "emoji": "🟡",
                "description": "Enhanced security level",
                "min_account_age": 3,
                "min_avatar": True
            },
            "hard": {
                "timeout": 900,
                "requirements": ["VERIFIED_EMAIL", "VERIFIED_PHONE", "MFA_ENABLED"],
                "emoji": "🔴",
                "description": "Maximum security level",
                "min_account_age": 7,
                "min_avatar": True
            }
        }
        self.guild_settings = {}
        self.pending_verifications = {}
        self.autorole_dict = {}
        self.verification_logs = {}
        self.log_channels = {}
        self.save_data()

    def save_data(self):
   
        self.guild_settings = {
            guild_id: {
                "verification_level": self.verification_levels,
                "autorole": self.autorole_dict.get(guild_id),
                "log_channel": self.log_channels.get(str(guild_id))
            }
            for guild_id in self.bot.guilds
        }

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def verify(self, ctx, level: str = None, timeout: int = None):
        """Advanced verification system configuration"""
        if not level:
            await self.show_verification_menu(ctx)
            return
        await self.set_verification_level(ctx, level, timeout)

    @verify.command(name="stats")
    @commands.has_permissions(administrator=True)
    async def verification_stats(self, ctx):
        """Show verification statistics"""
        stats = self.verification_logs.get(ctx.guild.id, {})
        embed = discord.Embed(
            title="📊 Verification Statistics",
            color=discord.Color.blue()
        )
        embed.add_field(name="Total Attempts", value=stats.get("total", 0))
        embed.add_field(name="Successful", value=stats.get("success", 0))
        embed.add_field(name="Failed", value=stats.get("failed", 0))
        await ctx.send(embed=embed)

    @commands.command(name="verifychannel")
    @commands.has_permissions(administrator=True)
    async def set_verify_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the verification logging channel"""
        if channel is None:
            if str(ctx.guild.id) in self.log_channels:
                del self.log_channels[str(ctx.guild.id)]
                embed = discord.Embed(
                    title="📝 Verification Logging Disabled",
                    description="Verification logging has been turned off.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="ℹ️ No Channel Set",
                    description="Please specify a channel to log verifications.",
                    color=discord.Color.blue()
                )
        else:
            self.log_channels[str(ctx.guild.id)] = channel.id
            embed = discord.Embed(
                title="✅ Verification Channel Set",
                description=f"Verification attempts will be logged in {channel.mention}",
                color=discord.Color.green()
            )
        await ctx.send(embed=embed)
        self.save_data()

    async def show_verification_menu(self, ctx):
        embed = discord.Embed(
            title="🛡️ Advanced Verification System",
            description="Configure server security and verification settings",
            color=discord.Color.blue()
        )
        
        for level, data in self.verification_levels.items():
            requirements_text = [
                f"• Account Age: {data['min_account_age']} days",
                f"• Profile Picture: {'Required' if data['min_avatar'] else 'Optional'}"
            ]
            requirements_text.extend([f"• {req.replace('_', ' ').title()}" for req in data["requirements"]])
            
            embed.add_field(
                name=f"{data['emoji']} {level.title()} Mode",
                value=f"```\n{data['description']}\nTimeout: {data['timeout']}s\n\nRequirements:\n{chr(10).join(requirements_text)}```",
                inline=False
            )

        embed.add_field(
            name="⚙️ Command Center",
            value=(
                "🔐 **Security Setup**\n"
                "➜ `!verify <easy/medium/hard>`\n\n"
                "📊 **Statistics**\n"
                "➜ `!verify stats`\n\n"
                "📝 **Logging**\n"
                "➜ `!verifychannel #channel`\n\n"
                "⚡ **Auto-Role**\n"
                "➜ `!verificationrole @role`"
            ),
            inline=False
        )
        
        embed.set_footer(text="✨ Advanced Security System")
        await ctx.send(embed=embed)

    async def set_verification_level(self, ctx, level: str, timeout: int = None):
        level = level.lower()
        if level not in self.verification_levels:
            embed = discord.Embed(
                title="❌ Invalid Verification Level",
                description="Please choose: `easy`, `medium`, or `hard`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        guild_settings = {
            "level": level,
            "member_role": None,
            "timeout": timeout or self.verification_levels[level]["timeout"]
        }

        verification_role = discord.utils.get(ctx.guild.roles, name="✓ Verified")
        if not verification_role:
            verification_role = await ctx.guild.create_role(
                name="✓ Verified",
                color=discord.Color.brand_green(),
                permissions=discord.Permissions.none(),
                hoist=True,
                mentionable=False,
                reason="Verification system role"
            )
        guild_settings["member_role"] = verification_role.id

        self.pending_verifications[ctx.guild.id] = guild_settings
        self.save_data()

        embed = discord.Embed(
            title=f"{self.verification_levels[level]['emoji']} Verification System Configured",
            description=f"Level set to: **{level}**\n"
                       f"Timeout: **{guild_settings['timeout']} seconds**\n"
                       f"Verification Role: {verification_role.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def verificationrole(self, ctx, role: discord.Role = None):
        """Toggle automatic role assignment for newly verified members"""
        if role is None:
            if ctx.guild.id in self.autorole_dict:
                current_role = ctx.guild.get_role(self.autorole_dict[ctx.guild.id])
                embed = discord.Embed(
                    title="ℹ️ Verification Role Status",
                    description=f"Currently active for role: {current_role.mention if current_role else 'None'}",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="ℹ️ Verification Role Status",
                    description="Verification role is currently disabled",
                    color=discord.Color.blue()
                )
        else:
            if ctx.guild.id in self.autorole_dict and self.autorole_dict[ctx.guild.id] == role.id:
                del self.autorole_dict[ctx.guild.id]
                embed = discord.Embed(
                    title="🔄 Verification Role Disabled",
                    description=f"Automatic role assignment for {role.mention} has been disabled",
                    color=discord.Color.red()
                )
            else:
                self.autorole_dict[ctx.guild.id] = role.id
                embed = discord.Embed(
                    title="✅ Verification Role Enabled",
                    description=f"Newly verified members will receive the {role.mention} role",
                    color=discord.Color.green()
                )
        await ctx.send(embed=embed)

    async def log_verification_attempt(self, member, success: bool, reason: str = None):
        guild_id = str(member.guild.id)
        if guild_id not in self.log_channels:
            return

        channel = self.bot.get_channel(self.log_channels[guild_id])
        if not channel:
            return

        embed = discord.Embed(
            title="🔒 Verification Attempt",
            description=f"User: {member.mention} ({member.id})",
            color=discord.Color.green() if success else discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name="Status", value="✅ Passed" if success else "❌ Failed", inline=True)
        embed.add_field(name="Account Age", value=f"{(datetime.now(timezone.utc) - member.created_at).days} days", inline=True)
        
        if not success and reason:
            embed.add_field(name="Failure Reason", value=reason, inline=False)

        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"User ID: {member.id}")

        await channel.send(embed=embed)
        
        if not success:
            try:
                await member.kick(reason=f"Failed verification: {reason}")
            except discord.Forbidden:
                await channel.send(f"⚠️ Failed to kick {member.mention} - Missing permissions")


    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        if member.guild.id not in self.pending_verifications:
            return
            
        if member.bot:
            return

        settings = self.pending_verifications[member.guild.id]
        
        if not settings.get("level"):
            return
            
        level_data = self.verification_levels[settings["level"]]
        
        self.verification_logs.setdefault(member.guild.id, {})
        self.verification_logs[member.guild.id]["total"] = self.verification_logs[member.guild.id].get("total", 0) + 1

        account_age = (datetime.now(timezone.utc) - member.created_at).days
        if account_age < level_data["min_account_age"]:
            await self.handle_failed_verification(member, f"Account too new (minimum {level_data['min_account_age']} days required)")
            return

        if level_data["min_avatar"] and not member.avatar:
            await self.handle_failed_verification(member, "Profile picture required")
            return

        qualified = await self.check_requirements(member, level_data["requirements"])
        if not qualified:
            await self.handle_failed_verification(member, "Missing verification requirements")
            return

        await self.handle_successful_verification(member, settings)
        self.save_data()

    async def check_requirements(self, member, requirements):
   
    
        checks = {}
        
        if "VERIFIED_EMAIL" in requirements:
            checks["VERIFIED_EMAIL"] = True  
            
        if "VERIFIED_PHONE" in requirements:
            checks["VERIFIED_PHONE"] = member.guild.verification_level >= discord.VerificationLevel.high
            
        if "MFA_ENABLED" in requirements:
            checks["MFA_ENABLED"] = member.guild.mfa_level >= 1
        
        return all(checks.get(req, False) for req in requirements)


    async def handle_failed_verification(self, member, reason):
        self.verification_logs[member.guild.id]["failed"] = self.verification_logs[member.guild.id].get("failed", 0) + 1
        
        level_data = self.verification_levels[self.pending_verifications[member.guild.id]["level"]]
        
        embed = discord.Embed(
            title="❌ Verification Failed",
            description=(
                f"You don't meet {member.guild.name}'s verification requirements.\n\n"
                f"**Reason:** {reason}\n\n"
                "**Server Requirements:**\n"
                f"• Account Age: {level_data['min_account_age']} days\n"
                f"• Profile Picture: {'Required' if level_data['min_avatar'] else 'Optional'}\n"
                f"• Verified Email: {'Required' if 'VERIFIED_EMAIL' in level_data['requirements'] else 'Optional'}\n"
                f"• Verified Phone: {'Required' if 'VERIFIED_PHONE' in level_data['requirements'] else 'Optional'}\n"
                f"• 2FA Enabled: {'Required' if 'MFA_ENABLED' in level_data['requirements'] else 'Optional'}\n\n"
                "Please meet these requirements and try joining again!"
            ),
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
        
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass
        
        await self.log_verification_attempt(member, False, reason)
        await member.kick(reason=f"Failed verification: {reason}")

    async def handle_successful_verification(self, member, settings):
        self.verification_logs[member.guild.id]["success"] = self.verification_logs[member.guild.id].get("success", 0) + 1

        timeout_duration = timedelta(seconds=settings["timeout"])
        try:
            await member.timeout(timeout_duration, reason="Verification security cooldown")
        except discord.Forbidden:
            pass  

        member_role = member.guild.get_role(settings["member_role"])
        if member_role:
            await member.add_roles(member_role)

        if member.guild.id in self.autorole_dict:
            role = member.guild.get_role(self.autorole_dict[member.guild.id])
            if role:
                try:
                    await member.add_roles(role)
                except discord.Forbidden:
                    pass

        await self.log_verification_attempt(member, True)

def setup(bot):
    bot.add_cog(VerificationSystem(bot))

class LevelingSystem(commands.Cog):                         # FULLY FIXED
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = int(os.getenv('BOT_OWNER_ID'))
        self.user_data: Dict[int, Dict[int, Dict]] = {}  # {guild_id: {user_id: data}}
        self.roles: Dict[int, Dict[int, int]] = {}       # {guild_id: {level: role_id}}
        self.achievements: Dict[int, Dict[str, Dict]] = {}  # {guild_id: {name: data}}
        self.xp_decay_rate = 0.01
        self.xp_gain_range = (15, 25)
        self.xp_multipliers: Dict[int, Dict[int, float]] = {}  # {guild_id: {role_id: multiplier}}
        self.data_file = "leveling_data.json"
        self.leaderboard_channels: Dict[int, int] = {}    # {guild_id: channel_id}
        self.announcement_channels: Dict[int, int] = {}   # {guild_id: channel_id}
        self.load_data()
        self.bot.loop.create_task(self.update_leaderboard_task())
        self.bot.loop.create_task(self.xp_decay_task())

    def load_data(self):
        """Load user data, roles, and achievements from a JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                
                self.user_data = {
                    int(guild_id): {
                        int(user_id): user_data 
                        for user_id, user_data in guild_data.items()
                    } for guild_id, guild_data in data.get('user_data', {}).items()
                }
                self.roles = data.get('roles', {})
                self.achievements = data.get('achievements', {})
                self.xp_multipliers = data.get('xp_multipliers', {})
                self.leaderboard_channels = data.get('leaderboard_channels', {})
                self.announcement_channels = data.get('announcement_channels', {})

    def save_data(self):
            """Save user data, roles, and achievements to a JSON file."""
            
            cleaned_user_data = {}
            for guild_id, guild_data in self.user_data.items():
                cleaned_user_data[str(guild_id)] = {
                    str(user_id): user_data
                    for user_id, user_data in guild_data.items()
                }

            with open(self.data_file, 'w') as f:
                json.dump({
                    'user_data': cleaned_user_data,
                    'roles': self.roles,
                    'achievements': self.achievements,
                    'xp_multipliers': self.xp_multipliers,
                    'leaderboard_channels': self.leaderboard_channels,
                    'announcement_channels': self.announcement_channels
                }, f, indent=4)

    def calculate_level(self, xp: int) -> int:
        """Calculate the user's level based on their XP."""
        return int((xp / 100) ** 0.5)  # Level = sqrt(XP / 100)

    def xp_for_next_level(self, level: int) -> int:
        """Calculate the XP required for the next level."""
        return (level + 1) ** 2 * 100

    async def add_xp(self, user_id: int, guild_id: int):
        """Add XP to a user and handle level-ups."""
        
        xp_gain = random.randint(*self.xp_gain_range)
        
        multiplier = float(self.xp_multipliers.get(guild_id, {}).get(str(user_id), 1.0))
        if isinstance(multiplier, dict):
            multiplier = 1.0
        xp_gain = int(xp_gain * multiplier)

        if guild_id not in self.user_data:
            self.user_data[guild_id] = {}
        if user_id not in self.user_data[guild_id]:
            self.user_data[guild_id][user_id] = {'xp': 0, 'last_message': datetime.now().isoformat()}

        user_data = self.user_data[guild_id][user_id]

        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        if member:
            for role_id, role_multiplier in self.xp_multipliers.get(guild_id, {}).items():
                if isinstance(role_multiplier, (int, float)) and role_id in [role.id for role in member.roles]:
                    xp_gain = int(xp_gain * float(role_multiplier))

        user_data['xp'] += xp_gain
        user_data['last_message'] = datetime.now().isoformat()

        old_level = self.calculate_level(user_data['xp'] - xp_gain)
        new_level = self.calculate_level(user_data['xp'])

        if new_level > old_level:
            await self.handle_level_up(user_id, guild_id, new_level)

        self.save_data()


    async def handle_level_up(self, user_id: int, guild_id: int, level: int):
        """
        Handle level-up announcements, role assignments, and achievements.
        - Sends an announcement to the specified channel.
        - Assigns the role for the new level (if set).
        - Removes the role for the previous level (if applicable).
        - Checks for achievements.
        """
        if guild_id not in self.announcement_channels:
            return

        guild = self.bot.get_guild(guild_id)
        if not guild:
            print(f"Guild {guild_id} not found")
            return

        member = guild.get_member(user_id)
        if not member:
            print(f"Member {user_id} not found in guild {guild_id}")
            return

        channel = self.bot.get_channel(self.announcement_channels.get(guild_id))
        if not channel:
            print("Announcement channel not found")
            return

        embed = discord.Embed(
            title="🌟 Level Up! 🌟",
            description=f"🎉 {member.mention} has reached **Level {level}**! 🎉",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Next Level", value=f"**{self.xp_for_next_level(level)} XP**", inline=False)

        try:
            await channel.send(embed=embed)
            print(f"Level-up announcement sent to {channel.name}")
        except discord.Forbidden:
            print(f"Bot does not have permission to send messages in {channel.name}")
        except discord.HTTPException as e:
            print(f"Failed to send level-up announcement: {e}")

        if guild_id in self.roles and level in self.roles[guild_id]:
            role = discord.utils.get(guild.roles, id=self.roles[guild_id][level])
            if role:
                try:
                    for lvl, role_id in self.roles[guild_id].items():
                        if lvl != level and role_id in [r.id for r in member.roles]:
                            previous_role = discord.utils.get(guild.roles, id=role_id)
                            if previous_role:
                                await member.remove_roles(previous_role)
                                print(f"Removed previous level role: {previous_role.name}")

                    await member.add_roles(role)
                    print(f"Assigned role {role.name} to {member.display_name}")
                except discord.Forbidden:
                    print(f"Bot does not have permission to manage roles for {member.display_name}")
                except discord.HTTPException as e:
                    print(f"Failed to assign role: {e}")
            else:
                print(f"Role for level {level} not found")
        else:
            print(f"No role assigned for level {level}")

        await self.check_achievements(user_id, guild_id, level)

    async def check_achievements(self, user_id: int, guild_id: int, level: int):
        """Check if the user has unlocked any achievements."""
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        if not member:
            return

        for achievement, data in self.achievements.items():
            if level >= data['required_level'] and achievement not in self.user_data[guild_id][user_id].get('achievements', []):
                self.user_data[guild_id][user_id].setdefault('achievements', []).append(achievement)
                embed = discord.Embed(
                    title="🏆 Achievement Unlocked! 🏆",
                    description=f"🎉 {member.mention} has unlocked the **{achievement}** achievement! 🎉",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Reward", value=data['reward'], inline=False)
                await guild.system_channel.send(embed=embed)

    async def update_leaderboard_task(self):
        """Task to update the leaderboard periodically."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.leaderboard_channels:
                for guild_id, channel_id in self.leaderboard_channels.items():
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await self.update_leaderboard(channel)
            await asyncio.sleep(1800)


    async def update_leaderboard(self, channel: discord.TextChannel):
        """Update the leaderboard in the specified channel."""
        guild_id = channel.guild.id
        if guild_id not in self.leaderboard_channels:
            return
            
        if guild_id not in self.user_data or not self.user_data[guild_id]:
            return

        sorted_users = sorted(
            self.user_data[guild_id].items(),
            key=lambda x: x[1]['xp'],
            reverse=True
        )[:10]

        embed = discord.Embed(
            title="🏆 Live Leaderboard 🏆",
            description="Top 10 users by XP",
            color=discord.Color.green()
        )

        for i, (user_id, data) in enumerate(sorted_users, 1):
            member = channel.guild.get_member(user_id)
            if member:
                embed.add_field(
                    name=f"{i}. {member.display_name}",
                    value=f"Level {self.calculate_level(data['xp'])} | {data['xp']} XP",
                    inline=False
                )

        async for message in channel.history(limit=10):
            if message.author == self.bot.user and "🏆 Live Leaderboard 🏆" in message.embeds[0].title:
                await message.delete()
                break

        await channel.send(embed=embed)

    async def xp_decay_task(self):
        """Task to decay XP over time."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild_id, users in self.user_data.items():
                for user_id, data in users.items():
                    last_message = datetime.fromisoformat(data['last_message'])
                    if (datetime.now() - last_message).days > 7:  
                        data['xp'] = max(0, int(data['xp'] * (1 - self.xp_decay_rate)))
            self.save_data()
            await asyncio.sleep(86400)  

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Track user messages and add XP."""
        if message.author.bot:
            return
        await self.add_xp(message.author.id, message.guild.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_level_role(self, ctx, level: int, role: discord.Role):
        """Set a role for a specific level."""
        self.roles[level] = role.id
        self.save_data()
        await ctx.send(f"✅ Role {role.name} will be assigned at level {level}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_leaderboard_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel for the live-updating leaderboard."""
        self.leaderboard_channels[ctx.guild.id] = channel.id
        self.save_data()
        await ctx.send(f"✅ Leaderboard will be updated in {channel.mention}.")
        await self.update_leaderboard(channel)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leaderboard(self, ctx):
        """Display the server's leveling leaderboard."""
        await self.update_leaderboard(ctx.channel)

    @commands.command()
    @commands.is_owner()
    async def set_xp(self, ctx, user: discord.Member, xp: int):
        """Bot owner command: Set a user's XP."""
        guild_id = ctx.guild.id
        if guild_id not in self.user_data:
            self.user_data[guild_id] = {}
        self.user_data[guild_id][user.id] = {'xp': xp, 'last_message': datetime.now().isoformat()}
        self.save_data()
        await ctx.send(f"✅ Set {user.mention}'s XP to {xp}.")

    @commands.command()
    @commands.is_owner()
    async def reset_levels(self, ctx):
        """Bot owner command: Reset all leveling data for the server."""
        guild_id = ctx.guild.id
        if guild_id in self.user_data:
            del self.user_data[guild_id]
            self.save_data()
            await ctx.send("✅ Reset all leveling data for this server.")
        else:
            await ctx.send("No leveling data found for this server.")

    @commands.command()
    async def my_level(self, ctx):
        """Check your current level and XP."""
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        if guild_id in self.user_data and user_id in self.user_data[guild_id]:
            xp = self.user_data[guild_id][user_id]['xp']
            level = self.calculate_level(xp)
            next_level_xp = self.xp_for_next_level(level)
            embed = discord.Embed(
                title=f"📊 {ctx.author.display_name}'s Level",
                description=f"Level: **{level}**\nXP: **{xp}/{next_level_xp}**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("You haven't earned any XP yet!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def levelsetup(self, ctx, channel: Optional[discord.TextChannel] = None):
        """
        Display leveling-related information or set the announcement channel.
        Usage:
        - !levelsetup: Show all leveling-related info.
        - !levelsetup <channel>: Set the channel for level-up announcements.
        """
        guild_id = ctx.guild.id
        
        if channel:
            self.announcement_channels[guild_id] = channel.id
            self.save_data()
            await ctx.send(f"✅ Level-up announcements will now be sent to {channel.mention}.")
        else:
            guild = ctx.guild
            embed = discord.Embed(
                title="📊 Leveling System Setup",
                description="All leveling-related information for this server.",
                color=discord.Color.blue()
            )

            leaderboard_channel = self.bot.get_channel(self.leaderboard_channels.get(guild_id))
            embed.add_field(
                name="Leaderboard Channel",
                value=leaderboard_channel.mention if leaderboard_channel else "Not set",
                inline=False
            )

            announcement_channel = self.bot.get_channel(self.announcement_channels.get(guild_id))
            embed.add_field(
                name="Announcement Channel",
                value=announcement_channel.mention if announcement_channel else "Not set",
                inline=False
            )

            roles_info = "\n".join(
                f"Level {level}: <@&{role_id}>"
                for level, role_id in self.roles.get(guild_id, {}).items()
            ) if guild_id in self.roles else "No roles assigned to levels."
            embed.add_field(name="Level Roles", value=roles_info, inline=False)

            multipliers_info = "\n".join(
                f"<@&{role_id}>: {multiplier}x"
                for role_id, multiplier in self.xp_multipliers.get(guild_id, {}).items()
            ) if guild_id in self.xp_multipliers else "No XP multipliers set."
            embed.add_field(name="XP Multipliers", value=multipliers_info, inline=False)

            achievements_info = "\n".join(
                f"{name}: Level {data['required_level']} (Reward: {data['reward']})"
                for name, data in self.achievements.get(guild_id, {}).items()
            ) if guild_id in self.achievements else "No achievements set."
            embed.add_field(name="Achievements", value=achievements_info, inline=False)

            embed.add_field(
                name="XP Decay Rate",
                value=f"{self.xp_decay_rate * 100}% per day after 7 days of inactivity",
                inline=False
            )

            embed.add_field(
                name="XP Gain Range",
                value=f"{self.xp_gain_range[0]} to {self.xp_gain_range[1]} XP per message",
                inline=False
            )

            total_users = len(self.user_data.get(guild_id, {}))
            embed.add_field(
                name="Total Users with XP",
                value=f"{total_users} users",
                inline=False
            )

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(LevelingSystem(bot))

class CustomLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging_config = {}  

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def togglelog(self, ctx, action: str, channel: discord.TextChannel = None):
        """
        Toggle logging for specific actions (e.g., bans, mutes, kicks).
        Usage: !togglelog <action> <channel>
        """
        action = action.lower()
        valid_actions = ["ban", "mute", "kick"]

        if action not in valid_actions:
            await ctx.send(f"❌ Invalid action. Use one of: {', '.join(valid_actions)}")
            return

        guild_id = ctx.guild.id
        if guild_id not in self.logging_config:
            self.logging_config[guild_id] = {}

        if channel:
            self.logging_config[guild_id][action] = channel.id
            await ctx.send(f"✅ Logging for `{action}` has been enabled in {channel.mention}.")
        else:
            if action in self.logging_config[guild_id]:
                del self.logging_config[guild_id][action]
                await ctx.send(f"✅ Logging for `{action}` has been disabled.")
            else:
                await ctx.send(f"❌ Logging for `{action}` is already disabled.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def toggleprelog(self, ctx):
        """
        Automatically create channels for bans, mutes, and kicks and enable logging.
        Usage: !toggleprelog
        """
        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ban_channel = await guild.create_text_channel("ban-logs", overwrites=overwrites)
        mute_channel = await guild.create_text_channel("mute-logs", overwrites=overwrites)
        kick_channel = await guild.create_text_channel("kick-logs", overwrites=overwrites)

        guild_id = guild.id
        self.logging_config[guild_id] = {
            "ban": ban_channel.id,
            "mute": mute_channel.id,
            "kick": kick_channel.id
        }

        await ctx.send("✅ Created logging channels and enabled logging for bans, mutes, and kicks.")

    async def log_action(self, guild_id, action, moderator, user, reason, duration=None):
        print(f"Logging {action} for {user} in guild {guild_id}")  # Debug print
        if guild_id not in self.logging_config or action not in self.logging_config[guild_id]:
            print("Logging not configured for this action.")  # Debug print
            return

        channel_id = self.logging_config[guild_id][action]
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found.")  # Debug print
            return

        embed = discord.Embed(
            title=f"🚨 {action.capitalize()} Log",
            description=f"**User:** {user.mention} (`{user.id}`)\n**Reason:** {reason}",
            color=discord.Color.red()
        )
        if duration:
            embed.add_field(name="Duration", value=duration)
        embed.add_field(name="Moderator", value=moderator.mention)
        embed.set_footer(text=f"Action performed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(CustomLogging(bot))

class MessagePurge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, condition: str, count: str = "nuke"):
        """
        Delete messages from bots, links, or specific users.
        Usage: !purge <user_id/bots/links> <count/nuke>
        """
        if count.lower() == "nuke":
            count = None  
        else:
            try:
                count = int(count)
                if count <= 0:
                    await ctx.send("❌ Count must be a positive number.")
                    return
            except ValueError:
                await ctx.send("❌ Invalid count. Use a number or 'nuke'.")
                return

        def check(message):
            if condition.lower() == "bots":
                return message.author.bot
            elif condition.lower() == "links":
                return "http://" in message.content or "https://" in message.content
            else:
                try:
                    user_id = int(condition)  
                    return message.author.id == user_id
                except ValueError:
                    return False

        if condition.lower() not in ["bots", "links"]:
            try:
                user_id = int(condition)  
            except ValueError:
                await ctx.send(f"❌ Invalid condition: `{condition}`. Use 'bots', 'links', or a valid user ID.", delete_after=5)
                return

        deleted = await ctx.channel.purge(limit=count, check=check)
        await ctx.send(f"✅ Deleted {len(deleted)} messages matching the condition: `{condition}`.", delete_after=5)


def setup(bot):
    bot.add_cog(MessagePurge(bot))

class ReminderSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = {}

    @commands.command(name="reminder")
    async def reminder(self, ctx):
        """
        Open a UI to set a reminder.
        Usage: !reminder
        """
        
        modal = discord.ui.Modal(title="Set a Reminder")
        modal.add_item(discord.ui.TextInput(
            label="Duration",
            placeholder="Enter duration (e.g., 1h, 30m, 2d)",
            required=True
        ))
        modal.add_item(discord.ui.TextInput(
            label="Color",
            placeholder="Enter color (e.g., red, #FF0000)",
            required=True
        ))
        modal.add_item(discord.ui.TextInput(
            label="Message",
            placeholder="Enter the reminder message",
            required=True
        ))
        modal.add_item(discord.ui.TextInput(
            label="Channel",
            placeholder="Mention the channel (e.g., #general)",
            required=True
        ))

        async def on_submit(interaction: discord.Interaction):
            try:
                duration = modal.children[0].value
                color = modal.children[1].value
                message = modal.children[2].value
                channel_input = modal.children[3].value

                duration_seconds = self.parse_duration(duration)
                if duration_seconds <= 0:
                    await interaction.response.send_message("❌ Invalid duration. Please specify a positive duration.", ephemeral=True)
                    return

                reminder_color = self.parse_color(color)
                if not reminder_color:
                    await interaction.response.send_message("❌ Invalid color. Please use a valid hex code or named color (e.g., red, green, blue, #FF0000).", ephemeral=True)
                    return

                channel = self.parse_channel(ctx, channel_input)
                if not channel:
                    await interaction.response.send_message("❌ Invalid channel. Please mention a valid channel or use its ID.", ephemeral=True)
                    return

                reminder_time = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
                self.reminders[ctx.author.id] = {
                    "time": reminder_time,
                    "message": message,
                    "color": reminder_color,
                    "channel": channel.id,
                    "user_id": ctx.author.id
                }

                embed = discord.Embed(
                    title="⏰ Reminder Set",
                    description=f"I'll remind you in {duration} in {channel.mention}.",
                    color=reminder_color
                )
                embed.add_field(name="Message", value=message, inline=False)
                await interaction.response.send_message(embed=embed)

                await self.start_reminder(ctx.author.id)

            except ValueError as e:
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

        modal.on_submit = on_submit

        view = discord.ui.View()
        button = discord.ui.Button(label="Set Reminder", style=discord.ButtonStyle.primary)
        async def button_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(modal)
        button.callback = button_callback
        view.add_item(button)

        await ctx.send("Click the button below to set a reminder:", view=view)

    @commands.command(name="editreminder")
    async def edit_reminder(self, ctx):
        """
        Open a panel to edit existing reminders.
        Usage: !editreminder
        """
        if ctx.author.id not in self.reminders:
            await ctx.send("❌ You don't have any active reminders to edit.")
            return

        reminder = self.reminders[ctx.author.id]

        view = discord.ui.View()
        select = discord.ui.Select(
            placeholder="Select a reminder to edit",
            options=[
                discord.SelectOption(
                    label=f"Reminder: {reminder['message'][:50]}...",
                    value="edit_reminder",
                    description=f"Due: {reminder['time'].strftime('%Y-%m-%d %H:%M:%S')}"
                )
            ]
        )
        select.callback = lambda interaction: self.handle_reminder_selection(interaction, reminder)
        view.add_item(select)

        await ctx.send("Select the reminder you want to edit:", view=view)

    async def handle_reminder_selection(self, interaction: discord.Interaction, reminder):
        """
        Handle the selection of a reminder to edit.
        """
        modal = discord.ui.Modal(title="Edit Reminder")
        modal.add_item(discord.ui.TextInput(
            label="New Message",
            placeholder="Enter the new reminder message",
            default=reminder["message"],
            required=True
        ))
        modal.add_item(discord.ui.TextInput(
            label="New Duration",
            placeholder="Enter the new duration (e.g., 1h, 30m)",
            required=True
        ))
        modal.add_item(discord.ui.TextInput(
            label="New Color",
            placeholder="Enter the new color (e.g., red, #FF0000)",
            required=True
        ))

        async def on_submit(interaction: discord.Interaction):
            try:
                new_message = modal.children[0].value
                new_duration = modal.children[1].value
                new_color = modal.children[2].value

                duration_seconds = self.parse_duration(new_duration)
                if duration_seconds <= 0:
                    await interaction.response.send_message("❌ Invalid duration. Please specify a positive duration.", ephemeral=True)
                    return

                reminder_color = self.parse_color(new_color)
                if not reminder_color:
                    await interaction.response.send_message("❌ Invalid color. Please use a valid hex code or named color (e.g., red, green, blue, #FF0000).", ephemeral=True)
                    return

                reminder["message"] = new_message
                reminder["time"] = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
                reminder["color"] = reminder_color

                embed = discord.Embed(
                    title="⏰ Reminder Updated",
                    description=f"Your reminder has been updated.",
                    color=reminder["color"]
                )
                embed.add_field(name="New Message", value=reminder["message"], inline=False)
                embed.add_field(name="New Duration", value=f"{new_duration}", inline=False)
                embed.add_field(name="New Color", value=f"{new_color}", inline=False)
                await interaction.response.send_message(embed=embed)

                await self.start_reminder(reminder["user_id"])

            except ValueError as e:
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

        modal.on_submit = on_submit
        await interaction.response.send_modal(modal)

    def parse_duration(self, duration: str) -> int:
        """
        Parse a duration string (e.g., 1h, 30m, 2d) into seconds.
        """
        duration = duration.lower()
        if duration.endswith("h"):
            return int(duration[:-1]) * 3600
        elif duration.endswith("m"):
            return int(duration[:-1]) * 60
        elif duration.endswith("d"):
            return int(duration[:-1]) * 86400
        elif duration.endswith("s"):
            return int(duration[:-1])
        else:
            raise ValueError("Invalid duration format. Use 'h' for hours, 'm' for minutes, 's' for seconds, or 'd' for days.")

    def parse_color(self, color: str) -> Optional[discord.Color]:
        """
        Parse a color string (hex code or named color) into a discord.Color object.
        """
        color = color.lower()
        named_colors = {
            "red": discord.Color.red(),
            "green": discord.Color.green(),
            "blue": discord.Color.blue(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange(),
            "gold": discord.Color.gold(),
            "teal": discord.Color.teal(),
            "dark_blue": discord.Color.dark_blue(),
            "dark_green": discord.Color.dark_green(),
            "dark_purple": discord.Color.dark_purple(),
            "dark_red": discord.Color.dark_red(),
            "dark_teal": discord.Color.dark_teal(),
            "dark_gold": discord.Color.dark_gold(),
            "dark_orange": discord.Color.dark_orange(),
            "dark_gray": discord.Color.dark_gray(),
            "light_gray": discord.Color.light_gray(),
            "blurple": discord.Color.blurple(),
            "greyple": discord.Color.greyple(),
            "fuchsia": discord.Color.fuchsia(),
            "yellow": discord.Color.yellow(),
            "black": discord.Color.default(),
        }
        if color in named_colors:
            return named_colors[color]
        try:
            return discord.Color.from_str(color)
        except ValueError:
            return None

    def parse_channel(self, ctx, channel_input: str) -> Optional[discord.TextChannel]:
        """
        Parse a channel mention or ID into a discord.TextChannel object.
        """
        try:
            if channel_input.startswith("<#") and channel_input.endswith(">"):
                channel_id = int(channel_input[2:-1])
            else:
                channel_id = int(channel_input)
            return ctx.guild.get_channel(channel_id)
        except (ValueError, AttributeError):
            return None

    async def start_reminder(self, user_id: int):
        """
        Start a reminder task for the specified user.
        """
        reminder = self.reminders.get(user_id)
        if not reminder:
            return

        reminder_time = reminder["time"]
        reminder_time = reminder["time"]
        delay = (reminder_time - datetime.now(timezone.utc)).total_seconds()

        if delay > 0:
            await asyncio.sleep(delay)

            channel = self.bot.get_channel(reminder["channel"])
            if channel:
                embed = discord.Embed(
                    title="⏰ Reminder",
                    description=reminder["message"],
                    color=reminder["color"]
                )
                await channel.send(f"<@{reminder['user_id']}>", embed=embed)

            self.reminders.pop(user_id, None)

def setup(bot):
    bot.add_cog(ReminderSystem(bot))


class Snipe(commands.Cog):       
    def __init__(self, bot):
        self.bot = bot
        self.deleted_messages = {} 
        self.edited_messages = {}  
        self.snipe_cooldown = {}  
        self.snipe_duration = 300  
        self.editsnipe_duration = 300  

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Track deleted messages."""
        if message.author.bot:  
            return

        self.deleted_messages[message.channel.id] = {
            "content": message.content,
            "author": message.author,
            "timestamp": message.created_at,
            "attachments": [attachment.url for attachment in message.attachments]
        }

        await asyncio.sleep(self.snipe_duration)  
        if message.channel.id in self.deleted_messages:
            del self.deleted_messages[message.channel.id]

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Track edited messages."""
        if before.author.bot: 
            return

        self.edited_messages[before.channel.id] = {
            "before": before.content,
            "after": after.content,
            "author": before.author,
            "timestamp": datetime.utcnow()
        }

        await asyncio.sleep(self.editsnipe_duration)  
        if before.channel.id in self.edited_messages:
            del self.edited_messages[before.channel.id]

    @commands.command(name="configuresnipe")
    @commands.has_permissions(manage_messages=True)
    async def configuresnipe(self, ctx, duration: int):
        """Configure the duration for which deleted messages are stored."""
        if duration < 0:
            await ctx.send("Duration cannot be negative.")
            return
        self.snipe_duration = duration
        await ctx.send(f"Deleted messages will now be stored for {duration} seconds.")

    @commands.command(name="configuresnipeedit")
    @commands.has_permissions(manage_messages=True)
    async def configuresnipeedit(self, ctx, duration: int):
        """Configure the duration for which edited messages are stored."""
        if duration < 0:
            await ctx.send("Duration cannot be negative.")
            return
        self.editsnipe_duration = duration
        await ctx.send(f"Edited messages will now be stored for {duration} seconds.")

    @commands.command(name="snipe_info")
    async def snipe_info(self, ctx):
        """Display the current snipe settings."""
        embed = discord.Embed(
            title="⚙️ Snipe Settings",
            color=discord.Color.green()
        )
        embed.add_field(name="Deleted Messages Duration", value=f"{self.snipe_duration} seconds", inline=False)
        embed.add_field(name="Edited Messages Duration", value=f"{self.editsnipe_duration} seconds", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="snipe")
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx):
        """Recover the last deleted message in the channel."""
        if ctx.author.id in self.snipe_cooldown:
            remaining = (self.snipe_cooldown[ctx.author.id] - datetime.utcnow()).total_seconds()
            if remaining > 0:
                await ctx.send(f"You're on cooldown! Try again in {int(remaining)} seconds.")
                return

        deleted_message = self.deleted_messages.get(ctx.channel.id)
        if not deleted_message:
            await ctx.send("No recently deleted messages found in this channel.")
            return

        embed = discord.Embed(
            title="🗑️ Sniped Message",
            description=deleted_message["content"],
            color=discord.Color.red()
        )
        embed.set_author(name=deleted_message["author"].display_name, icon_url=deleted_message["author"].avatar.url)
        embed.set_footer(text=f"Deleted at {deleted_message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        if deleted_message["attachments"]:
            embed.add_field(name="Attachments", value="\n".join(deleted_message["attachments"]), inline=False)

        await ctx.send(embed=embed)

        self.snipe_cooldown[ctx.author.id] = datetime.utcnow() + timedelta(seconds=30)

    @commands.command(name="editsnipe")
    @commands.has_permissions(manage_messages=True)
    async def editsnipe(self, ctx):
        """Recover the last edited message in the channel."""
        if ctx.author.id in self.snipe_cooldown:
            remaining = (self.snipe_cooldown[ctx.author.id] - datetime.utcnow()).total_seconds()
            if remaining > 0:
                await ctx.send(f"You're on cooldown! Try again in {int(remaining)} seconds.")
                return

        edited_message = self.edited_messages.get(ctx.channel.id)
        if not edited_message:
            await ctx.send("No recently edited messages found in this channel.")
            return

        embed = discord.Embed(
            title="✏️ Edited Message",
            color=discord.Color.blue()
        )
        embed.set_author(name=edited_message["author"].display_name, icon_url=edited_message["author"].avatar.url)
        embed.add_field(name="Before", value=edited_message["before"], inline=False)
        embed.add_field(name="After", value=edited_message["after"], inline=False)
        embed.set_footer(text=f"Edited at {edited_message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        await ctx.send(embed=embed)

        self.snipe_cooldown[ctx.author.id] = datetime.utcnow() + timedelta(seconds=30)

def setup(bot):
    bot.add_cog(Snipe(bot))


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AdvancedInviteTracker")

class AdvancedInviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache: Dict[int, Dict[str, Dict]] = {}  
        self.known_joins: Dict[int, Dict] = {}  
        self.data_file = "invite_tracking_data.json"
        self.db_file = "invite_tracking.db"
        self.setup_database()

        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.invite_cache = data.get("invites", {})
                    self.known_joins = data.get("known_joins", {})
            except json.JSONDecodeError:
                logger.error("Failed to load invite tracking data: Invalid JSON format")

    def setup_database(self):
        """Initialize the SQLite database for invite tracking."""
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invites (
                guild_id INTEGER,
                invite_code TEXT,
                uses INTEGER,
                inviter TEXT,
                created_at TEXT,
                PRIMARY KEY (guild_id, invite_code)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS joins (
                member_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                invite_code TEXT,
                inviter TEXT,
                joined_at TEXT
            )
        ''')
        self.conn.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        """Cache all invites when the bot is ready."""
        logger.info("Bot is ready. Syncing invites...")
        for guild in self.bot.guilds:
            try:
                invites = await guild.invites()
                self.invite_cache[guild.id] = {
                    invite.code: {
                        "uses": invite.uses,
                        "inviter": invite.inviter.name if invite.inviter else "Unknown",
                        "created_at": invite.created_at.isoformat() if invite.created_at else "Unknown"
                    }
                    for invite in invites
                }
                self.update_database(guild.id, invites)
            except discord.Forbidden:
                logger.warning(f"Missing permission to fetch invites for guild: {guild.name}")
        logger.info("Invite sync complete.")

    def update_database(self, guild_id: int, invites: List[discord.Invite]):
        """Update the database with the latest invite data."""
        for invite in invites:
            self.cursor.execute('''
                INSERT OR REPLACE INTO invites (guild_id, invite_code, uses, inviter, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, invite.code, invite.uses, invite.inviter.name if invite.inviter else "Unknown", invite.created_at.isoformat() if invite.created_at else "Unknown"))
        self.conn.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Track which invite was used when a member joins."""
        try:
            invites_before = self.invite_cache.get(member.guild.id, {})
            current_invites = await member.guild.invites()

            for invite in current_invites:
                cached_invite = invites_before.get(invite.code)
                if cached_invite and invite.uses > cached_invite["uses"]:
                    inviter = invite.inviter.name if invite.inviter else "Unknown"
                    invite_code = invite.code

                    self.known_joins[member.id] = {
                        "joined_at": member.joined_at.isoformat() if member.joined_at else "Unknown",
                        "invite_code": invite_code,
                        "inviter": inviter
                    }
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO joins (member_id, guild_id, invite_code, inviter, joined_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (member.id, member.guild.id, invite_code, inviter, member.joined_at.isoformat() if member.joined_at else "Unknown"))
                    self.conn.commit()

                    self.invite_cache[member.guild.id][invite.code]["uses"] = invite.uses
                    await self.log_join(member, invite_code, inviter)
                    break

            self.backup_data()

        except discord.Forbidden:
            logger.warning(f"Missing permission to fetch invites for guild: {member.guild.name}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Track when a member leaves the server."""
        if member.id in self.known_joins:
            del self.known_joins[member.id]
            self.cursor.execute('DELETE FROM joins WHERE member_id = ?', (member.id,))
            self.conn.commit()
            self.backup_data()
            logger.info(f"Member {member.name} ({member.id}) left the server.")

    async def log_join(self, member: discord.Member, invite_code: str, inviter: str):
        """Log the member join to a designated log channel."""
        log_channel = discord.utils.get(member.guild.text_channels, name='join-logs')
        if log_channel:
            embed = discord.Embed(
                title="👤 Member Joined",
                description=f"{member.mention} joined using invite `{invite_code}` created by **{inviter}**.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await log_channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def view_historic(self, ctx):
        """View historic tracking of invite joins."""
        self.cursor.execute('SELECT * FROM joins WHERE guild_id = ?', (ctx.guild.id,))
        joins = self.cursor.fetchall()

        if not joins:
            await ctx.send("📊 No historic join data available.")
            return

        entries = []
        for join in joins:
            member_id, guild_id, invite_code, inviter, joined_at = join
            member = ctx.guild.get_member(member_id)
            member_name = member.name if member else "Unknown Member"
            entries.append(
                f"👤 **{member_name}** (ID: {member_id})\n"
                f"🎟️ Invite: `{invite_code}` by **{inviter}**\n"
                f"📅 Joined: {joined_at}\n"
            )

        page_size = 5
        pages = [entries[i:i + page_size] for i in range(0, len(entries), page_size)]

        for page_num, page_content in enumerate(pages, 1):
            embed = discord.Embed(
                title=f"📊 Historic Invite Tracking (Page {page_num}/{len(pages)})",
                description="\n\n".join(page_content),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Tracked {len(joins)} total joins.")
            await ctx.send(embed=embed)

    def backup_data(self):
        """Backup invite tracking data to a JSON file."""
        data = {
            "invites": self.invite_cache,
            "known_joins": self.known_joins
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=4)

    def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        self.conn.close()

def setup(bot):
    bot.add_cog(AdvancedInviteTracker(bot))


class Analytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_tracker = {}  # {guild_id: {invite_code: invite_data}}
        self.join_tracker = {}    # {guild_id: {date: count}}
        self.analytics_channels = {}  # {guild_id: {interval: channel}}
        self.analytics_tasks = {}  # {guild_id: {interval: task}}

    async def fetch_existing_invites(self):
        for guild in self.bot.guilds:
            if guild.id not in self.invite_tracker:
                self.invite_tracker[guild.id] = {}
            try:
                invites = await guild.invites()
                for invite in invites:
                    self.invite_tracker[guild.id][invite.code] = {
                        'code': invite.code,
                        'creator': invite.inviter.name if invite.inviter else "Unknown",
                        'uses': invite.uses,
                        'max_uses': invite.max_uses,
                        'expires_at': invite.expires_at
                    }
            except Exception as e:
                print(f"Error fetching invites for guild {guild.name}: {e}")

    async def check_and_setup_analytics(self):
        while True:
            for guild_id in self.analytics_channels:
                for interval, channel in self.analytics_channels[guild_id].items():
                    if channel is None:
                        print(f"Channel for {interval} analytics not found in guild {guild_id}. Retrying in 5 minutes...")
                        await asyncio.sleep(300)
                        continue

                    task_key = f"{guild_id}_{interval}"
                    if task_key not in self.analytics_tasks or self.analytics_tasks[task_key].done():
                        self.analytics_tasks[task_key] = self.bot.loop.create_task(
                            self._send_analytics(guild_id, interval)
                        )
                        print(f"Analytics task for {interval} started in {channel.mention} (Guild: {guild_id})")
            await asyncio.sleep(300)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def analyse(self, ctx, interval: str = None, channel: discord.TextChannel = None):
        guild_id = ctx.guild.id
        
        if guild_id not in self.analytics_channels:
            self.analytics_channels[guild_id] = {}
            
        if interval:
            if interval.lower() not in ['daily', 'weekly', 'monthly']:
                await ctx.send("❌ Invalid interval. Use 'daily', 'weekly', or 'monthly'.")
                return

            self.analytics_channels[guild_id][interval.lower()] = channel or ctx.channel
            task_key = f"{guild_id}_{interval.lower()}"
            
            if task_key not in self.analytics_tasks or self.analytics_tasks[task_key].done():
                self.analytics_tasks[task_key] = self.bot.loop.create_task(
                    self._send_analytics(guild_id, interval.lower())
                )

            embed = discord.Embed(
                title="✅ Analytics Setup Complete",
                description=f"Analytics will be posted {interval.lower()} in {(channel or ctx.channel).mention}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="📊 Analytics Status",
                description="Current analytics configurations",
                color=discord.Color.blue()
            )

            for interval in ['daily', 'weekly', 'monthly']:
                if interval in self.analytics_channels.get(guild_id, {}) and self.analytics_channels[guild_id][interval] is not None:
                    embed.add_field(
                        name=f"{interval.capitalize()} Analytics",
                        value=f"Active in {self.analytics_channels[guild_id][interval].mention}",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"{interval.capitalize()} Analytics",
                        value="Not active",
                        inline=False
                    )

            await ctx.send(embed=embed)

    async def _send_analytics(self, guild_id, interval):
        while True:
            print(f"Running analytics task for {interval} in guild {guild_id}")
            try:
                if interval == 'daily':
                    await asyncio.sleep(86400)
                elif interval == 'weekly':
                    await asyncio.sleep(604800)
                elif interval == 'monthly':
                    await asyncio.sleep(2592000)

                if guild_id not in self.analytics_channels or interval not in self.analytics_channels[guild_id]:
                    continue

                embed = self._generate_analytics_report(guild_id, interval)
                await self.analytics_channels[guild_id][interval].send(embed=embed)
            except Exception as e:
                print(f"Error in _send_analytics for guild {guild_id}: {e}")
                continue

    def _generate_analytics_report(self, guild_id, interval):
        embed = discord.Embed(
            title=f"📊 Server Analytics Report ({interval.capitalize()})",
            description="Detailed server activity and statistics",
            color=discord.Color.blue()
        )

        guild_invites = self.invite_tracker.get(guild_id, {})
        active_invites = [invite for invite in guild_invites.values() if invite['uses'] > 0]
        expired_invites = [invite for invite in guild_invites.values() if invite['uses'] == 0]

        embed.add_field(
            name="🔗 Invites",
            value=f"Active: {len(active_invites)}\nExpired: {len(expired_invites)}\nTotal Uses: {sum(invite['uses'] for invite in guild_invites.values())}",
            inline=False
        )

        guild_joins = self.join_tracker.get(guild_id, {})
        total_joins = sum(guild_joins.values())
        embed.add_field(
            name="👥 Member Joins",
            value=f"Total Joins ({interval}): {total_joins}",
            inline=False
        )

        if active_invites:
            invite_details = "\n".join(
                f"• {invite['code']}: {invite['uses']} uses (Created by {invite['creator']})"
                for invite in active_invites
            )
            embed.add_field(name="Active Invites", value=invite_details, inline=False)

        return embed

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        if guild_id not in self.join_tracker:
            self.join_tracker[guild_id] = {}
        today = datetime.now().date()
        self.join_tracker[guild_id][today] = self.join_tracker[guild_id].get(today, 0) + 1

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        guild_id = invite.guild.id
        if guild_id not in self.invite_tracker:
            self.invite_tracker[guild_id] = {}
        self.invite_tracker[guild_id][invite.code] = {
            'code': invite.code,
            'creator': invite.inviter.name if invite.inviter else "Unknown",
            'uses': invite.uses,
            'max_uses': invite.max_uses,
            'expires_at': invite.expires_at
        }

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        guild_id = invite.guild.id
        if guild_id in self.invite_tracker and invite.code in self.invite_tracker[guild_id]:
            del self.invite_tracker[guild_id][invite.code]

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = member.guild.id
        invites = await member.guild.invites()
        if guild_id not in self.invite_tracker:
            self.invite_tracker[guild_id] = {}
        for invite in invites:
            if invite.code in self.invite_tracker[guild_id]:
                self.invite_tracker[guild_id][invite.code]['uses'] = invite.uses
            else:
                self.invite_tracker[guild_id][invite.code] = {
                    'code': invite.code,
                    'creator': invite.inviter.name if invite.inviter else "Unknown",
                    'uses': invite.uses,
                    'max_uses': invite.max_uses,
                    'expires_at': invite.expires_at
                }

    @commands.Cog.listener()
    async def on_ready(self):
        await self.fetch_existing_invites()
        self.bot.loop.create_task(self.check_and_setup_analytics())

def setup(bot):
    bot.add_cog(Analytics(bot))


class WebhookLogger:
    def __init__(self, bot):
        self.bot = bot
        self.webhook_url = os.getenv('LOGGING_WEBHOOK_URL')
        self.session = aiohttp.ClientSession()

    async def send_to_webhook(self, content=None, embeds=None, files=None):
        if not self.webhook_url:
            return

        webhook = discord.Webhook.from_url(self.webhook_url, session=self.session)

        try:
            if isinstance(embeds, list) and len(embeds) > 0 and isinstance(embeds[0], discord.Embed):
                await webhook.send(
                    content=content,
                    embeds=embeds,  
                    files=files
                )
            else:
                await webhook.send(
                    content=content,
                    embed=embeds[0] if embeds and isinstance(embeds[0], discord.Embed) else None, 
                    files=files
                )
        except Exception as e:
            print(f"Webhook send error details: {str(e)}")


    async def log_message(self, message):
        if message.author.bot:
            return

        embed = EmbedBuilder(
            f"Message in {message.guild.name}",
            message.content or "No content"
        ).set_color(discord.Color.blue())
    
        embed.add_field("Author", f"{message.author} ({message.author.id})")
        embed.add_field("Channel", f"{message.channel.name} ({message.channel.id})")
        embed.add_field("Timestamp", message.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

        if message.reference:
            embed.add_field("Reply to", f"Message ID: {message.reference.message_id}", inline=False)
    
        if message.edited_at:
            embed.add_field("Edited", message.edited_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

        files = []
    
        for attachment in message.attachments:
            try:
                file_data = await attachment.read()
                file = discord.File(io.BytesIO(file_data), filename=attachment.filename)
                files.append(file)
            
                file_info = (
                    f"📎 Name: {attachment.filename}\n"
                    f"📊 Size: {attachment.size:,} bytes\n"
                    f"📑 Type: {attachment.content_type}\n"
                    f"🔗 URL: {attachment.url}"
            )
                embed.add_field("File Attachment", file_info, inline=False)
            except Exception as e:
                embed.add_field("⚠️ File Error", f"Failed to process {attachment.filename}: {str(e)}", inline=False)

        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        embed.add_field("Message Link", message_link, inline=False)
    
        embed.set_footer(f"Message ID: {message.id} | Guild ID: {message.guild.id}")
    
        if message.author.avatar:
            embed.set_thumbnail(message.author.avatar.url)

        await self.send_to_webhook(embeds=[embed.build()], files=files)

    async def log_command(self, ctx):
        embed = EmbedBuilder(
            f"Command Used in {ctx.guild.name}",
            f"Command: {ctx.command}\nArgs: {ctx.args[2:]}"
        ).set_color(discord.Color.green())
        
        embed.add_field("User", f"{ctx.author} ({ctx.author.id})")
        embed.add_field("Channel", f"{ctx.channel.name} ({ctx.channel.id})")
        
        await self.send_to_webhook(embeds=[embed.build()])

    def __del__(self):
        if self.session:
            asyncio.create_task(self.session.close())

class TicTacToeButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(style=discord.ButtonStyle.secondary, label="⠀", row=y)
        self.x = x
        self.y = y


    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        if interaction.user != view.current_player:
            return
        
        if view.board[self.x][self.y] != " ":
            return

        mark = "X" if view.current_player == view.player1 else "O"
        view.board[self.x][self.y] = mark
        self.label = mark
        self.disabled = True
        self.style = discord.ButtonStyle.danger if mark == "X" else discord.ButtonStyle.success

        if view.check_winner():
            for child in view.children:
                child.disabled = True
            embed = EmbedBuilder(
                "🎮 Game Over!",
                f"🎉 {view.current_player.mention} wins!"
            ).set_color(discord.Color.gold())
            await interaction.response.edit_message(view=view, embed=embed.build())
            
            rematch_view = discord.ui.View()
            rematch_button = discord.ui.Button(label="Rematch", style=discord.ButtonStyle.primary)
            close_button = discord.ui.Button(label="Close", style=discord.ButtonStyle.red)
            
            async def rematch_callback(i):
                new_game = TicTacToeView(view.player1, view.player2)
                embed = EmbedBuilder(
                    "🎮 New Game Started!",
                    f"{view.player1.mention} vs {view.player2.mention}"
                ).set_color(discord.Color.blue())
                await i.response.send_message(embed=embed.build(), view=new_game)
                
            async def close_callback(i):
                await i.channel.delete()
                
            rematch_button.callback = rematch_callback
            close_button.callback = close_callback
            rematch_view.add_item(rematch_button)
            rematch_view.add_item(close_button)
            await interaction.channel.send(view=rematch_view)
            return

        if view.is_board_full():
            embed = EmbedBuilder(
                "🎮 Game Over!",
                "It's a tie!"
            ).set_color(discord.Color.greyple())
            await interaction.response.edit_message(view=view, embed=embed.build())
            return

        view.current_player = view.player2 if view.current_player == view.player1 else view.player1
        embed = EmbedBuilder(
            "🎮 TicTacToe",
            f"It's {view.current_player.mention}'s turn!"
        ).set_color(discord.Color.blue())
        await interaction.response.edit_message(view=view, embed=embed.build())

class TicTacToeView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=120)
        self.current_player = player1
        self.player1 = player1
        self.player2 = player2
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        
        for i in range(3):
            for j in range(3):
                self.add_item(TicTacToeButton(i, j))

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return True
        return False

    def is_board_full(self):
        return all(self.board[i][j] != " " for i in range(3) for j in range(3))

    async def on_timeout(self):
        await self.message.channel.delete()

class MinigamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def numbergame(self, ctx, number: int, channel: discord.TextChannel):
        """Start a number guessing game in a specific channel"""
        if not 1 <= number <= 10000:
            await ctx.send("Please choose a number between 1 and 10000!")
            return
            
        if channel.id in self.active_games:
            await ctx.send("A game is already running in that channel!")
            return
            
        self.active_games[channel.id] = number
            
        embed = EmbedBuilder(
            "🎮 Number Guessing Game Started!",
            "A new number guessing game has begun!\n\n"
            "Simply type numbers in the chat to guess.\n"
            "First person to guess correctly wins! 🏆"
        ).set_color(discord.Color.blue()).build()
        
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
            
        if message.channel.id not in self.active_games:
            return
            
        if not message.content.isdigit():
            return
            
        guess = int(message.content)
        correct_number = self.active_games[message.channel.id]
        
        if guess == correct_number:
            win_embed = EmbedBuilder(
                "🎉 We Have a Winner!",
                f"Congratulations {message.author.mention}!\n"
                f"The correct number was {correct_number}!"
            ).set_color(discord.Color.gold()).build()
            await message.channel.send(embed=win_embed)
            del self.active_games[message.channel.id]

    @commands.command()
    async def tictactoe(self, ctx):
        """Start a game of TicTacToe"""
        embed = EmbedBuilder(
        "🎮 TicTacToe Challenge",
        f"{ctx.author.mention} wants to play TicTacToe!\nClick Accept within 2 minutes to play."
    ).set_color(discord.Color.blue())
   
        view = discord.ui.View(timeout=120)
   
        async def accept_callback(interaction):
            if interaction.user == ctx.author:
                return
       
            overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }
       
            channel = await ctx.guild.create_text_channel(
            f"tictactoe-{ctx.author.name}-{interaction.user.name}",
            overwrites=overwrites
        )
       
            game_view = TicTacToeView(ctx.author, interaction.user)
            game_embed = EmbedBuilder(
            "🎮 TicTacToe",
            f"{ctx.author.mention} vs {interaction.user.mention}\n{ctx.author.mention}'s turn!"
        ).set_color(discord.Color.blue())
       
            await interaction.response.defer()
            message = await channel.send(embed=game_embed.build(), view=game_view)
            game_view.message = message
            await interaction.message.delete()

        accept_button = discord.ui.Button(
        label="Accept Challenge",
        style=discord.ButtonStyle.green,
        emoji="✅"
    )
        accept_button.callback = accept_callback
        view.add_item(accept_button)
   
        await ctx.send(embed=embed.build(), view=view)

    @commands.command()
    async def joke(self, ctx):
        """Tell a random joke from our collection"""
        try:
            with open('jokes.txt', 'r', encoding='utf-8') as file:
                jokes = [joke.strip() for joke in file.readlines() if joke.strip()]
            
            if not jokes:
                return await ctx.send("The joke book is empty! 📚")
                
            random_joke = random.choice(jokes)
            setup, punchline = random_joke.split('<>')
            
            embed = EmbedBuilder(
                "😄 Here's a joke!",
                setup.strip()
            ).set_color(discord.Color.blue())
            
            view = discord.ui.View(timeout=60)
            reveal_button = discord.ui.Button(
                label="Reveal Punchline",
                style=discord.ButtonStyle.green,
                emoji="🎭"
            )
            
            async def reveal_callback(interaction):
                if interaction.user != ctx.author:
                    return
                
                reveal_embed = EmbedBuilder(
                    "😄 Here's a joke!",
                    f"{setup.strip()}\n\n**{punchline.strip()}**"
                ).set_color(discord.Color.blue())
                
                await interaction.response.edit_message(embed=reveal_embed.build(), view=None)
            
            reveal_button.callback = reveal_callback
            view.add_item(reveal_button)
            
            await ctx.send(embed=embed.build(), view=view)
            
        except FileNotFoundError:
            await ctx.send("Oops! I couldn't find my joke book! 📚")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")


def setup(bot):
    bot.add_cog(MinigamesCog(bot))

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def serialize_color(self, config_dict):
        """Convert Color objects to serializable format"""
        if isinstance(config_dict, dict):
            for key, value in config_dict.items():
                if isinstance(value, discord.Color):
                    config_dict[key] = value.value
                elif isinstance(value, dict):
                    self.serialize_color(value)
        return config_dict

    def deserialize_color(self, config_dict):
        """Convert serialized colors back to Color objects"""
        if isinstance(config_dict, dict):
            for key, value in config_dict.items():
                if key == "color" and isinstance(value, int):
                    config_dict[key] = discord.Color(value)
                elif isinstance(value, dict):
                    self.deserialize_color(value)
        return config_dict

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def exportconfig(self, ctx):
        """Export server configuration to a JSON file"""
        welcome_config = dict(self.bot.get_cog("WelcomeSystem").welcome_configs.get(ctx.guild.id, {}))
        analytics_cog = self.bot.get_cog("Analytics")
        snipe_cog = self.bot.get_cog("Snipe")
        logging_cog = self.bot.get_cog("CustomLogging")
        leveling_cog = self.bot.get_cog("LevelingSystem")
        mute_cog = self.bot.get_cog("MuteSystem")
        verification_cog = self.bot.get_cog("VerificationSystem")
        bot_verification_cog = self.bot.get_cog("BotVerificationSystem")


        bot_verification_config = {
        "bot_log_channels": bot_verification_cog.bot_log_channels if bot_verification_cog else {}
    }

        verification_config = {
        "pending_verifications": verification_cog.pending_verifications.get(ctx.guild.id, {}),
        "autorole": verification_cog.autorole_dict.get(ctx.guild.id),
        "log_channel": verification_cog.log_channels.get(str(ctx.guild.id)),
        "verification_logs": verification_cog.verification_logs.get(ctx.guild.id, {})
            }

        logging_config = logging_cog.logging_config.get(ctx.guild.id, {}) if logging_cog else {}

        analytics_config = {
            "daily_channel": analytics_cog.analytics_channels.get(ctx.guild.id, {}).get("daily").id if analytics_cog and isinstance(analytics_cog.analytics_channels.get(ctx.guild.id, {}).get("daily"), discord.TextChannel) else None,
            "weekly_channel": analytics_cog.analytics_channels.get(ctx.guild.id, {}).get("weekly").id if analytics_cog and isinstance(analytics_cog.analytics_channels.get(ctx.guild.id, {}).get("weekly"), discord.TextChannel) else None,
            "monthly_channel": analytics_cog.analytics_channels.get(ctx.guild.id, {}).get("monthly").id if analytics_cog and isinstance(analytics_cog.analytics_channels.get(ctx.guild.id, {}).get("monthly"), discord.TextChannel) else None
        }

        snipe_config = {
            "snipe_duration": snipe_cog.snipe_duration if snipe_cog else 0,
            "editsnipe_duration": snipe_cog.editsnipe_duration if snipe_cog else 0
        }

        leveling_config = {
            "roles": leveling_cog.roles.get(ctx.guild.id, {}) if leveling_cog else {},

            "xp_multipliers": leveling_cog.xp_multipliers.get(ctx.guild.id, {}) if leveling_cog else {},

            "leaderboard_channel_id": leveling_cog.leaderboard_channels.get(ctx.guild.id) if leveling_cog else None,
            "announcement_channel_id": leveling_cog.announcement_channels.get(ctx.guild.id) if leveling_cog else None,
            "achievements": leveling_cog.achievements.get(ctx.guild.id, {}) if leveling_cog else {},
            "xp_decay_rate": leveling_cog.xp_decay_rate if leveling_cog else 0,
            "xp_gain_range": leveling_cog.xp_gain_range if leveling_cog else [0, 0]
        }


        mute_config = {}
        if mute_cog and hasattr(mute_cog, 'mute_roles'):
            guild_mute_roles = mute_cog.mute_roles
            if ctx.guild.id in guild_mute_roles:
                mute_config["mute_roles"] = guild_mute_roles[ctx.guild.id]
            else:
                mute_config["mute_roles"] = {}

        config = {
            "bot_verification_config": bot_verification_config,
            "verification_config": verification_config,
            "server_id": ctx.guild.id,
            "server_name": ctx.guild.name,
            "timestamp": str(datetime.now()),
            "welcome_config": self.serialize_color(welcome_config),
            "autorole": self.bot.get_cog("ServerManagement").autorole_dict.get(ctx.guild.id),
            "ticket_config": {
                "support_roles": self.bot.get_cog("TicketSystem").support_roles.get(ctx.guild.id),
                "admin_roles": self.bot.get_cog("TicketSystem").admin_roles.get(ctx.guild.id, [])
            },
            "automod": {
                "caps_threshold": self.bot.get_cog("AutoMod").caps_threshold,
                "spam_threshold": getattr(self.bot.get_cog("AutoMod"), 'spam_threshold', 5),
                "spam_interval": getattr(self.bot.get_cog("AutoMod"), 'spam_interval', 5),
                "spam_timeout_minutes": getattr(self.bot.get_cog("AutoMod"), 'spam_timeout_minutes', 10), 
                "banned_words": list(self.bot.get_cog("AutoMod").banned_words),
                "link_whitelist": list(self.bot.get_cog("AutoMod").link_whitelist)
            },
            "mute_config": mute_config,
            "role_configs": self.serialize_color(dict(self.bot.get_cog("RoleManager").role_configs.get(ctx.guild.id, {}))),
            "analytics_config": analytics_config,
            "snipe_config": snipe_config,
            "logging_config": logging_config,
            "leveling_config": leveling_config
        }

        filename = f"config_{ctx.guild.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        file = discord.File(filename)
        embed = discord.Embed(
            title="⚙️ Configuration Exported",
            description=f"Complete server settings exported for {ctx.guild.name}",
            color=discord.Color.green()
        )
        embed.add_field(name="Included Settings",
                    value="• Welcome System\n• Ticket System\n• AutoMod\n• Role Management\n• Server Management\n• Analytics\n• Snipe Configurations\n• Leveling System\n• Mute System\n• Verification System")

        embed.add_field(name="Export Time", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        embed.set_footer(text=f"Server ID: {ctx.guild.id}")

        await ctx.send(embed=embed, file=file)
        os.remove(filename)

    @commands.command()                                          # FULLY FIXED
    @commands.has_permissions(administrator=True)
    async def importconfig(self, ctx):
        """Import server configuration from a JSON file"""
        if not ctx.message.attachments:
            await ctx.send("Please attach a configuration file!")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith('.json'):
            await ctx.send("Please provide a valid JSON file!")
            return

        try:
            config_content = await attachment.read()
            config = json.loads(config_content)

            if config["server_id"] != ctx.guild.id:
                await ctx.send("This configuration file is for a different server!")
                return

            welcome_config = self.deserialize_color(config["welcome_config"])
            self.bot.get_cog("WelcomeSystem").welcome_configs[ctx.guild.id] = welcome_config

            if config["autorole"]:
                self.bot.get_cog("ServerManagement").autorole_dict[ctx.guild.id] = config["autorole"]

            if config["ticket_config"]["support_roles"]:
                self.bot.get_cog("TicketSystem").support_roles[ctx.guild.id] = config["ticket_config"]["support_roles"]
            if config["ticket_config"].get("admin_roles"):
                self.bot.get_cog("TicketSystem").admin_roles[ctx.guild.id] = config["ticket_config"]["admin_roles"]

            automod = self.bot.get_cog("AutoMod")
            if automod:
                automod.caps_threshold = config["automod"]["caps_threshold"]
                automod.spam_threshold = config["automod"]["spam_threshold"]
                automod.spam_interval = config["automod"].get("spam_interval", 5)
                automod.spam_timeout_minutes = config["automod"].get("spam_timeout_minutes", 10)
                automod.banned_words = set(config["automod"]["banned_words"])
                automod.link_whitelist = set(config["automod"]["link_whitelist"])

            role_configs = self.deserialize_color(config["role_configs"])
            self.bot.get_cog("RoleManager").role_configs[ctx.guild.id] = role_configs

            analytics_cog = self.bot.get_cog("Analytics")
            if analytics_cog and "analytics_config" in config:
                analytics_config = config["analytics_config"]
                analytics_cog.analytics_channels[ctx.guild.id] = {}
                
                for interval in ['daily', 'weekly', 'monthly']:
                    channel_id = analytics_config.get(f"{interval}_channel")
                    if channel_id:
                        channel = ctx.guild.get_channel(channel_id)
                        if channel:
                            analytics_cog.analytics_channels[ctx.guild.id][interval] = channel
                            
                            task_key = f"{ctx.guild.id}_{interval}"
                            if task_key not in analytics_cog.analytics_tasks or analytics_cog.analytics_tasks[task_key].done():
                                analytics_cog.analytics_tasks[task_key] = self.bot.loop.create_task(
                                    analytics_cog._send_analytics(ctx.guild.id, interval)
                                )
                                print(f"Started analytics task for {interval} in guild {ctx.guild.id}")

            bot_verification_cog = self.bot.get_cog("BotVerificationSystem")
            if bot_verification_cog and "bot_verification_config" in config:
                bot_verification_cog.bot_log_channels = config["bot_verification_config"].get("bot_log_channels", {})

            snipe_cog = self.bot.get_cog("Snipe")
            if snipe_cog and "snipe_config" in config:
                snipe_cog.snipe_duration = config["snipe_config"]["snipe_duration"]
                snipe_cog.editsnipe_duration = config["snipe_config"]["editsnipe_duration"]

            mute_cog = self.bot.get_cog("MuteSystem")
            if mute_cog and "mute_config" in config:
                mute_config = config["mute_config"]
                mute_cog.mute_roles[ctx.guild.id] = mute_config.get("mute_roles", {})
           
            leveling_cog = self.bot.get_cog("LevelingSystem")
            if leveling_cog and "leveling_config" in config:
                leveling_config = config["leveling_config"]
                leveling_cog.roles[ctx.guild.id] = leveling_config.get("roles", {})


                leveling_cog.xp_multipliers[ctx.guild.id] = {
                    k: float(v) if isinstance(v, (int, float, str)) else 1.0 
                    for k, v in leveling_config.get("xp_multipliers", {}).items()
                }


                leveling_cog.leaderboard_channels[ctx.guild.id] = leveling_config.get("leaderboard_channel_id")
                leveling_cog.announcement_channels[ctx.guild.id] = leveling_config.get("announcement_channel_id")
                leveling_cog.achievements[ctx.guild.id] = leveling_config.get("achievements", {})
                leveling_cog.xp_decay_rate = leveling_config.get("xp_decay_rate", 0.01)
                leveling_cog.xp_gain_range = leveling_config.get("xp_gain_range", (15, 25))

                if leveling_config.get("leaderboard_channel_id"):
                    leaderboard_channel = ctx.guild.get_channel(leveling_config["leaderboard_channel_id"])
                    if leaderboard_channel:
                        await leveling_cog.update_leaderboard(leaderboard_channel)

            verification_cog = self.bot.get_cog("VerificationSystem")
            if verification_cog and "verification_config" in config:
                verif_config = config["verification_config"]
                verification_cog.pending_verifications[ctx.guild.id] = verif_config.get("pending_verifications", {})
                verification_cog.autorole_dict[ctx.guild.id] = verif_config.get("autorole")
                verification_cog.verification_logs[ctx.guild.id] = verif_config.get("verification_logs", {})
                
                if "log_channel" in verif_config:
                    channel_id = verif_config["log_channel"]
                    if isinstance(channel_id, str):
                        channel_id = int(channel_id)
                    verification_cog.log_channels[str(ctx.guild.id)] = channel_id

            logging_cog = self.bot.get_cog("CustomLogging")
            if logging_cog and "logging_config" in config:
                logging_cog.logging_config[ctx.guild.id] = config["logging_config"]

            embed = EmbedBuilder(
                "✅ Configuration Imported",
                f"All server settings have been restored for {ctx.guild.name}"
            ).set_color(discord.Color.green())

            embed.add_field("Restored Settings",
            "• Welcome System\n• Ticket System\n• AutoMod\n• Role Management\n• Server Management\n• Analytics\n• Snipe Configurations\n• Custom Logging\n• Leveling System\n• Mute System\n• Verification System")
            embed.add_field("Import Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            embed.set_footer(f"Server ID: {ctx.guild.id}")

            await ctx.send(embed=embed.build())

        except json.JSONDecodeError:
            await ctx.send("Invalid JSON file format!")
        except KeyError as e:
            await ctx.send(f"Missing required configuration key: {e}")
        except Exception as e:
            await ctx.send(f"An error occurred during import: {str(e)}")

bot.add_cog(Config(bot))

class BackupSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx, full: bool = False, messages_limit: int = 100):
        """Create comprehensive server backup"""
        progress_msg = await ctx.send("📦 Starting backup process...")

        backup_data = {
        "server_name": ctx.guild.name,
        "server_icon": str(ctx.guild.icon.url) if ctx.guild.icon else None,
        "server_banner": str(ctx.guild.banner.url) if ctx.guild.banner else None,
        "roles": [],
        "categories": [],
        "channels": [],
        "emojis": [],
        "webhooks": [],
        "settings": {},
        "messages": [] if full else None,
        "timestamp": str(datetime.now())
    }

        await progress_msg.edit(content="📦 Backing up roles...")
        for role in reversed(ctx.guild.roles):
            if not role.is_default():
                backup_data["roles"].append({
                "name": role.name,
                "color": str(role.color),
                "permissions": int(role.permissions.value),  
                "position": role.position,
                "mentionable": role.mentionable,
                "hoist": role.hoist
            })

        await progress_msg.edit(content="📦 Backing up channels and categories...")
        for category in ctx.guild.categories:
            cat_data = {
            "name": category.name,
            "position": category.position,
            "channels": []
        }

            for channel in category.channels:
                chan_data = {
                "name": channel.name,
                "type": str(channel.type),
                "position": channel.position,
                "topic": getattr(channel, 'topic', None),
                "slowmode_delay": getattr(channel, 'slowmode_delay', None),
                "nsfw": getattr(channel, 'nsfw', False),
                "overwrites": []
            }

                for target, overwrite in channel.overwrites.items():
                    allow, deny = overwrite.pair()
                    chan_data["overwrites"].append({
                    "target_name": target.name,
                    "permissions": [int(allow.value), int(deny.value)]  
                })

                if full and isinstance(channel, discord.TextChannel):
                    messages = []
                    try:
                        async for msg in channel.history(limit=messages_limit):
                            messages.append({
                            "content": msg.content,
                            "author": str(msg.author),
                            "timestamp": str(msg.created_at),
                            "attachments": [a.url for a in msg.attachments],
                            "embeds": [e.to_dict() for e in msg.embeds],
                            "pinned": msg.pinned
                        })
                    except discord.Forbidden:
                        pass
                    chan_data["messages"] = messages

                cat_data["channels"].append(chan_data)
            backup_data["categories"].append(cat_data)

        await progress_msg.edit(content="📦 Backing up emojis...")
        backup_data["emojis"] = [{
        "name": emoji.name,
        "url": str(emoji.url)
    } for emoji in ctx.guild.emojis]

        await progress_msg.edit(content="📦 Backing up webhooks...")
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    webhooks = await channel.webhooks()
                    backup_data["webhooks"].extend([{
                        "name": webhook.name,
                        "channel": channel.name,
                        "avatar": str(webhook.avatar.url) if webhook.avatar else None
                    } for webhook in webhooks])
                except discord.Forbidden:
                    pass

        backup_data["settings"] = {
        "verification_level": str(ctx.guild.verification_level),
        "explicit_content_filter": str(ctx.guild.explicit_content_filter),
        "default_notifications": str(ctx.guild.default_notifications),
        "afk_timeout": ctx.guild.afk_timeout,
        "afk_channel": ctx.guild.afk_channel.name if ctx.guild.afk_channel else None
    }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{ctx.guild.id}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=4)

        file = discord.File(filename, filename=filename)

        embed = EmbedBuilder(
        "📦 Server Backup Complete",
        f"Backup completed for {ctx.guild.name}"
    ).set_color(discord.Color.green())

        embed.add_field("Roles", str(len(backup_data["roles"])))
        embed.add_field("Categories", str(len(backup_data["categories"])))
        embed.add_field("Emojis", str(len(backup_data["emojis"])))
        embed.add_field("Webhooks", str(len(backup_data["webhooks"])))
        if full:
            embed.add_field("Messages", f"Up to {messages_limit} per channel")

        await progress_msg.delete()
        await ctx.send(embed=embed.build(), file=file)
        os.remove(filename)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def restore(self, ctx):
        """Restore server from backup file"""
        if not ctx.message.attachments:
            await ctx.send("Please attach a backup file with this command!")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith('.json'):
            await ctx.send("Please provide a valid backup file (.json)")
            return

        progress_msg = await ctx.send("🔄 Starting restoration process...")
        backup_content = await attachment.read()
        backup_data = json.loads(backup_content)

        bot_member = ctx.guild.get_member(ctx.bot.user.id)
        if not bot_member.guild_permissions.administrator:
            await ctx.send("I need Administrator permissions to perform a full restore!")
            return

        try:
            bot_role = bot_member.top_role
            positions = {r: r.position for r in ctx.guild.roles}
            positions[bot_role] = len(positions) - 1 
            await ctx.guild.edit_role_positions(positions=positions)
        except Exception as e:
            print(f"Could not move bot role: {e}")

        try:
            temp_channel = await ctx.guild.create_text_channel('temp-restore-status')
            progress_msg = await temp_channel.send("🔄 Starting restoration process...")
        except Exception as e:
            print(f"Could not create temporary channel: {e}")
            return

        await progress_msg.edit(content="🗑️ Cleaning up existing server content...")
    
        temp_channel_id = temp_channel.id
        try:
            for channel in ctx.guild.channels:
                if channel.id != temp_channel_id:
                    try:
                        await channel.delete()
                        await asyncio.sleep(0.5)
                    except discord.NotFound:
                        continue
        except Exception as e:
            print(f"Error during channel cleanup: {e}")

        try:
            for role in reversed(ctx.guild.roles[1:]):
                try:
                    await role.delete()
                    await asyncio.sleep(0.5)
                except discord.NotFound:
                    continue
        except Exception as e:
            print(f"Error during role cleanup: {e}")

        try:
            for emoji in ctx.guild.emojis:
                try:
                    await emoji.delete()
                    await asyncio.sleep(0.5)
                except discord.NotFound:
                    continue
        except Exception as e:
            print(f"Error during emoji cleanup: {e}")

        await progress_msg.edit(content="🔄 Restoring roles...")
        roles_cache = {}
        for role_data in reversed(backup_data["roles"]):
            try:
                role = await ctx.guild.create_role(
                    name=role_data["name"],
                    color=discord.Color.from_str(role_data["color"]),
                    permissions=discord.Permissions(role_data["permissions"]),
                    hoist=role_data["hoist"],
                    mentionable=role_data["mentionable"]
                )
                roles_cache[role_data["name"]] = role
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error creating role {role_data['name']}: {e}")

        total_categories = len(backup_data["categories"])
        for cat_index, cat_data in enumerate(backup_data["categories"], 1):
            try:
                category = await ctx.guild.create_category(name=cat_data["name"])
                await progress_msg.edit(content=f"📁 Creating categories... ({cat_index}/{total_categories})")

                total_channels = len(cat_data["channels"])
                for chan_index, chan_data in enumerate(cat_data["channels"], 1):
                    try:
                        if chan_data["type"] == "text":
                            channel = await category.create_text_channel(
                            name=chan_data["name"],
                            topic=chan_data.get("topic"),
                            nsfw=chan_data.get("nsfw", False),
                            slowmode_delay=chan_data.get("slowmode_delay", 0)
                        )

                            for overwrite in chan_data.get("overwrites", []):
                                role = roles_cache.get(overwrite["target_name"])
                                if role:
                                    allow, deny = overwrite["permissions"]
                                    await channel.set_permissions(
                                        role,
                                        overwrite=discord.PermissionOverwrite.from_pair(
                                        discord.Permissions(allow),
                                        discord.Permissions(deny)
                                    )
                                )

                            if "messages" in chan_data:
                                webhook = await channel.create_webhook(name="RestoreBot")
                                for msg_data in reversed(chan_data["messages"]):
                                    try:
                                        await webhook.send(
                                        content=msg_data["content"],
                                        username=msg_data["author"],
                                        embeds=[discord.Embed.from_dict(e) for e in msg_data.get("embeds", [])]
                                    )
                                        await asyncio.sleep(0.5)
                                    except Exception as e:
                                        print(f"Error restoring message: {e}")
                                await webhook.delete()

                        elif chan_data["type"] == "voice":
                            channel = await category.create_voice_channel(name=chan_data["name"])
                        
                            for overwrite in chan_data.get("overwrites", []):
                                role = roles_cache.get(overwrite["target_name"])
                                if role:
                                    allow, deny = overwrite["permissions"]
                                    await channel.set_permissions(
                                        role,
                                        overwrite=discord.PermissionOverwrite.from_pair(
                                        discord.Permissions(allow),
                                        discord.Permissions(deny)
                                    )
                                )

                        if chan_index % 5 == 0:
                            await progress_msg.edit(content=f"💬 Creating channels in {cat_data['name']}... ({chan_index}/{total_channels})")
                    
                        await asyncio.sleep(0.5)

                    except Exception as e:
                        print(f"Error creating channel {chan_data['name']}: {e}")
                        continue

            except Exception as e:
                print(f"Error creating category {cat_data['name']}: {e}")
                continue

        await progress_msg.edit(content="🔄 Restoring emojis...")
        async with aiohttp.ClientSession() as session:
            total_emojis = len(backup_data["emojis"])
            for emoji_index, emoji_data in enumerate(backup_data["emojis"], 1):
                try:
                    async with session.get(emoji_data["url"]) as resp:
                        if resp.status == 200:
                            emoji_bytes = await resp.read()
                            await ctx.guild.create_custom_emoji(
                            name=emoji_data["name"],
                            image=emoji_bytes
                        )
                    if emoji_index % 5 == 0:
                        await progress_msg.edit(content=f"🔄 Restoring emojis... ({emoji_index}/{total_emojis})")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Error restoring emoji {emoji_data['name']}: {e}")

        await progress_msg.edit(content="🔄 Restoring webhooks...")
        for webhook_data in backup_data["webhooks"]:
            try:
                channel = discord.utils.get(ctx.guild.channels, name=webhook_data["channel"])
                if channel and isinstance(channel, discord.TextChannel):
                    await channel.create_webhook(
                    name=webhook_data["name"],
                    avatar=webhook_data.get("avatar")
                )
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error restoring webhook {webhook_data['name']}: {e}")

        embed = EmbedBuilder(
        "✅ Restoration Complete",
        "Server has been restored from backup"
    ).set_color(discord.Color.green())

        await progress_msg.delete()
        await ctx.send(embed=embed.build())

bot.add_cog(BackupSystem(bot))

class EmbedBuilder:
    def __init__(self, title, description=None):
        self.embed = discord.Embed(
            title=title,
            description=description,
            timestamp=datetime.now(timezone.utc)
        )
        self.set_default_color()

    def set_image(self, url):
        self.embed.set_image(url=url)
        return self

        
    def set_default_color(self):
        self.embed.color = discord.Color.blue()
        return self
        
    def add_field(self, name, value, inline=True):
        self.embed.add_field(name=name, value=value, inline=inline)
        return self
        
    def set_color(self, color):
        self.embed.color = color
        return self
        
    def set_thumbnail(self, url):
        self.embed.set_thumbnail(url=url)
        return self
        
    def set_footer(self, text, icon_url=None):
        self.embed.set_footer(text=text, icon_url=icon_url)
        return self
        
    def build(self):
        return self.embed

class LoggingManager:
    def __init__(self, bot):
        self.bot = bot
        self.log_types = {
            'ban': ('🔨 Ban', discord.Color.red()),
            'kick': ('👢 Kick', discord.Color.orange()),
            'mute': ('🔇 Mute', discord.Color.yellow()),
            'warn': ('⚠️ Warning', discord.Color.gold()),
            'clear': ('🧹 Clear', discord.Color.blue()),
            'lockdown': ('🔒 Lockdown', discord.Color.purple())
        }
        
    async def log_action(self, guild, action_type, moderator, target, reason=None, duration=None):
        log_channel = discord.utils.get(guild.channels, name='mod-logs')
        if not log_channel:
            return
            
        emoji, color = self.log_types.get(action_type, ('📝 Action', discord.Color.default()))
        
        embed = EmbedBuilder(
            f"{emoji} {action_type.title()} Action",
            f"A moderation action has been taken."
        ).set_color(color)
        
        embed.add_field("Moderator", f"{moderator.name} ({moderator.id})")
        embed.add_field("Target", f"{target.name} ({target.id})")
        
        if duration:
            embed.add_field("Duration", duration)
        if reason:
            embed.add_field("Reason", reason, inline=False)
            
        embed.set_footer(f"Action ID: {random.randint(10000, 99999)}")
        
        await log_channel.send(embed=embed.build())

log_manager = LoggingManager(bot)

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = EmbedBuilder(
                "❌ Permission Denied",
                "You don't have the required permissions for this command."
            ).set_color(discord.Color.red()).build()
            
        elif isinstance(error, commands.MemberNotFound):
            embed = EmbedBuilder(
                "❌ Member Not Found",
                "The specified member could not be found."
            ).set_color(discord.Color.red()).build()
            
        else:
            embed = EmbedBuilder(
                "❌ Error",
                f"An error occurred: {str(error)}"
            ).set_color(discord.Color.red()).build()
            
        await ctx.send(embed=embed, delete_after=10)

bot.add_cog(CommandErrorHandler(bot))

import os
import json
from discord.ext import commands

class MuteSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_roles = {}
        self.data_file = "mute_data.json"
        self.load_data()

    def load_data(self):
        """Load mute roles from JSON if the file exists."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                try:
                    data = json.load(f)
                    self.mute_roles = {int(k): int(v) for k, v in data.get('mute_roles', {}).items()}
                    print(f"Loaded mute roles: {self.mute_roles}")
                except json.JSONDecodeError:
                    print(f"Failed to decode {self.data_file}, starting with empty roles.")
                    self.mute_roles = {}

    def save_data(self):
        """Save mute roles to JSON."""
        with open(self.data_file, 'w') as f:
            json.dump({'mute_roles': {str(k): v for k, v in self.mute_roles.items()}}, f, indent=4)
        print(f"Saved mute roles: {self.mute_roles}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Notify when the cog is ready."""
        print(f"{self.__class__.__name__} is ready with roles: {self.mute_roles}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_mute_role(self, ctx, role_id: int):
        """Manually set the mute role for the current guild."""
        self.mute_roles[ctx.guild.id] = role_id
        self.save_data()
        await ctx.send(f"✅ Mute role set to <@&{role_id}> for this server.")



class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_roles = {}
        self.data_file = "moderation_data.json"
        self.load_data()
        


    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.mute_roles = data.get('mute_roles', {})

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump({
                'mute_roles': self.mute_roles
            }, f, indent=4)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def invite_view(self, ctx):
        """View all active server invites and their details"""
        invites = await ctx.guild.invites()
    
        embed = EmbedBuilder(
        "🔗 Server Invites",
        f"Total active invites: {len(invites)}"
    ).set_color(discord.Color.blue())

        for invite in invites:
            time_left = "Unlimited"
            if invite.max_age > 0:
                if invite.created_at:
                
                    now = datetime.utcnow().replace(tzinfo=timezone.utc)
                    expires_at = invite.created_at + timedelta(seconds=invite.max_age)
                    if expires_at > now:
                        time_left = str(expires_at - now).split('.')[0]
                    else:
                        time_left = "Expired"
                    
            uses_info = f"{invite.uses}/{invite.max_uses}" if invite.max_uses else f"{invite.uses}/∞"
        
            invite_info = (
            f"Channel: {invite.channel.mention}\n"
            f"Creator: {invite.inviter.mention}\n"
            f"Duration: {time_left}\n"
            f"Uses: {uses_info}\n"
            f"Created: {invite.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
            embed.add_field(
            f"Invite: {invite.code}",
            invite_info,
            inline=False
        )

        await ctx.send(embed=embed.build())

    @commands.command()
    @commands.has_permissions(create_instant_invite=True)
    async def invite(self, ctx, duration: int = 0, uses: int = 0):
        """Create an invite link with optional duration and uses limit
        Usage: !invite [duration in minutes] [number of uses]
        Use 0 for unlimited duration/uses"""
    
        try:
            invite = await ctx.channel.create_invite(
            max_age=duration * 60 if duration > 0 else 0,
            max_uses=uses if uses > 0 else 0
        )
        
            embed = EmbedBuilder(
            "🔗 Invite Created",
            f"Here's your invite link: {invite.url}"
        ).set_color(discord.Color.green())
        
            embed.add_field(
            "Duration", 
            "Unlimited" if duration == 0 else f"{duration} minutes"
        )
            embed.add_field(
            "Uses",
            "Unlimited" if uses == 0 else str(uses)
        )
        
            await ctx.send(embed=embed.build())
        
        except discord.Forbidden:
            embed = EmbedBuilder(
            "❌ Error",
            "I don't have permission to create invites in this channel"
        ).set_color(discord.Color.red())
            await ctx.send(embed=embed.build())

    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def addchannel(self, ctx, channel: discord.TextChannel, member: discord.Member):
        """Add a member to a channel"""
        await channel.set_permissions(member, read_messages=True, send_messages=True)
        embed = EmbedBuilder(
        "✅ Channel Access Granted",
        f"{member.mention} has been added to {channel.mention}"
    ).set_color(discord.Color.green()).build()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def removechannel(self, ctx, channel: discord.TextChannel, member: discord.Member):
        """Remove a member from a channel"""
        await channel.set_permissions(member, read_messages=False, send_messages=False)
        embed = EmbedBuilder(
        "🚫 Channel Access Removed",
        f"{member.mention} has been removed from {channel.mention}"
    ).set_color(discord.Color.red()).build()
        await ctx.send(embed=embed)

    @commands.command()
    async def poll(self, ctx, question, *options):
        """Create a poll with reactions"""
        if len(options) > 10:
            return await ctx.send("Maximum 10 options allowed!")
        
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
        description = []
        for i, option in enumerate(options):
            description.append(f"{reactions[i]} {option}")
        
        embed = EmbedBuilder(
        f"📊 {question}",
        "\n".join(description)
    ).set_color(discord.Color.blue())
        embed.set_footer(f"Poll by {ctx.author.name}")
    
        poll_msg = await ctx.send(embed=embed.build())
        for i in range(len(options)):
            await poll_msg.add_reaction(reactions[i])

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def embed(self, ctx, title, *, description):
        """Create a custom embed message"""
        embed = EmbedBuilder(
        title,
        description
    ).set_color(discord.Color.blue()).build()
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """Show user's avatar in full size"""
        member = member or ctx.author
        embed = EmbedBuilder(
        f"{member.name}'s Avatar",
        ""
    ).set_color(member.color)
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed.build())

    @commands.command()
    async def ping(self, ctx):
        """Check bot's latency"""
        embed = EmbedBuilder(
        "🏓 Pong!",
        f"Latency: {round(self.bot.latency * 1000)}ms"
    ).set_color(discord.Color.green()).build()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def say(self, ctx, channel: discord.TextChannel, *, message):
        """Make the bot say something in a specific channel"""
        await channel.send(message)
        await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        """Recreates a channel to completely clear it"""
        channel = channel or ctx.channel
        position = channel.position
        new_channel = await channel.clone()
        await new_channel.edit(position=position)
        await channel.delete()
    
        embed = EmbedBuilder(
        "💥 Channel Nuked",
        "Channel has been completely reset"
    ).set_color(discord.Color.orange()).build()
        await new_channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def vcmute(self, ctx, member: discord.Member):
        """Mute someone in voice chat"""
        await member.edit(mute=True)
        embed = EmbedBuilder(
        "🔇 Voice Muted",
        f"{member.mention} has been muted in voice channels"
    ).set_color(discord.Color.red()).build()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def vcunmute(self, ctx, member: discord.Member):
        """Unmute someone in voice chat"""
        await member.edit(mute=False)
        embed = EmbedBuilder(
        "🔊 Voice Unmuted", 
        f"{member.mention} has been unmuted in voice channels"
    ).set_color(discord.Color.green()).build()
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def massrole(self, ctx, role: discord.Role):
        """Add a role to all members"""
        for member in ctx.guild.members:
            await member.add_roles(role)
    
        embed = EmbedBuilder(
        "✅ Mass Role Added",
        f"Added {role.mention} to all members"
    ).set_color(discord.Color.blue()).build()
        await ctx.send(embed=embed)

    @commands.command()
    async def servericon(self, ctx):
        """Shows the server icon in full size"""
        embed = EmbedBuilder(
        "🖼️ Server Icon",
        ctx.guild.name
    ).set_color(discord.Color.blue())

        if ctx.guild.icon:  
            embed.set_image(url=ctx.guild.icon.url)
        else:
            embed.description = "This server has no custom icon."
            embed.set_image(url="https://cdn.discordapp.com/embed/avatars/0.png")  

        await ctx.send(embed=embed.build())


    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, user_id: int, *, nickname=None):
        """Change or remove a user's nickname.
        Usage:
        - !nickname <user_id> <nickname>: Change the user's nickname.
        - !nickname <user_id>: Remove the user's nickname.
        """
        member = ctx.guild.get_member(user_id)
        if not member:
            await ctx.send("❌ User not found in this server.")
            return

        try:
            if nickname:  
                await member.edit(nick=nickname)
                embed = EmbedBuilder(
                    "✅ Nickname Changed",
                    f"{member.mention}'s nickname has been changed to '{nickname}'."
                ).set_color(discord.Color.green())
            else:  
                await member.edit(nick=None)
                embed = EmbedBuilder(
                    "✅ Nickname Removed",
                    f"{member.mention}'s nickname has been removed."
                ).set_color(discord.Color.green())

        except discord.Forbidden:
            embed = EmbedBuilder(
                "❌ Permission Denied",
                "I don't have permission to change nicknames for this user."
            ).set_color(discord.Color.red())

        except discord.HTTPException as e:
            embed = EmbedBuilder(
                "❌ Failed to Change Nickname",
                f"An error occurred: {str(e)}"
            ).set_color(discord.Color.red())

        await ctx.send(embed=embed.build())

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User | int, *, reason="No reason provided"):
        if isinstance(user, int):
            try:
                user = await self.bot.fetch_user(user)
            except discord.NotFound:
                await ctx.send("User not found.")
                return

        embed = EmbedBuilder(
            "⚡ Ban Hammer Struck!",
            f"{user.mention} has been banned from the server."
        ).set_color(discord.Color.dark_red())

        embed.add_field("Target", f"{user.name} ({user.id})")
        embed.add_field("Moderator", ctx.author.mention)
        embed.add_field("Reason", reason, inline=False)
        embed.set_thumbnail(user.avatar.url)

        try:
            dm_embed = EmbedBuilder(
                "🚫 You've Been Banned",
                f"You were banned from {ctx.guild.name}"
            ).set_color(discord.Color.red())
            dm_embed.add_field("Reason", reason)
            dm_embed.add_field("Appeal", "https://discord.gg/4A3MBZrxJM (Appeal Server)")
            await user.send(embed=dm_embed.build())
        except:
            embed.add_field("Note", "⚠️ Could not DM user", inline=False)

        await ctx.guild.ban(user, reason=f"{reason} | By {ctx.author}")
        await ctx.send(embed=embed.build())

        logging_cog = self.bot.get_cog("CustomLogging")
        if logging_cog:
            await logging_cog.log_action(ctx.guild, 'ban', ctx.author, user, reason)



    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason="No reason provided"):
        embed = EmbedBuilder(
            "👢 Member Kicked",
            f"{user.mention} has been kicked from the server."
        ).set_color(discord.Color.orange())

        embed.add_field("Target", f"{user.name} ({user.id})")
        embed.add_field("Moderator", ctx.author.mention)
        embed.add_field("Reason", reason, inline=False)

        await user.kick(reason=f"{reason} | By {ctx.author}")
        await ctx.send(embed=embed.build())

        logging_cog = self.bot.get_cog("CustomLogging")
        if logging_cog:
            await logging_cog.log_action(ctx.guild, 'kick', ctx.author, user, reason)



    @commands.command()
    @commands.has_permissions(administrator=True)
    async def mutesetup(self, ctx, role: discord.Role = None):
        """Setup the mute system with a custom role"""
        guild_id = ctx.guild.id
        
        if role:
            self.mute_roles[guild_id] = role.id
            self.save_data()
            embed = discord.Embed(
                title="✅ Mute System Setup",
                description=f"Muted members will now receive the {role.mention} role",
                color=discord.Color.green()
            )
        else:
            
            embed = discord.Embed(
                title="🔇 Mute System Configuration",
                description="Current mute system settings",
                color=discord.Color.blue()
            )
            
            current_role = ctx.guild.get_role(self.mute_roles.get(guild_id))
            embed.add_field(
                name="Mute Role",
                value=current_role.mention if current_role else "Not set",
                inline=False
            )
            
        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        """Unmute a member with optional reason and success notification"""
        guild_id = ctx.guild.id
        
        if guild_id in self.mute_roles:
            mute_role = ctx.guild.get_role(self.mute_roles[guild_id])
            if mute_role and mute_role in member.roles:
                await member.remove_roles(mute_role)
        
        await member.timeout(None, reason=reason)

        embed = discord.Embed(
            title="🔊 Member Unmuted",
            description=f"**Member:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason or 'No reason provided'}",
            color=discord.Color.green()
        )
        msg = await ctx.send(embed=embed)

        logging_cog = self.bot.get_cog("CustomLogging")
        if logging_cog:
            await logging_cog.log_action(ctx.guild, 'unmute', ctx.author, member, reason)

        try:
            await member.send(f"You have been unmuted in {ctx.guild.name}")
        except:
            pass

        await asyncio.sleep(3)
        await msg.delete()

    @commands.command()
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.Member, duration: int, *, reason="No reason provided"):
        time_delta = timedelta(minutes=duration)
        guild_id = ctx.guild.id

        mute_role = None
        if guild_id in self.mute_roles:
            mute_role = ctx.guild.get_role(self.mute_roles[guild_id])

        embed = EmbedBuilder(
            "🔇 Member Muted",
            f"{user.mention} has been muted."
        ).set_color(discord.Color.yellow())

        embed.add_field("Duration", f"{duration} minutes")
        embed.add_field("Moderator", ctx.author.mention)
        embed.add_field("Reason", reason, inline=False)

        await user.timeout(time_delta, reason=reason)
        if mute_role:
            await user.add_roles(mute_role, reason=reason)
            embed.add_field("Role Applied", mute_role.mention, inline=False)

        await ctx.send(embed=embed.build())

        logging_cog = self.bot.get_cog("CustomLogging")
        if logging_cog:
            await logging_cog.log_action(ctx.guild, 'mute', ctx.author, user, reason, f"{duration} minutes")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason="No reason provided"):
        """Warn a user and notify them via DM"""
    
        embed = EmbedBuilder(
        "⚠️ Warning Issued",
        f"{user.mention} has been warned."
    ).set_color(discord.Color.orange())

        embed.add_field("User", f"{user.name} ({user.id})")
        embed.add_field("Moderator", ctx.author.mention)
        embed.add_field("Reason", reason, inline=False)

        await ctx.send(embed=embed.build())

        try:
            dm_embed = EmbedBuilder(
            "⚠️ You Have Been Warned",
            f"You have been warned in **{ctx.guild.name}**."
        ).set_color(discord.Color.red())

            dm_embed.add_field("Moderator", ctx.author.mention)
            dm_embed.add_field("Reason", reason, inline=False)
            dm_embed.set_footer("Please follow the server rules to avoid further action.")

            await user.send(embed=dm_embed.build())
        except:
            await ctx.send(f"⚠️ {user.mention} has DMs disabled. Unable to send warning via DM.")

        await log_manager.log_action(ctx.guild, "warn", ctx.author, user, reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="No reason provided"):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=f"{reason} | By {ctx.author}")
        
            embed = EmbedBuilder(
                "🔓 Member Unbanned",
                f"{user.name} has been unbanned from the server."
            ).set_color(discord.Color.green())
        
            embed.add_field("User ID", user_id)
            embed.add_field("Moderator", ctx.author.mention)
            embed.add_field("Reason", reason, inline=False)
        
            await ctx.send(embed=embed.build())
            await log_manager.log_action(ctx.guild, 'unban', ctx.author, user, reason)
        
        except discord.NotFound:
            embed = EmbedBuilder(
                "❌ User Not Found",
                f"No banned user found with ID: {user_id}"
            ).set_color(discord.Color.red()).build()
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        embed = EmbedBuilder(
            "🧹 Messages Cleared",
            f"Cleared {amount} messages"
        ).set_color(discord.Color.blue()).build()
        await ctx.send(embed=embed, delete_after=5)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, user_id: int, role: discord.Role):
        """Add a role to a member using their ID"""
        member = ctx.guild.get_member(user_id)
        if not member:
            embed = EmbedBuilder(
                "❌ User Not Found",
                f"No user found with ID: {user_id}"
            ).set_color(discord.Color.red()).build()
            return await ctx.send(embed=embed)
        
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = EmbedBuilder(
                "❌ Role Error",
                "You can't assign roles higher than your own!"
            ).set_color(discord.Color.red()).build()
            return await ctx.send(embed=embed)
        
        await member.add_roles(role)
        embed = EmbedBuilder(
            "✅ Role Added",
            f"Successfully added {role.mention} to {member.mention}"
        ).set_color(discord.Color.green())
        embed.add_field("User ID", user_id)
        embed.add_field("Moderator", ctx.author.mention)
        await ctx.send(embed=embed.build())

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, user_id: int, role: discord.Role):
        """Remove a role from a member using their ID"""
        member = ctx.guild.get_member(user_id)
        if not member:
            embed = EmbedBuilder(
                "❌ User Not Found",
                f"No user found with ID: {user_id}"
            ).set_color(discord.Color.red()).build()
            return await ctx.send(embed=embed)
        
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            embed = EmbedBuilder(
                "❌ Role Error",
                "You can't remove roles higher than your own!"
            ).set_color(discord.Color.red()).build()
            return await ctx.send(embed=embed)
        
        await member.remove_roles(role)
        embed = EmbedBuilder(
            "✅ Role Removed",
            f"Successfully removed {role.mention} from {member.mention}"
        ).set_color(discord.Color.green())
        embed.add_field("User ID", user_id)
        embed.add_field("Moderator", ctx.author.mention)
        await ctx.send(embed=embed.build())

class TicketView(discord.ui.View):
    def __init__(self, bot, button_style=discord.ButtonStyle.blurple):
        super().__init__(timeout=None)
        self.bot = bot
        self.button_style = button_style

    @discord.ui.button(label="Create Ticket", emoji="🎫", custom_id="create_ticket", style=discord.ButtonStyle.blurple)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = self.bot.get_cog('TicketSystem').TicketModal()
        await interaction.response.send_modal(modal)

class OwnerPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.authorized_id = int(os.getenv("BOT_OWNER_ID", "0"))

    @discord.ui.button(label="Owner Commands", style=discord.ButtonStyle.gray, emoji="🔒")
    async def show_owner_commands(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.authorized_id:
            return
            
        embed = EmbedBuilder(
            "🔒 Owner-Only Commands",
            "Exclusive commands for bot owner"
        ).set_color(discord.Color.purple())
        
        commands_list = {
            "!owner": "Open this interactive control panel",
            "!leaveserver <guild_id>": "Make bot leave a specific server",
            "!executecmd <guild_id> <channel_id> <command>": "Execute commands in other servers",
            "!botinfo": "View detailed bot statistics",
            "Interactive Buttons": {
                "📋 Server List": "View all servers with details",
                "📊 Statistics": "Real-time bot performance metrics",
                "⚙️ Server Management": "Access server management tools",
                "📢 Mass Message": "Send message to all servers",
                "⚡ Execute Command": "Run commands remotely",
                "🚪 Leave Server": "Remove bot from servers"
            }
        }
        
        for cmd, desc in commands_list.items():
            if isinstance(desc, dict):
                subcommands = "\n".join(f"• {subcmd}: {subdesc}" for subcmd, subdesc in desc.items())
                embed.add_field(cmd, subcommands, inline=False)
            else:
                embed.add_field(cmd, desc, inline=False)
        
        await interaction.response.send_message(embed=embed.build(), ephemeral=True)

    @discord.ui.button(label="Server List", style=discord.ButtonStyle.blurple, emoji="📋")
    async def show_servers(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.authorized_id:
            return
            
        embed = EmbedBuilder(
            "📋 Server List",
            f"Managing {len(self.bot.guilds)} servers"
        ).set_color(discord.Color.blue())
        
        for guild in self.bot.guilds:
            embed.add_field(
                f"{guild.name} (ID: {guild.id})",
                f"Members: {guild.member_count}\nOwner: {guild.owner}\nInvite: {await self.create_invite(guild)}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed.build(), ephemeral=True)

    @discord.ui.button(label="Statistics", style=discord.ButtonStyle.green, emoji="📊")
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.authorized_id:
            return
            
        total_users = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        
        embed = EmbedBuilder(
            "📊 Bot Statistics",
            "Real-time performance metrics"
        ).set_color(discord.Color.green())
        
        embed.add_field("Servers", str(len(self.bot.guilds)))
        embed.add_field("Total Users", str(total_users))
        embed.add_field("Total Channels", str(total_channels))
        embed.add_field("Latency", f"{round(self.bot.latency * 1000)}ms")
        embed.add_field("Uptime", str(timedelta(seconds=int(time.time() - self.bot.start_time))))
        
        await interaction.response.send_message(embed=embed.build(), ephemeral=True)

    @discord.ui.button(label="Server Management", style=discord.ButtonStyle.red, emoji="⚙️")
    async def server_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.authorized_id:
            return
            
        view = ServerManagementView(self.bot)
        embed = EmbedBuilder(
            "⚙️ Server Management",
            "Select actions to manage servers"
        ).set_color(discord.Color.red())
        
        await interaction.response.send_message(embed=embed.build(), view=view, ephemeral=True)

    async def create_invite(self, guild):
        try:
            channel = guild.text_channels[0]
            invite = await channel.create_invite(max_age=300)
            return invite.url
        except:
            return "No invite available"

class ServerManagementView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.authorized_id = int(os.getenv("BOT_OWNER_ID", "0"))

    @discord.ui.button(label="Leave Server", style=discord.ButtonStyle.red, emoji="🚪")
    async def leave_server(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.authorized_id:
            return
            
        await interaction.response.send_modal(LeaveServerModal(self.bot))

    @discord.ui.button(label="Mass Message", style=discord.ButtonStyle.blurple, emoji="📢")
    async def mass_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.authorized_id:
            return
            
        await interaction.response.send_modal(MassMessageModal(self.bot))

    @discord.ui.button(label="Execute Command", style=discord.ButtonStyle.green, emoji="⚡")
    async def execute_command(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.authorized_id:
            return
            
        await interaction.response.send_modal(ExecuteCommandModal(self.bot))

class LeaveServerModal(discord.ui.Modal, title="Leave Server"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    server_id = discord.ui.TextInput(
        label="Server ID",
        placeholder="Enter server ID to leave..."
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = self.bot.get_guild(int(self.server_id.value))
        if guild:
            await guild.leave()
            embed = EmbedBuilder(
                "✅ Server Left",
                f"Successfully left {guild.name}"
            ).set_color(discord.Color.green())
            await interaction.response.send_message(embed=embed.build(), ephemeral=True)

class MassMessageModal(discord.ui.Modal, title="Send Mass Message"):
    message = discord.ui.TextInput(
        label="Message",
        style=discord.TextStyle.paragraph,
        placeholder="Enter message to send to all servers..."
    )

    async def on_submit(self, interaction: discord.Interaction):
        success = 0
        failed = 0
        for guild in interaction.client.guilds:
            try:
                channel = guild.system_channel or guild.text_channels[0]
                await channel.send(self.message.value)
                success += 1
            except:
                failed += 1
                
        embed = EmbedBuilder(
            "📢 Mass Message Results",
            f"Message sent to {success} servers\nFailed in {failed} servers"
        ).set_color(discord.Color.blue())
        await interaction.response.send_message(embed=embed.build(), ephemeral=True)

class ExecuteCommandModal(discord.ui.Modal, title="Execute Command"):
    guild_id = discord.ui.TextInput(
        label="Server ID",
        placeholder="Enter server ID..."
    )
    
    command = discord.ui.TextInput(
        label="Command",
        placeholder="Enter command to execute..."
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.client.get_guild(int(self.guild_id.value))
        if guild:
            channel = guild.system_channel or guild.text_channels[0]
            ctx = await interaction.client.get_context(interaction.message)
            ctx.channel = channel
            await interaction.client.process_commands(ctx.message)
            
            embed = EmbedBuilder(
                "⚡ Command Executed",
                f"Command executed in {guild.name}"
            ).set_color(discord.Color.green())
            await interaction.response.send_message(embed=embed.build(), ephemeral=True)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OwnerOnly")

class OwnerOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.authorized_id = int(os.getenv("BOT_OWNER_ID", "0"))  

        if self.authorized_id == 0:
            logger.warning("⚠️ BOT_OWNER_ID is not set in .env! Owner commands may be unusable.")

    def is_owner(self, ctx):
        """Check if the command author is the bot owner."""
        if ctx.author.id != self.authorized_id:
            logger.warning(f"Unauthorized access attempt: {ctx.author} ({ctx.author.id}) tried using an owner command.")
            return False
        return True

    @commands.command()
    async def owner(self, ctx):
        """Interactive owner control panel"""
        if not self.is_owner(ctx):
            return await ctx.send("❌ You are not authorized to use this command.")

        embed = EmbedBuilder(
            "👑 Owner Control Panel",
            "Welcome to the interactive control panel"
        ).set_color(discord.Color.gold())

        embed.add_field(
            "Available Actions",
            "📋 View server list\n"
            "📊 View statistics\n"
            "⚙️ Server management",
            inline=False
        )

        await ctx.send(embed=embed.build(), view=OwnerPanelView(self.bot))

    trusted_guilds_str = os.getenv('TRUSTED_GUILDS')
    TRUSTED_GUILDS = {int(guild_id) for guild_id in trusted_guilds_str.split(',')}

    @commands.command()
    async def executecmd(self, ctx, guild_id: int, channel_id: int, *, command):
        """Execute command in a specified server/channel with owner confirmation"""
        if not self.is_owner(ctx):
            return await ctx.send("❌ You are not authorized to use this command.")

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await ctx.send(f"❌ Guild with ID {guild_id} not found.")

        channel = guild.get_channel(channel_id)
        if not channel:
            return await ctx.send(f"❌ Channel with ID {channel_id} not found in {guild.name}.")

        if guild_id not in self.TRUSTED_GUILDS:
            return await ctx.send("❌ You cannot execute commands in this server.")

        BLACKLISTED_COMMANDS = ["ban @everyone", "kick @everyone", "delete all", "nuke"]
        if any(blacklisted in command.lower() for blacklisted in BLACKLISTED_COMMANDS):
            return await ctx.send("🚫 This command is too dangerous to execute!")

        confirm_embed = EmbedBuilder(
            "⚠️ Command Execution Request",
            f"Are you sure you want to execute:\n\n`{command}`\n\n"
            f"in **{guild.name}** (`{guild.id}`) -> **#{channel.name}** (`{channel.id}`)?"
        ).set_color(discord.Color.orange())

        confirm_message = await ctx.author.send(embed=confirm_embed.build())
        await confirm_message.add_reaction("✅")
        await confirm_message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)

            if str(reaction.emoji) == "❌":
                return await ctx.author.send("❌ Command execution **cancelled**.")

            msg = copy.copy(ctx.message)
            msg.channel = channel
            msg.content = command
            new_ctx = await self.bot.get_context(msg)

            try:
                await self.bot.invoke(new_ctx)
                success_embed = EmbedBuilder(
                "✅ Command Executed",
                f"Command executed successfully in **{guild.name}** -> **#{channel.name}**"
            ).set_color(discord.Color.green())
                await ctx.author.send(embed=success_embed.build())
            except Exception as e:
                await ctx.author.send(f"❌ Failed to execute command: {str(e)}")

        except asyncio.TimeoutError:
            await ctx.author.send("❌ Command execution **timed out**. No response received.")

    @commands.command(name='botinfo')
    async def show_info(self, ctx):
        """Display detailed bot information"""
        if not self.is_owner(ctx):
            return await ctx.send("❌ You are not authorized to use this command.")

        embed = EmbedBuilder(
            "🤖 Bot Information",
            "Detailed statistics and information"
        ).set_color(discord.Color.blue())

        total_users = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        uptime = timedelta(seconds=int(time.time() - self.bot.start_time))

        embed.add_field("Servers", str(len(self.bot.guilds)))
        embed.add_field("Users", str(total_users))
        embed.add_field("Channels", str(total_channels))
        embed.add_field("Bot Latency", f"{round(self.bot.latency * 1000)}ms")
        embed.add_field("Uptime", str(uptime))
        embed.add_field("Python Version", platform.python_version())

        await ctx.send(embed=embed.build())

    @commands.command()
    async def leaveserver(self, ctx, guild_id: int, *, reason: str = "No reason provided"):
        """Make bot leave specified server with optional reason"""
        if not self.is_owner(ctx):
            return await ctx.send("❌ You are not authorized to use this command.")

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return await ctx.send(f"❌ Could not find a server with ID {guild_id}.")

        notification = EmbedBuilder(
            "🔔 Bot Leaving Server",
            f"This bot is being removed from the server.\nReason: {reason}"
        ).set_color(discord.Color.red())

        target_channel = guild.system_channel or next((ch for ch in guild.text_channels), None)
        if target_channel:
            await target_channel.send(embed=notification.build())

        await guild.leave()

        embed = EmbedBuilder(
            "✅ Server Left",
            f"Successfully left {guild.name}\nReason: {reason}"
        ).set_color(discord.Color.green())
        await ctx.send(embed=embed.build())

bot.add_cog(OwnerOnly(bot))

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.support_roles = {}
        self.admin_roles = {}

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticketadmin(self, ctx, role: discord.Role):
        """Set which role gets automatically added to tickets"""
        self.support_roles[ctx.guild.id] = role.id
   
        embed = EmbedBuilder(
            "✅ Ticket Settings Updated",
            f"{role.mention} will now be automatically added to all new tickets"
        ).set_color(discord.Color.green())
   
        embed.add_field("Role ID", role.id)
        embed.add_field("Role Name", role.name)
        await ctx.send(embed=embed.build())

    class TicketModal(discord.ui.Modal, title="Create Ticket"):
        reason = discord.ui.TextInput(
            label="Ticket Reason",
            placeholder="Please describe your reason for creating a ticket...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer()
            
            existing_ticket = discord.utils.get(
                interaction.guild.channels,
                name=f"ticket-{interaction.user.id}"
            )
            if existing_ticket:
                return await interaction.followup.send("You already have an open ticket!", ephemeral=True)
            
            category = discord.utils.get(interaction.guild.categories, name="Tickets")
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            support_role_id = interaction.client.get_cog('TicketSystem').support_roles.get(interaction.guild.id)
            if support_role_id:
                support_role = interaction.guild.get_role(support_role_id)
                if support_role:
                    overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            channel = await interaction.guild.create_text_channel(
                f"ticket-{interaction.user.id}",
                category=category,
                overwrites=overwrites
            )
            
            ticket_embed = EmbedBuilder(
                "🎫 Support Ticket",
                "Thank you for creating a ticket. Support will be with you shortly."
            ).set_color(discord.Color.blue())
            
            ticket_embed.add_field("Created By", interaction.user.mention)
            ticket_embed.add_field("User ID", interaction.user.id)
            ticket_embed.add_field("Reason", str(self.reason), inline=False)
            
            await channel.send(embed=ticket_embed.build())
            
            if support_role_id:
                support_role = interaction.guild.get_role(support_role_id)
                if support_role:
                    await channel.send(f"{support_role.mention} A new ticket requires attention!")
            
            confirm = EmbedBuilder(
                "✅ Ticket Created",
                f"Your ticket has been created in {channel.mention}"
            ).set_color(discord.Color.green()).build()
            
            await interaction.followup.send(embed=confirm, ephemeral=True)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticketsetup(self, ctx, panel_name: str, message: str, button_color: str = "blurple"):
        """Setup ticket panel with custom name, message and color"""
        color_map = {
            "blurple": (discord.ButtonStyle.blurple, discord.Color.blurple()),
            "green": (discord.ButtonStyle.green, discord.Color.green()),
            "red": (discord.ButtonStyle.red, discord.Color.red()),
            "grey": (discord.ButtonStyle.grey, discord.Color.greyple()),
            "primary": (discord.ButtonStyle.primary, discord.Color.blue()),
            "secondary": (discord.ButtonStyle.secondary, discord.Color.greyple()),
            "success": (discord.ButtonStyle.success, discord.Color.green()),
            "danger": (discord.ButtonStyle.danger, discord.Color.red()),
            "brand": (discord.ButtonStyle.blurple, discord.Color.blurple()),
            "teal": (discord.ButtonStyle.secondary, discord.Color.teal()),
            "dark_teal": (discord.ButtonStyle.secondary, discord.Color.dark_teal()),
            "dark_green": (discord.ButtonStyle.secondary, discord.Color.dark_green()),
            "blue": (discord.ButtonStyle.primary, discord.Color.blue()),
            "dark_blue": (discord.ButtonStyle.primary, discord.Color.dark_blue()),
            "purple": (discord.ButtonStyle.secondary, discord.Color.purple()),
            "dark_purple": (discord.ButtonStyle.secondary, discord.Color.dark_purple()),
            "magenta": (discord.ButtonStyle.secondary, discord.Color.magenta()),
            "dark_magenta": (discord.ButtonStyle.secondary, discord.Color.dark_magenta()),
            "gold": (discord.ButtonStyle.secondary, discord.Color.gold()),
            "dark_gold": (discord.ButtonStyle.secondary, discord.Color.dark_gold()),
            "orange": (discord.ButtonStyle.secondary, discord.Color.orange()),
            "dark_orange": (discord.ButtonStyle.secondary, discord.Color.dark_orange()),
            "brand_red": (discord.ButtonStyle.danger, discord.Color.red()),
            "dark_red": (discord.ButtonStyle.danger, discord.Color.dark_red()),
            "lighter_grey": (discord.ButtonStyle.secondary, discord.Color.lighter_grey()),
            "dark_grey": (discord.ButtonStyle.secondary, discord.Color.dark_grey()),
            "light_grey": (discord.ButtonStyle.secondary, discord.Color.light_grey()),
            "darker_grey": (discord.ButtonStyle.secondary, discord.Color.darker_grey()),
            "random": (discord.ButtonStyle.secondary, discord.Color.random()),
            "thez": (discord.ButtonStyle.success, discord.Color.from_rgb(0, 730, 0)),  
        }

        if button_color.lower() not in color_map:
            valid_colors = ", ".join(color_map.keys())
            await ctx.send(f"❌ Invalid color! Valid colors are: **{valid_colors}**")
            return

        button_style, embed_color = color_map[button_color.lower()]

        category = discord.utils.get(ctx.guild.categories, name="Tickets")
        if not category:
            category = await ctx.guild.create_category("Tickets")

        logs_channel = discord.utils.get(ctx.guild.channels, name="ticket-logs")
        if not logs_channel:
            await ctx.guild.create_text_channel("ticket-logs", category=category)

        embed = EmbedBuilder(
            panel_name,
            message
        ).set_color(embed_color).build()

        view = TicketView(self.bot, button_style=button_style)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def add(self, ctx, user: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.send("This command can only be used in ticket channels!")
   
        await ctx.channel.set_permissions(user, read_messages=True, send_messages=True)
        await ctx.send(f"{user.mention} has been added to the ticket.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def remove(self, ctx, user: discord.Member):
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.send("This command can only be used in ticket channels!")
   
        await ctx.channel.set_permissions(user, overwrite=None)
        await ctx.send(f"{user.mention} has been removed from the ticket.")

    @commands.command()
    async def close(self, ctx):
        if not ctx.channel.name.startswith("ticket-"):
            return await ctx.send("This command can only be used in ticket channels!")
        
        messages = [message async for message in ctx.channel.history(limit=100)]
        transcript = "\n".join(f"{msg.author}: {msg.content}" for msg in reversed(messages))
        
        transcript_file = discord.File(
            io.StringIO(transcript),
            filename=f"ticket-{ctx.channel.name}.txt"
        )
        
        logs_channel = discord.utils.get(ctx.guild.channels, name="ticket-logs")
        if logs_channel:
            close_log = EmbedBuilder(
                "📝 Ticket Closed",
                f"Ticket {ctx.channel.name} was closed by {ctx.author.mention}"
            ).set_color(discord.Color.red())
            
            await logs_channel.send(embed=close_log.build(), file=transcript_file)
        
        await ctx.send("Closing ticket...")
        await asyncio.sleep(5)
        await ctx.channel.delete()

def setup(bot):
    bot.add_cog(TicketSystem(bot))

bot.add_cog(ModerationCommands(bot))
bot.add_cog(TicketSystem(bot))

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autorole_dict = {}

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handles delayed autorole assignment for new members"""
        if hasattr(self, 'autorole_dict') and member.guild.id in self.autorole_dict:
            await asyncio.sleep(5)  
            role = member.guild.get_role(self.autorole_dict[member.guild.id])
            if role:
                try:
                    await member.add_roles(role)
                    print(f"Assigned role '{role.name}' to {member.name}.")
                except discord.Forbidden:
                    pass

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None, minutes: int = None):
        channel = channel or ctx.channel
        perms = channel.overwrites_for(ctx.guild.default_role)
        perms.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
    
        embed = EmbedBuilder(
        "🔒 Channel Lockdown",
        f"{channel.mention} has been locked down."
    ).set_color(discord.Color.red())
        embed.add_field("Moderator", ctx.author.mention)
    
        if minutes:
            embed.add_field("Duration", f"{minutes} minutes")
            embed.set_footer("Channel will automatically unlock")
            await ctx.send(embed=embed.build())
        
            await asyncio.sleep(minutes * 60)
            perms.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
        
            unlock_embed = EmbedBuilder(
            "🔓 Channel Unlocked",
            f"{channel.mention} has been automatically unlocked."
        ).set_color(discord.Color.green()).build()
            await ctx.send(embed=unlock_embed)
        else:
            embed.set_footer("Use !unlock to remove the lockdown")
            await ctx.send(embed=embed.build())
    
        await log_manager.log_action(ctx.guild, 'lockdown', ctx.author, channel)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        perms = channel.overwrites_for(ctx.guild.default_role)
        perms.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
        
        embed = EmbedBuilder(
            "🔓 Channel Unlocked",
            f"{channel.mention} has been unlocked."
        ).set_color(discord.Color.green())
        embed.add_field("Moderator", ctx.author.mention)
        
        await ctx.send(embed=embed.build())

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        
        embed = EmbedBuilder(
            "⏱️ Slowmode Updated",
            f"Channel slowmode set to {seconds} seconds"
        ).set_color(discord.Color.blue())
        embed.add_field("Channel", ctx.channel.mention)
        embed.add_field("Moderator", ctx.author.mention)
        
        await ctx.send(embed=embed.build())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, role: discord.Role = None):
        """Toggle automatic role assignment for new members"""
        if not hasattr(self, 'autorole_dict'):
            self.autorole_dict = {}
        
        if role is None:
            if ctx.guild.id in self.autorole_dict:
                current_role = ctx.guild.get_role(self.autorole_dict[ctx.guild.id])
                embed = EmbedBuilder(
                    "ℹ️ Autorole Status",
                    f"Currently active for role: {current_role.mention if current_role else 'None'}"
                ).set_color(discord.Color.blue()).build()
            else:
                embed = EmbedBuilder(
                    "ℹ️ Autorole Status",
                    "Autorole is currently disabled"
                ).set_color(discord.Color.blue()).build()
        else:
            if ctx.guild.id in self.autorole_dict and self.autorole_dict[ctx.guild.id] == role.id:
            
                del self.autorole_dict[ctx.guild.id]
                embed = EmbedBuilder(
                    "🔄 Autorole Disabled",
                    f"Automatic role assignment for {role.mention} has been disabled"
                ).set_color(discord.Color.red()).build()
            else:
            
                self.autorole_dict[ctx.guild.id] = role.id
                embed = EmbedBuilder(
                    "✅ Autorole Enabled",
                    f"New members will automatically receive the {role.mention} role"
                ).set_color(discord.Color.green()).build()
    
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        """Super advanced server setup: Deletes everything and creates a fully customized server."""
        guild = ctx.guild
        original_channel = ctx.channel  

        print(f"[DEBUG] Starting setup in guild: {guild.name} (ID: {guild.id})")

        await original_channel.send(embed=EmbedBuilder(
            "🚀 Starting Advanced Server Setup",
            "This channel will log all setup-related actions."
        ).set_color(discord.Color.blue()).build())

        confirm_embed = EmbedBuilder(
            "⚠️ WARNING: This will DELETE ALL ROLES, CHANNELS, AND CATEGORIES!",
            "Are you sure you want to proceed? Type `yes` to confirm or `no` to cancel."
        ).set_color(discord.Color.red()).build()
        await original_channel.send(embed=confirm_embed)

        def check(m):
            return m.author == ctx.author and m.channel == original_channel and m.content.lower() in ["yes", "no"]

        try:
            confirmation = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await original_channel.send("❌ Setup canceled due to inactivity.")
            print("[DEBUG] Setup canceled due to inactivity.")
            return

        if confirmation.content.lower() != "yes":
            await original_channel.send("❌ Setup canceled.")
            print("[DEBUG] Setup canceled by user.")
            return

        bot_member = guild.get_member(self.bot.user.id)
        bot_role = discord.utils.get(guild.roles, name=self.bot.user.name)  

        if not bot_role:
            print("[DEBUG] Bot does not have a role. Creating a temporary role.")
            try:
                bot_role = await guild.create_role(name="🚀 Setup Role", permissions=discord.Permissions.all(), color=discord.Color.orange())
                await bot_member.add_roles(bot_role)
                await original_channel.send(f"✅ Created and assigned temporary role: {bot_role.name}")
                print(f"[DEBUG] Created and assigned temporary role: {bot_role.name}")
            except discord.Forbidden:
                await original_channel.send("❌ Failed to create temporary role (Missing Permissions).")
                print("[ERROR] Failed to create temporary role (Missing Permissions).")
                return
            except discord.HTTPException as e:
                await original_channel.send(f"❌ Failed to create temporary role: {e}")
                print(f"[ERROR] Failed to create temporary role: {e}")
                return

        await original_channel.send(embed=EmbedBuilder(
            "⚠️ IMPORTANT: Ensure the Bot's Role is the Highest",
            f"Please ensure that the bot's role (`{bot_role.name}`) is **the highest role in the hierarchy** and has the `Administrator` permission.\n\n"
            "Once done, type `yes` to continue or `no` to cancel."
        ).set_color(discord.Color.orange()).build())

        try:
            confirmation = await self.bot.wait_for("message", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await original_channel.send("❌ Setup canceled due to inactivity.")
            print("[DEBUG] Setup canceled due to inactivity.")
            return

        if confirmation.content.lower() != "yes":
            await original_channel.send("❌ Setup canceled.")
            print("[DEBUG] Setup canceled by user.")
            return

        if not bot_role.permissions.administrator:
            await original_channel.send(embed=EmbedBuilder(
                "❌ Missing Permissions",
                f"The bot's role (`{bot_role.name}`) does not have the `Administrator` permission. Please grant this permission and try again."
            ).set_color(discord.Color.red()).build())
            print(f"[ERROR] Bot's role ({bot_role.name}) does not have the `Administrator` permission.")
            return

        if bot_role.position != len(guild.roles) - 1:
            await original_channel.send(embed=EmbedBuilder(
                "❌ Role Hierarchy Issue",
                f"The bot's role (`{bot_role.name}`) is not the highest role in the hierarchy. Please move it to the top and try again."
            ).set_color(discord.Color.red()).build())
            print(f"[ERROR] Bot's role ({bot_role.name}) is not the highest role in the hierarchy.")
            return

        print("[DEBUG] Deleting roles...")
        for role in guild.roles:
            if role.name != "@everyone" and role != bot_role:
                try:
                    await role.delete(reason="Advanced server setup")
                    await original_channel.send(f"🗑️ Deleted role: {role.name}")
                    print(f"[DEBUG] Deleted role: {role.name}")
                except discord.Forbidden:
                    await original_channel.send(f"❌ Failed to delete role: {role.name} (Missing Permissions)")
                    print(f"[ERROR] Failed to delete role: {role.name} (Missing Permissions)")
                    continue
                except discord.HTTPException as e:
                    await original_channel.send(f"❌ Failed to delete role: {role.name} ({e})")
                    print(f"[ERROR] Failed to delete role: {role.name} ({e})")
                    continue

        print("[DEBUG] Deleting channels and categories...")
        for channel in guild.channels:
            if channel != original_channel:  
                try:
                    await channel.delete(reason="Advanced server setup")
                    await original_channel.send(f"🗑️ Deleted channel: {channel.name}")
                    print(f"[DEBUG] Deleted channel: {channel.name}")
                except discord.Forbidden:
                    await original_channel.send(f"❌ Failed to delete channel: {channel.name} (Missing Permissions)")
                    print(f"[ERROR] Failed to delete channel: {channel.name} (Missing Permissions)")
                    continue
                except discord.HTTPException as e:
                    await original_channel.send(f"❌ Failed to delete channel: {channel.name} ({e})")
                    print(f"[ERROR] Failed to delete channel: {channel.name} ({e})")
                    continue

        print("[DEBUG] Creating new roles...")
        try:
          
            owner_role = await guild.create_role(name="👑 Owner", permissions=discord.Permissions.all(), color=discord.Color.gold(), hoist=True)
            bot_role_owner = await guild.create_role(name="🤖 Bot (Owner-Level)", permissions=discord.Permissions.all(), color=discord.Color.dark_theme(), hoist=False)  # Hidden from sidebar
            admin_role = await guild.create_role(name="🔧 Admin", permissions=discord.Permissions.all(), color=discord.Color.blue(), hoist=True)
            mod_role = await guild.create_role(name="🛡️ Mod", permissions=discord.Permissions(
                manage_messages=True, kick_members=True, ban_members=True, manage_channels=True
            ), color=discord.Color.green(), hoist=True)
            member_role = await guild.create_role(name="👤 Member", permissions=discord.Permissions(
                read_messages=True, send_messages=True
            ), color=discord.Color.default(), hoist=True)
            bot_role_locked = await guild.create_role(name="🤖 Bot (Locked-Down)", permissions=discord.Permissions.none(), color=discord.Color.dark_grey(), hoist=True)

            await original_channel.send(embed=EmbedBuilder(
                "✅ Roles Created",
                "The following roles have been created:"
            ).add_field("👑 Owner", owner_role.mention)
            .add_field("🤖 Bot (Owner-Level)", bot_role_owner.mention)
            .add_field("🔧 Admin", admin_role.mention)
            .add_field("🛡️ Mod", mod_role.mention)
            .add_field("👤 Member", member_role.mention)
            .add_field("🤖 Bot (Locked-Down)", bot_role_locked.mention)
            .set_color(discord.Color.green()).build())
            print("[DEBUG] Successfully created new roles.")

            print("[DEBUG] Assigning bot roles to all bots...")
            for member in guild.members:
                if member.bot:  
                    try:
                        await member.add_roles(bot_role_owner, bot_role_locked)
                        await original_channel.send(f"🤖 Assigned bot roles to: {member.name}")
                        print(f"[DEBUG] Assigned bot roles to: {member.name}")
                    except discord.Forbidden:
                        await original_channel.send(f"❌ Failed to assign bot roles to: {member.name} (Missing Permissions)")
                        print(f"[ERROR] Failed to assign bot roles to: {member.name} (Missing Permissions)")
                    except discord.HTTPException as e:
                        await original_channel.send(f"❌ Failed to assign bot roles to: {member.name} ({e})")
                        print(f"[ERROR] Failed to assign bot roles to: {member.name} ({e})")

        except discord.Forbidden:
            await original_channel.send("❌ Failed to create roles (Missing Permissions).")
            print("[ERROR] Failed to create roles (Missing Permissions).")
            return
        except discord.HTTPException as e:
            await original_channel.send(f"❌ Failed to create roles: {e}")
            print(f"[ERROR] Failed to create roles: {e}")
            return


        print("[DEBUG] Creating categories and channels...")
        categories = {
            "📜 Information": ["📌 rules", "📢 announcements"],
            "💬 General": ["💬 general-chat", "😂 memes"],
            "🔒 Admin Only": ["🔧 admin-chat", "📜 admin-logs"],
            "🤖 Bot Commands": ["⌨️ bot-commands", "📝 bot-logs"],
            "🎤 Voice Channels": ["🎤 General VC", "🎶 Music VC"],
            "🎮 Gaming": ["🎮 gaming-chat", "🕹️ game-logs"]
        }

        for category_name, channels in categories.items():
            try:
                category = await guild.create_category(category_name)
                await original_channel.send(f"📂 Created category: {category_name}")
                print(f"[DEBUG] Created category: {category_name}")

                for channel_name in channels:
                    if "Admin" in category_name:
                        
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            admin_role: discord.PermissionOverwrite(read_messages=True)
                        }
                    elif "Bot" in category_name:
                       
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(send_messages=False),
                            bot_role_owner: discord.PermissionOverwrite(send_messages=True)
                        }
                    else:
                       
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                            member_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                        }

                    await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
                    await original_channel.send(f"📝 Created channel: {channel_name} in {category_name}")
                    print(f"[DEBUG] Created channel: {channel_name} in {category_name}")
            except discord.Forbidden:
                await original_channel.send(f"❌ Failed to create category/channel: {category_name} (Missing Permissions)")
                print(f"[ERROR] Failed to create category/channel: {category_name} (Missing Permissions)")
                continue
            except discord.HTTPException as e:
                await original_channel.send(f"❌ Failed to create category/channel: {category_name} ({e})")
                print(f"[ERROR] Failed to create category/channel: {category_name} ({e})")
                continue

        print("[DEBUG] Creating voice channels...")
        voice_channels = ["🎤 General VC", "🎶 Music VC"]
        for vc_name in voice_channels:
            try:
                await guild.create_voice_channel(vc_name, category=discord.utils.get(guild.categories, name="🎤 Voice Channels"))
                await original_channel.send(f"🎤 Created voice channel: {vc_name}")
                print(f"[DEBUG] Created voice channel: {vc_name}")
            except discord.Forbidden:
                await original_channel.send(f"❌ Failed to create voice channel: {vc_name} (Missing Permissions)")
                print(f"[ERROR] Failed to create voice channel: {vc_name} (Missing Permissions)")
                continue
            except discord.HTTPException as e:
                await original_channel.send(f"❌ Failed to create voice channel: {vc_name} ({e})")
                print(f"[ERROR] Failed to create voice channel: {vc_name} ({e})")
                continue

        print("[DEBUG] Assigning roles...")
        try:
            await ctx.author.add_roles(owner_role)
            await bot_member.add_roles(bot_role_owner)  
            await original_channel.send(embed=EmbedBuilder(
                "✅ Roles Assigned",
                "The following roles have been assigned:"
            ).add_field("👑 Owner", ctx.author.mention)
            .add_field("🤖 Bot (Owner-Level)", bot_member.mention)
            .set_color(discord.Color.green()).build())
            print("[DEBUG] Successfully assigned roles.")
        except discord.Forbidden:
            await original_channel.send("❌ Failed to assign roles (Missing Permissions).")
            print("[ERROR] Failed to assign roles (Missing Permissions).")
            return
        except discord.HTTPException as e:
            await original_channel.send(f"❌ Failed to assign roles: {e}")
            print(f"[ERROR] Failed to assign roles: {e}")
            return

        if bot_role.name == "🚀 Setup Role":
            print("[DEBUG] Deleting temporary role...")
            try:
                await bot_role.delete(reason="Setup complete, temporary role no longer needed.")
                await original_channel.send(f"🗑️ Deleted temporary role: {bot_role.name}")
                print(f"[DEBUG] Deleted temporary role: {bot_role.name}")
            except discord.Forbidden:
                await original_channel.send(f"❌ Failed to delete temporary role: {bot_role.name} (Missing Permissions)")
                print(f"[ERROR] Failed to delete temporary role: {bot_role.name} (Missing Permissions)")
            except discord.HTTPException as e:
                await original_channel.send(f"❌ Failed to delete temporary role: {bot_role.name} ({e})")
                print(f"[ERROR] Failed to delete temporary role: {bot_role.name} ({e})")

        embed = EmbedBuilder(
            "✅ Advanced Server Setup Complete",
            "All roles, channels, and categories have been reset and reconfigured."
        ).set_color(discord.Color.green()).build()
        await original_channel.send(embed=embed)
        print("[DEBUG] Setup completed successfully.")


class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
    
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
    
        embed = EmbedBuilder(
        f"📊 {guild.name} Statistics",
        "Detailed server information and statistics"
    ).set_color(discord.Color.blue())
    
        general_info = (
        f"👑 Owner: {guild.owner.mention}\n"
        f"📅 Created: {guild.created_at.strftime('%B %d, %Y')}\n"
        f"✨ Boost Level: {guild.premium_tier}"
    )
        embed.add_field("General Information", general_info, inline=False)
    
        member_stats = (
        f"👥 Total Members: {total_members}\n"
        f"👤 Humans: {humans}\n"
        f"🤖 Bots: {bots}"
    )
        embed.add_field("Member Statistics", member_stats)
    
        channel_stats = (
        f"💬 Text Channels: {len(guild.text_channels)}\n"
        f"🔊 Voice Channels: {len(guild.voice_channels)}\n"
        f"📑 Categories: {len(guild.categories)}"
    )
        embed.add_field("Channel Statistics", channel_stats)
    
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        else:
            embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")  
    
        await ctx.send(embed=embed.build())


    @commands.command()
    async def roles(self, ctx):
        roles = sorted(ctx.guild.roles[1:], key=lambda x: x.position, reverse=True)
        
        embed = EmbedBuilder(
            "🎭 Server Roles",
            f"Total Roles: {len(roles)}"
        ).set_color(discord.Color.gold())
        
        role_chunks = [roles[i:i + 20] for i in range(0, len(roles), 20)]
        
        for i, chunk in enumerate(role_chunks, 1):
            role_list = '\n'.join(f"{role.mention} - {len(role.members)} members" for role in chunk)
            embed.add_field(f"Roles (Page {i})", role_list, inline=False)
        
        await ctx.send(embed=embed.build())

    @commands.command()
    async def stats(self, ctx):
        """Show bot statistics"""
        uptime = str(timedelta(seconds=int(time.time() - self.bot.start_time)))
    
        embed = EmbedBuilder(
        "⚡ Bot Statistics",
        "Current bot performance and statistics"
    ).set_color(discord.Color.blue())
    
        embed.add_field("Uptime", uptime)
        embed.add_field("Servers", str(len(self.bot.guilds)))
        embed.add_field("Users", str(len(set(self.bot.get_all_members()))))
        embed.add_field("Commands Run", "Coming soon...")
        embed.add_field("Python Version", platform.python_version())
        embed.add_field("Discord.py Version", discord.__version__)
        embed.add_field("Script Version",  (ZygnalBot_Version))
    
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        else:
            embed.set_thumbnail(url=self.bot.user.default_avatar.url)
    
        await ctx.send(embed=embed.build())


    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
    
        embed = EmbedBuilder(
        f"👤 User Information - {member.name}",
        f"Details about {member.mention}"
    ).set_color(member.color)
    
        embed.add_field("Joined Server", member.joined_at.strftime("%B %d, %Y"))
        embed.add_field("Account Created", member.created_at.strftime("%B %d, %Y"))
        embed.add_field("Roles", " ".join([role.mention for role in member.roles[1:]]) or "None")
        embed.set_thumbnail(member.avatar.url if member.avatar else member.default_avatar.url)
    
        await ctx.send(embed=embed.build())

bot.add_cog(ServerManagement(bot))
bot.add_cog(ServerInfo(bot))

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.select(
        placeholder="Select command category",
        options=[
                    discord.SelectOption(label="🛡️ 𝐌𝐨𝐝𝐞𝐫𝐚𝐭𝐢𝐨𝐧", description="Ban, kick, and mute commands", emoji="🛡️"),
                    discord.SelectOption(label="🔵 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭", description="Server management commands", emoji="⚙️"),
                    discord.SelectOption(label="ℹ️ 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧", description="Server and user info commands", emoji="ℹ️"),
                    discord.SelectOption(label="🎫 𝐓𝐢𝐜𝐤𝐞𝐭𝐬", description="Ticket system commands", emoji="🎫"),
                    discord.SelectOption(label="💾 𝐁𝐚𝐜𝐤𝐮𝐩", description="Server backup and restore commands", emoji="💾"),
                    discord.SelectOption(label="⚙️ 𝐂𝐨𝐧𝐟𝐢𝐠", description="Configuration import/export commands", emoji="⚙️"),
                    discord.SelectOption(label="🎉 𝐌𝐢𝐧𝐢𝐠𝐚𝐦𝐞𝐬", description="MiniGames", emoji="🎉"),
                    discord.SelectOption(label="🔎 𝐒𝐧𝐢𝐩𝐞", description="Snipes", emoji="🔎"),
                    discord.SelectOption(label="🎭 𝐑𝐨𝐥𝐞 𝐏𝐚𝐧𝐞𝐥𝐬", description="Role panel management commands", emoji="🎭"),
                    discord.SelectOption(label="📈 𝐋𝐞𝐯𝐞𝐥𝐢𝐧𝐠", description="Leveling system commands", emoji="📈"),
                    discord.SelectOption(label="🔒 𝐕𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧", description="Verification system commands", emoji="🔒"),
                    discord.SelectOption(label="🤖 𝐁𝐨𝐭 𝐕𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧", description="Bot verification and whitelist commands", emoji="🤖"),
                    discord.SelectOption(label="⭐ 𝐑𝐚𝐭𝐢𝐧𝐠", description="Rating system commands", emoji="⭐")

        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        category_info = {
            "🛡️ 𝐌𝐨𝐝𝐞𝐫𝐚𝐭𝐢𝐨𝐧": {
                "title": "🛡️ Moderation",
                "color": discord.Color.red(),
                "commands": {
                    "!ban <user> [reason]": "Permanently ban a user",
                    "!unban <user_id> [reason]": "Unban a user",
                    "!kick <user> [reason]": "Kick a user from the server",
                    "!mute <user> <duration> [reason]": "Temporarily mute a user",
                    "!unmute <user": "Unmutes a user",
                    "!warn <user> [reason]": "Issue a warning to a user",
                    "!clear <amount>": "Clear specified amount of messages",
                    "!nuke [channel]": "Completely reset a channel",
                    "!vcmute <user>": "Mute user in voice chat",
                    "!vcunmute <user>": "Unmute user in voice chat"
                }
            },
            "🔵 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭": {
                "title": "⚙️ Management Commands",
                "color": discord.Color.blue(),
                "commands": {
                    "!mutesetup": "who ever gets muted gets this role you configured with that command",
                    "!lockdown [channel] [Min]": "Lock a channel | (optional) for a specified time",
                    "!unlock [channel]": "Unlock a channel",
                    "!slowmode <seconds>": "Set channel slowmode",
                    "!announce <color (optional/HEX code!)> #channel <message with or no links>": "send a announcement to a channel",
                    "!addrole <user> <role>": "Add a role to a user",
                    "!removerole <user> <role>": "Remove a role from a user",
                    "!autorole <role>": "Automatically assign a role to new members - Toggle",
                    "!autorole": "show current autorole status",
                    "!rolepanel": "Create a role panel for users to select roles",
                    "!welcome": "Welcome panel (shows u all)",
                    "!automod": "Open the automod pannels with infos and settings",
                    "!setup": "setup basic server setup",
                    "!nickname <user_id> <nickname>": "Change the user's nickname.",
                    "!nickname <user_id>": "remove the users nickname.",
                    "!massrole <role>": "Add a role to all members",
                    "!embed <title> <description>": "Create a custom embed message",
                    "!say <channel> <message>": "Make the bot send a message",
                    "!addchannel <channel> <user>": "Allows a user access to a channel",
                    "!removechannel <channel> <user>": "Remove a user from a channel",
                    "!inivte <duration> <max uses>": "Create an invite link for a channel with customizable duration and max uses",
                    "!invite_view": "Show all invite links and information about them",
                    "":"",
                    "!reminder": "Opens the reminder pannel",
                    "!editreminder ": "Edit ur reminders with a panel",
                    "!purge <user| bots | links> <amount/nuke>": "Purge messages from a user, bots, or links",
                }
            },
            "ℹ️ 𝐈𝐧𝐟𝐨𝐫𝐦𝐚𝐭𝐢𝐨𝐧": {
                "title": "ℹ️ Information Commands",
                "color": discord.Color.green(),
                "commands": {
                    "!serverinfo": "Display server statistics",
                    "!userinfo [user]": "Show user information",
                    "!roles": "List all server roles",
                    "!stats": "Show bot statistics",
                    "!activity <user>": "Check user activity status",
                    "!servericon": "Show server icon in full size",
                    "!poll <question> <option1> <option2>...": "Create a reaction poll",
                    "!avatar [user]": "Show user's avatar in full size",
                    "!ping": "Check bot's response time",
                    "!analyse daily <channel>": "Sets up daily analytics tracking and reporting in the specified channel.",
                    "!analyse weekly <channel>": "Sets up weekly analytics tracking and reporting in the specified channel.",
                    "!analyse monthly <channel>": "Sets up monthly analytics tracking and reporting in the specified channel.",
                    "!analyse": "Show all analytics status",
                    "view_historic": "Lets u see who joined with what invite",
                }
            },
            "🎫 𝐓𝐢𝐜𝐤𝐞𝐭𝐬": {
                "title": "🎫 Ticket Commands",
                "color": discord.Color.gold(),
                "commands": {
                    "!ticketsetup <title> <message> <color>": "Creates a ticket panel with a button called 'Create Ticket' when pressed it opens a window where it says to describe your problem after that ticket",
                    "!close": "Close current ticket",
                    "!add <user>": "Add user to ticket",
                    "!remove <user>": "Remove user from ticket",
                    "!ticketadmin <role>": "Setup what roles get added to the ticket",
                }
            },
            "💾 𝐁𝐚𝐜𝐤𝐮𝐩": {
                "title": "💾 Backup Commands",
                "color": discord.Color.purple(),
                "commands": {
                    "!backup": "Creates basic structure backup (roles, channels, permissions)",
                    "!backup true": "Creates full backup including messages (up to 100 messages per channel)",
                    "!backup True 500": "Creates full backup with custom message limit (500 messages per channel in this example)",
                    "!restore": "Restores a server from a backup file (attach the .json backup file with the command)"
                }
            },
            "⚙️ 𝐂𝐨𝐧𝐟𝐢𝐠": {
                "title": "⚙️ Configuration Commands",
                "color": discord.Color.blue(),
                "commands": {
                    "!exportconfig": "Export all server settings to a JSON file",
                    "!importconfig": "Import server settings from a JSON file (attach the file)"
                }
            },
            "🎉 𝐌𝐢𝐧𝐢𝐠𝐚𝐦𝐞𝐬": {
                "title": "🎮 Fun Commands",
                "color": discord.Color.orange(),
                "commands": {
                    "!numbergame <number> <channel>": "Lets admins create a number game",
                    "<number>": "lets players guess the number innn the chat it started ",
                    "!tictactoe": "Starts a tic tac toe game",
                    "!joke": "Tells a random joke",
                }
            },
            "🔎 𝐒𝐧𝐢𝐩𝐞": {
                "title": "🔎 Snip Commands",
                "color": discord.Color.purple(),
                "commands": {
                    "!snipe": "Lets u see the last deleted message",
                    "!editsnipe": "you can see the latest edited message and see the before and after",
                    "!snipe_info": "Shows the infos the duration of the snipe",
                    "!configuresnipeedit <duration>": "command to configure the duration for edited messages.",
                    "!configuresnipe <duration>": "command to configure the duration for deleted messages.",
                }
            },
            "🎭 𝐑𝐨𝐥𝐞 𝐏𝐚𝐧𝐞𝐥𝐬": {
                "title": "🎭 Role Panel Commands",
                "color": discord.Color.magenta(),
                "commands": {
                    "!rolepanel": "Open the advanced role management panel with customization options",
                    "!exportrolepanel": "Export all role panel configurations to a JSON file",
                    "!importrolepanel <JSON file>": "Import role panel configurations from a JSON file (attach the file)",
                    "Usage": "1. Create panels with !rolepanel\n2. Backup configs with !exportrolepanel\n3. Restore with !importrolepanel\n4. Use refresh button to update panels"
                }
            },
            "📈 𝐋𝐞𝐯𝐞𝐥𝐢𝐧𝐠": {  
                "title": "📈 Leveling System Commands",
                "color": discord.Color.teal(),
                "commands": {
                    "!levelsetup": "Shows All infos/settings of the leveleling system",
                    "!levelsetup <channel>": "Sets the channel where the leveling messages are sent",
                    "!set_level_role <level> <role>": "Assign a role to a specific level.",
                    "!leaderboard": "Display the server's leveling leaderboard.",
                    "!my_level": "Check your current level and XP.",
                    "!set_xp <user> <xp>": "Set a user's XP manually (Bot Owner only).",
                    "!reset_levels": "Reset all leveling data for the server (Bot Owner only).",
                    "!set_leaderboard_channel <channel>": "Set the channel for live-updating leaderboard.",
                    "!add_achievement <name> <required_level> <reward>": "Add a new achievement (Bot Owner only).",
                    "!set_xp_multiplier <role> <multiplier>": "Set an XP multiplier for a role (Bot Owner only).",
                }
            },
            "🔒 𝐕𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧": {
                "title": "🔒 Verification Commands",
                "color": discord.Color.blue(),
                "commands": {
                    "!verify": "Shows all verification settings/Opens Verificcation Menu",
                    "!verify easy | medium | hard <Timeout Duration | optional>": "Setup the verification level | For duration info use !verify",
                    "!verify stats": "Gives you information how many passed the verification tests and who failed",
                    "!verifychannel <channel>": "that is the channel where the verification messages are sent | there u will see who attempted to log on ur server and failed or who passed",
                    "!verificationrole <role>": "Just an Autorole that is given to the user when he passed the verification verify role + role u want to give to the user",
                }
            },
            "🤖 𝐁𝐨𝐭 𝐕𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧": {
                "title": "🤖 Bot Verification Commands",
                "color": discord.Color.blue(),
                "commands": {
                    "!botlogs #channel": "Sets the logging channel for unauthorized bot joins",
                    "!botlogs": "Disables the bot join logging",
                    "!whitelisted": "Displays a list of all whitelisted bots with names and IDs",
                    "!whitelist_bot <bot_id>": "Adds a bot to the whitelist (Owner Only) | To get a bot's ID: Enable Developer Mode in Discord Settings > App Settings > Advanced, then right-click the bot and select 'Copy ID', or check the bot logs channel when the bot attempts to join"
                }
            },
            "⭐ 𝐑𝐚𝐭𝐢𝐧𝐠": {
                "title": "⭐ Rating System Commands",
                "color": discord.Color.gold(),
                "commands": {
                    "!ratingsetup": "Create interactive rating panels with customizable stars/numbers/percentages",
                    "!seerating": "View all rating panels with statistics and management options",
                    "!ratingrefresh <panel_id>": "Refresh statistics for a specific rating panel",
                    "!importrating <JSON file>": "Import rating configurations from a JSON file (attach the file)",
                    "!exportrating": "Export all rating configurations to a JSON file",
                    "Features": "• Star Ratings (1-5)\n• Number Ratings (1-10)\n• Percentage Ratings (0-100%)\n• Real-time statistics\n• Visual vote tracking\n• One-click voting"
                    
                }
            }

        }

        category = category_info[select.values[0]]
        
        embed = EmbedBuilder(
            category["title"],
            "Detailed command information"
        ).set_color(category["color"])
        
        commands = list(category["commands"].items())
        
        for cmd, desc in commands[:24]:
            embed.add_field(cmd, desc, inline=False)
        
        remaining = len(commands) - 24
        footer_text = "🔹 Required <> | Optional []"
        if remaining > 0:
            footer_text += f" | {remaining} more commands available - Use !help {category['title']} for full list"
        
        embed.set_footer(footer_text)
        await interaction.response.edit_message(embed=embed.build(), view=self)

class HelpSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='panel')
    async def help_command(self, ctx):
        embed = EmbedBuilder(
            "⚡ Command Center - TheZ",
            "Select a category below to view available commands"
        ).set_color(discord.Color.blue())
        
        embed.set_thumbnail(ctx.guild.icon.url)
        embed.add_field(
            "Quick Tips",
            f"• Version: {ZygnalBot_Version}\n"
            "• All commands start with !\n"                                  
            "• Some commands require special permissions",
            inline=False
        )
        
        await ctx.send(embed=embed.build(), view=HelpView())

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_check = {}  
        self.caps_threshold = 0.7  
        self.spam_threshold = 5  
        self.spam_interval = 5  
        self.spam_timeout_minutes = 10  
        self.link_whitelist = set()  
        self.banned_words = set()  
        self.load_config()  
        

    def load_config(self):
        
        self.banned_words = {
        "nga", "btc",   
        "hurensohn", "hure", "hurre", "hur3", "hur3ns0hn", "h.u.r.e", "h_u_r_e", 
        "h-u-r-e", "h.u.r.e.n.s.o.h.n", "h_u_r_e_n_s_o_h_n", "h-u-r-e-n-s-o-h-n", 
        "hur3n50hn", "huhrensohn", "hurns0hn", "hurenson", "hurens0hn", "huurensohn", 
        "hureens0hn", "hur3nsohn", "hu-rensohn", "h***ensohn", "hurenzohn", 
        "hurenzoon", "h.uhrensohn", "h@rensohn", "hu~~rensohn", "hurens0*h", 
        "hurenson~", "hu-r3n50hn",
        "schlampe", "schl4mp3", "schl4mpe", "schl.4.mp3", "schl_4_mp3", 
        "schl-4-mp3", "schlamp@", "schlam.p3", "sch|ampe", "schla.mpe", 
        "schl**ampe", "sch|4mp3", "sch~lampe", "schlamp3!", "schlampe-", 
        "sch4mpe", "schl#mp3", "schlamp#", "s-chlampe", "sch|4mp3",
        "fotze", "f0tz3", "f.o.t.z.e", "f_o_t_z_e", "f-o-t-z-e", "f0tz3nkn3cht", 
        "fotz3", "f0t.z3", "fo_tz3", "f*tz3", "fötze", "fö.tze", "fot~ze", 
        "f0~~tz3", "fo~tze", "fotz#", "fot_z3", "f0tz3n~knecht", 
        "arschloch", "4rschl0ch", "arschl0ch", "4rschloch", "4r5chl0ch", 
        "4r5chl0ch", "arsch|och", "ar-schloch", "arsch.loch", "ar.sch.l0ch", 
        "arsch~loch", "arsch-l0ch", "arschl#ch", "ars~hloch", "arsc.hloch", 
        "schwuchtel", "schwul", "schw.u.l", "schw_u_l", "schw-u-l", "schwuul", 
        "schw~ul", "schwül", "schwu~~l", "sch~wuchtel", "schwu|chtel", "schwucht@l", 
        "schw@ul", "sch~wul", "schwu|l", 
        "nazi", "naz1", "n4z1", "n.a.z.i", "n_a_z_i", "n-a-z-i", "n4z1st", 
        "na~~zi", "n~azi", "na!!zi", "na.z.i", "n-a~zi", "n4zi!", 
        "heil", "h31l", "h.e.i.l", "h_e_i_l", "h-e-i-l", "h31l3r", 
        "hitler", "h1tl3r", "hitl3r", "h1tler", "h1.tl3r", "h1_tl3r", 
        "h|tl3r", "hi~tler", "h***ler", "h@tl3r", "hi!tler", 
        "wichser", "w1chs3r", "w1chser", "wichs3r", "w1.chs3r", "w1_chs3r", 
        "wi-chser", "w|chs3r", "wi~chser", "w!chser", "w*chs3r", "wi.chs3r", 
        "spast", "sp4st", "sp.4.st", "sp_4_st", "sp-4-st", "sp4st1", 
        "sp.ast", "sp~ast", "sp@st", "sp~~ast", "s-p4st", "sp**st", 
        "kanake", "k4n4k3", "k4nake", "kan4ke", "k4n.4k3", "k4n_4k3", 
        "ka.nake", "kan~ake", "kan@ke", "k@nake", "k4n4k3!", "ka**ke", 
        "missgeburt", "m1ssgeburt", "missg3burt", "m1ssg3burt", "m1ssg3.burt", 
        "mi~ssgeburt", "mis|geburt", "miss~geburt", "missg3b~urt", "m1ss-g3burt", 
        "nutte", "n0tt3", "nutt3", "n0tte", "n.u.t.t.e", "n_u_t_t_e", 
        "nut~te", "nutt@e", "n~utte", "nutte!", "nu~~tte", "nu.t.te", 
        "fick", "f1ck", "f.i.c.k", "f_i_c_k", "f-i-c-k", "f1ck3n", 
        "ficken", "f1ck3n", "f1cken", "fick3n", "f1.ck3n", "f1_ck3n", 
        "fi~cken", "fick**", "fi~~ck3n", "fi*cken", 
        "scheisse", "sch31ss3", "scheiss3", "sche1sse", "sch.31ss3", 
        "sch~eisse", "sch#isse", "schei~~sse", "sch3iss3", "sche***sse", 
        "fotzenknecht", "f0tz3nkn3cht", "fotz3nknecht", "f0tzenknecht", 
        "fo~~tzenknecht", "fotzen~knecht", "fotzenk~~necht", "fo**knecht", 
        "drecksau", "dr3cks4u", "drecks4u", "dr3cksau", "dr3.cks4u", 
        "dreck~~sau", "dre~cksau", "drecks4u!", "dr3cks@u", 
        "drecksfotze", "dr3cksf0tz3", "drecksf0tze", "dr3cksfotze", 
        "dr~ecksfotze", "drecksf~otze", "dr3~cksfotze", 
        "whore", "wh0re", "whoree", "whör", "wh0r3", "w.h.o.r.e", "w_h_o_r_e",
        "wh0r3h0und", "wh0r3.h0und", "wh0r3_h0und", "wh0r3-h0und", 
        "who.re", "wh*r3", "wh@re", "wh~ore", "whor3", "wh0r@", "wh***re", 
        "wh.re", "who_r3", "who--re", "who~~re", "wh*r3h0und", "wh0_r3h0und",
        "bitch", "b1tch", "b!tch", "b*tch", "b1tch3s", "b!tches", "b17ch", 
        "b.i.t.c.h", "b_i_t_c_h", "b-i-t-c-h", "b1.t.ch", "b1_t_ch", 
        "bitch3s", "b!tch3s", "b1**h", "b*tch3", "bi**h", "bi.t.ch", "b!t.ch",
        "b*ches", "bitc#h", "bi7ch", "bi***h", "b_1tch", "b*t@ches", "b!7ch", 
        "cunt", "kunt", "c*nt", "cxnt", "cvnt", "cuntz", "kuntz", "c0nt", 
        "c.u.n.t", "c_u_n_t", "c-u-n-t", "c0.nt", "c0_nt", "c0-nt", 
        "c.nt", "cu.nt", "k_nt", "kun.t", "cu~nt", "cun7", "c@n7", "k*nt", 
        "slut", "sl*t", "sl4t", "slutz", "sl0t", "slvt", "sl_t", "s1ut", 
        "s.l.u.t", "s_l_u_t", "s-l-u-t", "sl.ut", "sl_ut", "sl-ut", 
        "s1ut", "sl~ut", "sl_tt", "s-l~ut", "slvvut", "sl@t", "s!ut", 
        "faggot", "f4gg0t", "f4ggot", "fag", "f4g", "f@g", "f@gg0t", 
        "f.a.g.g.o.t", "f_a_g_g_o_t", "f-a-g-g-o-t", "f4.gg0t", 
        "f.g.g.o.t", "fa~~g", "f4got", "fa.ggot", "f*g", "fa@@t", "fa!got", 
        "retard", "ret4rd", "r3t4rd", "r3tard", "r3t@rd", "ret@rd", 
        "r.e.t.a.r.d", "r_e_t_a_r_d", "r-e-t-a-r-d", "r3.t4rd", 
        "ret@rded", "r-tard", "re**rd", "re~tard", "r3tard", "r.t~rd", 
        "pussy", "pussies", "p*ssy", "p*ss", "puss1", "p0ssy", "pvssy", 
        "p.u.s.s.y", "p_u_s_s_y", "p-u-s-s-y", "p0.ssy", "p0_ssy", 
        "pussycat", "p*ss!es", "p0ussy", "pu~~ssy", "pu$s", "pu.ssy", 
        "dick", "d1ck", "d!ck", "d*ck", "d1ckhead", "dickhead", "d1ckh34d", 
        "d.i.c.k", "d_i_c_k", "d-i-c-k", "d1.ck", "d1_ck", "d1-ck", 
        "d1cky", "d!cks", "dickz", "di.ck", "dic~k", "di*c", "dic#k", 
        "cock", "c0ck", "cxck", "c*ck", "c0cks", "c0ckz", "cocksucker", 
        "c.o.c.k", "c_o_c_k", "c-o-c-k", "c0.ck", "c0_ck", "c0-ck", 
        "cocks", "co~ck", "c**ks", "c0c*k", "cx*ck", "c@ck", "co~cks",
        "s*upid", 
        "penis", "p3n1s", "pen1s", "p3nis", "p3n!s", "pen!s", "p3n15", 
        "p.e.n.i.s", "p_e_n_i_s", "p-e-n-i-s", "p3.n1s", "p3_n1s", 
        "p.nis", "p3n@s", "pen*s", "p3~~nis", "p3ni$", "pe!nis", "pen!5", 
        "WHORE", "BITCH", "CUNT", "SLUT", "FAGGOT", "RETARD", "PUSSY", 
        "DICK", "COCK", "PENIS", "WH0RE", "B1TCH", "C*NT", "SL*UT", 
        "F@GGOT", "RE**ARD", "P*SSY", "D!CK", "C*CK", "P3N1S",
        "putain", "put1n", "put@in", "put@1n", "putaine", "put@ine", "put@1ne",
        "p.u.t.a.i.n", "p_u_t_a_i_n", "p-u-t-a-i-n", "put.1n", "put_1n", 
        "put*ain", "p!utain", "pu**ain", "p#tain", "p~utain", "pûtain", 
        "putăin", "putäin", "pu&tain", "p.u.tain", "pu|tain", "p-u-t-4-i-n", 
        "pu++ain", "put@!", "putin@", "put@ne", "pu7ain", "put@1n!", 
        "salope", "sal0pe", "s@l0pe", "s@lope", "s@l0p3", "sal0p3", "s@lop3", 
        "s.a.l.o.p.e", "s_a_l_o_p_e", "s-a-l-o-p-e", "s@l.0pe", "s@l_0pe", 
        "sal*pe", "s!lope", "s@l0pe", "s4l0p3", "sälöpe", "sä|ope", "sal0p@", 
        "sal~~ope", "sa|ope", "sa!!pe", "sa---lope", "s@lop@", "s@lo&pe", 
        "connard", "c0nnard", "conn@rd", "c0nn@rd", "c0nn4rd", "c0nn@rd", 
        "c.o.n.n.a.r.d", "c_o_n_n_a_r_d", "c-o-n-n-a-r-d", "c0nn.@rd", 
        "con**ard", "conn@r!", "çonnard", "çønnard", "con~~nard", "co#nard", 
        "conn|ard", "co--nnard", "con.n@rd", "cónnard", "cónnärd", "ç0nn4rd", 
        "merde", "m3rd3", "m3rde", "m3rd3", "m@rd3", "m@rde", "m3rd@", 
        "m.e.r.d.e", "m_e_r_d_e", "m-e-r-d-e", "m3.rd3", "m3_rd3", 
        "me**de", "m3**d3", "me@rde", "mer.d3", "mer_d@", "mêrde", 
        "mérde", "mërdè", "m~~erde", "mèrde", "mérd@", "m3r@de", 
        "enculé", "encu1é", "encu1e", "encu*é", "encülé", "encul@", "encu1@", 
        "en.c.u.l.é", "en_c_u_l_é", "en-cu-lé", "en-cu**é", "encu|é", 
        "bâtard", "batard", "b4tard", "b@tard", "b4t@rd", "bätärd", "ba**ard", 
        "bordel", "b0rd3l", "bord3l", "b0rd@l", "b0rdel", "bord*l", "bor~~del", 
        "pute", "pu**e", "p@ute", "pu~te", "pu_te", "pu-t-e", "pu.te", 
        "foutre", "f0utr3", "f@utre", "foutr@", "fout~re", "fo!tre", "foutr3", 
        "p..utain", "s@l***pe", "c~onnard", "me!rd@", "fo~~utre", "bat~~ard", 
        "enc~~ulé", "bo~~rdel", "pu**t@ine", "m3**rd3", "pu--t-ai-ne", 
        "encul@d", "encu1-@", "c#onnard", "m€rde", "sa|op@", "putain*", 
        "f**tre", "p.ut.in", "s_a_l.o_pe", "conn~ard", "m.rd@", "en_cu&lé", 
        "pute", "putte", "poutain", "poutine", "pootain", "sallop", "salaupe", 
        "merdre", "merrde", "merdd", "connars", "conart", "connar", 
        "enculéé", "encule", "encûlé", "encoulé", "bâtars", "batards", "batar", 
        "vazy", "vasi", "vasie", "va chier", "va te faire", "vaff", "fauteuil", 
        "PUTAIN", "PUT@IN", "SALOPE", "CONNARD", "MERDE", "ENCULÉ", "BÂTARD", 
        "BORDEL", "PUTE", "FOUTRE", "S@LOPE", "C*NNARD", "M3RDE", "ENCUL3", 
        "EN_CU_LÉ", "BA**ARD", "FOU_TRE", "PU-TE", "ME-RDE", "VAFFANCULO",
        "puttana", "putt4n4", "putt@n@", "putt@n4", "putt4n@", "putt4n4",
        "p.u.t.t.a.n.a", "p_u_t_t_a_n_a", "p-u-t-t-a-n-a", "putt.4n4", 
        "p*uttana", "p!uttana", "pu**tana", "p@uttana", "putta!na", "pu.t.t.a.n.a",
        "put.tana", "putt_a_na", "p--u-t-t-a-n-a", "p~u~t~t~a~n~a", 
        "puttan4", "pút.tànà", "pu##ana", "puttan@", "puʇʇanɐ",
        "cazzo", "c4zz0", "c@zz0", "c@zzo", "c4zzo", "c@zz0", "c4zz0",
        "c.a.z.z.o", "c_a_z_z_o", "c-a-z-z-o", "c4.zz0", "c4_zz0", 
        "càzzò", "cäzzö", "c*zzo", "ca##o", "c@zzo!", "çazzo", 
        "ca_zzo", "c-a.z.z-o", "c~azz0", "k4zz0", "căzzô", "ç@zz0",
        "stronzo", "str0nz0", "str0nzo", "str0nz@", "str0nz4", "str0nz0",
        "s.t.r.o.n.z.o", "s_t_r_o_n_z_o", "s-t-r-o-n-z-o", "str0.nz0", 
        "stronz0", "str0n.z.o", "st-r-on-z-o", "str0n*z@", "s~tronzo", 
        "strömzø", "st_ronz0", "s-t_r_o-n-z-o", "ştronzo", "str0nz#", 
        "merda", "m3rd@", "m3rd4", "m.e.r.d.a", "m_e_r_d_a", "m-e-r-d-a", "m3rda",
        "figa", "f1g@", "f1ga", "f.i.g.a", "f_i_g_a", "f-iga", "fig@", "fi**a",
        "bastardo", "b4st@rd0", "b4stardo", "b.a.s.t.a.r.d.o", "b_a_s_t_a_r_d_o",
        "vaffanculo", "v4ff4ncul0", "v@ff@nculo", "vaff@nculo", "vaffancul@", 
        "pezzo di m3rd@", "pezzo_di_merda", "p.e.z.z.o.d.i.m.e.r.d.a", "pezzo.d.m.", 
        "co****ne", "c0*****e", "co--gli**ne", "çoglione", "c-o-g-l-i-o-n-e", 
        "zoccola", "z0ccol@", "z0ccola", "z.o.c.c.o.l.a", "z_o_c_c_o_l_a", 
        "figliodiputtana", "figli0diputt4n@", "figli0_diputt@n@", 
        "vaf*****ulo", "vaff@*********", "c****0 di m***a", 
        "p._utt4n@", "c.4_zz0", "s_t**nzo", "me$$da", "fi@@a", "va~~fan~~culo", 
        "str**nz@", "put&@n@", "fig.o~", "bas***do", "za!ccola", "pe##o", 
        "vaff_~anculo", "c0gl!ion#", "c.o.g.l.-o.n.e", "pez*dimerda", 
        "potana", "pottana", "puttna", "putna", "pzzo", "strunzo", "stronza", 
        "strozno", "strozo", "bastard@", "merd@", "merdino", "vafan", "vafanc", 
        "vafa!", "fanculo", "fan****lo", "fu***", "cul0", "culo!", "cul@", "kulo",
        "figh@", "figha", "fi*ha", "f1gh@", "figh3", "ma****", "mannaggia", 
        "mann@ggia", "mann***ia", "mannagg1a",
        "Puttana", "PUTTANA", "PUTT4N4", "PUTT@n@", "PUTT@n4", "PUTT@N@", 
        "CAZZO", "C4ZZO", "C@ZZO", "C.A.Z.Z.O", "C-A-Z-Z-O", "MERDA", "FIGA",
        "STRONZO", "Vaffanculo", "COGLIONE", "ZOCCOLA", "BASTARDO", "CUL0",
        "FAN****LO", "FI@HA", "POTANA", "VAFFA",
        "馬鹿", "バカ", "死ね", "クソ", "カス", "ちんこ", "まんこ", "おっぱい",
        "baka", "b4k4", "b@k@", "b@k4", "b4k@", "b@k@", "b4k4", "b@k4",
        "b.a.k.a", "b_a_k_a", "b-a-k-a", "b4.k4", "b4_k4", "b4-k4",
        "kuso", "kus0", "ku50", "kus@", "ku5@", "kus0", "ku50", "kus@",
        "k.u.s.o", "k_u_s_o", "k-u-s-o", "kus.0", "kus_0", "kus-0",
        "baka-san", "baka-chan", "baka-kun", "baka-sama", "baka desu", 
        "baka da", "baka ne", "baka yo", "baka baka", "baka na", "baka janai",
        "baka mitai", "baka sugiru", "baka deshou", "baka desho", 
        "baka hontou", "baka shinde", "baka shine", "baka yarou", "baka mono",
        "kusotare", "kusogaki", "kuso yarou", "kuso baka", "kuso shine",
        "kuso janai", "kuso mitai", "kuso desu", "kuso da", "kuso yo",
        "kuso kuso", "kuso mono", "kuso ne", "kuso sugiru", "kusottare",
        "kuso baka shine", "kuso yarou shine", "kusoyarou baka",
        "kusoyarou shine", "kusottare shine", "kusoyarou baka shine",
        "baka kuso", "baka kusoyarou", "baka kusottare", "baka shine yo",
        "baka kuso shine", "baka kusoyarou shine", "baka kusottare shine",
        "chinko", "chinkokun", "chinkochan", "chinko shine", "chinko baka",
        "chinko kuso", "chinko yarou", "chinko shine yo", "chinko shine ne",
        "chinko sugiru", "chinko yarou baka", "chinko baka shine",
        "manman", "manmanko", "mankosu", "mankoyarou", "manko shine",
        "manko baka", "manko kuso", "manko yarou", "manko shine yo",
        "manko shine ne", "manko sugiru", "manko yarou baka", "manko baka shine",
        "manko kusoyarou", "manko kusottare", "oppai", "oppai yarou", 
        "oppai baka", "oppai kuso", "oppai shine", "oppai baka shine", 
        "oppai kusoyarou", "oppai kusottare", "oppai sugiru", 
        "oppai yarou baka", "oppai baka shine", "oppai kusoyarou shine",
        "shine", "shine yo", "shine ne", "shine baka", "shine kuso",
        "shine yarou", "shine desu", "shine na", "shine mitai", 
        "shine sugiru", "shine janai", "shine yarou baka", "shine baka kuso",
        "shine kusoyarou", "shine kusottare", "shine baka shine",
        "kusoyarou", "kusoyarou shine yo", "kusoyarou shine ne",
        "kusoyarou shine baka", "kusoyarou shine kuso", "kusoyarou baka shine",
        "kusottare shine", "kusottare shine yo", "kusottare shine ne",
        "kusottare shine baka", "kusottare shine kuso", "kusottare baka shine",
        "baka yarou shine", "baka yarou shine yo", "baka yarou shine ne",
        "baka yarou shine baka", "baka yarou shine kuso", "baka yarou kuso shine",
        "baka yarou kusoyarou", "baka yarou kusottare", "baka yarou baka shine",
        "baka yarou kuso shine baka", "baka yarou kusoyarou shine",
        "baka yarou kusottare shine", "baka yarou kuso baka shine",
        "baka yarou kuso baka shine yo", "baka yarou kuso baka shine ne",
        "baka yarou kuso baka shine sugiru", "baka yarou kuso baka shine desu",
        "baka yarou kuso baka shine janai", "baka yarou kuso baka shine mitai",
        "baka yarou kuso baka shine hontou",
        "n1gg4", "n1gg3r", "n1663r", "n166a", "n1664", "nigg4", "nigg3r",
        "n.i.g.g.4", "n_i_g_g_4", "n-i-g-g-4", "n1.gg4", "n1_gg4",
        "f.u.c.k", "f_u_c_k", "f-u-c-k", "f.v.c.k", "f_v_c_k", "f-v-c-k",
        "fvck", "phuck", "phvck", "fück", "fuck", "f*ck", "f**k", "fuk",
        "fucc", "fukk", "fuking", "fucking", "fvcking", "phucking",
        "motherfucker", "mothafucka", "muthafucka", "mtherfcker",
        "mthrfckr", "motherfckr", "mothafckr", "mthafckr", "mtherfker",
        "n1ggar", "n1gger", "niggah", "niggar", "niggur", "niggarz", "niggahz",
        "nigga", "nigger", "btch", "bitch", "b1tch", "b1tchz", "b1tchaz",
        "n1ggah", "niggaz", "n1ggaz", "nigguh", "n1gguh", "nigguz", "n1gguz",
        "fukc", "fukkk", "fukkin", "fukker", "fukerz", "fukken", "fukingz",
        "fuckz", "fuckinn", "fuckinnz", "fuckers", "fuckersz", "fuckar",
        "fuckah", "fvckz", "fvcukk", "fvcukz", "fvckah", "fvckar", "fvckez",
        "phuk", "phukk", "phucker", "phuckar", "phuckah", "phukerz",
        "phucken", "phukking", "phukers", "fukz", "fukah", "fukkez", "fukers",
        "motherfuck", "mthrfuck", "mtherfuk", "mtherfuckah", "mtherfuckar",
        "mthafucka", "muthafukah", "mthrfkkr", "mtherfkerz", "motherfkkr",
        "muthrfcker", "mthafker", "motherfkerz", "mtherfkkr", "mtherfukah",
        "fukcinn", "fuckinnah", "fuckahzz", "fuckarzz", "fvcah", "fvcar",
        "fvcuck", "fvckahz", "fukinnzz", "phuckinn", "phukin", "phuckk",
        "phukinzz", "phuckkk", "phuckerzz", "phukingg", "mothafker", "mthafkr",
        "muthafkr", "mthrfck", "mothrfckr", "mthafcker", "mthrfkerz",
        "motherfkrz", "mthrfuckk", "mtherfukker", "mthrfukkerz", "motherfker",
        "mtherfkrz", "mthafukker", "mthrfker", "mthrfkrr", "motherfukkerz",
        "fuckinnn", "fukcinnn", "fukkerz", "fukinnzz", "fvckinn", "fvckinnz",
        "phuckah", "phuckahz", "fvcker", "fvckerz", "phukahz", "phukinzz",
        "phuckeninn", "phuckerinn", "phukerszz", "fukking", "fuckinggg",
        "fuckkinnz", "fuckinz", "fuckennz", "fvcukinnz", "fukahnn", "fvcahz",
        "fvcahh", "fvckarh", "fukkerinn", "fuckkerinn", "fuckennn", "fukennz",
        "fvcukinn", "fvcukkinn", "phvcukk", "phvcukkah", "fvckinnnn",
        "fvckennnn", "fvckennz", "phukenn", "phuckeninnzz", "fukcah", "phukah",
        "fukinnnzz", "fuckarrr", "fvckarrr", "phuckarrr", "phukenarrr",
        "phukckk", "phvckk", "fvckarzz", "fuckarz", "fuckinnzzz", "fvckinnz",
        "phukz", "fukkzzz", "fukkahz", "phukkahzz", "mtherfkr", "mtherfkkr",
        "mthrfkkrz", "mthrfkrz", "mthrfkkrr", "mthrfuckkrr", "mtherfkkrr",
        "motherfkkrr", "motherfkrr", "motherfuckahrr", "motherfkkrz",
        "mthrfukkrz", "mthrfuckarrr", "mthrfkerinn", "motherfkerinn",
        "motherfuckerinn", "mthrfkerah", "mtherfukkerzz", "motherfukkerinnzz",
        "mthrfkerahzz", "fukkz", "fuckkz", "fvckzz", "fvckahzz", "phvcah",
        "phvcukz", "fvcckzz", "fvcckah", "fukkkah", "phukahzz", "phvcukah",
        "phvcukahzz", "phukckkzz", "phvcukenn", "fukenn", "fuckkinnzz", 
        "fvckennzz", "phuckar", "phuckarrrzz", "fukinnnnz", "fvckinnnnz", 
        "phuckinnzz", "phuckerinnzz", "fvccahnn", "fvccahh", "fvccukzz",
        "fvccennzz", "fvccenn", "fvccukennzz", "fvccahz", "phuckennzz",
        "fvccahnnzz", "fukahz", "phukahh", "phvcukahh", "fvccahinnzz", 
        "fvccahkk", "phuckkkinn", "phvcukinn", "phvcukinnzz", "fvccukahh", 
        "fvcckerzz", "fvcckerinnzz", "phvcahzz", "fvccennnnz",
        "kys", "k y s", "k.y.s", "k_y_s", "k-y-s", "k.y.s.", "k_y_s_",
        "kill yourself", "k1ll y0urs3lf", "k!ll y0urs3lf", "k1ll y0urs3lf",
        "k.i.l.l.y.o.u.r.s.e.l.f", "k_i_l_l_y_o_u_r_s_e_l_f",
        "suicide", "su1c1d3", "su1c1de", "suic1de", "su1cide", "su!c!de",
        "s.u.i.c.i.d.e", "s_u_i_c_i_d_e", "s-u-i-c-i-d-e", "su1.c1d3",
        "self harm", "s3lf h4rm", "s3lf.h4rm", "s3lf_h4rm", "s3lf-h4rm",
        "s.e.l.f.h.a.r.m", "s_e_l_f_h_a_r_m", "s-e-l-f-h-a-r-m",
        "kys now", "kys immediately", "kys today", "kys please", "kys fast",
        "kill_urself", "kill_ur_self", "kill-yourself-now", "kill yourself fast",
        "kill yourself today", "just kill yourself", "why not kys", "go kys now",
        "you should kys", "how to kys", "kys tutorial", "suicide now", 
        "do suicide", "go do suicide", "commit suicide", "suicide guide",
        "suicide fast", "suicide quickly", "suicide tonight", "suicide tomorrow",
        "suicide for sure", "s u i c i d e", "sui cide", "suicide plans",
        "plan suicide", "suicide instructions", "suicide advice",
        "suicide methods", "suicide help", "how to self harm", 
        "self_harm_now", "self harm tutorial", "commit self harm", 
        "self harm guide", "self harm plan", "start self harm", 
        "self harm immediately", "self harm today", "self harm please",
        "self harm now", "you should self harm", "just self harm", 
        "self harm instructions", "self harm advice", "self harm tips",
        "how to commit self harm", "self_harm_tutorial", "self harm tonight",
        "go self harm", "self harm methods", "self harm fast", 
        "self_harm_quickly", "self harm quickly", "commit_self_harm",
        "self harm tomorrow", "self harm suggestions", "ways to self harm",
        "steps to self harm", "suicide plans now", "self harm guide online",
        "why not suicide", "learn suicide", "find suicide tips",
        "kill your self", "kill yourself today", "kill yourself tips",
        "kys easily", "kys guide", "how to kys quickly", 
        "kys suggestions", "kys steps", "how to kys instructions",
        "kys easily today", "kys methods online", "kys safely",
        "self harm safely", "self harm today fast", "commit self harm tonight",
        "self harm immediately tips", "suicide now guide", 
        "suicide fast steps", "commit suicide tomorrow", 
        "do suicide plans", "just suicide", "you should suicide now",
        "go and suicide", "kys faster", "kys slower", "kill your self today",
        "suicide now tutorial", "suicide now advice", "why suicide is good",
        "how suicide works", "self harm is okay", "start self harming now",
        "self_harm_help", "self harm techniques", "self harm advice online",
        "kys instructions online", "suicide tips fast", "suicide now tutorial",
        "commit self harm tutorial", "start_kys", "kys help", "kys now please",
        "suicide please", "help me suicide", "suicide suggestions",
        "kys planning", "kys execution", "suicide execution", "suicide tonight",
        "commit_suicide_fast", "plan your suicide", "how to kys properly",
        "suicide guide instructions", "how to commit_self_harm",
        "self harm advice safely", "how to end it all", "end your life now",
        "suicide today", "learn how to kys", "you should kys now",
        "kys_step_by_step", "ways to end it", "self_harm_online",
        "go harm yourself", "just go kys", "suicide plans fast",
        "commit_suicide_instructions", "kill_your_self_guide", "end it tutorial",
        "self harm method", "method for self harm", "suicide execution guide",
        "suicide execution tips", "suicide execution methods",
        "kys_today", "kill_your_self_fast", "suicide fast tonight",
        "self harm tonight plans", "commit self harm fast guide",
        "suicide tomorrow plans", "harm yourself safely", 
        "harm yourself guide", "harm yourself tips", 
        "harm yourself methods", "harm yourself fast", 
        "harm yourself now tutorial", "how to harm yourself easily", 
        "suicide step guide", "suicide instruction plans", 
        "suicide_tips", "suicide safely guide", "self harm safely tips",
        "harm yourself now", "why harm yourself", "why not self harm",
        "harm yourself techniques", "harm yourself execution",
        "harm yourself tools", "tools for suicide", "tools for harm",
        "suicide techniques safely", "harm yourself fast online", 
        "tools for self harm", "harm yourself instructions", 
        "commit_harm", "commit_self_harm_steps", "suicide safely tutorial",
        "free nitro", "fr33 n1tr0", "free.nitro", "fr33.n1tr0", "fr33_n1tr0",
        "f.r.e.e.n.i.t.r.o", "f_r_e_e_n_i_t_r_o", "f-r-e-e-n-i-t-r-o",
        "steam gift", "st34m g1ft", "steam.gift", "st34m.g1ft", "st34m_g1ft",
        "s.t.e.a.m.g.i.f.t", "s_t_e_a_m_g_i_f_t", "s-t-e-a-m-g-i-f-t",
        "robux generator", "r0bux g3n3r4t0r", "robux.generator",
        "r.o.b.u.x.g.e.n.e.r.a.t.o.r", "r_o_b_u_x_2_g_e_n_e_r_a_t_o_r",
        "free_nitro_code", "free nitro giveaway", "free nitro bot",
        "get free nitro", "nitro giveaway free", "free nitro now",
        "steam_gift_card", "steam gift codes", "steam_gift_now",
        "free_steam_gift", "robux free generator", "robux gift generator",
        "robux free codes", "robux generator free", "robux generator online",
        "free_nitro_code_2023", "free_nitro_generator", "nitro free discord",
        "free discord nitro", "nitro discount free", "discord gift nitro",
        "steam_discount_gift", "steam freebie gift", "free_robux_now",
        "robux free access", "robux generator new", "robux generator giveaway",
        "robux hack generator", "free_robux_bot", "discord_free_gift",
        "discord_nitro_bot", "get_free_robux", "robux_online_tool",
        "discord_code_generator", "discord_nitro_free", "steam_gift_online",
        "steam_card_gift", "steam_card_discount", "robux_hack_tool",
        "robux_promo_codes", "robux_gift_online", "robux_tool_generator",
        "free_gift_online", "discord_promo_bot", "steam_promo_codes",
        "steam_code_hack", "free_steam_codes", "robux_promo_tool",
        "robux_access_generator", "get_steam_card", "free_gift_steam",
        "nitro_giveaway_bot", "discord_promo_code", "free_bot_gift",
        "nitro_code_promo", "steam_bot_codes", "nitro_hack_tool",
        "get_promo_nitro", "steam_gift_key", "steam_gift_discount",
        "robux_key_generator", "free_promo_code", "discord_tool_bot",
        "free_nitro_access", "robux_key_hack", "promo_code_generator",
        "free_steam_access", "gift_code_online", "nitro_online_tool",
        "steam_access_gift", "robux_online_access", "nitro_bot_generator",
        "get_robux_now", "free_promo_generator", "robux_gift_discount",
        "robux_promo_key", "robux_gift_code", "nitro_card_promo",
        "steam_online_gift", "free_steam_discount", "gift_bot_robux",
        "robux_bot_tool", "discord_promo_codes", "steam_gift_code_now",
        "robux_card_tool", "promo_tool_robux", "steam_gift_bot",
        "robux_tool_now", "robux_online_bot", "robux_gift_tool",
        "steam_code_promo", "free_key_nitro", "free_robux_code",
        "discord_hack_gift", "robux_tool_card", "promo_tool_discount",
        "nitro_discount_tool", "robux_hack_codes", "steam_discount_code",
        "free_gift_tool", "robux_code_tool", "discord_card_generator",
        "free_tool_gift", "robux_key_discount", "robux_discount_bot",
        "free_tool_card", "steam_key_promo", "nitro_tool_bot",
        "nitro_gift_codes", "steam_key_generator", "free_promo_gift",
        "free_bot_promo", "gift_card_online", "robux_access_promo",
        "free_key_discount", "free_key_tool", "nitro_promo_discount",
        "nitro_gift_online", "nitro_key_codes", "robux_discount_tool",
        "steam_bot_gift", "nitro_discount_bot", "steam_promo_tool",
        "discord_promo_generator", "nitro_bot_key", "robux_card_promo",
        "steam_tool_discount", "robux_discount_codes", "nitro_key_online",
        "steam_card_key", "promo_gift_code", "gift_tool_online",
        "gift_key_promo", "nitro_online_access", "steam_discount_bot",
        "nitro_giveaway_tool", "promo_access_bot", "robux_code_promo",
        "gift_code_promo", "free_nitro_promo", "gift_access_tool",
        "free_nitro_key", "nitro_card_codes", "free_access_tool",
        "steam_giveaway_bot", "promo_code_bot", "robux_promo_bot",
        "promo_card_tool", "free_access_promo", "steam_access_code",
        "free_gift_key", "promo_discount_tool", "promo_discount_bot",
        "promo_key_bot", "promo_key_tool", "promo_gift_tool",
        "discount_gift_bot", "promo_bot_discount", "promo_access_tool",
        "gift_card_promo", "nitro_gift_discount", "free_discount_code",
        "discord_promo_gift", "promo_code_discount", "promo_key_code",
        "discount_bot_key", "discount_tool_code", "promo_bot_card",
        "promo_key_promo", "discount_key_promo", "gift_card_access",
        "promo_code_online", "gift_key_online", "promo_code_access",
        "promo_access_code", "discount_bot_tool", "promo_code_card",
        "promo_discount_card", "gift_discount_tool", "promo_card_key",
        "promo_key_access", "discount_access_bot", "promo_discount_access",
        "promo_code_key", "promo_discount_key", "promo_key_online",
        "gift_key_card", "discount_promo_bot", "promo_giveaway_card",
        "promo_bot_online", "gift_tool_discount", "discount_giveaway_tool",
        "promo_code_giveaway", "promo_tool_access", "promo_key_discount",
        "discount_card_tool", "gift_bot_discount", "promo_key_gift",
        "discount_key_gift", "promo_gift_access", "promo_card_access",
        "promo_discount_gift", "promo_giveaway_access", "promo_key_tool",
        "discount_gift_access", "promo_tool_key", "promo_card_discount",
        "promo_discount_code", "promo_card_tool", "discount_card_key",
        "promo_key_generator", "promo_tool_online", "promo_tool_gift",
        "promo_discount_bot", "promo_gift_code", "discount_key_tool",
        "promo_access_card", "promo_tool_discount", "promo_bot_access",
        "promo_discount_tool", "promo_key_tool", "promo_discount_access",
        "promo_code_tool", "promo_card_key", "promo_key_online",
        "promo_tool_card", "promo_discount_key", "promo_access_tool",
        "🖕", "promo",
        }
        
    
    async def check_banned_words(self, message):
        """Check for banned words, including bypassed versions."""
        content = message.content.lower()
        for word, pattern in self.banned_regex.items():
            if pattern.search(content):
                await message.delete()
                await self.send_warning(message.channel, message.author, "banned_words")
                return True
        return False
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or isinstance(message.channel, discord.DMChannel):
            return

        await self.check_message(message)

    async def check_message(self, message):
        checks = [
            self.check_spam,
            self.check_caps,
            self.check_links,
            self.check_banned_words
        ]

        for check in checks:
            action = await check(message)
            if action:
                return

    async def check_spam(self, message):
        
        author_id = message.author.id
        current_time = time.time()

        if author_id not in self.spam_check:
            self.spam_check[author_id] = {"messages": 1, "last_message": current_time}
            return False

        if current_time - self.spam_check[author_id]["last_message"] > 5:
            self.spam_check[author_id] = {"messages": 1, "last_message": current_time}
            return False

        self.spam_check[author_id]["messages"] += 1
        
        if self.spam_check[author_id]["messages"] >= 5:
            await message.author.timeout(timedelta(minutes=(self.spam_timeout_minutes)), reason="Spam detection")
            await self.send_warning(message.channel, message.author, "spam")
            return True

        self.spam_check[author_id]["last_message"] = current_time
        return False

    async def check_caps(self, message):
        if len(message.content) < 8:
            return False

        caps_ratio = sum(1 for c in message.content if c.isupper()) / len(message.content)
        if caps_ratio > self.caps_threshold:
            await message.delete()
            await self.send_warning(message.channel, message.author, "caps")
            return True
        return False

    async def check_links(self, message):
    
        BOT_OWNER_ID = os.getenv('BOT_OWNER_ID')

        if not BOT_OWNER_ID or not BOT_OWNER_ID.isdigit():
            raise ValueError("Invalid BOT_OWNER_ID in .env file. It must be a numeric Discord ID.")

        BOT_OWNER_ID = int(BOT_OWNER_ID)

        if message.author.guild_permissions.manage_messages or message.author.id == BOT_OWNER_ID:
            return False

        words = message.content.lower().split()
        for word in words:
        
            if any(link in word for link in ['http://', 'https://', 'discord.gg']):
            
                if not any(allowed in word for allowed in self.link_whitelist):
              
                    await message.delete()
                    await self.send_warning(message.channel, message.author, "links")
                    return True
        return False

    async def check_banned_words(self, message):
        if any(word in message.content.lower() for word in self.banned_words):
            await message.delete()
            await self.send_warning(message.channel, message.author, "banned_words")
            return True
        return False

    async def send_warning(self, channel, user, violation_type):
        warnings = {
            "spam": "Please do not spam messages.",
            "caps": "Please avoid using excessive caps.",
            "links": "Unauthorized links are not allowed.",
            "banned_words": "Please watch your language."
        }

        embed = EmbedBuilder(
            "⚠️ Warning",
            warnings.get(violation_type, "Rule violation detected.")
        ).set_color(discord.Color.orange())
        
        embed.add_field("User", user.mention)
        embed.add_field("Violation", violation_type.title())
        
        await channel.send(embed=embed.build(), delete_after=10)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def automod(self, ctx, setting: str = None, value: str = None, timeout_minutes: int = None):
        """Configure AutoMod settings or display current settings and commands."""
        if timeout_minutes is None:
            timeout_minutes = self.spam_timeout_minutes

        if setting is None:
            embed = EmbedBuilder(
                "⚙️ AutoMod Settings Panel",
                "Here are the current AutoMod settings and available commands:"
            ).set_color(discord.Color.blue())

            embed.add_field("Spam Threshold", f"{self.spam_threshold} messages in {self.spam_interval} seconds")
            embed.add_field("Spam Timeout", f"{self.spam_timeout_minutes} minutes")
            embed.add_field("Caps Threshold", f"{self.caps_threshold * 100}%")

            whitelist_display = "\n".join(list(self.link_whitelist)[:5]) if self.link_whitelist else "None"
            embed.add_field("Whitelisted Links (First 5)", whitelist_display)

            banned_words_display = "\n".join(list(self.banned_words)[:5]) if self.banned_words else "None"
            embed.add_field("Banned Words (First 5)", banned_words_display)

            commands_explanation = (
                "**Commands:**\n"
                "`!automod caps_threshold <value>` - Set the maximum allowed percentage of caps in a message (0.0-1.0).\n"
                "`!automod spam_threshold <value> [timeout_minutes]` - Set the number of messages allowed before spam detection and the timeout duration.\n"
                "`!automod add_banned_word <word>` - Add a word to the banned words list.\n"
                "`!automod add_whitelist <url>` - Add a URL to the link whitelist.\n"
                "`!automod` - Display the current AutoMod settings and available commands."
            )
            embed.add_field("Available Commands", commands_explanation)

            await ctx.send(embed=embed.build())
            return

        settings = {
            'caps_threshold': float,
            'spam_threshold': int,
            'add_banned_word': str,
            'add_whitelist': str
        }

        if setting not in settings:
            return await ctx.send("Invalid setting!")

        try:
            if setting == 'spam_threshold':
                self.spam_check = {}
                self.spam_threshold = int(value)
                self.spam_timeout_minutes = timeout_minutes

                embed = EmbedBuilder(
                    "⚙️ AutoMod Spam Settings Updated",
                    f"Threshold: {value} messages in {self.spam_interval} seconds\nTimeout: {timeout_minutes} minutes"
                ).set_color(discord.Color.green()).build()

            elif setting in ['add_banned_word', 'add_whitelist']:
                if setting == 'add_banned_word':
                    self.banned_words.add(value.lower())
                else:
                    self.link_whitelist.add(value.lower())
                embed = EmbedBuilder(
                    "⚙️ AutoMod Updated",
                    f"Setting `{setting}` updated with value `{value}`"
                ).set_color(discord.Color.green()).build()
            else:
                setattr(self, setting, settings[setting](value))
                embed = EmbedBuilder(
                    "⚙️ AutoMod Updated",
                    f"Setting `{setting}` updated to `{value}`"
                ).set_color(discord.Color.green()).build()

            await ctx.send(embed=embed)
        except ValueError:
            await ctx.send("Invalid value format!")

bot.add_cog(HelpSystem(bot))
bot.add_cog(AutoMod(bot))

class WelcomeSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_configs = {}

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """Welcome message configuration commands"""
        embed = EmbedBuilder(
            "Welcome System Commands",
            "Available commands for welcome message configuration"
        ).set_color(discord.Color.blue())
        
        embed.add_field("!welcome message <message>", "Set welcome message\nVariables: {user}, {server}, {count}")
        embed.add_field("!welcome color <color>", "Set embed color (e.g. red, blue, green)")
        embed.add_field("!welcome test", "Preview current welcome message")
        embed.add_field("!welcome reset", "Reset to default message")
        embed.add_field("!welcome channel #channel", "Set welcome channel")
        
        await ctx.send(embed=embed.build())

    @welcome.command(name="message")
    @commands.has_permissions(administrator=True)
    async def set_message(self, ctx, *, message: str):
        """Set a custom welcome message"""
        if ctx.guild.id not in self.welcome_configs:
            self.welcome_configs[ctx.guild.id] = {}
            
        self.welcome_configs[ctx.guild.id]["message"] = message
        
        preview = message.replace("{user}", ctx.author.mention)
        preview = preview.replace("{server}", ctx.guild.name)
        preview = preview.replace("{count}", str(len(ctx.guild.members)))
        
        embed = EmbedBuilder(
            "✅ Welcome Message Set",
            "New welcome message configured"
        ).set_color(discord.Color.green())
        
        embed.add_field("Preview", preview)
        await ctx.send(embed=embed.build())

    @welcome.command(name="color")
    @commands.has_permissions(administrator=True)
    async def set_color(self, ctx, color: str):
        """Set welcome embed color"""
        colors = {
            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "gold": discord.Color.gold(),
            "purple": discord.Color.purple()
        }
        
        if color.lower() not in colors:
            valid_colors = ", ".join(colors.keys())
            return await ctx.send(f"Valid colors: {valid_colors}")
            
        if ctx.guild.id not in self.welcome_configs:
            self.welcome_configs[ctx.guild.id] = {}
            
        self.welcome_configs[ctx.guild.id]["color"] = colors[color.lower()]
        
        embed = EmbedBuilder(
            "🎨 Welcome Color Set",
            f"Welcome message color set to {color}"
        ).set_color(colors[color.lower()]).build()
        
        await ctx.send(embed=embed)

    @welcome.command(name="test")
    @commands.has_permissions(administrator=True)
    async def test_welcome(self, ctx):
        """Preview current welcome message"""
        config = self.welcome_configs.get(ctx.guild.id, {})
        message = config.get("message", f"Welcome {'{user}'} to {'{server}'}!")
        color = config.get("color", discord.Color.brand_green())
        
        preview = message.replace("{user}", ctx.author.mention)
        preview = preview.replace("{server}", ctx.guild.name)
        preview = preview.replace("{count}", str(len(ctx.guild.members)))
        
        embed = EmbedBuilder(
            "👋 Welcome Preview",
            preview
        ).set_color(color)
        
        embed.add_field("Member Count", f"#{len(ctx.guild.members)}")
        embed.add_field("Account Created", ctx.author.created_at.strftime("%B %d, %Y"))
        embed.set_thumbnail(ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        
        await ctx.send(embed=embed.build())

    @welcome.command(name="channel")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Set welcome message channel"""
        if ctx.guild.id not in self.welcome_configs:
            self.welcome_configs[ctx.guild.id] = {}
            
        self.welcome_configs[ctx.guild.id]["channel_id"] = channel.id
        
        embed = EmbedBuilder(
            "📝 Welcome Channel Set",
            f"Welcome messages will be sent to {channel.mention}"
        ).set_color(discord.Color.green()).build()
        
        await ctx.send(embed=embed)

    @welcome.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_welcome(self, ctx):
        """Reset welcome message to default"""
        if ctx.guild.id in self.welcome_configs:
            del self.welcome_configs[ctx.guild.id]
            
        embed = EmbedBuilder(
            "🔄 Welcome Reset",
            "Welcome message configuration has been reset to default"
        ).set_color(discord.Color.blue()).build()
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
    
        config = self.welcome_configs.get(member.guild.id, {})
        channel_id = config.get("channel_id")
        welcome_channel = member.guild.get_channel(channel_id) if channel_id else discord.utils.get(member.guild.channels, name="welcome")

        if welcome_channel:
            message = config.get("message", f"Welcome {member.mention} to {member.guild.name}!")
            color = config.get("color", discord.Color.brand_green())

            message = message.replace("{user}", member.mention)
            message = message.replace("{server}", member.guild.name)
            message = message.replace("{count}", str(len(member.guild.members)))

            embed = EmbedBuilder(
                "👋 Welcome to the Server!",
                message
            ).set_color(color)

            embed.add_field("Member Count", f"#{len(member.guild.members)}")
            embed.add_field("Account Created", member.created_at.strftime("%B %d, %Y"))
            embed.set_thumbnail(member.avatar.url if member.avatar else member.default_avatar.url)

            rules_channel = discord.utils.get(member.guild.channels, name="rules")
            if rules_channel:
                embed.add_field("Important", f"Please read {rules_channel.mention}", inline=False)

            await welcome_channel.send(embed=embed.build())

        server_management_cog = self.bot.get_cog("ServerManagement")
        if server_management_cog and hasattr(server_management_cog, "autorole_dict"):
            autorole_dict = server_management_cog.autorole_dict
            if member.guild.id in autorole_dict:
                role_id = autorole_dict[member.guild.id]
                role = member.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role)
                        print(f"Assigned role '{role.name}' to {member.name}.")
                    except discord.Forbidden:
                        print(f"Error: Insufficient permissions to assign the role '{role.name}' to {member.name}.")
                    except discord.HTTPException as e:
                        print(f"HTTP Exception: {e}")
                else:
                    print(f"Role ID {role_id} not found in guild {member.guild.name}.")

class ReactionRoles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🎮 Gamer", style=discord.ButtonStyle.blurple, custom_id="role_gamer")
    async def gamer_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "Gamer")

    @discord.ui.button(label="🎵 Music", style=discord.ButtonStyle.green, custom_id="role_music")
    async def music_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "Music")

    @discord.ui.button(label="🎨 Artist", style=discord.ButtonStyle.red, custom_id="role_artist")
    async def artist_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "Artist")

    async def toggle_role(self, interaction: discord.Interaction, role_name: str):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            role = await interaction.guild.create_role(name=role_name)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            embed = EmbedBuilder(
                "Role Removed",
                f"Removed {role.mention} role"
            ).set_color(discord.Color.red()).build()
        else:
            await interaction.user.add_roles(role)
            embed = EmbedBuilder(
                "Role Added",
                f"Added {role.mention} role"
            ).set_color(discord.Color.green()).build()

        await interaction.response.send_message(embed=embed, ephemeral=True)

class DesignStudioView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog

    @discord.ui.button(label="Color Theme", style=discord.ButtonStyle.blurple, emoji="🎨")
    async def color_theme(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ColorThemeModal(self.cog))

    @discord.ui.button(label="Button Styles", style=discord.ButtonStyle.green, emoji="🔘")
    async def button_styles(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ButtonStyleModal(self.cog))

    @discord.ui.button(label="Layout Options", style=discord.ButtonStyle.gray, emoji="📐")
    async def layout(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LayoutModal(self.cog))

    @discord.ui.button(label="Edit Text", style=discord.ButtonStyle.primary, emoji="✏️")
    async def edit_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TextEditModal(self.cog))


class CreateRoleGroupModal(discord.ui.Modal, title="Create Role Group"):
    group_name = discord.ui.TextInput(
        label="Group Name",
        placeholder="Enter a name for this role group",
        required=True
    )
    role_ids = discord.ui.TextInput(
        label="Role IDs",
        placeholder="Enter role IDs separated by commas",
        required=True
    )
    description = discord.ui.TextInput(
        label="Description",
        placeholder="Describe what this group is for",
        required=False,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, cog, guild_id, panel_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Role group created!", ephemeral=True)

class ExclusiveRolesModal(discord.ui.Modal, title="Set Exclusive Roles"):
    group_id = discord.ui.TextInput(
        label="Group ID",
        placeholder="Enter the group ID to make exclusive",
        required=True
    )
    exclusive = discord.ui.TextInput(
        label="Exclusive",
        placeholder="Type 'yes' to make roles exclusive",
        required=True
    )

    def __init__(self, cog, guild_id, panel_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Exclusive roles set!", ephemeral=True)

class EditGroupModal(discord.ui.Modal, title="Edit Role Group"):
    group_id = discord.ui.TextInput(
        label="Group ID",
        placeholder="Enter the group ID to edit",
        required=True
    )
    new_name = discord.ui.TextInput(
        label="New Name",
        placeholder="Enter new group name",
        required=False
    )
    new_roles = discord.ui.TextInput(
        label="New Role IDs",
        placeholder="Enter new role IDs (comma separated)",
        required=False
    )

    def __init__(self, cog, guild_id, panel_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Group updated successfully!", ephemeral=True)


class GroupConfigView(discord.ui.View):
    def __init__(self, cog, guild_id, panel_id):
        super().__init__(timeout=300)
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id

    @discord.ui.button(label="Create Group", style=discord.ButtonStyle.green, emoji="➕", row=0)
    async def create_group(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateRoleGroupModal(self.cog, self.guild_id, self.panel_id))

    @discord.ui.button(label="Edit Group", style=discord.ButtonStyle.blurple, emoji="✏️", row=0)
    async def edit_group(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditGroupModal(self.cog, self.guild_id, self.panel_id))

    @discord.ui.button(label="Exclusive Roles", style=discord.ButtonStyle.gray, emoji="🔒", row=0)
    async def set_exclusive(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ExclusiveRolesModal(self.cog, self.guild_id, self.panel_id))

    @discord.ui.button(label="Role Requirements", style=discord.ButtonStyle.red, emoji="🔑", row=1)
    async def set_requirements(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RoleRequirementsModal(self.cog, self.guild_id, self.panel_id))

class RoleRequirementsModal(discord.ui.Modal, title="Role Requirements"):
    target_role = discord.ui.TextInput(
        label="Target Role ID",
        placeholder="Enter the role ID that needs requirements",
        required=True
    )
    required_roles = discord.ui.TextInput(
        label="Required Role IDs",
        placeholder="Enter role IDs needed to get this role (comma separated)",
        required=True
    )
    level_requirement = discord.ui.TextInput(
        label="Level Requirement (Optional)",
        placeholder="Minimum level needed (if using leveling system)",
        required=False
    )

    def __init__(self, cog, guild_id, panel_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id

    async def on_submit(self, interaction: discord.Interaction):
        target = self.target_role.value
        requirements = self.required_roles.value.split(',')
        
        if not self.cog.role_configs.get(self.guild_id, {}).get('role_requirements'):
            self.cog.role_configs[self.guild_id]['role_requirements'] = {}
            
        self.cog.role_configs[self.guild_id]['role_requirements'][target] = {
            'required_roles': requirements,
            'level_requirement': self.level_requirement.value if self.level_requirement.value else None
        }
        
        self.cog.save_configs()
        await interaction.response.send_message("Role requirements have been set!", ephemeral=True)



class SettingsView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog

    @discord.ui.button(label="Role Limits", style=discord.ButtonStyle.blurple, emoji="🔢")
    async def role_limits(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RoleLimitsModal(self.cog))

    @discord.ui.button(label="Verification Settings", style=discord.ButtonStyle.green, emoji="✅")
    async def verification(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerificationSettingsModal(self.cog))

    @discord.ui.button(label="Cooldown Settings", style=discord.ButtonStyle.gray, emoji="⏲️")
    async def cooldown(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CooldownSettingsModal(self.cog))

class ColorThemeModal(discord.ui.Modal, title="Color Theme Settings"):
    theme_choice = discord.ui.TextInput(
        label="Theme Color",
        placeholder="modern, classic, minimal, or custom",
        required=True
    )
    custom_color = discord.ui.TextInput(
        label="Custom Color (hex)",
        placeholder="#000000 (only if using custom theme)",
        required=False
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        theme = self.theme_choice.value.lower()
        await interaction.response.send_message(f"Theme updated to: {theme}", ephemeral=True)

class AnimatedButton(discord.ui.Button):
    def __init__(self, style=None, animation_type=None, **kwargs):
        super().__init__(**kwargs)
        self.style = style or discord.ButtonStyle.secondary
        self.animation_type = animation_type or "none"
        self.original_label = kwargs.get('label', '')
        self.original_style = self.style
        self.animations = {
            'pulse': self._pulse_effect,
            'fade': self._fade_effect,
            'bounce': self._bounce_effect,
            'shimmer': self._shimmer_effect,
            'rainbow': self._rainbow_effect,
            'wave': self._wave_effect,
            'blink': self._blink_effect,
            'slide': self._slide_effect,
            'glow': self._glow_effect,
            'spin': self._spin_effect
        }

    async def callback(self, interaction: discord.Interaction):
        if self.animation_type != "none":
            await interaction.response.defer()
            animation_func = self.animations.get(self.animation_type)
            if animation_func:
                await animation_func(interaction)
                self.style = self.original_style
                self.label = self.original_label
                await interaction.message.edit(view=self.view)
        
        await super().callback(interaction)
    async def _pulse_effect(self, interaction):
        styles = [ButtonStyle.primary, ButtonStyle.success, ButtonStyle.secondary]
        for style in styles:
            self.style = style
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.5)

    async def _fade_effect(self, interaction):
        labels = [self.label + "⠀", self.label + "⠈", self.label]
        for label in labels:
            self.label = label
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.3)

    async def _bounce_effect(self, interaction):
        positions = ["↑" + self.label, "↓" + self.label, self.label]
        for pos in positions:
            self.label = pos
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.2)

    async def _shimmer_effect(self, interaction):
        sparkles = ["✨", "⭐", "🌟", "💫"]
        for sparkle in sparkles:
            self.label = f"{sparkle} {self.label} {sparkle}"
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.4)

    async def _rainbow_effect(self, interaction):
        colors = [0xFF0000, 0xFFA500, 0xFFFF00, 0x00FF00, 0x0000FF, 0x4B0082, 0x9400D3]
        embed = interaction.message.embeds[0]
        for color in colors:
            embed.color = color
            await interaction.message.edit(embed=embed)
            await asyncio.sleep(0.3)

    async def _wave_effect(self, interaction):
        frames = ["⋮", "⋰", "⋯", "⋱"]
        for frame in frames:
            self.label = f"{frame} {self.label} {frame}"
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.3)

    async def _blink_effect(self, interaction):
        for _ in range(3):
            self.disabled = True
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.2)
            self.disabled = False
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.2)

    async def _slide_effect(self, interaction):
        spaces = ["⠀" * i + self.label + "⠀" * (5-i) for i in range(6)]
        for space in spaces:
            self.label = space
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.2)

    async def _glow_effect(self, interaction):
        styles = [ButtonStyle.secondary, ButtonStyle.success, ButtonStyle.primary]
        emojis = ["✨", "🌟", "💫", "⭐"]
        for style, emoji in zip(styles, emojis):
            self.style = style
            self.emoji = emoji
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.4)

    async def _spin_effect(self, interaction):
        spin_frames = ["◜", "◝", "◞", "◟"]
        for frame in spin_frames:
            self.label = f"{frame} {self.label} {frame}"
            await interaction.message.edit(view=self.view)
            await asyncio.sleep(0.2)

class ButtonStyleModal(discord.ui.Modal, title="Button Style Settings"):
    style_choice = discord.ui.TextInput(
        label="Button Style",
        placeholder="default, primary, success, or danger",
        required=True
    )
    animation_choice = discord.ui.TextInput(
        label="Animation Style",
        placeholder="pulse, grow, fade, bounce, or none",
        required=False,
        default="none"
    )
    custom_color = discord.ui.TextInput(
        label="Custom Color (optional)",
        placeholder="Enter hex color code (#RRGGBB)",
        required=False
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        style = self.style_choice.value.lower()
        animation = self.animation_choice.value.lower() if self.animation_choice.value else "none"
        
        guild_id = str(interaction.guild_id)
        if guild_id not in self.cog.role_configs:
            self.cog.role_configs[guild_id] = {}
        
        self.cog.role_configs[guild_id]["button_style"] = style
        self.cog.role_configs[guild_id]["animation"] = animation
        
        if self.custom_color.value:
            self.cog.role_configs[guild_id]["custom_color"] = self.custom_color.value
        
        self.cog.save_configs()
        
        await interaction.response.send_message(
            "Button style updated! Use the Refresh button to see your changes.", 
            ephemeral=True
        )

class LayoutModal(discord.ui.Modal, title="Layout Settings"):
    layout_type = discord.ui.TextInput(
        label="Layout Type",
        placeholder="grid, list, or compact",
        required=True
    )
    columns = discord.ui.TextInput(
        label="Number of Columns",
        placeholder="1-5 (for grid layout)",
        required=False
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        layout = self.layout_type.value.lower()
        await interaction.response.send_message(f"Layout updated to: {layout}", ephemeral=True)

class TextEditModal(discord.ui.Modal, title="Edit Text Settings"):
    title_text = discord.ui.TextInput(
        label="Panel Title",
        placeholder="Enter new panel title",
        required=False
    )
    description = discord.ui.TextInput(
        label="Panel Description",
        placeholder="Enter new description",
        style=discord.TextStyle.paragraph,
        required=False
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Text settings updated!", ephemeral=True)

class RoleLimitsModal(discord.ui.Modal, title="Role Limits"):
    max_roles = discord.ui.TextInput(
        label="Maximum Roles",
        placeholder="Enter max number of roles per user (0 for unlimited)",
        required=True
    )
    exclusive_groups = discord.ui.TextInput(
        label="Exclusive Groups",
        placeholder="Enter role groups (comma separated)",
        required=False
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Role limits updated!", ephemeral=True)

class VerificationSettingsModal(discord.ui.Modal, title="Verification Settings"):
    require_verification = discord.ui.TextInput(
        label="Require Verification",
        placeholder="yes/no",
        required=True
    )
    verification_role = discord.ui.TextInput(
        label="Required Role ID",
        placeholder="Enter role ID required for access",
        required=False
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Verification settings updated!", ephemeral=True)

class CooldownSettingsModal(discord.ui.Modal, title="Cooldown Settings"):
    cooldown_time = discord.ui.TextInput(
        label="Cooldown Duration",
        placeholder="Enter cooldown in seconds",
        required=True
    )
    bypass_roles = discord.ui.TextInput(
        label="Bypass Role IDs",
        placeholder="Enter role IDs that bypass cooldown (comma separated)",
        required=False
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Cooldown settings updated!", ephemeral=True)

class EditPanelModal(discord.ui.Modal, title="Edit Role Panel"):
    panel_id = discord.ui.TextInput(
        label="Panel ID",
        placeholder="Enter the panel ID to edit",
        required=True
    )
    
    new_title = discord.ui.TextInput(
        label="New Title",
        placeholder="Enter new panel title...",
        required=False
    )
    
    new_description = discord.ui.TextInput(
        label="New Description",
        placeholder="Enter new description...",
        required=False,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild_id)
        panel = self.cog.role_configs[guild_id].get(self.panel_id.value)
        
        if panel:
            if self.new_title.value:
                panel["title"] = self.new_title.value
            if self.new_description.value:
                panel["description"] = self.new_description.value
            
            self.cog.save_configs()
            await interaction.response.send_message("Panel updated successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("Panel not found!", ephemeral=True)

class DeletePanelModal(discord.ui.Modal, title="Delete Role Panel"):
    panel_id = discord.ui.TextInput(
        label="Panel ID",
        placeholder="Enter the panel ID to delete",
        required=True
    )
    
    confirmation = discord.ui.TextInput(
        label="Confirmation",
        placeholder="Type 'DELETE' to confirm",
        required=True
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        if self.confirmation.value != "DELETE":
            await interaction.response.send_message("Deletion cancelled.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        if self.panel_id.value in self.cog.role_configs[guild_id]:
            del self.cog.role_configs[guild_id][self.panel_id.value]
            self.cog.save_configs()
            await interaction.response.send_message("Panel deleted successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("Panel not found!", ephemeral=True)

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_configs = {}
        self.load_configs()
        self.color_options = {
            "Red": discord.Color.red(),
            "Blue": discord.Color.blue(),
            "Green": discord.Color.green(),
            "Purple": discord.Color.purple(),
            "Gold": discord.Color.gold()
        }
        self.style_options = {
            "Default": discord.ButtonStyle.secondary,
            "Primary": discord.ButtonStyle.primary,
            "Success": discord.ButtonStyle.success,
            "Danger": discord.ButtonStyle.danger
        }


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def exportrolepanel(self, ctx):
        """Export all role panel configurations to a JSON file"""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.role_configs or not self.role_configs[guild_id]:
            return await ctx.send("No role panels found to export!")
        
        config_data = self.role_configs[guild_id]
        file_content = json.dumps(config_data, indent=4)
        
        file = discord.File(
            io.StringIO(file_content),
            filename=f"role_panel_config_{ctx.guild.name}.json"
        )
        await ctx.send("Here's your role panel configuration:", file=file)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def importrolepanel(self, ctx):
        """Import role panel configurations from a JSON file"""
        if not ctx.message.attachments:
            return await ctx.send("Please attach a JSON configuration file!")
            
        attachment = ctx.message.attachments[0]
        if not attachment.filename.endswith('.json'):
            return await ctx.send("Please provide a valid JSON file!")
            
        try:
            config_data = json.loads(await attachment.read())
            guild_id = str(ctx.guild.id)
            self.role_configs[guild_id] = config_data
            self.save_configs()
            
            await ctx.send("✅ Role panel configuration imported successfully! Use the refresh button in !rolepanel to update the panels.")
        except json.JSONDecodeError:
            await ctx.send("❌ Invalid JSON file format!")

    def load_configs(self):
        try:
            with open('role_configs.json', 'r', encoding='utf-8') as f:
                self.role_configs = json.load(f)
        except FileNotFoundError:
            self.role_configs = {}

    def save_configs(self):
        with open('role_configs.json', 'w', encoding='utf-8') as f:
            json.dump(self.role_configs, f, indent=4)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rolepanel(self, ctx):
        """Open the advanced role management panel"""
        embed = discord.Embed(
            title="🎮 Ultimate Role Management Suite",
            description="Create stunning role selection menus with advanced features!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎨 Design Features",
            value="• Custom Panel Themes\n• Animated Buttons\n• Custom Emojis\n• Multiple Layouts\n• Dynamic Colors\n• Custom Icons",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Advanced Options",
            value="• Role Requirements\n• Group Roles\n• Temporary Roles\n• Role Limits\n• Role Categories\n• Role Chains",
            inline=True
        )
        
        embed.add_field(
            name="🔒 Security Features",
            value="• Permission Checks\n• Role Hierarchy\n• Anti-Abuse System\n• Rate Limiting\n• Role Conflicts",
            inline=False
        )

        await ctx.send(embed=embed, view=RoleManagerMainView(self))

class RoleManagerMainView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
        self.current_page = 0

    @discord.ui.button(label="Create Panel", style=discord.ButtonStyle.green, emoji="✨", row=0)
    async def create_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreatePanelModal(self.cog))

    @discord.ui.button(label="Manage Panels", style=discord.ButtonStyle.blurple, emoji="📋", row=0)
    async def manage_panels(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_panel_manager(interaction)

    @discord.ui.button(label="Design Studio", style=discord.ButtonStyle.gray, emoji="🎨", row=0)
    async def design_studio(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎨 Design Studio",
            description="Customize your role panel appearance",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Design Features",
            value="• Custom Panel Themes\n• Animated Buttons\n• Custom Emojis\n• Multiple Layouts\n• Dynamic Colors\n• Custom Icons",
            inline=False
        )
        embed.add_field(
            name="Available Themes",
            value="• Modern\n• Classic\n• Minimal\n• Custom",
            inline=True
        )
        embed.add_field(
            name="Layout Options",
            value="• Grid\n• List\n• Compact\n• Custom",
            inline=True
        )
        await interaction.response.send_message(embed=embed, view=DesignStudioView(self.cog), ephemeral=True)

    @discord.ui.button(label="Role Groups", style=discord.ButtonStyle.primary, emoji="📑", row=0)
    async def manage_groups(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Role Group Management",
            description="Create and manage role groups for better organization",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Advanced Options",
            value="• Role Requirements\n• Group Roles\n• Temporary Roles\n• Role Limits\n• Role Categories\n• Role Chains",
            inline=False
        )
        embed.add_field(
            name="Group Features",
            value="• Exclusive Roles\n• Role Hierarchy\n• Role Dependencies\n• Auto Roles",
            inline=True
        )
        await interaction.response.send_message(
            embed=embed,
            view=GroupConfigView(self.cog, str(interaction.guild_id), "main"),
            ephemeral=True
        )

    @discord.ui.button(label="Settings", style=discord.ButtonStyle.gray, emoji="⚙️", row=1)
    async def settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="⚙️ Settings",
            description="Configure global role panel settings",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Security Features",
            value="• Permission Checks\n• Role Hierarchy\n• Anti-Abuse System\n• Rate Limiting\n• Role Conflicts",
            inline=False
        )
        embed.add_field(
            name="Configuration Options",
            value="• Global Cooldowns\n• Verification Requirements\n• Logging Settings\n• Backup Options",
            inline=True
        )
        await interaction.response.send_message(embed=embed, view=SettingsView(self.cog), ephemeral=True)

    @discord.ui.button(label="Refresh Panels", style=discord.ButtonStyle.success, emoji="🔄", row=1)
    async def refresh_panels(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        panels = self.cog.role_configs.get(guild_id, {})
        
        for panel_id, panel_data in panels.items():
            try:
                channel_id = int(panel_data.get("channel", 0))
                channel = interaction.guild.get_channel(channel_id)
                
                if channel:
                    async for message in channel.history(limit=50):
                        if message.author == interaction.guild.me and message.embeds:
                            await message.delete()

                    embed = discord.Embed(
                        title=panel_data["title"],
                        description=panel_data["description"],
                        color=self.get_theme_color(panel_data.get("theme", "modern"))
                    )
                    await channel.send(embed=embed, view=DeployedRoleView(self.cog, guild_id, panel_id))
                    
            except (ValueError, KeyError, AttributeError):
                continue

        await interaction.followup.send("All role panels have been refreshed!", ephemeral=True)


    def get_theme_color(self, theme):
        theme_colors = {
            "modern": discord.Color.blue(),
            "classic": discord.Color.gold(),
            "minimal": discord.Color.light_grey(),
            "custom": discord.Color.purple()
        }
        return theme_colors.get(theme, discord.Color.blue())

    async def show_panel_manager(self, interaction):
        panels = self.cog.role_configs.get(str(interaction.guild_id), {})
        if not panels:
            await interaction.response.send_message("No panels exist yet! Create one first.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 Panel Manager",
            description="Manage your existing role panels",
            color=discord.Color.blue()
        )

        for panel_id, panel in panels.items():
            embed.add_field(
                name=f"Panel: {panel['title']}",
                value=f"ID: {panel_id}\nChannel: <#{panel['channel']}>\nRoles: {len(panel.get('roles', []))}\nStyle: {panel.get('style', {}).get('theme', 'Default')}",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            view=PanelManagerView(self.cog, panels),
            ephemeral=True
        )
    async def show_design_studio(self, interaction):
        embed = discord.Embed(
            title="🎨 Design Studio",
            description="Customize your role panel appearance",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Available Customizations",
            value="• Theme Selection\n• Button Styles\n• Layout Options\n• Color Schemes\n• Animation Settings\n• Custom Icons",
            inline=False
        )
        await interaction.response.send_message(embed=embed, view=DesignStudioView(self.cog), ephemeral=True)

    async def show_settings(self, interaction):
        embed = discord.Embed(
            title="⚙️ Settings",
            description="Configure global role panel settings",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Global Settings",
            value="• Permission Management\n• Rate Limits\n• Verification Requirements\n• Logging Options\n• Backup Settings",
            inline=False
        )
        await interaction.response.send_message(embed=embed, view=SettingsView(self.cog), ephemeral=True)

class CreatePanelModal(discord.ui.Modal, title="Create Role Panel"):
    title_input = discord.ui.TextInput(
        label="Panel Title",
        placeholder="Enter an attractive title for your panel...",
        max_length=256,
        required=True
    )
    
    description = discord.ui.TextInput(
        label="Panel Description", 
        placeholder="Describe what this role panel is for...",
        style=discord.TextStyle.paragraph,
        required=True
    )
    
    channel_id = discord.ui.TextInput(
        label="Channel ID",
        placeholder="Enter the channel ID for the panel",
        required=True
    )
    
    theme = discord.ui.TextInput(
        label="Theme & Style",
        placeholder="modern, classic, minimal, or custom",
        required=False,
        default="modern"
    )
    
    roles_config = discord.ui.TextInput(
        label="Initial Roles",
        placeholder="Role IDs separated by commas",
        required=False,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        
        panel_data = {
            "title": self.title_input.value,
            "description": self.description.value,
            "channel": self.channel_id.value,
            "theme": self.theme.value.lower(),
            "roles": [],
            "settings": {
                "requires_verification": False,
                "cooldown": 0,
                "max_roles": 0,
                "exclusive_groups": []
            },
            "style": {
                "color": "blue",
                "button_style": "default",
                "layout": "grid",
                "animations": True
            }
        }

        guild_id = str(interaction.guild_id)
        if guild_id not in self.cog.role_configs:
            self.cog.role_configs[guild_id] = {}
        
        panel_id = str(len(self.cog.role_configs[guild_id]) + 1)
        self.cog.role_configs[guild_id][panel_id] = panel_data
        self.cog.save_configs()

        await interaction.response.send_message(
            "Panel created! Let's configure the roles and settings:",
            view=PanelConfigView(self.cog, guild_id, panel_id),
            ephemeral=True
        )

class PanelConfigView(discord.ui.View):
    def __init__(self, cog, guild_id, panel_id):
        super().__init__(timeout=300)
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id

    @discord.ui.button(label="Add Roles", style=discord.ButtonStyle.green, emoji="➕", row=0)
    async def add_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddRoleModal(self.cog, self.guild_id, self.panel_id))

    @discord.ui.button(label="Role Groups", style=discord.ButtonStyle.blurple, emoji="📑", row=0)
    async def configure_groups(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_group_config(interaction)

    @discord.ui.button(label="Preview", style=discord.ButtonStyle.gray, emoji="👁️", row=1)
    async def preview_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        panel = self.cog.role_configs[self.guild_id][self.panel_id]
        preview_embed = discord.Embed(
            title=panel["title"],
            description=panel["description"],
            color=self.get_theme_color(panel.get("theme", "modern"))
        )
        await interaction.response.send_message(
            embed=preview_embed,
            view=PreviewRoleView(self.cog, self.guild_id, self.panel_id),
            ephemeral=True
        )

    @discord.ui.button(label="Deploy", style=discord.ButtonStyle.success, emoji="🚀", row=1)
    async def deploy_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.deploy_to_channel(interaction)

    def get_theme_color(self, theme):
        theme_colors = {
            "modern": discord.Color.blue(),
            "classic": discord.Color.gold(),
            "minimal": discord.Color.light_grey(),
            "custom": discord.Color.purple()
        }
        return theme_colors.get(theme, discord.Color.blue())
    
    async def show_group_config(self, interaction):
        panel = self.cog.role_configs[self.guild_id][self.panel_id]
        embed = discord.Embed(
            title="📑 Role Groups Configuration",
            description="Manage role groups and requirements",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=GroupConfigView(self.cog, self.guild_id, self.panel_id), ephemeral=True)

    async def deploy_to_channel(self, interaction):
        panel = self.cog.role_configs[self.guild_id][self.panel_id]
        channel = interaction.guild.get_channel(int(panel["channel"]))
        
        if not channel:
            await interaction.response.send_message("Target channel not found!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=panel["title"],
            description=panel["description"],
            color=self.get_theme_color(panel.get("theme", "modern"))
        )
        
        await channel.send(embed=embed, view=DeployedRoleView(self.cog, self.guild_id, self.panel_id))
        await interaction.response.send_message("Panel deployed successfully!", ephemeral=True)


class PanelManagerView(discord.ui.View):
    def __init__(self, cog, panels):
        super().__init__(timeout=300)
        self.cog = cog
        self.panels = panels

    @discord.ui.button(label="Edit Panel", style=discord.ButtonStyle.blurple, emoji="✏️")
    async def edit_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditPanelModal(self.cog))

    @discord.ui.button(label="Delete Panel", style=discord.ButtonStyle.red, emoji="🗑️")
    async def delete_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DeletePanelModal(self.cog))

class DeployedRoleView(discord.ui.View):
    def __init__(self, cog, guild_id, panel_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id
        self.setup_buttons()

    def get_button_style(self, style_name):
        styles = {
            "default": discord.ButtonStyle.secondary,
            "primary": discord.ButtonStyle.primary,
            "success": discord.ButtonStyle.success,
            "danger": discord.ButtonStyle.danger
        }
        return styles.get(style_name, discord.ButtonStyle.secondary)

    def setup_buttons(self):
        panel = self.cog.role_configs[self.guild_id][self.panel_id]
        for role_data in panel.get("roles", []):
            style = self.get_button_style(role_data.get("style", "default"))
            button = AnimatedButton(
                style=style,
                label=role_data["label"],
                emoji=role_data.get("emoji"),
                custom_id=f"role_{role_data['id']}",
                animation_type=role_data.get("animation_type", "none")
            )
            button.callback = self.handle_role_click
            self.add_item(button)

    async def handle_role_click(self, interaction: discord.Interaction):
        custom_id = interaction.data.get('custom_id', '')
        role_id = int(custom_id.split("_")[1])
        member = interaction.user
        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message("Role not found!", ephemeral=True)
            return

        try:
            if role in member.roles:
                await member.remove_roles(role)
                await interaction.response.send_message(f"Removed role: {role.name}", ephemeral=True)
            else:
                await member.add_roles(role)
                await interaction.response.send_message(f"Added role: {role.name}", ephemeral=True)
                
            if hasattr(interaction.message, 'edit'):
                await interaction.message.edit(view=self)
                
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to manage that role!", ephemeral=True)

class PanelManagerView(discord.ui.View):
    def __init__(self, cog, panels):
        super().__init__(timeout=300)
        self.cog = cog
        self.panels = panels

    @discord.ui.button(label="Edit Panel", style=discord.ButtonStyle.blurple, emoji="✏️")
    async def edit_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditPanelModal(self.cog))

    @discord.ui.button(label="Delete Panel", style=discord.ButtonStyle.red, emoji="🗑️")
    async def delete_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DeletePanelModal(self.cog))

class AddRoleModal(discord.ui.Modal, title="Add Role to Panel"):
    role_id = discord.ui.TextInput(
        label="Role ID",
        placeholder="Enter the role ID to add",
        required=True
    )
    
    button_label = discord.ui.TextInput(
        label="Button Label",
        placeholder="Text to show on the button",
        required=True
    )
    
    emoji = discord.ui.TextInput(
        label="Button Emoji",
        placeholder="Optional: Add an emoji",
        required=False
    )
    
    style = discord.ui.TextInput(
        label="Button Style",
        placeholder="default, primary, success, or danger",
        required=False,
        default="default"
    )

    def __init__(self, cog, guild_id, panel_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id

    async def on_submit(self, interaction: discord.Interaction):
        role_data = {
            "id": self.role_id.value,
            "label": self.button_label.value,
            "emoji": self.emoji.value if self.emoji.value else None,
            "style": self.style.value.lower()
        }
        
        self.cog.role_configs[self.guild_id][self.panel_id]["roles"].append(role_data)
        self.cog.save_configs()
        
        await interaction.response.send_message(
            f"Role added successfully with label: {self.button_label.value}",
            ephemeral=True
        )

class PreviewRoleView(discord.ui.View):
    def __init__(self, cog, guild_id, panel_id):
        super().__init__(timeout=60)
        self.cog = cog
        self.guild_id = guild_id
        self.panel_id = panel_id
        self.setup_preview_buttons()

    def setup_preview_buttons(self):
        panel = self.cog.role_configs[self.guild_id][self.panel_id]
        for role_data in panel.get("roles", []):
            style = self.get_button_style(role_data.get("style", "default"))
            button = discord.ui.Button(
                style=style,
                label=role_data["label"],
                emoji=role_data.get("emoji"),
                disabled=True  
            )
            self.add_item(button)

    def get_button_style(self, style_name):
        styles = {
            "default": discord.ButtonStyle.secondary,
            "primary": discord.ButtonStyle.primary,
            "success": discord.ButtonStyle.success,
            "danger": discord.ButtonStyle.danger
        }
        return styles.get(style_name, discord.ButtonStyle.secondary)

class UserTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_activity = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = message.author.id
        if user_id not in self.user_activity:
            self.user_activity[user_id] = {
                "messages": 0,
                "last_active": None,
                "commands_used": 0
            }

        self.user_activity[user_id]["messages"] += 1
        self.user_activity[user_id]["last_active"] = datetime.now(timezone.utc)

    @commands.command()
    async def activity(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_data = self.user_activity.get(member.id, {
            "messages": 0,
            "last_active": None,
            "commands_used": 0
        })

        embed = EmbedBuilder(
            f"📊 Activity Stats - {member.name}",
            "User activity information"
        ).set_color(discord.Color.blue())
        
        embed.add_field("Messages Sent", str(user_data["messages"]))
        embed.add_field("Commands Used", str(user_data["commands_used"]))
        
        if user_data["last_active"]:
            embed.add_field(
                "Last Active",
                user_data["last_active"].strftime("%Y-%m-%d %H:%M:%S UTC"),
                inline=False
            )
            
        embed.set_thumbnail(member.avatar.url if member.avatar else member.default_avatar.url)
        await ctx.send(embed=embed.build())

bot.add_cog(WelcomeSystem(bot))
bot.add_cog(RoleManager(bot))
bot.add_cog(UserTracker(bot))

TOKEN = os.getenv('D15C0RD_T0K3N')  # Do  NOT   hardcode your Discord Token here! 

if __name__ == "__main__":

    logging.basicConfig(                                        # Removable
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log')
        ]
    )
    @bot.event
    async def on_message(message):
        await bot.webhook_logger.log_message(message)
        await bot.process_commands(message)

    @bot.event 
    async def on_command(ctx):
        await bot.webhook_logger.log_command(ctx)

    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        logging.error("Invalid token provided")
    except Exception as e:
        logging.error(f"Error during bot startup: {e}")

# Maintained and Created by: TheZ 

