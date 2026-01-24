"""Reframe Service - Transform negative thoughts into positive ones."""

import random

from app.data import REFRAME_TEMPLATES
from app.models.interactive import ReframeRequest, ReframeResponse


class ReframeService:
    """Reframe negative thoughts with Ted Lasso positivity."""

    DAILY_AFFIRMATIONS = [
        "I am capable of handling whatever comes my way today.",
        "My worth is not determined by my productivity or others' opinions.",
        "I choose progress over perfection.",
        "I am exactly where I need to be on my journey.",
        "Today, I will be curious, not judgmental - especially with myself.",
        "I have overcome hard things before, and I will do it again.",
        "My feelings are valid, but they don't define my reality.",
        "I am growing, learning, and becoming better every day.",
        "I deserve kindness, especially from myself.",
        "I believe in myself, even when it's hard to.",
    ]

    DR_SHARON_INSIGHTS = [
        "What evidence do you have that this thought is true? Often our minds present fears as facts.",
        "This thought seems to be protecting you from something. What might that be?",
        "Notice how this thought makes you feel in your body. Our thoughts create physical responses.",
        "You're identifying with this thought, but you are not your thoughts. You're the observer of them.",
        "Consider: would you say this to a friend? Why do we treat ourselves more harshly?",
        "The truth will set you free, but first it will piss you off. That discomfort is growth.",
    ]

    TED_PERSPECTIVES = [
        "Now hold on there, friend. That negative thought? It's just your brain trying to protect you from disappointment. "
        "But here's the thing - you can't be disappointed if you never try, but you also can't win.",
        "You know what I think? I think that thought's been hanging around so long it forgot to update itself. "
        "Time to give it a little renovation.",
        "Here's the deal - your brain is like a muscle. It's been doing negative push-ups for so long, "
        "it's real strong at that. But we can train it to do positive push-ups instead.",
        "That thought right there? It's not a fact, it's a feeling dressed up in a facts costume. "
        "And Halloween's over, my friend.",
    ]

    @classmethod
    def reframe(cls, request: ReframeRequest) -> ReframeResponse:
        """Reframe a negative thought."""
        original = request.negative_thought.lower()

        # Find matching template or use default
        reframed_thought = None
        ted_perspective = None

        for template in REFRAME_TEMPLATES:
            if template["pattern"] in original:
                reframed_thought = template["reframe"]
                ted_perspective = template["ted_perspective"]
                break

        # Default reframe if no pattern matches
        if not reframed_thought:
            reframed_thought = cls._generate_default_reframe(request.negative_thought)
            ted_perspective = random.choice(cls.TED_PERSPECTIVES)

        # Add Dr. Sharon insight for recurring thoughts
        dr_sharon_insight = None
        if request.recurring:
            dr_sharon_insight = random.choice(cls.DR_SHARON_INSIGHTS)

        # Get daily affirmation
        daily_affirmation = random.choice(cls.DAILY_AFFIRMATIONS)

        return ReframeResponse(
            original_thought=request.negative_thought,
            reframed_thought=reframed_thought,
            ted_perspective=ted_perspective,
            dr_sharon_insight=dr_sharon_insight,
            daily_affirmation=daily_affirmation,
        )

    @classmethod
    def _generate_default_reframe(cls, negative_thought: str) -> str:
        """Generate a default reframe for unmatched patterns."""
        reframes = [
            "This is a challenging moment, not a permanent state. I am resilient and capable of growth.",
            "I acknowledge this feeling without letting it define me. I choose to focus on what I can control.",
            "This thought is just one perspective. I can choose to see this differently.",
            "I am learning from this experience. Every challenge contains an opportunity for growth.",
        ]
        return random.choice(reframes)
