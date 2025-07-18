import discord
from discord.ext import commands
import redis
import json
import asyncio
import os
import random
import shutil
from datetime import datetime

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

BOT_NAME = os.getenv('BOT_NAME')
IS_LEADER = os.getenv('IS_LEADER', 'false').lower() == 'true'

@bot.event
async def on_ready():
    print(f'{bot.user} ({BOT_NAME}) is ready!')
    print(f'Is Leader: {IS_LEADER}')
    
    # Check FFmpeg availability
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        print(f'FFmpeg found at: {ffmpeg_path}')
    else:
        print('WARNING: FFmpeg not found in PATH!')
    
    # Check audio file
    audio_file = os.path.join(os.path.dirname(__file__), 'akatsuki_theme.mp3')
    if os.path.exists(audio_file):
        print(f'Audio file found: {audio_file}')
    else:
        print(f'WARNING: Audio file not found at {audio_file}')
    
    # Subscribe to Redis channel
    asyncio.create_task(listen_for_summons())

async def listen_for_summons():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('akatsuki-summon')
    
    while True:
        try:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                if data['action'] == 'summon':
                    await handle_summon(data['channel_id'], data.get('user_id'))
            
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in listen_for_summons: {e}")
            await asyncio.sleep(1)

async def handle_summon(channel_id, user_id=None):
    channel = bot.get_channel(int(channel_id))
    if not channel:
        return
    
    try:
        # Non-leader bots subscribe to leave signal BEFORE joining
        leave_listener_task = None
        if not IS_LEADER:
            leave_listener_task = asyncio.create_task(listen_for_leave_signal_early())
        # Délais plus naturels avec variabilité
        delays = {
            'Pain': 0.5,     # Leader rejoint en premier après le délai
            'Konan': 1.5 + random.uniform(0.3, 0.8),
            'Itachi': 2.8 + random.uniform(0.2, 0.9),
            'Kisame': 4.2 + random.uniform(0.4, 1.2),
            'Deidara': 6.1 + random.uniform(0.3, 0.7),
            'Sasori': 7.8 + random.uniform(0.5, 1.0),
            'Hidan': 9.3 + random.uniform(0.2, 0.8),
            'Kakuzu': 11.0 + random.uniform(0.4, 1.1),
            'Tobi': 12.8 + random.uniform(0.3, 0.9),
            'Zetsu': 14.5 + random.uniform(0.2, 0.6)
        }
        
        delay = delays.get(BOT_NAME, 1.0)
        print(f"{BOT_NAME} waiting {delay}s before joining...")
        await asyncio.sleep(delay)
        
        # Check if already connected
        if bot.voice_clients:
            return
        
        # Join the voice channel with retry logic
        max_retries = 3
        retry_count = 0
        vc = None
        
        while retry_count < max_retries:
            try:
                vc = await channel.connect(timeout=30.0, reconnect=True)
                print(f"{BOT_NAME} joined {channel.name}")
                break
            except Exception as e:
                retry_count += 1
                print(f"{BOT_NAME} failed to connect (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    await asyncio.sleep(2.0)
                else:
                    print(f"{BOT_NAME} giving up after {max_retries} attempts")
                    return
        
        # Wait a bit to ensure connection is stable
        await asyncio.sleep(1.0)
        
        # If this is Pain (leader), play the theme
        if IS_LEADER:
            # Wait just a bit for connection to stabilize, then play immediately
            await asyncio.sleep(3.0)
            
            if vc and vc.is_connected():
                print(f"{BOT_NAME} is ready to play the Akatsuki theme!")
                
                # Play the Akatsuki theme
                audio_file = os.path.join(os.path.dirname(__file__), 'akatsuki_theme.mp3')
                if os.path.exists(audio_file):
                    try:
                        # Create audio source with explicit executable path
                        ffmpeg_path = shutil.which('ffmpeg') or 'ffmpeg'
                        audio_source = discord.FFmpegPCMAudio(audio_file, executable=ffmpeg_path)
                        vc.play(audio_source)
                        print(f"{BOT_NAME} is playing the Akatsuki theme!")
                        
                        # Wait for the audio to finish
                        while vc.is_playing():
                            await asyncio.sleep(0.5)
                        
                        print(f"{BOT_NAME} finished playing the theme!")
                    except Exception as e:
                        print(f"ERROR playing audio: {e}")
                        print(f"FFmpeg executable: {shutil.which('ffmpeg')}")
                        print(f"Audio file exists: {os.path.exists(audio_file)}")
                        print(f"Voice client connected: {vc.is_connected()}")
                        import traceback
                        traceback.print_exc()
                        await asyncio.sleep(5)  # Simulate music duration
                else:
                    print(f"ERROR: akatsuki_theme.mp3 not found at {audio_file}!")
                    print(f"Current directory: {os.getcwd()}")
                    print(f"Directory contents: {os.listdir(os.path.dirname(__file__))}")
                    await asyncio.sleep(5)  # Simulate music duration
                
                # Wait to ensure all bots have joined AND subscribed to the leave channel
                await asyncio.sleep(5.0)
                
                # Signal others to leave with staggered timing
                leave_message = {
                    'action': 'leave',
                    'timestamp': datetime.now().isoformat()
                }
                redis_client.publish('akatsuki-leave', json.dumps(leave_message))
                print(f"{BOT_NAME} sent leave signal to all members")
                
                # Pain leaves first after a short delay
                await asyncio.sleep(1.0)
                await vc.disconnect()
                print(f"{BOT_NAME} left the voice channel")
            else:
                print(f"{BOT_NAME} connection lost, cannot play theme")
        
        else:
            # Non-leader bots: assign the voice client to global variable
            global voice_client_global
            voice_client_global = vc
            print(f"{BOT_NAME} assigned voice client for leave signal")
        
    except Exception as e:
        print(f"Error in handle_summon for {BOT_NAME}: {e}")

# Global variable for non-leader bots
voice_client_global = None

async def listen_for_leave_signal_early():
    """Start listening for leave signal before joining voice"""
    global voice_client_global
    pubsub = redis_client.pubsub()
    pubsub.subscribe('akatsuki-leave')
    print(f"{BOT_NAME} subscribed to leave channel early")
    
    try:
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                if data['action'] == 'leave':
                    # Wait for voice client to be set
                    wait_time = 0
                    while voice_client_global is None and wait_time < 10:
                        await asyncio.sleep(0.5)
                        wait_time += 0.5
                    
                    if voice_client_global and voice_client_global.is_connected():
                        # Attendre le délai spécifique avant de partir (plus naturel)
                        leave_delays = {
                            'Zetsu': 0.8 + random.uniform(0.1, 0.4),    # Part en premier après Pain
                            'Tobi': 1.5 + random.uniform(0.3, 0.7),
                            'Kakuzu': 2.3 + random.uniform(0.2, 0.6),
                            'Hidan': 3.1 + random.uniform(0.4, 0.8),
                            'Sasori': 4.0 + random.uniform(0.2, 0.5),
                            'Deidara': 4.8 + random.uniform(0.3, 0.7),
                            'Kisame': 5.7 + random.uniform(0.2, 0.6),
                            'Itachi': 6.5 + random.uniform(0.3, 0.8),
                            'Konan': 7.4 + random.uniform(0.1, 0.5)     # Part en dernier
                        }
                        delay = leave_delays.get(BOT_NAME, 1.0)
                        print(f"{BOT_NAME} waiting {delay}s before leaving...")
                        await asyncio.sleep(delay)
                        
                        await voice_client_global.disconnect()
                        print(f"{BOT_NAME} left the voice channel")
                        voice_client_global = None
                        break
            
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Error in listen_for_leave_signal_early: {e}")
    finally:
        pubsub.unsubscribe('akatsuki-leave')
        if voice_client_global and voice_client_global.is_connected():
            await voice_client_global.disconnect()

async def listen_for_leave_signal(voice_client):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('akatsuki-leave')
    
    # Délais fixes pour un départ échelonné (dans l'ordre inverse de l'arrivée)
    leave_delays = {
        'Zetsu': 1.0,    # Part en premier après Pain
        'Tobi': 2.0,
        'Kakuzu': 3.0,
        'Hidan': 4.0,
        'Sasori': 5.0,
        'Deidara': 6.0,
        'Kisame': 7.0,
        'Itachi': 8.0,
        'Konan': 9.0     # Part en dernier
    }
    
    try:
        while voice_client.is_connected():
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                if data['action'] == 'leave':
                    # Attendre le délai spécifique avant de partir
                    delay = leave_delays.get(BOT_NAME, 1.0)
                    print(f"{BOT_NAME} waiting {delay}s before leaving...")
                    await asyncio.sleep(delay)
                    
                    await voice_client.disconnect()
                    print(f"{BOT_NAME} left the voice channel")
                    break
            
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Error in listen_for_leave_signal: {e}")
    finally:
        pubsub.unsubscribe('akatsuki-leave')
        if voice_client.is_connected():
            await voice_client.disconnect()

if __name__ == '__main__':
    bot.run(os.getenv('BOT_TOKEN'))