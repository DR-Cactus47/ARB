import discord
from discord.ext import commands
from discord import app_commands, ui, File


TOKEN = ''  # ⚠️ Replace with your real token securely
GUILD_ID = 1281862287254093824
ADMIN_ROLE_ID = 1303815987405131890
WELCOME_CHANNEL_ID = 1296548729536643163
TICKET_MENU_CHANNEL_ID = 1296549858945007687
TICKET_CATEGORY_ID = 1296549797289000971
TICKET_ADMIN_ROLE_ID = 1296609988088692757
RULES_CHANNEL_ID = 1296549918260989996
AUTO_ROLE_ID = 1395279971332915405

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ============= WELCOME  FUNCTION =============
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title="ARBAB™",
        description=(
            f"درود {member.mention} به چنل ارباب خوش آمدید\n"
            f"جهت ارتباط با تیم‌های رنک به <#{TICKET_MENU_CHANNEL_ID}> مراجعه کنید.\n"
            f"قطعا <#{RULES_CHANNEL_ID}> رو مطالعه کنید"
        ),
        color=0xFFD700  # Golden
    )
    embed.set_footer(text="ARBAB FOR EVER")

    await channel.send(embed=embed)
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role:
        await member.add_roles(role)
# ============= SLASH COMMAND =============
@bot.tree.command(name="say", description="(admin only)")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def say(interaction: discord.Interaction, message: str):
    # Check if user has admin role
    if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("⛔ این کامند فقط برای ادمین ها قابل استفاده است", ephemeral=True)
        return

    # Send message anonymously through bot
    await interaction.channel.send(message)
    
@bot.tree.command(name="userinfo", description="مشاهده اطلاعات کاربر")
@app_commands.describe(user="کاربری که می‌خواهید اطلاعاتش را ببینید")
@app_commands.guilds(discord.Object(id=GUILD_ID))  # optional: limits to your server
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user  # Defaults to the command invoker

    embed = discord.Embed(
        title=f"📄 پروفایل {user.display_name}",
        color=0x00BFFF
    )
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="🆔 نام کامل", value=f"{user.name}#{user.discriminator}", inline=True)
    embed.add_field(name="🪪 آیدی", value=str(user.id), inline=True)
    embed.add_field(name="📅 ورود به سرور", value=user.joined_at.strftime("%Y/%m/%d"), inline=False)
    embed.add_field(name="🏷️ بالاترین نقش", value=user.top_role.mention, inline=True)
    embed.add_field(name="📆 ساخت اکانت", value=user.created_at.strftime("%Y/%m/%d"), inline=True)
    embed.set_footer(text="ARBAB™")

    await interaction.response.send_message(embed=embed)
    
# ============= MEMBERSHIP FORM =============
class MembershipModal(ui.Modal, title="🎯 فرم عضویت در گنگ ارباب"):
    name = ui.TextInput(label="📛 Name:", placeholder="Ic Va Ooc", max_length=100)
    sen = ui.TextInput(label="🔞 Sen (سن):", placeholder="مثال: 20", max_length=10)
    level = ui.TextInput(label="🎚 Level (لول):", placeholder="مثال: 50", max_length=10)
    time_play = ui.TextInput(label="⏱ Time Play Ruzane:", placeholder="مثال: 5", max_length=10)
    aim = ui.TextInput(label="🎯 Aim (از ۱ تا ۱۰):", placeholder="مثال: 7", max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        category = bot.get_channel(TICKET_CATEGORY_ID)
        if category is None:
            await interaction.response.send_message("❌ Ticket category not found. Contact admin.", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        ticket = await category.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=overwrites)

        embed = discord.Embed(title="📥 فرم عضویت جدید", color=0x2ecc71, description=f"ارسال شده توسط: {interaction.user.mention}")
        embed.add_field(name="📛 Name (IC / OOC)", value=self.name.value, inline=False)
        embed.add_field(name="🔞 Age", value=self.sen.value, inline=True)
        embed.add_field(name="🎚️ Level", value=self.level.value, inline=True)
        embed.add_field(name="⏰ Time Play", value=self.time_play.value, inline=True)
        embed.add_field(name="🎯 Aim", value=self.aim.value, inline=True)

        confirm = ui.Button(label="بستن تیکت", style=discord.ButtonStyle.red, custom_id="confirm_close")
        view = ui.View(timeout=None)
        view.add_item(confirm)

        await ticket.send(content="تیم ارباب درحال بررسی فرم شما هستند. لطفاً صبور باشید. ||<@&1296609988088692757>||", embed=embed, view=view)
        await interaction.response.send_message(f"تیکت عضویت شما با موفقیت ساخته شد: {ticket.mention}", ephemeral=True)

# ============= TICKET BUTTONS =============
class TicketMenuView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="🎫 عضویت", style=discord.ButtonStyle.green, custom_id="open_membership"))
        self.add_item(ui.Button(label="✉️ موارد دیگر", style=discord.ButtonStyle.red, custom_id="open_simple"))

class CloseConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ui.Button(label="بله", style=discord.ButtonStyle.green, custom_id="close_yes"))
        self.add_item(ui.Button(label="خیر", style=discord.ButtonStyle.red, custom_id="close_no"))

# ============= ON READY =============
@bot.event
async def on_ready():
    print(f"Bot is ready: {bot.user}")
    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"❌ Sync error: {e}")

    menu_channel = bot.get_channel(TICKET_MENU_CHANNEL_ID)
    if menu_channel is None:
        print("❌ Ticket menu channel not found.")
        return

    await menu_channel.purge(limit=20)

    embed = discord.Embed(title="ARBAB™", description="برای باز کردن تیکت روی دکمه‌های زیر کلیک کنید", color=0xFFD700)
    embed.set_footer(text="Made By DR_Cactus")

    await menu_channel.send(embed=embed, view=TicketMenuView())

# ============= INTERACTION HANDLER =============
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    cid = interaction.data.get('custom_id')

    if cid == "open_membership":
        await interaction.response.send_modal(MembershipModal())

    elif cid == "open_simple":
        category = bot.get_channel(TICKET_CATEGORY_ID)
        if category is None:
            await interaction.response.send_message("❌ Ticket category not found. Contact admin.", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        ticket = await category.create_text_channel(name=f"support-{interaction.user.name}", overwrites=overwrites)

        view = ui.View(timeout=None)
        view.add_item(ui.Button(label="بستن تیکت", style=discord.ButtonStyle.red, custom_id="confirm_close"))

        await ticket.send(
            content=f"درود {interaction.user.mention} تیم ارباب درحال بررسی تیکت شما هستند لطفاً صبور باشید\n||<@&{TICKET_ADMIN_ROLE_ID}>||",
            view=view
        )
        await interaction.response.send_message(f"تیکت شما ساخته شد: {ticket.mention}", ephemeral=True)

    elif cid == "confirm_close":
        await interaction.response.send_message("آیا از بستن تیکت مطمئن هستید؟", view=CloseConfirmView(), ephemeral=True)

    elif cid == "close_yes":
        await interaction.channel.delete()

    elif cid == "close_no":
        await interaction.response.send_message("بستن تیکت لغو شد.", ephemeral=True)

# ============= START BOT =============
bot.run(TOKEN)
