import logging
import re

import musicbrainzngs
from django.core.management.base import BaseCommand
from fuzzywuzzy import fuzz

from concerts.models import Artist

# Suppress the musicbrainzngs' INFO logs
logging.getLogger("musicbrainzngs").setLevel(logging.WARNING)

# Set up the MusicBrainz API (Replace 'AppName' with your app's name or another user agent)
musicbrainzngs.set_useragent("concertelephant.com", "0.8", "sam.oehlert@gmail.com")


class Command(BaseCommand):
    help = "Lookup artists in MusicBrainz and print the results based on their scores"

    def normalize_string(self, s):
        # Convert to lowercase
        s = s.lower()

        # Replace certain characters or words
        s = s.replace("&", "and")
        s = s.replace("+", "and")

        # Remove words like "the"
        s = re.sub(r"\bthe\b", "", s)

        # Strip leading and trailing whitespaces
        s = s.strip()

        return s

    def handle(self, *args, **options):
        # Fetch all artists who haven't been processed for MusicBrainz and don't have a MusicBrainz ID
        artists_to_lookup = Artist.objects.filter(
            processed_for_musicbrainz=False, musicbrainz_id__isnull=True
        ).order_by("-created_at")[:9]

        for artist_obj in artists_to_lookup:
            artist_name_to_search = artist_obj.name  # Get the artist name from the artist_obj

            try:
                result = musicbrainzngs.search_artists(artist=artist_name_to_search, limit=5)
                normalized_search = self.normalize_string(artist_name_to_search)
                potential_matches = []

                for mb_artist in result["artist-list"]:
                    artist_name = mb_artist.get("name", "N/A")
                    artist_id = mb_artist.get("id", "N/A")
                    artist_score = int(mb_artist.get("ext:score", 0))
                    normalized_artist_name = self.normalize_string(artist_name)
                    fuzz_score = fuzz.ratio(normalized_search, normalized_artist_name)

                    if artist_score > 95 and fuzz_score > 95:
                        potential_matches.append(
                            {
                                "artist": mb_artist,
                                "artist_id": artist_id,
                                "artist_score": artist_score,
                                "fuzz_score": fuzz_score,
                            }
                        )

                if len(potential_matches) == 1:
                    self.process_artist(artist_obj, potential_matches[0])
                elif len(potential_matches) >= 2:
                    self.stdout.write("Multiple potential matches found:")

                    for idx, match in enumerate(potential_matches):
                        mb_artist = match["artist"]
                        artist_name = mb_artist.get("name", "N/A")
                        disambiguation = mb_artist.get("disambiguation", "N/A")
                        data = mb_artist
                        self.stdout.write(f"{idx + 1}. {artist_name} - {disambiguation} - {data}")

                    self.stdout.write(f"{len(potential_matches) + 1}. None of the above")
                    choice = int(input("Please select a number corresponding to the match you want to accept: ")) - 1

                    if choice < len(potential_matches):
                        self.process_artist(artist_obj, potential_matches[choice])

                # At the end of processing (either found or not found), mark this artist as processed
                artist_obj.processed_for_musicbrainz = True
                artist_obj.save()

            except musicbrainzngs.MusicBrainzError as e:
                self.stdout.write(
                    self.style.ERROR(f'Error fetching results from MusicBrainz for "{artist_name_to_search}": {e}')
                )

    def process_artist(self, artist_obj, matched_artist_data):
        artist_obj.musicbrainz_id = matched_artist_data["artist_id"]
        artist_obj.name = matched_artist_data["artist"]["name"]
        artist_obj.save()
        self.stdout.write(
            f"Accepted Artist: {artist_obj.name} with MusicBrainz ID: {matched_artist_data['artist_id']}"
        )
