"""Interactive endpoint models for Ted Lasso API."""

from enum import Enum

from pydantic import BaseModel, Field

# === Believe Engine Models ===


class SituationType(str, Enum):
    """Types of situations the Believe Engine can handle."""

    WORK_CHALLENGE = "work_challenge"
    PERSONAL_SETBACK = "personal_setback"
    TEAM_CONFLICT = "team_conflict"
    SELF_DOUBT = "self_doubt"
    BIG_DECISION = "big_decision"
    FAILURE = "failure"
    NEW_BEGINNING = "new_beginning"
    RELATIONSHIP = "relationship"


class BelieveRequest(BaseModel):
    """Request for the Believe Engine."""

    situation: str = Field(
        min_length=10,
        description="Describe your situation",
        json_schema_extra={
            "example": "I just got passed over for a promotion I've been working toward for two years."
        },
    )
    situation_type: SituationType = Field(
        description="Type of situation",
        json_schema_extra={"example": "work_challenge"},
    )
    context: str | None = Field(
        default=None,
        description="Additional context",
        json_schema_extra={
            "example": "I've always tried to be a team player and support my colleagues."
        },
    )
    intensity: int = Field(
        ge=1,
        le=10,
        default=5,
        description="How intense is the response needed (1=gentle, 10=full Ted)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "situation": "I just got passed over for a promotion I've been working toward for two years.",
                "situation_type": "work_challenge",
                "context": "I've always tried to be a team player and support my colleagues.",
                "intensity": 7,
            }
        }
    }


class BelieveResponse(BaseModel):
    """Response from the Believe Engine."""

    ted_response: str = Field(description="Ted's motivational response")
    relevant_quote: str = Field(description="A relevant Ted Lasso quote")
    action_suggestion: str = Field(description="Suggested action to take")
    goldfish_wisdom: str = Field(
        description="A reminder to have a goldfish memory when needed"
    )
    believe_score: int = Field(
        ge=0, le=100, description="Your current believe-o-meter score"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "ted_response": "Well shoot, partner, I know that stings like a bee that just watched Field of Dreams. But here's the thing about getting passed over - it don't mean you're not good enough, it just means your moment ain't arrived yet. And let me tell you, when it does? It's gonna be sweeter than my Aunt Mildred's pecan pie.",
                "relevant_quote": "I believe in believe.",
                "action_suggestion": "Schedule a one-on-one with your manager to understand what growth areas they'd like to see, and ask them to be your partner in getting you ready for the next opportunity.",
                "goldfish_wisdom": "Remember, a goldfish has a 10-second memory. Feel this disappointment, then let it swim on by. Tomorrow's a new tank, friend.",
                "believe_score": 78,
            }
        }
    }


# === Conflict Resolution Models ===


class ConflictType(str, Enum):
    """Types of conflicts."""

    INTERPERSONAL = "interpersonal"
    TEAM_DYNAMICS = "team_dynamics"
    LEADERSHIP = "leadership"
    EGO = "ego"
    MISCOMMUNICATION = "miscommunication"
    COMPETITION = "competition"


class ConflictRequest(BaseModel):
    """Request for conflict resolution."""

    parties_involved: list[str] = Field(
        min_length=2,
        description="Who is involved in the conflict",
        json_schema_extra={"example": ["Me", "My teammate Alex"]},
    )
    conflict_type: ConflictType = Field(
        description="Type of conflict", json_schema_extra={"example": "interpersonal"}
    )
    description: str = Field(
        min_length=20,
        description="Describe the conflict",
        json_schema_extra={
            "example": "Alex keeps taking credit for my ideas in meetings and I'm getting resentful."
        },
    )
    attempts_made: list[str] | None = Field(
        default=None,
        description="What you've already tried",
        json_schema_extra={"example": ["Mentioned it casually", "Avoided them"]},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "parties_involved": ["Me", "My teammate Alex"],
                "conflict_type": "interpersonal",
                "description": "Alex keeps taking credit for my ideas in meetings and I'm getting resentful.",
                "attempts_made": ["Mentioned it casually", "Avoided them"],
            }
        }
    }


class ConflictResolution(BaseModel):
    """Conflict resolution response."""

    diagnosis: str = Field(description="Understanding the root cause")
    ted_approach: str = Field(description="How Ted would handle this")
    diamond_dogs_advice: str = Field(
        description="Advice from the Diamond Dogs support group"
    )
    steps_to_resolution: list[str] = Field(
        description="Concrete steps to resolve the conflict"
    )
    potential_outcome: str = Field(description="What resolution could look like")
    barbecue_sauce_wisdom: str = Field(description="A folksy metaphor to remember")

    model_config = {
        "json_schema_extra": {
            "example": {
                "diagnosis": "This ain't really about credit, partner. It's about feeling seen and valued. When Alex takes credit, you feel invisible, and that's gonna build up like steam in a pressure cooker.",
                "ted_approach": "I'd bring Alex a coffee, maybe a biscuit, and say 'Hey, can we chat?' No accusations, just curiosity. Ask them how they think the project's going and what they see as everyone's contributions.",
                "diamond_dogs_advice": "Roy says: 'Tell them to their face.' Higgins says: 'Perhaps document your contributions in emails beforehand.' Coach Beard just nodded mysteriously and quoted Sun Tzu.",
                "steps_to_resolution": [
                    "Request a private, casual conversation with Alex",
                    "Share how you've been feeling using 'I' statements",
                    "Ask if they're aware this has been happening",
                    "Propose a collaboration system where you both present together",
                    "Set up a weekly sync to align on contributions",
                ],
                "potential_outcome": "Y'all might discover Alex didn't even realize they were doing it. Could turn a rival into an ally, like Roy and Jamie... eventually.",
                "barbecue_sauce_wisdom": "You know what they say - you catch more flies with honey than vinegar. But you also gotta speak up, 'cause a closed mouth don't get fed.",
            }
        }
    }


