"""Match Simulation Service - Generates live match events for WebSocket streaming."""

import asyncio
import random
import uuid
from typing import AsyncGenerator

from app.models.websocket import (
    LiveMatchEvent,
    LiveMatchEventType,
    TeamSide,
    MatchScore,
    MatchStats,
    PlayerInfo,
    MatchConfig,
)


class MatchSimulationService:
    """Service for simulating live football matches."""

    # AFC Richmond players (home team default)
    RICHMOND_PLAYERS = [
        PlayerInfo(name="Sam Obisanya", number=24, position="Forward"),
        PlayerInfo(name="Jamie Tartt", number=9, position="Forward"),
        PlayerInfo(name="Dani Rojas", number=10, position="Midfielder"),
        PlayerInfo(name="Roy Kent", number=6, position="Midfielder"),
        PlayerInfo(name="Isaac McAdoo", number=5, position="Defender"),
        PlayerInfo(name="Colin Hughes", number=7, position="Midfielder"),
        PlayerInfo(name="Richard Montlaur", number=3, position="Defender"),
        PlayerInfo(name="Jan Maas", number=4, position="Defender"),
        PlayerInfo(name="Moe Bumbercatch", number=11, position="Midfielder"),
        PlayerInfo(name="Zoreaux", number=1, position="Goalkeeper"),
    ]

    # Generic away team players
    AWAY_PLAYERS = [
        PlayerInfo(name="Marcus Sterling", number=9, position="Forward"),
        PlayerInfo(name="João Silva", number=10, position="Midfielder"),
        PlayerInfo(name="Ahmed Hassan", number=7, position="Forward"),
        PlayerInfo(name="Oliver Thompson", number=8, position="Midfielder"),
        PlayerInfo(name="David Campbell", number=4, position="Defender"),
        PlayerInfo(name="Michael Brown", number=5, position="Defender"),
        PlayerInfo(name="James Wilson", number=3, position="Defender"),
        PlayerInfo(name="Patrick O'Brien", number=6, position="Midfielder"),
        PlayerInfo(name="Thomas Mueller", number=11, position="Midfielder"),
        PlayerInfo(name="Carlos Ramirez", number=1, position="Goalkeeper"),
    ]

    TED_REACTIONS = {
        LiveMatchEventType.GOAL: [
            "Well, hot diggity dog! That's what I call putting the biscuit in the basket!",
            "*pumps both fists* NOW we're cooking with gas, y'all!",
            "That right there is what happens when you BELIEVE!",
            "*hugs Coach Beard* Did you see that?! Football IS life!",
            "Goldfish memory on the last play, but THIS one we remember forever!",
        ],
        LiveMatchEventType.YELLOW_CARD: [
            "*winces* Ooh, that's gonna leave a mark on the wallet.",
            "Well, that's what my mama would call a 'learning opportunity'.",
            "*turns to Beard* Is that bad? That seems bad.",
        ],
        LiveMatchEventType.RED_CARD: [
            "Well... that escalated quickly.",
            "*stares in disbelief* I think we're gonna need a bigger bench.",
            "Time for someone to go think about what they've done.",
        ],
        LiveMatchEventType.SAVE: [
            "WHAT A SAVE! That keeper's got hands like my Aunt Patty catching biscuits!",
            "*applauds* Now THAT is some Grade-A goalkeeping right there!",
        ],
        LiveMatchEventType.PENALTY_AWARDED: [
            "*nervously adjusts cap* This is fine. Everything is fine.",
            "Alright, everyone take a deep breath. And then one more. And maybe one more.",
        ],
        LiveMatchEventType.HALFTIME: [
            "*gathers team* Okay fellas, time for some biscuits and wisdom!",
            "Halftime! Let's go be goldfish and forget any mistakes!",
        ],
        LiveMatchEventType.MATCH_END: [
            "Win or lose, I'm proud of every single one of you!",
            "That's football, y'all! Now who wants barbecue?",
        ],
    }

    CROWD_REACTIONS = {
        LiveMatchEventType.GOAL: [
            "The crowd ERUPTS! Nelson Road is absolutely bouncing!",
            "SCENES! Fans are hugging complete strangers!",
            "Listen to that roar! You can hear it three blocks away!",
            "The BELIEVE banner is waving wildly in the stands!",
        ],
        LiveMatchEventType.YELLOW_CARD: [
            "Boos rain down from the home supporters.",
            "The crowd voices their displeasure with the referee.",
        ],
        LiveMatchEventType.RED_CARD: [
            "Absolute chaos in the stands! Half the crowd is booing, half is stunned silent.",
            "The away fans are celebrating while home supporters are furious!",
        ],
        LiveMatchEventType.SAVE: [
            "A collective gasp followed by thunderous applause!",
            "The crowd rises to their feet for that save!",
        ],
        LiveMatchEventType.PENALTY_AWARDED: [
            "The stadium holds its collective breath...",
            "You could hear a pin drop at Nelson Road right now.",
        ],
        LiveMatchEventType.MATCH_START: [
            "The Richmond faithful are in full voice as we kick off!",
        ],
        LiveMatchEventType.HALFTIME: [
            "Fans head for the tea and biscuits as we reach the break.",
        ],
        LiveMatchEventType.MATCH_END: [
            "The final whistle brings cheers (or groans) around the ground!",
            "Players applaud the fans as another match concludes at Nelson Road.",
        ],
    }

    COMMENTARY = {
        LiveMatchEventType.MATCH_START: [
            "And we're underway! The referee blows his whistle and the match begins!",
            "Here we go! 90 minutes of football ahead of us!",
        ],
        LiveMatchEventType.GOAL: [
            "GOOOOOAL! What a strike! The net is absolutely bulging!",
            "IT'S IN! Scenes of jubilation!",
            "GOAL! You won't see a better finish than that!",
            "HE'S DONE IT! What a moment!",
        ],
        LiveMatchEventType.POSSESSION_CHANGE: [
            "Possession changes hands as the ball is intercepted.",
            "Good defensive work there to win back the ball.",
            "A loose pass and the other side takes over.",
        ],
        LiveMatchEventType.FOUL: [
            "The referee blows for a foul. Perhaps a bit harsh there.",
            "Free kick given as the player is brought down.",
            "That's a clear foul. No complaints there.",
        ],
        LiveMatchEventType.YELLOW_CARD: [
            "And that's a booking! The yellow card comes out.",
            "He's been cautioned. The referee reaches for his pocket.",
        ],
        LiveMatchEventType.RED_CARD: [
            "RED CARD! He's off! What drama!",
            "That's a straight red! He's seen his last action today.",
        ],
        LiveMatchEventType.PENALTY_AWARDED: [
            "PENALTY! The referee points to the spot!",
            "It's a penalty! This could be huge!",
        ],
        LiveMatchEventType.PENALTY_SCORED: [
            "SCORED! Cool as you like from the penalty spot!",
            "No chance for the keeper! Penalty converted!",
        ],
        LiveMatchEventType.PENALTY_MISSED: [
            "SAVED! The keeper guesses right!",
            "Over the bar! He's ballooned it!",
        ],
        LiveMatchEventType.SUBSTITUTION: [
            "A change for the team. Fresh legs coming on.",
            "Tactical substitution here from the manager.",
        ],
        LiveMatchEventType.CORNER: [
            "Corner kick coming in from the right.",
            "They've won a corner. Set piece opportunity here.",
        ],
        LiveMatchEventType.FREE_KICK: [
            "Free kick in a dangerous area here.",
            "He'll fancy this free kick, just outside the box.",
        ],
        LiveMatchEventType.SHOT_ON_TARGET: [
            "Shot! But it's straight at the keeper.",
            "Good effort but the goalkeeper holds it comfortably.",
        ],
        LiveMatchEventType.SHOT_OFF_TARGET: [
            "He tries his luck but it's well wide.",
            "Shot! But that's gone into row Z.",
        ],
        LiveMatchEventType.SAVE: [
            "WHAT A SAVE! Incredible reflexes!",
            "The keeper comes up huge with a stunning stop!",
        ],
        LiveMatchEventType.OFFSIDE: [
            "The flag goes up. Offside.",
            "He was just ahead of the last defender there.",
        ],
        LiveMatchEventType.HALFTIME: [
            "And that's halftime! Time for team talks and tactical adjustments.",
            "The whistle goes for the break. Plenty to discuss in the dressing room.",
        ],
        LiveMatchEventType.SECOND_HALF_START: [
            "We're back underway for the second half!",
            "The second 45 begins. Can we see a change in fortunes?",
        ],
        LiveMatchEventType.ADDED_TIME: [
            "The board goes up. Added time to be played.",
            "Into injury time now. Every second counts!",
        ],
        LiveMatchEventType.MATCH_END: [
            "And that's full time! What a match we've witnessed!",
            "The final whistle blows! It's all over!",
        ],
        LiveMatchEventType.INJURY: [
            "The physio is on the pitch. Hopefully nothing serious.",
            "Play has stopped as we have a player down.",
        ],
    }

    def __init__(self, config: MatchConfig):
        """Initialize a match simulation with the given configuration."""
        self.config = config
        self.match_id = str(uuid.uuid4())[:8]
        self.score = MatchScore(home=0, away=0)
        self.stats = MatchStats(
            possession_home=50.0,
            possession_away=50.0,
            shots_home=0,
            shots_away=0,
            shots_on_target_home=0,
            shots_on_target_away=0,
            corners_home=0,
            corners_away=0,
            fouls_home=0,
            fouls_away=0,
            yellow_cards_home=0,
            yellow_cards_away=0,
            red_cards_home=0,
            red_cards_away=0,
        )
        self.event_id = 0
        self.home_players = self.RICHMOND_PLAYERS.copy()
        self.away_players = self.AWAY_PLAYERS.copy()

    def _get_player(self, team: TeamSide) -> PlayerInfo:
        """Get a random player from the specified team."""
        players = self.home_players if team == TeamSide.HOME else self.away_players
        return random.choice(players)

    def _get_commentary(self, event_type: LiveMatchEventType) -> str:
        """Get random commentary for an event type."""
        templates = self.COMMENTARY.get(event_type, ["Action on the pitch."])
        return random.choice(templates)

    def _get_ted_reaction(self, event_type: LiveMatchEventType) -> str | None:
        """Get Ted's reaction if applicable."""
        reactions = self.TED_REACTIONS.get(event_type)
        if reactions and random.random() > 0.3:
            return random.choice(reactions)
        return None

    def _get_crowd_reaction(self, event_type: LiveMatchEventType) -> str | None:
        """Get crowd reaction if applicable."""
        reactions = self.CROWD_REACTIONS.get(event_type)
        if reactions:
            return random.choice(reactions)
        return None

    def _update_possession(self):
        """Randomly shift possession percentages."""
        shift = random.uniform(-5, 5)
        self.stats.possession_home = max(30, min(70, self.stats.possession_home + shift))
        self.stats.possession_away = 100 - self.stats.possession_home

    def _create_event(
        self,
        event_type: LiveMatchEventType,
        minute: int,
        team: TeamSide | None = None,
        player: PlayerInfo | None = None,
        secondary_player: PlayerInfo | None = None,
        description: str | None = None,
        added_time: int | None = None,
    ) -> LiveMatchEvent:
        """Create a match event."""
        self.event_id += 1
        self._update_possession()

        if description is None:
            description = self._get_commentary(event_type)

        return LiveMatchEvent(
            event_id=self.event_id,
            event_type=event_type,
            minute=minute,
            added_time=added_time,
            team=team,
            player=player,
            secondary_player=secondary_player,
            description=description,
            score=self.score.model_copy(),
            stats=self.stats.model_copy(),
            ted_reaction=self._get_ted_reaction(event_type),
            crowd_reaction=self._get_crowd_reaction(event_type),
            commentary=self._get_commentary(event_type),
        )

    def _generate_random_event(self, minute: int) -> LiveMatchEvent | None:
        """Generate a random match event based on excitement level."""
        # Higher excitement = more events
        if random.random() > (self.config.excitement_level / 15):
            return None

        team = random.choice([TeamSide.HOME, TeamSide.AWAY])
        player = self._get_player(team)

        # Weight event types by likelihood
        event_weights = [
            (LiveMatchEventType.POSSESSION_CHANGE, 30),
            (LiveMatchEventType.FOUL, 15),
            (LiveMatchEventType.SHOT_OFF_TARGET, 12),
            (LiveMatchEventType.SHOT_ON_TARGET, 10),
            (LiveMatchEventType.CORNER, 8),
            (LiveMatchEventType.OFFSIDE, 6),
            (LiveMatchEventType.SAVE, 5),
            (LiveMatchEventType.FREE_KICK, 5),
            (LiveMatchEventType.YELLOW_CARD, 3),
            (LiveMatchEventType.GOAL, 2 + self.config.excitement_level // 3),
            (LiveMatchEventType.INJURY, 2),
            (LiveMatchEventType.PENALTY_AWARDED, 1),
            (LiveMatchEventType.RED_CARD, 0.5),
        ]

        events, weights = zip(*event_weights)
        event_type = random.choices(events, weights=weights)[0]

        # Handle event-specific logic
        if event_type == LiveMatchEventType.GOAL:
            return self._handle_goal(minute, team, player)
        elif event_type == LiveMatchEventType.YELLOW_CARD:
            return self._handle_yellow_card(minute, team, player)
        elif event_type == LiveMatchEventType.RED_CARD:
            return self._handle_red_card(minute, team, player)
        elif event_type == LiveMatchEventType.PENALTY_AWARDED:
            return self._handle_penalty(minute, team)
        elif event_type in (LiveMatchEventType.SHOT_ON_TARGET, LiveMatchEventType.SAVE):
            return self._handle_shot_on_target(minute, team, player)
        elif event_type == LiveMatchEventType.SHOT_OFF_TARGET:
            return self._handle_shot_off_target(minute, team, player)
        elif event_type == LiveMatchEventType.CORNER:
            return self._handle_corner(minute, team)
        elif event_type == LiveMatchEventType.FOUL:
            return self._handle_foul(minute, team, player)
        else:
            return self._create_event(event_type, minute, team, player)

    def _handle_goal(
        self, minute: int, team: TeamSide, scorer: PlayerInfo
    ) -> LiveMatchEvent:
        """Handle a goal being scored."""
        if team == TeamSide.HOME:
            self.score.home += 1
            self.stats.shots_home += 1
            self.stats.shots_on_target_home += 1
        else:
            self.score.away += 1
            self.stats.shots_away += 1
            self.stats.shots_on_target_away += 1

        # Sometimes add an assist
        assister = None
        if random.random() > 0.3:
            assister = self._get_player(team)
            while assister.name == scorer.name:
                assister = self._get_player(team)

        team_name = self.config.home_team if team == TeamSide.HOME else self.config.away_team
        description = f"GOAL! {scorer.name} scores for {team_name}!"
        if assister:
            description += f" Assisted by {assister.name}."

        return self._create_event(
            LiveMatchEventType.GOAL,
            minute,
            team,
            scorer,
            assister,
            description,
        )

    def _handle_yellow_card(
        self, minute: int, team: TeamSide, player: PlayerInfo
    ) -> LiveMatchEvent:
        """Handle a yellow card."""
        if team == TeamSide.HOME:
            self.stats.yellow_cards_home += 1
            self.stats.fouls_home += 1
        else:
            self.stats.yellow_cards_away += 1
            self.stats.fouls_away += 1

        return self._create_event(
            LiveMatchEventType.YELLOW_CARD,
            minute,
            team,
            player,
            description=f"Yellow card shown to {player.name} for a reckless challenge.",
        )

    def _handle_red_card(
        self, minute: int, team: TeamSide, player: PlayerInfo
    ) -> LiveMatchEvent:
        """Handle a red card."""
        if team == TeamSide.HOME:
            self.stats.red_cards_home += 1
            self.stats.fouls_home += 1
        else:
            self.stats.red_cards_away += 1
            self.stats.fouls_away += 1

        return self._create_event(
            LiveMatchEventType.RED_CARD,
            minute,
            team,
            player,
            description=f"RED CARD! {player.name} is sent off!",
        )

    def _handle_penalty(self, minute: int, team: TeamSide) -> LiveMatchEvent:
        """Handle a penalty being awarded and taken."""
        self.event_id += 1
        player = self._get_player(team)

        # First, create penalty awarded event (this will be yielded by the generator)
        # The actual penalty result is determined here
        if random.random() > 0.25:  # 75% conversion rate
            if team == TeamSide.HOME:
                self.score.home += 1
                self.stats.shots_home += 1
                self.stats.shots_on_target_home += 1
            else:
                self.score.away += 1
                self.stats.shots_away += 1
                self.stats.shots_on_target_away += 1

            team_name = self.config.home_team if team == TeamSide.HOME else self.config.away_team
            return self._create_event(
                LiveMatchEventType.PENALTY_SCORED,
                minute,
                team,
                player,
                description=f"PENALTY SCORED! {player.name} sends the keeper the wrong way!",
            )
        else:
            if team == TeamSide.HOME:
                self.stats.shots_home += 1
            else:
                self.stats.shots_away += 1

            return self._create_event(
                LiveMatchEventType.PENALTY_MISSED,
                minute,
                team,
                player,
                description=f"PENALTY MISSED! {player.name} fails to convert!",
            )

    def _handle_shot_on_target(
        self, minute: int, team: TeamSide, player: PlayerInfo
    ) -> LiveMatchEvent:
        """Handle a shot on target (saved)."""
        if team == TeamSide.HOME:
            self.stats.shots_home += 1
            self.stats.shots_on_target_home += 1
        else:
            self.stats.shots_away += 1
            self.stats.shots_on_target_away += 1

        return self._create_event(
            LiveMatchEventType.SAVE,
            minute,
            team,
            player,
            description=f"Great save! {player.name}'s shot is kept out by the goalkeeper!",
        )

    def _handle_shot_off_target(
        self, minute: int, team: TeamSide, player: PlayerInfo
    ) -> LiveMatchEvent:
        """Handle a shot off target."""
        if team == TeamSide.HOME:
            self.stats.shots_home += 1
        else:
            self.stats.shots_away += 1

        return self._create_event(
            LiveMatchEventType.SHOT_OFF_TARGET,
            minute,
            team,
            player,
            description=f"{player.name} shoots but it goes wide of the target.",
        )

    def _handle_corner(self, minute: int, team: TeamSide) -> LiveMatchEvent:
        """Handle a corner kick."""
        if team == TeamSide.HOME:
            self.stats.corners_home += 1
        else:
            self.stats.corners_away += 1

        team_name = self.config.home_team if team == TeamSide.HOME else self.config.away_team
        return self._create_event(
            LiveMatchEventType.CORNER,
            minute,
            team,
            description=f"Corner kick for {team_name}.",
        )

    def _handle_foul(
        self, minute: int, team: TeamSide, player: PlayerInfo
    ) -> LiveMatchEvent:
        """Handle a foul."""
        if team == TeamSide.HOME:
            self.stats.fouls_home += 1
        else:
            self.stats.fouls_away += 1

        return self._create_event(
            LiveMatchEventType.FOUL,
            minute,
            team,
            player,
            description=f"Foul by {player.name}. Free kick awarded.",
        )

    async def simulate_match(self) -> AsyncGenerator[LiveMatchEvent, None]:
        """Simulate a full match, yielding events as they occur."""
        base_delay = 0.5 / self.config.speed  # Base delay between events

        # Match start
        yield self._create_event(
            LiveMatchEventType.MATCH_START,
            0,
            description=f"Kick-off! {self.config.home_team} vs {self.config.away_team} is underway!",
        )
        await asyncio.sleep(base_delay)

        # First half (0-45 minutes)
        for minute in range(1, 46):
            event = self._generate_random_event(minute)
            if event:
                yield event
                await asyncio.sleep(random.uniform(base_delay * 0.5, base_delay * 1.5))

        # Halftime
        yield self._create_event(
            LiveMatchEventType.HALFTIME,
            45,
            description="The referee blows for halftime!",
        )
        await asyncio.sleep(base_delay * 3)  # Longer pause at halftime

        # Second half start
        yield self._create_event(
            LiveMatchEventType.SECOND_HALF_START,
            45,
            description="We're back underway for the second half!",
        )
        await asyncio.sleep(base_delay)

        # Second half (46-90 minutes)
        for minute in range(46, 91):
            event = self._generate_random_event(minute)
            if event:
                yield event
                await asyncio.sleep(random.uniform(base_delay * 0.5, base_delay * 1.5))

        # Added time
        added_minutes = random.randint(1, 5)
        yield self._create_event(
            LiveMatchEventType.ADDED_TIME,
            90,
            description=f"{added_minutes} minutes of added time to be played.",
        )
        await asyncio.sleep(base_delay)

        # Added time events
        for added in range(1, added_minutes + 1):
            event = self._generate_random_event(90)
            if event:
                event.added_time = added
                yield event
                await asyncio.sleep(random.uniform(base_delay * 0.5, base_delay * 1.5))

        # Final whistle
        yield self._create_event(
            LiveMatchEventType.MATCH_END,
            90,
            added_time=added_minutes,
            description=f"Full time! {self.config.home_team} {self.score.home} - {self.score.away} {self.config.away_team}",
        )
