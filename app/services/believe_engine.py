"""Believe Engine - Ted Lasso's motivational response generator."""

import random
from typing import Optional

from app.data import BELIEVE_RESPONSES, QUOTES
from app.models.interactive import BelieveRequest, BelieveResponse


class BelieveEngine:
    """Generate Ted Lasso-style motivational responses."""

    GOLDFISH_WISDOM = [
        "Remember: be a goldfish. 10-second memory for the bad stuff, eternal memory for the good.",
        "You know what a goldfish never does? Dwell. Be a goldfish.",
        "Goldfish don't worry about yesterday's problems. Neither should you.",
        "The happiest animal on Earth has a 10-second memory. There's a lesson there.",
    ]

    ACTION_SUGGESTIONS = {
        "work_challenge": [
            "Take one small step today. Just one. That's all you need to do.",
            "Talk to someone you trust about it. Diamond Dogs style.",
            "Write down three things that could go right instead of wrong.",
        ],
        "personal_setback": [
            "Do something kind for yourself today - you've earned it.",
            "Call someone who makes you laugh. Laughter is underrated medicine.",
            "Take a walk. Sometimes the best thinking happens when you're moving.",
        ],
        "team_conflict": [
            "Invite the other person for coffee. Neutral ground works wonders.",
            "Ask one genuine question about their perspective before sharing yours.",
            "Write down what you both actually want - you might find it's the same thing.",
        ],
        "self_doubt": [
            "Make a list of three things you've done well this week. No matter how small.",
            "Tell someone you trust how you're feeling. Vulnerability is strength.",
            "Do one thing that scares you a little - confidence comes from action.",
        ],
        "failure": [
            "Write down what you learned. Every failure is a lesson in disguise.",
            "Reach out to someone who's failed their way to success. You'd be surprised how many there are.",
            "Give yourself permission to try again tomorrow. Fresh starts are free.",
        ],
        "big_decision": [
            "List the pros and cons, then throw the list away and trust your gut.",
            "Talk to someone who's made a similar decision. Learn from their journey.",
            "Sleep on it, but set a deadline. Decisions need breathing room, not forever.",
        ],
        "new_beginning": [
            "Embrace the discomfort - it means you're growing.",
            "Connect with one new person in your new situation today.",
            "Create a small ritual that feels like home, wherever you are.",
        ],
        "relationship": [
            "Say what you mean and mean what you say - clearly and kindly.",
            "Remember why you care about this person in the first place.",
            "Listen twice as much as you speak. Revolutionary, I know.",
        ],
    }

    @classmethod
    def generate_response(cls, request: BelieveRequest) -> BelieveResponse:
        """Generate a motivational response based on the situation."""
        situation_type = request.situation_type.value

        # Get appropriate Ted response
        responses = BELIEVE_RESPONSES.get(situation_type, BELIEVE_RESPONSES["self_doubt"])
        ted_response = random.choice(responses)

        # Adjust based on intensity
        if request.intensity >= 8:
            ted_response = f"Now you listen here, friend. {ted_response} And that's the truth!"
        elif request.intensity <= 3:
            ted_response = f"Hey, I hear you. {ted_response}"

        # Get a relevant quote
        relevant_quotes = [
            q for q in QUOTES.values() if q["is_inspirational"] and q["character_id"] == "ted-lasso"
        ]
        relevant_quote = random.choice(relevant_quotes)["text"]

        # Get action suggestion
        actions = cls.ACTION_SUGGESTIONS.get(situation_type, cls.ACTION_SUGGESTIONS["self_doubt"])
        action_suggestion = random.choice(actions)

        # Get goldfish wisdom
        goldfish_wisdom = random.choice(cls.GOLDFISH_WISDOM)

        # Calculate believe score based on intensity and situation
        base_score = 70
        if request.context:
            base_score += 10  # Extra points for providing context
        believe_score = min(100, base_score + request.intensity * 2)

        return BelieveResponse(
            ted_response=ted_response,
            relevant_quote=relevant_quote,
            action_suggestion=action_suggestion,
            goldfish_wisdom=goldfish_wisdom,
            believe_score=believe_score,
        )
