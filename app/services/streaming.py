"""Streaming Service - SSE streaming for pep talks and match commentary."""

import asyncio
import random
from collections.abc import AsyncGenerator

from app.data import MATCHES, PEP_TALK_SEGMENTS
from app.models.interactive import (
    CommentaryEventType,
    MatchCommentaryEvent,
    PepTalkChunk,
    PepTalkResponse,
)


class StreamingService:
    """Service for streaming content via SSE."""

    MATCH_COMMENTARY_TEMPLATES = {
        CommentaryEventType.KICKOFF: [
            "And we're off! The referee blows the whistle and the match begins!",
            "Here we go! The crowd roars as the ball starts rolling!",
        ],
        CommentaryEventType.GOAL: [
            "GOOOOAL! What a strike! The net is bulging!",
            "HE'S SCORED! Absolute scenes at Nelson Road!",
            "INCREDIBLE! That's gone in! What a moment!",
        ],
        CommentaryEventType.NEAR_MISS: [
            "Ohhh, so close! That was inches away from being a goal!",
            "The keeper is beaten but the post saves them!",
            "What a chance! How did that not go in?!",
        ],
        CommentaryEventType.SAVE: [
            "Brilliant save! The goalkeeper comes up huge!",
            "What reflexes! That was destined for the top corner!",
        ],
        CommentaryEventType.FOUL: [
            "The referee blows for a foul. That looked like a tactical stop.",
            "Free kick given. Perhaps a bit harsh on the defender there.",
        ],
        CommentaryEventType.SUBSTITUTION: [
            "A change for the team. Fresh legs coming on for the final push.",
            "Tactical substitution here as the manager looks to change things up.",
        ],
        CommentaryEventType.HALFTIME: [
            "And that's halftime! Time for Ted's famous locker room talk.",
            "The whistle goes for the break. What a half of football!",
        ],
        CommentaryEventType.TED_REACTION: [
            "Ted Lasso is on his feet, applauding his players!",
            "Look at Ted on the sideline - that mustache is practically smiling!",
            "Ted turns to Coach Beard with a knowing nod. Something's brewing.",
        ],
        CommentaryEventType.CROWD_MOMENT: [
            "Listen to that! The crowd is absolutely singing their hearts out!",
            "The supporters are on their feet! This atmosphere is electric!",
            "You can hear the BELIEVE chant echoing around the stadium!",
        ],
        CommentaryEventType.FINAL_WHISTLE: [
            "And that's the final whistle! What a match we've witnessed!",
            "IT'S ALL OVER! The players embrace as the final whistle sounds!",
        ],
    }

    TED_REACTIONS = [
        "Well butter my biscuit, did you see that?!",
        "*pumps fist* That's what I'm talkin' about!",
        "*claps enthusiastically* Football IS life!",
        "*turns to Beard* We practiced that exact play!",
        "*whistles* Now that's what teamwork looks like!",
        "*does a little dance on the sideline*",
    ]

    CROWD_REACTIONS = [
        "The crowd erupts in cheers!",
        "Fans are hugging strangers in the stands!",
        "The Richmond faithful are bouncing in unison!",
        "Someone's thrown a scarf onto the pitch in celebration!",
        "The away supporters have gone quiet...",
    ]

    @classmethod
    def _get_emotional_beat(cls, segment: str, index: int, is_final: bool) -> str | None:
        """Determine the emotional beat for a pep talk segment."""
        if "tough" in segment.lower():
            return "acknowledgment"
        elif "goldfish" in segment.lower():
            return "wisdom"
        elif "believe" in segment.lower():
            return "affirmation"
        elif index == 0:
            return "greeting"
        elif is_final:
            return "encouragement"
        return None

    @classmethod
    def get_pep_talk(cls) -> PepTalkResponse:
        """Get a complete pep talk from Ted."""
        chunks = []
        for i, segment in enumerate(PEP_TALK_SEGMENTS):
            is_final = i == len(PEP_TALK_SEGMENTS) - 1
            chunk = PepTalkChunk(
                chunk_id=i,
                text=segment,
                is_final=is_final,
                emotional_beat=cls._get_emotional_beat(segment, i, is_final),
            )
            chunks.append(chunk)

        full_text = " ".join(segment for segment in PEP_TALK_SEGMENTS)
        return PepTalkResponse(text=full_text, chunks=chunks)

    @classmethod
    async def stream_pep_talk(cls) -> AsyncGenerator[PepTalkChunk, None]:
        """Stream a motivational pep talk from Ted, chunk by chunk."""
        for i, segment in enumerate(PEP_TALK_SEGMENTS):
            is_final = i == len(PEP_TALK_SEGMENTS) - 1

            chunk = PepTalkChunk(
                chunk_id=i,
                text=segment,
                is_final=is_final,
                emotional_beat=cls._get_emotional_beat(segment, i, is_final),
            )

            yield chunk

            # Variable delay based on text length (simulating speech pace)
            delay = len(segment) * 0.02  # Roughly 50 chars per second
            delay = max(0.1, min(delay, 0.5))  # Clamp between 0.1 and 0.5 seconds
            await asyncio.sleep(delay)

    @classmethod
    async def stream_match_commentary(
        cls, match_id: str
    ) -> AsyncGenerator[MatchCommentaryEvent, None]:
        """Stream live match commentary events."""
        # Get match data if it exists
        match_data = MATCHES.get(match_id)

        # Generate match events
        events = cls._generate_match_events(match_data)

        for i, event in enumerate(events):
            event["event_id"] = i
            event["is_final"] = i == len(events) - 1

            yield MatchCommentaryEvent(**event)

            # Delay between events (variable to simulate real match pacing)
            if event["event_type"] == CommentaryEventType.HALFTIME:
                await asyncio.sleep(1.0)  # Longer pause at halftime
            else:
                await asyncio.sleep(random.uniform(0.3, 0.8))

    @classmethod
    def _generate_match_events(cls, match_data: dict | None) -> list[dict]:
        """Generate a sequence of match events."""
        events = []

        # Kickoff
        events.append(
            {
                "minute": 0,
                "event_type": CommentaryEventType.KICKOFF,
                "description": "The match kicks off at Nelson Road",
                "commentary": random.choice(
                    cls.MATCH_COMMENTARY_TEMPLATES[CommentaryEventType.KICKOFF]
                ),
                "ted_sideline_reaction": None,
                "crowd_reaction": "The home fans are in full voice!",
            }
        )

        # First half events
        for minute in [12, 23, 34, 42]:
            event_type = random.choice(
                [
                    CommentaryEventType.NEAR_MISS,
                    CommentaryEventType.SAVE,
                    CommentaryEventType.FOUL,
                    CommentaryEventType.TED_REACTION,
                    CommentaryEventType.CROWD_MOMENT,
                ]
            )
            events.append(cls._create_event(minute, event_type))

        # First half goal
        events.append(
            {
                "minute": 38,
                "event_type": CommentaryEventType.GOAL,
                "description": "Richmond takes the lead! A beautiful team move!",
                "commentary": random.choice(
                    cls.MATCH_COMMENTARY_TEMPLATES[CommentaryEventType.GOAL]
                ),
                "ted_sideline_reaction": random.choice(cls.TED_REACTIONS),
                "crowd_reaction": random.choice(cls.CROWD_REACTIONS),
            }
        )

        # Halftime
        events.append(
            {
                "minute": 45,
                "event_type": CommentaryEventType.HALFTIME,
                "description": "The referee signals for halftime",
                "commentary": random.choice(
                    cls.MATCH_COMMENTARY_TEMPLATES[CommentaryEventType.HALFTIME]
                ),
                "ted_sideline_reaction": "Ted gathers the team for his famous halftime wisdom",
                "crowd_reaction": "Fans head for tea and biscuits",
            }
        )

        # Second half events
        for minute in [52, 63, 71, 78]:
            event_type = random.choice(
                [
                    CommentaryEventType.NEAR_MISS,
                    CommentaryEventType.SAVE,
                    CommentaryEventType.SUBSTITUTION,
                    CommentaryEventType.TED_REACTION,
                    CommentaryEventType.CROWD_MOMENT,
                ]
            )
            events.append(cls._create_event(minute, event_type))

        # Late drama - another goal
        events.append(
            {
                "minute": 85,
                "event_type": CommentaryEventType.GOAL,
                "description": "Equalizer! The visitors strike back!",
                "commentary": random.choice(
                    cls.MATCH_COMMENTARY_TEMPLATES[CommentaryEventType.GOAL]
                ),
                "ted_sideline_reaction": "Ted applauds - 'That's football, y'all!'",
                "crowd_reaction": "A collective groan from the home fans",
            }
        )

        # Final whistle
        events.append(
            {
                "minute": 90,
                "event_type": CommentaryEventType.FINAL_WHISTLE,
                "description": "Full time at Nelson Road",
                "commentary": random.choice(
                    cls.MATCH_COMMENTARY_TEMPLATES[CommentaryEventType.FINAL_WHISTLE]
                ),
                "ted_sideline_reaction": "Ted shakes hands with both teams, smiling warmly",
                "crowd_reaction": "The fans applaud their team despite the result",
            }
        )

        return events

    @classmethod
    def _create_event(cls, minute: int, event_type: CommentaryEventType) -> dict:
        """Create a single match event."""
        descriptions = {
            CommentaryEventType.NEAR_MISS: "A shot goes just wide of the target",
            CommentaryEventType.SAVE: "The goalkeeper makes a crucial stop",
            CommentaryEventType.FOUL: "The referee stops play for an infringement",
            CommentaryEventType.SUBSTITUTION: "A tactical change on the touchline",
            CommentaryEventType.TED_REACTION: "Ted makes his presence felt on the sideline",
            CommentaryEventType.CROWD_MOMENT: "The supporters create an incredible atmosphere",
        }

        return {
            "minute": minute,
            "event_type": event_type,
            "description": descriptions.get(event_type, "Action on the pitch"),
            "commentary": random.choice(cls.MATCH_COMMENTARY_TEMPLATES[event_type]),
            "ted_sideline_reaction": random.choice(cls.TED_REACTIONS)
            if random.random() > 0.5
            else None,
            "crowd_reaction": random.choice(cls.CROWD_REACTIONS)
            if random.random() > 0.5
            else None,
        }