# === Reframe Models ===


class ReframeRequest(BaseModel):
    """Request to reframe a negative thought."""

    negative_thought: str = Field(
        min_length=5,
        description="The negative thought to reframe",
        json_schema_extra={"example": "I'm not good enough for this job."},
    )
    recurring: bool = Field(default=False, description="Is this a recurring thought?")

    model_config = {
        "json_schema_extra": {
            "example": {
                "negative_thought": "I'm not good enough for this job.",
                "recurring": True,
            }
        }
    }


class ReframeResponse(BaseModel):
    """Reframed perspective response."""

    original_thought: str = Field(description="The original negative thought")
    reframed_thought: str = Field(description="The thought reframed positively")
    ted_perspective: str = Field(description="Ted's take on this thought")
    dr_sharon_insight: str | None = Field(
        default=None, description="Dr. Sharon's therapeutic insight"
    )
    daily_affirmation: str = Field(description="A daily affirmation to practice")

    model_config = {
        "json_schema_extra": {
            "example": {
                "original_thought": "I'm not good enough for this job.",
                "reframed_thought": "I'm still learning and growing in this role, and that's exactly where I should be.",
                "ted_perspective": "You know what? Imposter syndrome is just your brain's way of telling you that you care. The folks who think they know everything? They're the ones you gotta worry about. You questioning yourself means you're paying attention.",
                "dr_sharon_insight": "This thought pattern often stems from comparing your internal experience to others' external presentations. Consider: what evidence do you have that contradicts this belief?",
                "daily_affirmation": "I am capable, I am learning, and I belong exactly where I am.",
            }
        }
    }


# === Press Conference Models ===


class PressConferenceRequest(BaseModel):
    """Request for press conference response."""

    question: str = Field(
        min_length=10,
        description="The press question to answer",
        json_schema_extra={
            "example": "Ted, your team just lost 5-0. How do you explain this embarrassing defeat?"
        },
    )
    hostile: bool = Field(
        default=False, description="Is this a hostile question from Trent Crimm?"
    )
    topic: str | None = Field(
        default=None,
        description="Topic category",
        json_schema_extra={"example": "match_result"},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "Ted, your team just lost 5-0. How do you explain this embarrassing defeat?",
                "hostile": True,
                "topic": "match_result",
            }
        }
    }


class PressConferenceResponse(BaseModel):
    """Ted's press conference response."""

    response: str = Field(description="Ted's press conference answer")
    deflection_humor: str | None = Field(
        default=None, description="Humorous deflection if appropriate"
    )
    actual_wisdom: str = Field(description="The actual wisdom beneath the humor")
    reporter_reaction: str = Field(description="How reporters would react")
    follow_up_dodge: str = Field(description="How Ted would dodge a follow-up")

    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "Well, I'll tell you what, that score reminded me of my high school combination lock - 5-0 - except instead of opening my locker, it opened up a whole lot of learning opportunities for us today.",
                "deflection_humor": "Speaking of combinations, did y'all know that the average person forgets their password 37 times a year? Unrelated, but I just think that's fascinating.",
                "actual_wisdom": "Every loss is a lesson. We didn't play our best today, but I saw something in those players' eyes at the final whistle - hunger. And you can't teach hunger.",
                "reporter_reaction": "Confused chuckles turn to thoughtful nods as they realize Ted has somehow made them feel better about a 5-0 loss.",
                "follow_up_dodge": "I'd love to answer that, but I promised Coach Beard I'd help him find his lucky whistle. Y'all have a good one!",
            }
        }
    }


# === Coaching Principles ===


class CoachingPrinciple(BaseModel):
    """A Ted Lasso coaching principle."""

    id: str = Field(description="Principle identifier")
    principle: str = Field(description="The coaching principle")
    explanation: str = Field(description="What this principle means")
    application: str = Field(description="How to apply this principle")
    example_from_show: str = Field(description="Example from the show")
    ted_quote: str = Field(description="Related Ted quote")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "be-curious",
                "principle": "Be curious, not judgmental",
                "explanation": "Approach people and situations with genuine curiosity rather than preconceived judgments. Everyone has a story worth understanding.",
                "application": "When someone frustrates you, ask questions before making assumptions. Seek to understand their perspective and motivations.",
                "example_from_show": "Ted uses this principle during the dart game with Rupert, explaining how people underestimated him his whole life because they judged before being curious.",
                "ted_quote": "Be curious, not judgmental. - Walt Whitman... I think.",
            }
        }
    }


