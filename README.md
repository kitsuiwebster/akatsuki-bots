# Akatsuki Discord Bots

Un ensemble de bots Discord qui invoquent l'Akatsuki quand un utilisateur reste seul dans un canal vocal.

## Concept

Lorsqu'un utilisateur reste seul plus de 3 secondes dans un canal vocal, tous les membres de l'Akatsuki rejoignent le canal. Pain joue alors le thème musical de l'organisation avant que tous ne quittent le canal.

## Architecture

- **Bot Coordinateur** : Surveille les canaux vocaux et déclenche l'invocation
- **Bots Akatsuki** : Un bot par membre (Pain, Konan, Itachi, Kisame, Deidara, Sasori, Hidan, Kakuzu, Tobi, Zetsu)
- **Redis** : Communication entre les bots
- **Portainer** : Interface de gestion des conteneurs

## Installation

1. **Créer 11 bots Discord** sur https://discord.com/developers/applications
   - 1 bot coordinateur
   - 10 bots Akatsuki

2. **Configurer les permissions** pour chaque bot :
   - View Channels
   - Connect
   - Speak

3. **Configurer l'environnement** :
   ```bash
   cp .env.example .env
   ```
   Éditer `.env` avec vos tokens et l'ID du serveur Discord

4. **Ajouter le thème musical** :
   Placer `akatsuki_theme.mp3` dans le dossier `bots/`

5. **Lancer les conteneurs** :
   ```bash
   docker-compose up -d
   ```

## Utilisation

1. Inviter tous les bots sur votre serveur Discord
2. Rejoindre un canal vocal
3. Attendre que tous les autres quittent
4. Après 3 secondes, l'Akatsuki apparaît !

## Gestion

Accéder à Portainer : http://localhost:9000

## Structure

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
    └── akatsuki_theme.mp3
```