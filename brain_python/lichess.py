import time
import berserk

# Read API token from file
with open("lichess_token.txt", "r") as file:
    token = file.read().strip()

# Create a session and client
session = berserk.TokenSession(token)
client = berserk.Client(session=session)

# Get your username
profile = client.account.get()
username = profile['username']
print(f"Hello, {username}!")

# Get ongoing games
print("\nOngoing games:")
games = client.games.get_ongoing()

ongoing = list(games)
if not ongoing:
    print("No ongoing games.")
else:
    for game in ongoing:
        opponent = game['opponent']['username']
        status = game['status']
        print(f"Game vs {opponent} | Status: {status} | ID: {game['gameId']}")


print("Polling for ongoing games every 10 seconds (Ctrl+C to stop)...")

known_ids = set()

def check_ongoing():
    games = list(client.games.get_ongoing())
    current_ids = set(g['gameId'] for g in games)

    new_ids = current_ids - known_ids
    for game in games:
        if game['gameId'] in new_ids:
            print(f"🔥 New game vs {game['opponent']['username']} (ID: {game['gameId']})")

    return current_ids

try:
    while True:
        known_ids = check_ongoing()
        time.sleep(10)
except KeyboardInterrupt:
    print("Stopped.")
