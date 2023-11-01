import random
from typing import Union
from dataclasses import dataclass, field

from models import *


NUM_FIELDS = 5


class CallbackManager:
    async def confirm(self, msg: str) -> bool:
        pass

    async def choose(self, msg: str, options: list) -> int:
        pass

    async def order(self, msg: str, options: list) -> list:
        pass

    async def show(self, msg: str, items: list) -> None:
        pass



class DefaultCallbackManager:
    async def confirm(self, msg: str) -> bool:
        return True

    async def choose(self, msg: str, options: list) -> int:
        if len(options):
            if "pass" in options:
                return options.index("pass")
            return 0
        return -1

    async def order(self, msg: str, options: list) -> list:
        return options

    async def show(self, msg: str, items: list) -> None:
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
        ctx["ability"] = ability
        await ability.activate(ctx)

    def reset(self):
        self.damage = self.card.damage
        self.health = self.card.health
        self.mods = []
        self.activated = True
        self.attacking = False
        self.blocking = False
        self.field_index = -1

    def can_cast(self, ctx: dict):
        return True
    
    def can_activate(self, ctx: dict):
        for ability in self.activated_abilities:
            if ability.can_activate(ctx):
                return True
        return False



@dataclass
class PlayedAbility:
    source: CardInstance
    ability: AquiredAbilities | None = None
    effects: list[tuple['PlayerState', str, list]] = field(default_factory=list)

    async def resolve(self, ctx: dict):
        for sub, eff, arg in self.effects:
            ctx["subject"] = sub
            match eff:
                case "draw":
                    await sub.draw(ctx, *arg)
                case "discard":
                    await sub.discard(ctx, *arg)
                case "create":
                    await sub.create(ctx, *arg)
                case "destroy":
                    await sub.destroy(ctx, *arg)
                case "search":
                    await sub.search(ctx, *arg)
                case "play":
                    await sub.play(ctx, *arg)
                case "copy":
                    await sub.copy(ctx, *arg)
                case "shuffle":
                    await sub.shuffle(ctx, *arg)
                case "counter":
                    await sub.counter(ctx, *arg)
                case "extraturn":
                    await sub.extraturn(ctx, *arg)
                case "look":
                    await sub.look(ctx, *arg)
                case "put":
                    await sub.put(ctx, *arg)