# === Biscuits ===


class BiscuitType(str, Enum):
    """Types of biscuits."""

    CLASSIC = "classic"
    SHORTBREAD = "shortbread"
    CHOCOLATE_CHIP = "chocolate_chip"
    OATMEAL_RAISIN = "oatmeal_raisin"


class Biscuit(BaseModel):
    """A biscuit from Ted."""

    id: str = Field(description="Biscuit identifier")
    type: BiscuitType = Field(description="Type of biscuit")
    message: str = Field(description="Message that comes with the biscuit")
    warmth_level: int = Field(ge=1, le=10, description="How warm and fresh (1-10)")
    pairs_well_with: str = Field(description="What this biscuit pairs well with")
    ted_note: str = Field(description="A handwritten note from Ted")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "biscuit-001",
                "type": "shortbread",
                "message": "Sometimes the best thing you can do is just show up with something warm.",
                "warmth_level": 9,
                "pairs_well_with": "A hot cup of tea and an honest conversation",
                "ted_note": "Made these thinking about you. Hope your day is as sweet as these little fellas. - Ted",
            }
        }
    }


# === Streaming Models ===


class PepTalkChunk(BaseModel):
    """A chunk of a streaming pep talk."""

    chunk_id: int = Field(description="Chunk sequence number")
    text: str = Field(description="The text of this chunk")
    is_final: bool = Field(default=False, description="Is this the final chunk")
    emotional_beat: str | None = Field(
        default=None, description="The emotional purpose of this chunk"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "chunk_id": 3,
                "text": "And that's the thing about hard times - they're like a good barbecue rub. ",
                "is_final": False,
                "emotional_beat": "building_metaphor",
            }
        }
    }


class PepTalkResponse(BaseModel):
    """A complete pep talk response."""

    text: str = Field(description="The full pep talk text")
    chunks: list[PepTalkChunk] = Field(description="Individual chunks of the pep talk")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Hey there, friend. I know things feel tough right now. And that's the thing about hard times - they're like a good barbecue rub. They might sting at first, but they're what give you flavor. You got this.",
                "chunks": [
                    {
                        "chunk_id": 1,
                        "text": "Hey there, friend. ",
                        "is_final": False,
                        "emotional_beat": "connection",
                    },
                    {
                        "chunk_id": 2,
                        "text": "I know things feel tough right now. ",
                        "is_final": False,
                        "emotional_beat": "acknowledgment",
                    },
                    {
                        "chunk_id": 3,
                        "text": "And that's the thing about hard times - they're like a good barbecue rub. ",
                        "is_final": False,
                        "emotional_beat": "building_metaphor",
                    },
                    {
                        "chunk_id": 4,
                        "text": "They might sting at first, but they're what give you flavor. ",
                        "is_final": False,
                        "emotional_beat": "wisdom",
                    },
                    {
                        "chunk_id": 5,
                        "text": "You got this.",
                        "is_final": True,
                        "emotional_beat": "encouragement",
                    },
                ],
            }
        }
    }


class CommentaryEventType(str, Enum):
    """Types of match commentary events."""

    KICKOFF = "kickoff"
    GOAL = "goal"
    NEAR_MISS = "near_miss"
    SAVE = "save"
    FOUL = "foul"
    SUBSTITUTION = "substitution"
    HALFTIME = "halftime"
    TED_REACTION = "ted_reaction"
    CROWD_MOMENT = "crowd_moment"
    FINAL_WHISTLE = "final_whistle"


class MatchCommentaryEvent(BaseModel):
    """A single commentary event during a match stream."""

    event_id: int = Field(description="Event sequence number")
    minute: int = Field(ge=0, le=120, description="Match minute")
    event_type: CommentaryEventType = Field(description="Type of event")
    description: str = Field(description="What happened")
    commentary: str = Field(description="Commentator's call")
    ted_sideline_reaction: str | None = Field(
        default=None, description="Ted's reaction on the sideline"
    )
    crowd_reaction: str | None = Field(
        default=None, description="How the crowd reacted"
    )
    is_final: bool = Field(default=False, description="Is this the final event")

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": 15,
                "minute": 67,
                "event_type": "goal",
                "description": "Jamie Tartt volleys it into the top corner from the edge of the box",
                "commentary": "TARTT! OH WHAT A STRIKE! The prodigal son has returned and how! Jamie Tartt has put Richmond ahead with an absolute thunderbolt!",
                "ted_sideline_reaction": "Ted leaps into Coach Beard's arms, mustache quivering with joy",
                "crowd_reaction": "Nelson Road erupts! The faithful are on their feet, scarves twirling above their heads!",
                "is_final": False,
            }
        }
    }
