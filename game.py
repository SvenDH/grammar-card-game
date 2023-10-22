import random
from typing import Union
from dataclasses import dataclass, field

from models import *


NUM_FIELDS = 5


class CallbackManager:
    def confirm(self) -> bool:
        pass

    def choose(self, options: list) -> int:
        pass

    def order(self, options: list) -> list:
        pass


@dataclass
class CardInstance:
    card: Card
    owner: 'PlayerState'
    controller: Union['PlayerState', None] = None
    mods: list = field(default_factory=list)
    damage: int = 1
    health: int = 1
    activated: bool = True
    attacking: bool = False
    blocking: bool = False
    side: bool = False
    location: ZoneEnum = ZoneEnum.deck
    field_index: int = -1

    @property
    def name(self) -> list[TypeEnum]:
        return self.card.name  # TODO: add modified name

    @property
    def type(self) -> list[TypeEnum]:
        return self.card.type  # TODO: add modified types

    @property
    def abilities(self) -> list[AquiredAbilities]:
        return self.card.abilities  # TODO: add modifiers
    
    @property
    def activated_abilities(self) -> list[ActivatedAbility]:
        # TODO: add modifiers
        return [c for c in self.card.abilities if isinstance(c, ActivatedAbility)]
    
    @property
    def color(self) -> set[ColorEnum]:
        # TODO: add modifiers
        return self.card.color
    
    def __repr__(self) -> str:
        return str(self.card)
    
    async def activate(self, ctx: dict, index: int):
        ability = self.activated_abilities[index]
        ctx["self"] = self
        ctx["owner"] = self.owner
        ctx["controller"] = self.controller
        await ability.activate(ctx)

    def destroy(self, ctx: dict):
        assert self.field_index >= 0
        player = self.controller
        place = player.board[self.field_index]
        assert self == place
        player.board[self.field_index] = None
        player.pile.append(self)
        self.on_destroy(ctx)
    
    def on_enter(self, ctx: dict):
        self.reset()
        self.location = ZoneEnum.field
        # TODO: trigger on enter effects

    def on_exit(self, ctx: dict):
        self.reset()
        # TODO: trigger on exit effects

    def on_destroy(self, ctx: dict):
        self.on_exit(ctx)
        self.location = ZoneEnum.discard
        # TODO: trigger on destory effects
        pass

    def reset(self):
        self.damage = self.card.damage
        self.health = self.card.health
        self.mods = []
        self.activated = True
        self.attacking = False
        self.blocking = False
        self.field_index = -1

    def copy(self, new_owner: 'PlayerState'):
        return CardInstance(card=self.card, owner=new_owner)


