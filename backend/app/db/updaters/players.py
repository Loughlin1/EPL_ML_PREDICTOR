from ..loaders.player_ratings import generate_initials
from ..models import Player, PlayerRating
from ..queries import get_players
from ..database import SessionLocal


# print(get_players(name_contains="rare"))
# print(get_players(name_contains="Normal"))

def remove_non_rare(name: str) -> str:
    name = name.replace("non-rare", "").strip()
    name = name.replace("Non-Rare", "").strip()
    return name


def merge_and_clean_non_rare_players():
    session = SessionLocal()
    try:
        # Find all players with "non-rare" in name or initials
        players = session.query(Player).filter(
            Player.name.contains("non-rare") | Player.initials.contains("non-rare")
        ).all()
        for player in players:
            print(f"Player to fix: {player}")
            cleaned_name = remove_non_rare(player.name)
            cleaned_initials = generate_initials(cleaned_name)
            print(f"Cleaned name: {cleaned_name}")
            # Check if a player with the cleaned name already exists
            existing = session.query(Player).filter(Player.name == cleaned_name).first()
            print(f"Existing player found: {existing}")
            if existing:
                # Reassign ratings to the existing player
                ratings = session.query(PlayerRating).filter(
                    PlayerRating.player_id == player.player_id
                ).all()
                print(ratings)
                for rating in ratings:
                    rating.player_id = existing.player_id
                    print(existing.player_id)
                    session.flush()

                session.delete(player)
                session.flush()
                print(f"Merged player '{player.name}' into '{existing.name}'")
            else:
                # Update the player’s name and initials
                old_name = player.name
                player.name = cleaned_name
                player.initials = cleaned_initials
                session.flush()
                print(f"Updated player '{old_name}' to cleaned name '{cleaned_name}'")
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error occurred: {e}")
        raise
    finally:
        session.close()

