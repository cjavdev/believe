"""Press Conference Simulator - Channel your inner Ted Lasso."""

import random

from app.models.interactive import PressConferenceRequest, PressConferenceResponse


class PressConferenceSimulator:
    """Simulate Ted Lasso-style press conference responses."""

    DEFLECTION_HUMOR = [
        "Well, you know what they say back in Kansas... actually, I don't remember what they say, but it was probably something about being kind.",
        "That's a great question. Have you ever had a biscuit? I find most questions are easier to answer after a good biscuit.",
        "You know, I once asked my goldfish that same question. He didn't have an answer either, but he seemed happy about it.",
        "I appreciate the question, but I'm still trying to figure out why they call it 'football' when y'all mostly use your feet. In America, we barely use our feet and we call it football. Life's funny that way.",
    ]

    HOSTILE_DEFLECTIONS = [
        "Now that's what I call a spicy meatball of a question. I respect the heat!",
        "Trent Crimm, The Independent! Always keeping me on my toes. Well, my toes appreciate the exercise.",
        "You know, that question feels like it came with a bit of hot sauce on it. I respect that. I'm more of a honey mustard guy myself.",
    ]

    ACTUAL_WISDOM = [
        "The truth is, I believe that success isn't measured in wins and losses. It's measured in whether we become better people along the way.",
        "At the end of the day, it's not about the scoreboard. It's about whether we gave everything we had and treated people right while doing it.",
        "You can judge a team by their results, sure. But I prefer to judge us by how we treat each other when things get hard.",
        "I think there's something beautiful about trying your hardest, even when the outcome isn't what you wanted. That's not failure - that's courage.",
    ]

    REPORTER_REACTIONS = [
        "The room goes silent for a moment, then a few reporters actually smile despite themselves.",
        "Trent Crimm nods slowly, a hint of respect in his eyes.",
        "A few reporters exchange glances, not quite sure how to respond to genuine optimism.",
        "One journalist can be heard muttering, 'I can't tell if he's brilliant or completely mad.'",
    ]

    FOLLOW_UP_DODGES = [
        "Oh, would you look at the time! I've got biscuits in the oven. Well, metaphorically. Thank you all for coming!",
        "That's a great follow-up, and I'd love to answer it, but Coach Beard is giving me the signal that means either 'wrap it up' or 'there's a bee.' Either way, I should go.",
        "I could answer that, or I could leave you all with a sense of mystery and wonder. I'm gonna go with option B. Y'all have a great day!",
        "Follow-up questions are like second helpings at Thanksgiving - always tempting, but sometimes you gotta know when to say when. Thanks everyone!",
    ]

    @classmethod
    def respond(cls, request: PressConferenceRequest) -> PressConferenceResponse:
        """Generate a Ted-style press conference response."""
        question_lower = request.question.lower()

        # Generate main response
        response = cls._generate_response(question_lower, request.hostile)

        # Add deflection humor if appropriate
        deflection = None
        if request.hostile:
            deflection = random.choice(cls.HOSTILE_DEFLECTIONS)
        elif (
            "loss" in question_lower
            or "defeat" in question_lower
            or "fail" in question_lower
        ):
            deflection = random.choice(cls.DEFLECTION_HUMOR)

        # Get wisdom
        wisdom = random.choice(cls.ACTUAL_WISDOM)

        # Reporter reaction
        reaction = random.choice(cls.REPORTER_REACTIONS)

        # Follow-up dodge
        dodge = random.choice(cls.FOLLOW_UP_DODGES)

        return PressConferenceResponse(
            response=response,
            deflection_humor=deflection,
            actual_wisdom=wisdom,
            reporter_reaction=reaction,
            follow_up_dodge=dodge,
        )

    @classmethod
    def _generate_response(cls, question: str, hostile: bool) -> str:
        """Generate the main press conference response."""
        # Loss-related questions
        if any(word in question for word in ["loss", "lost", "defeat", "embarrass"]):
            responses = [
                "Well, I'll tell you what - we didn't get the result we wanted today. But I saw a team out there "
                "that fought hard and cared about each other. And in my book, that's never a loss.",
                "You know, losing hurts. It really does. But I always say, every setback is a setup for a comeback. "
                "These boys will learn from this, and they'll be better for it.",
                "Was it our best day? No sir, it was not. But was it our last day? Also no. "
                "We'll be back at it tomorrow, better than ever. That's what teams do.",
            ]
        # Win-related questions
        elif any(word in question for word in ["win", "victory", "success"]):
            responses = [
                "I'm real proud of the boys today. But here's the thing - I was proud of them before the match too. "
                "The result just gives everyone else a reason to see what I see every day.",
                "Winning feels good, I won't lie. But you know what feels better? Seeing this team come together "
                "and play for each other. That's the real victory.",
                "We got the W today, and that's great. But I'm more excited about how we got it - "
                "together, as a family. That's what makes it special.",
            ]
        # Criticism/doubt
        elif any(word in question for word in ["doubt", "critic", "skeptic", "wrong"]):
            responses = [
                "You know, I've never been too bothered by doubters. I was doubting myself for years before it became popular. "
                "All I can do is be curious about what I can learn and keep showing up.",
                "Critics serve an important purpose - they help you figure out what you actually believe in. "
                "And I believe in this team. That's not gonna change based on what folks say.",
                "Be curious, not judgmental. That applies to critics too. Maybe they see something I don't. "
                "I'm always willing to learn. But I'm not willing to stop believing.",
            ]
        # Default response
        else:
            responses = [
                "That's a really thoughtful question, and I appreciate you asking it. "
                "Here's what I know: we're gonna keep working hard, treating people right, and believing in each other. "
                "Everything else tends to work itself out.",
                "You know, I could give you some fancy answer full of sports cliches. "
                "But the truth is simpler: we care about each other, we work hard, and we believe. "
                "That's our whole strategy.",
                "I've learned that the best answer to most questions is just to be honest. "
                "So here's my honest answer: I don't have all the answers. But I've got a great team, "
                "and together we'll figure it out.",
            ]

        return random.choice(responses)
