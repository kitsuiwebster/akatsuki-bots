import discord
from discord.ext import commands
import redis
import json
import asyncio
import os
import sys
import random
from datetime import datetime

# Force unbuffered output
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

GUILD_ID = int(os.getenv('GUILD_ID'))
ALONE_THRESHOLD = 300  # 5 minutes in seconds
AKATSUKI_SPAWN_CHANCE = 0.1  # 10% chance
NOTIFICATION_CHANNEL_ID = 1395763162422186105  # Channel to send notifications

voice_timers = {}

@bot.event
async def on_ready():
    print(f'{bot.user} is online as Coordinator!')
    print(f'Attempting to monitor guild ID: {GUILD_ID}')
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f'Monitoring guild: {guild.name}')
        print(f'Voice channels in guild: {len(guild.voice_channels)}')
    else:
        print(f'ERROR: Could not find guild with ID {GUILD_ID}')
        print(f'Available guilds: {[g.name for g in bot.guilds]}')

@bot.command(name='aka')
async def manual_summon(ctx):
    """Manually summon the Akatsuki to the user's voice channel"""
    if not ctx.author.voice:
        await ctx.send("❌ You must be in a voice channel to summon the Akatsuki!")
        return
    
    voice_channel = ctx.author.voice.channel
    
    # Send signal to all Akatsuki bots via Redis
    message = {
        'action': 'summon',
        'channel_id': voice_channel.id,
        'user_id': ctx.author.id,
        'timestamp': datetime.now().isoformat()
    }
    
    redis_client.publish('akatsuki-summon', json.dumps(message))
    
    await ctx.send(f"🌙 **The Akatsuki has been summoned to {voice_channel.name}!**")
    print(f"Manual summon by {ctx.author.name} in {voice_channel.name}")

@bot.event
async def on_voice_state_update(member, before, after):
    print(f'Voice state update: {member.name} in guild {member.guild.name}')
    
    if member.bot:
        return
    
    guild = member.guild
    if guild.id != GUILD_ID:
        print(f'Ignoring update from guild {guild.id} (monitoring {GUILD_ID})')
        return
    
    # User joined a channel
    if after.channel and not before.channel:
        await check_voice_channel(after.channel)
    
    # User left a channel
    elif before.channel and not after.channel:
        await check_voice_channel(before.channel)
    
    # User moved channels
    elif before.channel != after.channel:
        if before.channel:
            await check_voice_channel(before.channel)
        if after.channel:
            await check_voice_channel(after.channel)

async def check_voice_channel(channel):
    non_bot_members = [m for m in channel.members if not m.bot]
    
    if len(non_bot_members) == 1:
        # Start timer for this user
        user_id = non_bot_members[0].id
        channel_id = channel.id
        
        # Cancel existing timer if any
        if channel_id in voice_timers:
            voice_timers[channel_id].cancel()
        
        # Create new timer
        timer = asyncio.create_task(trigger_akatsuki(channel_id, user_id))
        voice_timers[channel_id] = timer
    else:
        # Cancel timer if exists
        if channel.id in voice_timers:
            voice_timers[channel.id].cancel()
            del voice_timers[channel.id]

async def trigger_akatsuki(channel_id, user_id):
    try:
        print(f"Starting 5-minute timer for user {user_id} in channel {channel_id}")
        await asyncio.sleep(ALONE_THRESHOLD)
        
        channel = bot.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} no longer exists, canceling summon")
            return
        
        non_bot_members = [m for m in channel.members if not m.bot]
        
        # Double check if user is still alone after 5 minutes
        if len(non_bot_members) == 1 and non_bot_members[0].id == user_id:
            print(f"User {non_bot_members[0].name} has been alone for {ALONE_THRESHOLD} seconds!")
            
            # Roll the dice - 10% chance of summoning Akatsuki
            if random.random() < AKATSUKI_SPAWN_CHANCE:
                print(f"🎲 Dice roll SUCCESS! Summoning the Akatsuki...")
                
                # Send signal to all Akatsuki bots via Redis
                message = {
                    'action': 'summon',
                    'channel_id': channel_id,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat()
                }
                
                redis_client.publish('akatsuki-summon', json.dumps(message))
                
                # Send notification to the specified channel
                notification_channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
                if notification_channel:
                    user_name = non_bot_members[0].name
                    voice_channel_name = channel.name
                    embed = discord.Embed(
                        title="🌙 Akatsuki Summoned",
                        description=f"**{user_name}** has been alone for 5 minutes in **{voice_channel_name}**\n\n*The Akatsuki has been summoned...*",
                        color=0x8B0000,  # Dark red
                        timestamp=datetime.now()
                    )
                    embed.set_footer(text="Random encounter • 10% chance")
                    await notification_channel.send(embed=embed)
                else:
                    print(f"⚠️  Could not find notification channel {NOTIFICATION_CHANNEL_ID}")
            else:
                print(f"🎲 Dice roll FAILED. No Akatsuki this time (need {AKATSUKI_SPAWN_CHANCE*100}% chance)")
        else:
            print(f"User is no longer alone in channel {channel_id}, canceling summon")
            
    except asyncio.CancelledError:
        print(f"Timer for channel {channel_id} was cancelled - someone else joined")
    finally:
        if channel_id in voice_timers:
            del voice_timers[channel_id]

if __name__ == '__main__':
    bot.run(os.getenv('BOT_TOKEN'))