@dataclass
class PlayerState:
    name: str
    game: 'Game'
    deck: list[CardInstance] = field(default_factory=list)
    board: list[CardInstance] = field(default_factory=list)
    pile: list[CardInstance] = field(default_factory=list)
    hand: list[CardInstance] = field(default_factory=list)
    side: list[Card] = field(default_factory=list)
    life: int = 20

    callback: CallbackManager | None = None
    subscribed: dict[str, list[CardInstance]] = field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        return self.name
    
    def print_hand(self) -> str:
        print(self.repr_stack(self.hand))
    
    def print_field(self) -> str:
        print(self.repr_stack(self.board))

    def print_pile(self) -> str:
        print(self.repr_stack(self.pile))

    @staticmethod
    def repr_stack(cards: list):
        if len(cards) == 0:
            return "No cards"
        n = 26
        line = ""
        card_text = [[s[i:i+n] for s in str(t).split("\n") for i in range(0, len(s), n)] for t in cards]
        h = max([len(t) for t in card_text])
        for i in range(h-1):
            line += "| "
            for c in card_text:
                l = c[i] if len(c) - 1 > i else ""
                line += l.ljust(n) + " | "
            line += "\n"
        line += "| "
        for c in card_text:
            if c:
                line += (c[-1] if c[-1] != "None" else "").rjust(n) + " | "
        return line

    @classmethod
    def from_cards(cls, name: str, game: 'Game', cards: list[Card], side_cards: list[Card]):
        p = cls(name=name, game=game, side=side_cards)
        p.deck=[CardInstance(owner=p, card=c) for c in cards]
        p.board = [None] * NUM_FIELDS
        return p

    def pick_free_field(self):
        fields = [i + 1 for i in range(len(self.board)) if self.board[i] is None]
        if not fields:
            return -1
        return fields[self.callback.choose("Choose field:", fields)]-1

    def draw(self, ctx: dict, n: int = 1, side: bool = False):
        # TODO: draw specific matched card
        # TODO: lose game when deck is empty
        assert side or n <= len(self.deck)
        for _ in range(n):
            if side:
                card = CardInstance(owner=self, card=random.choice(self.side), side=True)
            else:
                card = self.deck.pop()
            self.hand.append(card)
            card.location = ZoneEnum.hand
            self.on_draw(ctx)

    def search(self, ctx: dict, zones: Zone, match: Objects | None = None):
        choices = self.game.query(ctx, match, place=zones)
        index = self.callback.choose("Choose a card:", choices)
        card = choices[index]
        self.hand.append(card)
        card.location = ZoneEnum.hand
    
    def discard(self, ctx: dict, n: int = 1, match: Objects | None = None):
        for _ in range(n):
            if len(self.hand) == 0:
                return
            if match:
                choices = self.query(ctx, match, place="hand")
            else:
                choices = self.hand
            index = self.callback.choose("Discard a card:", choices)
            index = self.hand.index(choices[index])
            card = self.hand.pop(index)
            self.pile.append(card)
            card.location = ZoneEnum.discard
            self.on_discard(ctx)

    def create(self, ctx: dict, card: Card, to_index: int):
        assert to_index >= 0 and to_index < len(self.board)
        assert self.board[to_index] is None  # TODO: should this be allowed?
        inst = CardInstance(card=card, controller=self, owner=self, field_index=to_index)
        self.board[to_index] = inst
        inst.on_enter(ctx)
    
    def destroy(self, ctx: dict, card: CardInstance):
        assert card in self.board
        card.destroy(ctx)

    def play(self, ctx: dict, card: CardInstance, to_index: int):
        assert to_index >= 0 and to_index < len(self.board)
        assert self.board[to_index] is None  # TODO: should this be allowed?
        assert card in self.hand
        self.hand.remove(card)
        self.board[to_index] = card
        card.controller = self
        card.field_index = to_index
        card.on_enter(ctx)

    def copy(self, ctx: dict, card: CardInstance, to_index: int):
        assert to_index >= 0 and to_index < len(self.board)
        assert self.board[to_index] is None  # TODO: should this be allowed?
        # TODO: add 'token' and 'copy' modifier
        inst = CardInstance(card=card.card, controller=self, owner=self, field_index=to_index)
        self.board[to_index] = inst
        inst.on_enter(ctx)

    def query(self, ctx: dict, obj: Player | Objects, place: ZoneEnum | None = None):
        found = []
        if place == ZoneEnum.field or place is None:
            for card in self.board:
                if card and obj.match(ctx, card):
                    found.append(card)
        if place == ZoneEnum.hand or place is None:
            for card in self.hand:
                if obj.match(ctx, card):
                    found.append(card)
        if place == ZoneEnum.discard or place is None:
            for card in self.pile:
                if obj.match(ctx, card):
                    found.append(card)
        if place == ZoneEnum.deck or place is None:
            for card in self.deck:
                if obj.match(ctx, card):
                    found.append(card)
        return found
    
    def on_draw(self, ctx: dict):
        pass
    
    def on_discard(self, ctx: dict):
        pass

    def on_endturn(self, ctx: dict):
        pass


