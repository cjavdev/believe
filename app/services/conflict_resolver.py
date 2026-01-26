"""Conflict Resolution Service - Diamond Dogs style."""

import random

from app.models.interactive import ConflictRequest, ConflictResolution


class ConflictResolver:
    """Resolve conflicts with Ted Lasso wisdom."""

    TED_APPROACHES = {
        "interpersonal": [
            "I'd sit down with both of 'em over some biscuits and just listen. Really listen. "
            "Most conflicts come from people feeling unheard.",
            "You know what I do? I ask questions. Be curious about why they feel the way they do. "
            "Judgment never solved anything, but curiosity? That's the Swiss Army knife of understanding.",
        ],
        "team_dynamics": [
            "This is a Diamond Dogs situation. Get everyone in a room, create a safe space, "
            "and let people speak their truth. No judgment, just support.",
            "Sometimes you gotta remember that a team is like a family - you might not always like each other, "
            "but you gotta love each other. Focus on what unites you.",
        ],
        "leadership": [
            "Leadership isn't about being right - it's about doing right. "
            "Sometimes that means admitting you don't have all the answers.",
            "The best leaders I know are the ones who lift others up, not push them down. "
            "Lead with kindness, and the respect will follow.",
        ],
        "ego": [
            "Ego is just fear wearing a fancy hat. The real strength is in vulnerability.",
            "You know what happens when ego wins? Everyone loses. Including the ego.",
        ],
        "miscommunication": [
            "Nine times out of ten, conflict comes from two people saying the same thing in different languages. "
            "Your job is to be the translator.",
            "Assume positive intent. Most people aren't trying to hurt you - they're just trying to be heard.",
        ],
        "competition": [
            "Competition can bring out the best in us, but it can also bring out the worst. "
            "The key is making sure you're competing with yourself, not against others.",
            "You know what's better than winning? Helping someone else become their best. That's the real victory.",
        ],
    }

    DIAMOND_DOGS_ADVICE = [
        "The Diamond Dogs say: Woof woof! Also, have you tried just... talking about your feelings?",
        "Diamond Dogs protocol: Listen first, advise second, support always. Roo roo roo!",
        "The pack has spoken: Every person in this conflict is going through something. Lead with empathy.",
        "Diamond Dogs wisdom: Sometimes the bravest thing you can do is admit you're scared.",
    ]

    BARBECUE_SAUCE_WISDOM = [
        "You know, this situation is like barbecue sauce - it can either make things delicious or make a real mess. "
        "The difference is how you apply it.",
        "My grandma used to say, 'Don't let the brisket burn while you're worrying about the sauce.' "
        "Focus on what matters.",
        "Conflict is like a Kansas summer - hot and uncomfortable, but it always passes. "
        "And you appreciate the cool days more after.",
        "You can't make cornbread without breaking a few eggs and getting your hands dirty. "
        "Same with working through conflict.",
    ]

    @classmethod
    def resolve(cls, request: ConflictRequest) -> ConflictResolution:
        """Generate a conflict resolution response."""
        conflict_type = request.conflict_type.value

        # Diagnosis
        diagnosis = cls._generate_diagnosis(request)

        # Ted's approach
        approaches = cls.TED_APPROACHES.get(
            conflict_type, cls.TED_APPROACHES["interpersonal"]
        )
        ted_approach = random.choice(approaches)

        # Diamond Dogs advice
        diamond_dogs_advice = random.choice(cls.DIAMOND_DOGS_ADVICE)

        # Steps to resolution
        steps = cls._generate_steps(request)

        # Potential outcome
        potential_outcome = cls._generate_outcome(request)

        # Folksy wisdom
        barbecue_sauce_wisdom = random.choice(cls.BARBECUE_SAUCE_WISDOM)

        return ConflictResolution(
            diagnosis=diagnosis,
            ted_approach=ted_approach,
            diamond_dogs_advice=diamond_dogs_advice,
            steps_to_resolution=steps,
            potential_outcome=potential_outcome,
            barbecue_sauce_wisdom=barbecue_sauce_wisdom,
        )

    @classmethod
    def _generate_diagnosis(cls, request: ConflictRequest) -> str:
        """Generate a diagnosis of the conflict's root cause."""
        party_count = len(request.parties_involved)
        conflict_type = request.conflict_type.value

        diagnoses = {
            "interpersonal": f"Sounds like there's some hurt feelings between {' and '.join(request.parties_involved)}. "
            "Usually that means someone feels disrespected or unheard.",
            "team_dynamics": f"With {party_count} people involved, this isn't about individuals - it's about the system. "
            "Something in how you all work together needs adjusting.",
            "leadership": "This is about trust. When leadership conflicts arise, it's usually because someone feels "
            "their voice doesn't matter or their expertise isn't valued.",
            "ego": "Ah, the old ego trap. Someone's protecting themselves because they're scared of being seen as weak. "
            "The irony is, that protection is what's making them weak.",
            "miscommunication": "This right here is a classic case of two people having different conversations about the same thing. "
            "Nobody's wrong, you're just speaking different languages.",
            "competition": "Healthy competition became unhealthy somewhere along the way. "
            "Probably when winning became more important than growing.",
        }

        return diagnoses.get(conflict_type, diagnoses["interpersonal"])

    @classmethod
    def _generate_steps(cls, request: ConflictRequest) -> list[str]:
        """Generate concrete steps to resolve the conflict."""
        base_steps = [
            "Take a breath and remember that everyone involved is a human being doing their best.",
            f"Reach out to {request.parties_involved[1] if len(request.parties_involved) > 1 else 'the other person'} "
            "and express genuine curiosity about their perspective.",
            "Listen - really listen - without planning your response while they're talking.",
            "Share how YOU feel using 'I' statements, not accusations.",
            "Find one thing you can both agree on, no matter how small.",
            "Make a plan together for how to move forward. Collaboration beats compromise.",
        ]

        if request.attempts_made:
            base_steps.insert(
                2,
                f"Acknowledge what you've already tried ({', '.join(request.attempts_made)}) "
                "and be honest that you want to try a different approach.",
            )

        return base_steps

    @classmethod
    def _generate_outcome(cls, request: ConflictRequest) -> str:
        """Generate a potential positive outcome."""
        outcomes = [
            f"If you approach this with curiosity and kindness, {' and '.join(request.parties_involved)} might just "
            "end up closer than before. Some of the best relationships are forged through working through hard stuff.",
            "Best case scenario? You both grow from this. You understand each other better, and you've got a template "
            "for handling future disagreements. That's called progress.",
            "Imagine a world where this conflict leads to a breakthrough. Where everyone feels heard, respected, "
            "and motivated. That world is one honest conversation away.",
        ]
        return random.choice(outcomes)
