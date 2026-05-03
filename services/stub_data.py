"""
Seed fixtures.

Used by services/seeder.py to populate dev/test databases with sample
content. Edit STORY_FIXTURES to add more sample stories. Each fixture
is a plain dict whose keys map directly to Story.__init__ kwargs.

This file is dev/test data only - it is not consulted at runtime once
the database is seeded.
"""

from datetime import datetime, timedelta


# Long enough on purpose so the "expand" affordance is exercised on
# the front end.
_LONG_TEXT_1 = (
    "It started with the static. Just a faint hiss behind every phone call, "
    "every voicemail, every recording I made. At first I thought it was the "
    "old wiring in my apartment, the kind of thing you live with in a "
    "pre-war building where the lights flicker when the elevator runs. "
    "Then I noticed the static had a rhythm. It pulsed in groups of three, "
    "then four, then three again, like someone breathing on the other end "
    "of a line that nobody had picked up.\n\n"
    "I work nights, transcribing audio for a legal firm. Depositions, mostly. "
    "Hours of dry questioning that I'm supposed to turn into clean text by "
    "morning. Two weeks ago I was working through a witness interview - "
    "routine stuff, a contractor disputing a deadline - when the static "
    "rose up under his voice and almost drowned him out. I rewound. I "
    "boosted the high end. The hiss got louder, and then, very clearly, "
    "underneath it, I heard my own name.\n\n"
    "Not the witness's name. Mine. Spoken in my mother's voice. My mother "
    "has been dead for nine years.\n\n"
    "I didn't tell anyone. I finished the transcript and submitted it and "
    "tried to sleep. The next file was a phone deposition recorded last "
    "Tuesday. The static was there too. So was her voice. She was telling "
    "me to come home. She was telling me the door was unlocked. She was "
    "telling me she had been waiting a long time and that the kitchen "
    "light was on for me, like it always used to be when I worked late "
    "in high school and walked back from the bus stop in the cold.\n\n"
    "I went to my supervisor. I asked, very carefully, whether the source "
    "files might be corrupted. She pulled them up on her own machine, "
    "headphones on, and listened for a full minute before shaking her head. "
    "Clean audio, she said. No static at all. She asked if I was getting "
    "enough sleep. I said yes. I lied."
)

_LONG_TEXT_2 = (
    "The hiking trail behind my grandfather's farm had a rule: if you saw "
    "a deer that didn't run from you, you turned around and went back. "
    "He told me this when I was seven and I laughed at him because deer "
    "ran from everything. He didn't laugh back. He just nodded like he "
    "was filing my reaction away for later.\n\n"
    "I'm thirty-one now and I went up there last month to clear out the "
    "house after he died. The trail was overgrown but you could still "
    "follow it if you knew where to look. I went up alone, around four in "
    "the afternoon, just to see the ridge one more time before the lawyers "
    "and the buyers and the rest of it took over.\n\n"
    "I saw a deer at the bend by the dry creek. It was standing in the "
    "trail, broadside to me, no more than ten meters away. It looked at "
    "me the way a person looks at someone they recognize across a crowded "
    "room - not surprised, not afraid, just acknowledging. I waited for it "
    "to bolt. It didn't. It blinked once, slowly, and took a step toward "
    "me. I remembered my grandfather's rule and I turned around and I "
    "walked back down the trail without running, because running felt "
    "like the wrong thing to do.\n\n"
    "Behind me I heard hooves on the dirt. Not retreating. Following. At "
    "the same pace as my own footsteps. When I sped up, the hooves sped "
    "up. When I slowed, they slowed. I did not look back. I made it to "
    "the porch and I locked the screen door, which is a stupid thing to "
    "do because a screen door doesn't lock anything out, and I sat in my "
    "grandfather's old chair and I waited until the sun went down.\n\n"
    "When I finally turned on the porch light there was a deer standing "
    "at the edge of the yard. It was watching the house. It watched the "
    "house all night. In the morning it was gone, and there were no tracks "
    "in the soft dirt where it had stood."
)

_LONG_TEXT_3 = (
    "We found the tape in a box of my aunt's things, labeled in her "
    "handwriting: DO NOT WATCH. Naturally we watched it. It was a home "
    "video from a birthday party in 1994. My cousin's sixth birthday. "
    "Twenty-two minutes of cake and streamers and a magician with a "
    "rabbit that wouldn't come out of the hat. Nothing wrong with it. "
    "Nothing wrong at all.\n\n"
    "Except none of us were at that party. My cousin's sixth birthday "
    "was held at a bowling alley. We have photos. We have other tapes. "
    "There is no version of events in which any of us, my mother "
    "included, were ever in that living room with that magician and that "
    "rabbit. And yet there we are on the tape, all of us, laughing and "
    "clapping and singing happy birthday in voices that sound exactly "
    "like ours."
)


_NOW = datetime.utcnow()

# Each fixture maps directly to Story.__init__ kwargs. The seeder may
# also generate a placeholder image and attach it - look up the story
# by title in seeder._SEED_IMAGES.
STORY_FIXTURES = [
    {
        "title": "THE STATIC ON THE LINE",
        "body": _LONG_TEXT_1,
        "author": "anonymous",
        "section_slug": "stories",
        "created_at": _NOW - timedelta(days=2),
    },
    {
        "title": "THE DEER ON THE RIDGE",
        "body": _LONG_TEXT_2,
        "author": "m. h.",
        "section_slug": "stories",
        "created_at": _NOW - timedelta(days=5),
    },
    {
        "title": "DO NOT WATCH",
        "body": _LONG_TEXT_3,
        "author": "found tape archive",
        "section_slug": "archive",
        "created_at": _NOW - timedelta(days=11),
    },
]