@dataclass
class Game:
    players: list[PlayerState] = field(default_factory=list)
    start_cards: int = 5
    turn: int = 0
    phase: PhaseEnum = PhaseEnum.activation
    queue: list[tuple[PlayerState, PlayerState| CardInstance, str, list]] = field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def add_player(self, name: str, deck: list[Card], side: list[Card] | None = None):
        player = PlayerState.from_cards(name, self, deck, side or [])
        self.players.append(player)
        return player
    
    async def start(self):
        # TODO: add muligan callbacks
        for player in self.players:
            for _ in range(self.start_cards):
                player.draw({})
        
        while True:
            # TODO: decide turn order
            player = self.players[self.turn % len(self.players)]

            await self.next_turn(player)

            self.turn += 1
        
    async def next_turn(self, player: PlayerState):
        ctx = {
            "game": self,
            "turn": self.turn,
            "current_player": player
        }
        player.draw(ctx)
        player.print_hand()

        done = False
        options = ["play", "activate", "hand", "field", "pile", "endturn"]
        while not done:
            # TODO: get possible actions
            idx = player.callback.choose("Choose action:", options)
            match options[idx]:
                case "hand":
                    player.print_hand()
                case "field":
                    player.print_field()
                case "pile":
                    player.print_pile()
                
                case "play":
                    from_index = player.callback.choose("Play from hand:", [o.name for o in player.hand])
                    positions = [i for i in range(5) if player.board[i] is None]
                    # TODO: get possible board positions
                    to_index = player.callback.choose("Place on board position:", [f"Position {i+1}" for i in positions])
                    player.play(ctx, player.hand[from_index], positions[to_index])
                
                case "activate":
                    # TODO: get payable and playable abilities
                    # TODO: include enemy abilities
                    card_options = [o.name for o in player.board if o and o.activated_abilities]
                    index = player.callback.choose("Activate ability of:", card_options)
                    card = player.board[index]
                    abilities = list(reversed(card.abilities))
                    abilities = [abilities.index(a) for a in card.activated_abilities]
                    texts = list(reversed(card.card.rule_texts))
                    abilities = [texts[a] for a in abilities]
                    index = player.callback.choose("Activate ability:", abilities)
                    await card.activate(ctx, index)
                
                case "endturn":
                    done = True
        
        # TODO: combat
        
        player.on_endturn(ctx)

    def pick(self, ctx: dict, obj: Player | Objects, place: ZoneEnum | Zone | None= None) -> list:
        n = obj.targets(ctx)
        if n > 0:
            player = ctx["controller"]
            ctx["targets"] = []
            for _ in range(n):
                found = self.query(ctx, obj, place)
                if len(found) == 0:
                    return ctx["targets"]
                i = player.callback.choose("Target one of:", found)
                ctx["targets"].append(found[i])
            return ctx["targets"]
        return self.query(ctx, obj, place)

    def query(self, ctx: dict, obj: Player | Objects, place: ZoneEnum | Zone | None = None) -> list:
        found = []
        for player in self.players:
            if obj.match(ctx, player):
                found.append(player)
            found.extend(player.query(ctx, obj, place))
        return found

    def enqueue(self, subject: PlayerEffect, effect: str, *args: Any):
        self.queue.append((subject, effect, args))
    
    def flush(self, ctx: dict):
        player = ctx["controller"]
        player.callback.confirm("Are you sure you want to do this action?")

        while len(self.queue) > 0:
            sub, eff, arg = self.queue.pop()
            ctx["subject"] = sub
            match eff:
                case "draw":
                    sub.draw(ctx, *arg)
                case "discard":
                    sub.discard(ctx, *arg)
                case "create":
                    sub.create(ctx, *arg)
                case "destroy":
                    sub.destroy(ctx, *arg)
                case "search":
                    sub.search(ctx, *arg)
                case "play":
                    sub.play(ctx, *arg)
                case "copy":
                    sub.copy(ctx, *arg)