@dataclass
class PlayerState:
    name: str
    game: 'Game'
    deck: list[CardInstance] = field(default_factory=list)
    board: list[CardInstance | None] = field(default_factory=list)
    pile: list[CardInstance] = field(default_factory=list)
    hand: list[CardInstance] = field(default_factory=list)
    side: list[Card] = field(default_factory=list)
    life: int = 20
    turnsafterthis: int = 0

    callback: CallbackManager = DefaultCallbackManager()
    actions: list[str] = ["play", "activate", "hand", "field", "pile", "pass"]
    subscribed: dict[str, list[CardInstance]] = field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        return self.name

    @classmethod
    def from_cards(cls, name: str, game: 'Game', cards: list[Card], side_cards: list[Card]):
        p = cls(name=name, game=game, side=side_cards)
        p.deck=[CardInstance(owner=p, card=c) for c in cards]
        p.board = [None] * NUM_FIELDS
        return p
    
    def can_cast(self, ctx: dict):
        # TODO: get castable cards not in hand
        for card in self.hand:
            if card.can_cast(ctx):
                return True
        return False
    
    def can_activate(self, ctx: dict):
        # TODO: get activatable cards not on board
        for card in self.board:
            if card is not None and card.can_activate(ctx):
                return True
        return False

    async def pick_free_field(self, ctx: dict, card: CardInstance) -> int:
        # TODO: check card stacking
        fields = [i + 1 for i in range(len(self.board)) if self.board[i] is None]
        if not fields:
            return -1
        return fields[await self.callback.choose("Choose field position:", fields)]-1

    async def draw(self, ctx: dict, n: int = 1, side: bool = False):
        # TODO: draw specific matched card
        # TODO: lose game when deck is empty
        assert side or n <= len(self.deck)
        for _ in range(n):
            if side:
                card = CardInstance(owner=self, card=random.choice(self.side), side=True)
            else:
                card = self.deck.pop()
            self.place(ctx, card, ZoneEnum.hand)
            self.on_draw(ctx, card)

    async def search(self, ctx: dict, zones: Zone, match: Objects | None = None):
        choices = self.game.query(ctx, match, place=zones)
        # TODO: search own fields if not otherwise specified
        index = await self.callback.choose("Choose a card:", choices)
        card = choices[index]
        self.pop(ctx, card)
        self.place(ctx, card, ZoneEnum.hand)
    
    async def discard(self, ctx: dict, n: int = 1, match: Objects | None = None):
        for _ in range(n):
            if len(self.hand) == 0:
                return
            if match:
                choices = self.query(ctx, match, place=ZoneEnum.hand)
            else:
                choices = self.hand
            index = await self.callback.choose("Discard a card:", choices)
            index = self.hand.index(choices[index])
            card = self.hand.pop(index)
            self.pile.append(card)
            card.location = ZoneEnum.pile
            self.on_discard(ctx, card)

    async def create(self, ctx: dict, card: Card, to_index: int):
        assert to_index >= 0 and to_index < len(self.board)
        assert self.board[to_index] is None  # TODO: should this be allowed?
        inst = CardInstance(card=card, controller=self, owner=self, field_index=to_index)
        self.place(ctx, inst, ZoneEnum.board, to_index)
    
    async def destroy(self, ctx: dict, card: CardInstance):
        self.pop(ctx, card)
        self.place(ctx, card, ZoneEnum.pile)
        self.on_destroy(ctx, card)

    async def play(self, ctx: dict, card: CardInstance, to_index: int):
        self.pop(ctx, card)
        self.place(ctx, card, ZoneEnum.board, to_index)
    
    async def cast(self, ctx: dict):
        from_index = await self.callback.choose("Play from hand:", [o.name for o in self.hand])
        card = self.hand.pop(from_index)
        card.location = ZoneEnum.stack
        ctx["self"] = card
        to_index = await self.pick_free_field(ctx, card)
        if to_index == -1:
            return
        # TODO: pay card costs
        await self.game.send(ctx, [(self, "play", [card, to_index])])

    async def activate(self, ctx: dict):
        # TODO: get payable and playable abilities
        # TODO: include enemy abilities
        card_options = [o.name for o in self.board if o and o.activated_abilities]
        index = await self.callback.choose("Activate ability of:", card_options)
        card: CardInstance = self.board[index]
        abilities = list(reversed(card.abilities))
        abilities = [abilities.index(a) for a in card.activated_abilities]
        texts = list(reversed(card.card.rule_texts))
        abilities = [texts[a] for a in abilities]
        index = await self.callback.choose("Choose ability:", abilities)
        await card.activate(ctx, index)

    async def copy(self, ctx: dict, card: CardInstance, to_index: int):
        # TODO: add 'token' and 'copy' modifier
        inst = CardInstance(card=card.card, controller=self, owner=self, field_index=to_index)
        self.place(ctx, inst, ZoneEnum.board, to_index)

    async def shuffle(self, ctx: dict, cards: list[CardInstance], zone: ZoneEnum):
        assert zone != ZoneEnum.hand and zone != ZoneEnum.board
        for card in cards:
            self.pop(ctx, card)
            self.place(ctx, card, zone)
        match zone:
            case ZoneEnum.deck:
                random.shuffle(self.deck)
            case ZoneEnum.pile:
                random.shuffle(self.pile)
    
    async def counter(self, ctx: dict, obj: CardInstance | PlayedAbility):
        assert obj in self.game.stack
        self.game.stack.remove(obj)
        self.on_counter(ctx, obj)
    
    async def extraturn(self, ctx: dict):
        self.turnsafterthis += 1

    async def look(self, ctx: dict, place: Zone, n: int):
        cards = self.game.query(ctx, None, place, n)
        await self.callback.show("Revealed cards:", cards)

    async def put(self, ctx: dict, card: CardInstance, to_index: int):
        self.pop(ctx, card)
        self.place(ctx, card, ZoneEnum.board, to_index)
    
    def place(self, ctx: dict, card: CardInstance, place: ZoneEnum, to_index: int | None = None, relative: PlaceEnum | None = None):
        if place == ZoneEnum.deck:
            if relative is None or relative == PlaceEnum.top:
                if to_index is None:
                    self.deck.append(card)
                else:
                    self.deck.insert(len(self.deck) - to_index, card)
            else:
                if to_index is None:
                    self.deck.insert(0, card)
                else:
                    self.deck.insert(to_index, card)
            card.location = ZoneEnum.deck
            card.field_index = -1
        elif place == ZoneEnum.pile:
            self.pile.append(card)
            card.location = ZoneEnum.pile
            card.field_index = -1
        elif place == ZoneEnum.hand:
            self.hand.append(card)
            card.location = ZoneEnum.hand
            card.field_index = -1
        elif place == ZoneEnum.board:
            assert to_index is not None and 0 <= to_index < NUM_FIELDS
            assert self.board[to_index] is None     # TODO: should this be allowed?
            self.board[to_index] = card
            card.location = ZoneEnum.board
            card.field_index = to_index
            card.controller = self
            self.on_enter(ctx, card)

    def pop(self, ctx: dict, card: CardInstance):
        card.reset()
        if card.location == ZoneEnum.deck:
            assert card in self.deck
            self.deck.remove(card)
        elif card.location == ZoneEnum.pile:
            assert card in self.pile
            self.pile.remove(card)
        elif card.location == ZoneEnum.hand:
            assert card in self.hand
            self.hand.remove(card)
        elif card.location == ZoneEnum.board:
            assert card in self.board
            self.board[self.board.index(card)] = None
            self.on_exit(ctx, card)

    def query(self, ctx: dict, obj: Player | Objects | None = None, place: Zone | ZoneEnum | None = None) -> list[CardInstance]:
        found = []
        if self._match_field(ctx, ZoneEnum.board, place):
            for card in self.board:
                if card and (obj is None or obj.match(ctx, card)):
                    found.append(card)
        if self._match_field(ctx, ZoneEnum.hand, place):
            for card in self.hand:
                if obj is None or obj.match(ctx, card):
                    found.append(card)
        if self._match_field(ctx, ZoneEnum.pile, place):
            for card in self.pile:
                if obj is None or obj.match(ctx, card):
                    found.append(card)
        if self._match_field(ctx, ZoneEnum.deck, place):
            for card in self.deck:
                if obj is None or obj.match(ctx, card):
                    found.append(card)
        return found
    
    def _match_field(self, ctx: dict, place: ZoneEnum, match: ZoneEnum | Zone | None) -> bool:
        if match is None:
            return True
        if isinstance(match, Zone):
            return match.match(ctx, place, self)
        return place == match

    def on_enter(self, ctx: dict, card: CardInstance):
        pass

    def on_exit(self, ctx: dict, card: CardInstance):
        pass

    def on_draw(self, ctx: dict, card: CardInstance):
        pass

    def on_discard(self, ctx: dict, card: CardInstance):
        pass
    
    def on_destroy(self, ctx: dict, card: CardInstance):
        pass

    def on_counter(self, ctx: dict, ability: CardInstance | PlayedAbility):
        pass

    def on_endturn(self, ctx: dict):
        pass


