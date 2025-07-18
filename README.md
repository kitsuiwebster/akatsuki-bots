# Akatsuki Discord Bots

A set of Discord bots that summon the Akatsuki when a user stays alone in a voice channel.

## Concept

When a user stays alone for 5 minutes in a voice channel, there's a 10% chance that all Akatsuki members will join the channel. Pain plays the organization's theme music before everyone leaves the channel with staggered timing.

## Features

- **🎲 Random Encounters**: 10% chance of Akatsuki appearing after 5 minutes alone
- **🎵 Theme Music**: Pain plays the official Akatsuki theme
- **⚡ Natural Timing**: Bots join and leave with randomized, natural delays
- **🔄 Smart Detection**: Timer cancels if someone else joins the channel

## Architecture

- **Coordinator Bot**: Monitors voice channels and triggers summons
- **Akatsuki Bots**: One bot per member (Pain, Konan, Itachi, Kisame, Deidara, Sasori, Hidan, Kakuzu, Tobi, Zetsu)
- **Redis**: Communication between bots
- **Portainer**: Container management interface

## Installation

1. **Create 11 Discord bots** at https://discord.com/developers/applications
   - 1 coordinator bot
   - 10 Akatsuki bots

2. **Configure permissions** for each bot:
   - View Channels
   - Connect
   - Speak

3. **Set up environment**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your tokens and Discord server ID

4. **Add theme music**:
   Place `akatuski_theme.mp3` in the `bots/` folder

5. **Launch containers**:
   ```bash
   docker-compose up -d --build
   ```

## How It Works

### Detection Phase
1. Coordinator bot monitors all voice channel activity
2. When a user joins a voice channel alone, starts a 5-minute timer
3. If someone else joins → timer cancels (no Akatsuki)
4. If user leaves → timer cancels

### Summon Phase (10% chance)
1. After 5 minutes, checks if user is still alone
2. Rolls dice: 10% chance of summoning Akatsuki
3. If successful, sends Redis signal to all Akatsuki bots

### Appearance Phase
1. **Pain** joins first (0.5s delay) as the leader
2. Other members join with randomized delays (1.5-15s)
3. **Pain** waits 3 seconds, then plays the Akatsuki theme
4. All members stay until the music ends

### Departure Phase
1. **Pain** sends leave signal via Redis
2. Members leave in reverse order with random delays
3. **Zetsu** leaves first, **Konan** leaves last
4. Natural, staggered departure timing

## Usage

1. Invite all bots to your Discord server
2. Join a voice channel
3. Wait for others to leave
4. Stay alone for 5 minutes
5. 🎲 10% chance the Akatsuki appears!

## Commands

- **!aka** - Manually summon the Akatsuki to your current voice channel (bypass the 5-minute timer and 10% chance)

## Management

Access Portainer: http://localhost:8999

## Project Structure

```
.
├── docker-compose.yml
├── .env.example
├── coordinator/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── coordinator.py
└── bots/
    ├── Dockerfile
    ├── requirements.txt
    ├── akatsuki_bot.py
    └── akatuski_theme.mp3
```

## Configuration

- **ALONE_THRESHOLD**: 300 seconds (5 minutes)
- **AKATSUKI_SPAWN_CHANCE**: 0.1 (10% chance)
- **Join delays**: Randomized between 1.5-15 seconds
- **Leave delays**: Randomized between 0.8-7.9 seconds

## Troubleshooting

- Make sure all bots have proper voice permissions
- Check that `akatuski_theme.mp3` exists in the bots folder
- Verify Redis is running for bot communication
- Use `docker-compose logs -f` to debug issues