@dataclass
class Game:
    players: list[PlayerState] = field(default_factory=list)
    start_cards: int = 5
    turn: int = 0
    phase: PhaseEnum = PhaseEnum.activation
    stack: list[PlayedAbility] = field(default_factory=list)

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
                await player.draw({})
        
        while True:
            # TODO: decide turn order
            player = self.players[self.turn % len(self.players)]

            await self.do_turn(player)
            # TODO: look at turnsafterthis for next player's turn

            self.turn += 1
        
    async def do_turn(self, player: PlayerState):
        ctx = {
            "game": self,
            "turn": self.turn,
            "current_player": player
        }
        await player.draw(ctx)
        self.print_hand(player)

        done = False
        while not done:
            done = await self._choose_action(ctx, player)
        
        # TODO: combat
        
        player.on_endturn(ctx)

    async def _choose_action(self, ctx: dict, player: PlayerState):
        # TODO: get possible actions
        choices = 
        idx = await player.callback.choose("Choose action:", choices)
        match choices[idx]:
            case "hand":
                self.print_hand(player)
            case "field":
                self.print_field(player)
            case "pile":
                self.print_pile(player)
            case "play":
                await player.cast(ctx)
            case "activate":
                await player.activate(ctx)
            case "pass":
                return True
        return False

    async def pick(self, ctx: dict, obj: Player | Objects, place: ZoneEnum | Zone | None= None) -> list:
        n = obj.targets(ctx)
        if n > 0:
            player: PlayerState = ctx["controller"]
            ctx["targets"] = []
            for _ in range(n):
                found = self.query(ctx, obj, place)
                if len(found) == 0:
                    return ctx["targets"]
                i = await player.callback.choose("Target one of:", found)
                ctx["targets"].append(found[i])
            return ctx["targets"]
        
        return self.query(ctx, obj, place)

    def query(self, ctx: dict, obj: Player | Objects, place: ZoneEnum | Zone | None = None, n: int = -1) -> list:
        found = []
        # TODO: add stack abilities
        for player in self.players:
            if obj.match(ctx, player):
                found.append(player)
            found.extend(player.query(ctx, obj, place))
        if n > 0:
            return found[:n]
        return found
    
    async def send(self, ctx: dict, effects: list[tuple[PlayerState, str, list]]):
        self.stack.append(PlayedAbility(source=ctx["self"], ability=ctx.get("ability"), effects=effects))
        while len(self.stack) > 0:
            for priority in range(len(self.players)):
                player = self.players[(self.turn + priority) % len(self.players)]
                done = False
                while not done:
                    done = await self._choose_action(ctx, player)
            await self.stack.pop().resolve(ctx)

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
    
    def print_hand(self, player: PlayerState) -> str:
        print(self.repr_stack(player.hand))
    
    def print_field(self, player: PlayerState) -> str:
        print(self.repr_stack(player.board))

    def print_pile(self, player: PlayerState) -> str:
        print(self.repr_stack(player.pile))
