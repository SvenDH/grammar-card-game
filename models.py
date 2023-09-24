import random
from enum import Enum
from typing import Literal, Any
from pydantic import BaseModel


NumberOrX = int | Literal["X"] | Literal["-X"] | Literal["that"]
Stats = tuple[NumberOrX, NumberOrX]


class GrammarEnum(Enum):
    @classmethod
    def to_grammar(cls):
        return " | ".join([f'( /[{v.value[0].lower()}{v.value[0].upper()}]/ "{v.value[1:]}")' for v in cls])


class ColorEnum(str, GrammarEnum):
    yellow = "Y"
    red = "R"
    green = "G"
    blue = "B"
    colorless = "U"
    multicolored = "M"
    monocolored = "O"


class Activation(str, GrammarEnum):
    activate = "Q"
    deactivate = "T"


class TypeEnum(str, GrammarEnum):
    UNIT = "unit"
    SPELL = "spell"
    TOKEN = "token"


class KeywordEnum(str, GrammarEnum):
    FLYING = "flying"
    SIEGE = "siege"
    POISON = "poison"


class NumbericalEnum(str, GrammarEnum):
    damage = "damage"
    health = "health"
    level = "level"


class ObjectActionEnum(str, GrammarEnum):
    attack = "attack"
    block = "block"
    attackorblock = "attack or block"
    beblocked = "be blocked"
    becountered = "be countered"
    activateability = "activate abilities"


class ConditonEnum(str, GrammarEnum):
    playedwhen = "played when"
    yourturn = "your turn"
    notyourturn = "not your turn"
    compare = "number compare"
    playercond = "player condition"
    objectcond = "object condition"
    thisturn = "this turn"


class ObjectRef(str, GrammarEnum):
    self = "~"
    it = "it"
    they = "they"
    rest = "the rest"
    sac = "the sacrificed"
    any = "any of"


class PlayerRef(str, GrammarEnum):
    your = "your"
    their = "their"


class Reference(str, GrammarEnum):
    this = "this"
    that = "that"
    another = "another"
    chosen = "the chosen"
    each = "each"
    all = "all"
    target = "target"
    atleast = "atleast"
    exactly = "exactly"
    ormore = "or more"
    fewerthan = "fewer than"
    anynumberof = "any number of"
    upto = "up to"
    oneof = "one of"


class DamageRef(str, GrammarEnum):
    itself = "itself"
    anytarget = "any target"


Countables = [Reference.exactly, Reference.atleast, Reference.ormore, Reference.fewerthan, Reference.upto, Reference.oneof, Reference.anynumberof]


class PrefixEnum(str, GrammarEnum):
    activated = "activated"
    attacking = "attacking"
    blocking = "blocking"
    attackingorblocking = "attacking or blocking"


class SuffixEnum(str, GrammarEnum):
    control = "control"
    nocontrol = "no control"
    own = "own"
    noown = "no own"
    inzone = "in zone"
    youplay = "you play"
    targets = "targets"
    targetsonly = "targets only"
    couldtarget = "could target"
    activatedthisway = "activated this way"
    deactivatedthisway = "deactivated this way"
    chosentype = "chosen type"
    amongthem = "among them"


class PureObject(str, GrammarEnum):
    ability = "ability"
    token = "token"
    card = "card"
    copies = "copies"


class ZoneEnum(str, GrammarEnum):
    deck = "deck"
    discard = "discard"
    hand = "hand"
    field = "field"
    it = "it"


class OperatorEnum(str, GrammarEnum):
    AND = "and"
    OR = "or"
    XOR = "xor"
    OPTIONAL = "optional"


class PlaceEnum(str, GrammarEnum):
    bottom = "bottom"
    top = "top"


class PlayerEnum(str, GrammarEnum):
    opponent = "opponent"
    player = "player"
    you = "you"
    they = "they"
    owner = "owner"
    controller = "controller"
    defending = "defending"
    attacking = "attacking"


class TriggerEnum(str, GrammarEnum):
    whenplay = "when play"
    whengainlife = "when gain life"
    whenloselife = "when lose life"
    whendamaged = "when damaged"
    endofturn = "end of turn"
    beginningofphase = "beginning of phase"


class PhaseEnum(str, GrammarEnum):
    turn = "turn"
    activation = "activation"
    draw = "draw step"
    play = "play phase"
    fight = "fight phase"
    cleanup = "cleanup"


class TurnQualifierEnum(str, GrammarEnum):
    each = "each"
    this = "this"
    that = "that"
    the = "the"


class BaseEffect(BaseModel):
    def activate(self, ctx: dict):
        raise NotImplementedError("Subclass BaseEffect and implement activate")


class Prefix(BaseModel):
    prefix: PrefixEnum | TypeEnum | ColorEnum | Stats
    non: bool = False

    def match(self, ctx: dict, other: Any) -> bool:
        if self.non:
            if isinstance(self.prefix, TypeEnum) and other.type == self.prefix:
                return False
            elif self.prefix == PrefixEnum.activated and other.activated:
                return False
            elif self.prefix == PrefixEnum.attacking and other.attacking:
                return False
            elif self.prefix == PrefixEnum.blocking  and other.blocking:
                return False
            elif self.prefix == PrefixEnum.attackingorblocking and (other.attacking or other.blocking):
                return False
            elif isinstance(self.prefix, Stats) and other.damage == self.prefix[0] and other.health == self.prefix[1]:
                return False
            elif isinstance(self.prefix, ColorEnum) and self.prefix in other.color:
                return False
        else:
            if isinstance(self.prefix, TypeEnum) and other.type != self.prefix:
                return False
            elif self.prefix == PrefixEnum.activated and not other.activated:
                return False
            elif self.prefix == PrefixEnum.attacking and not other.attacking:
                return False
            elif self.prefix == PrefixEnum.blocking  and not other.blocking:
                return False
            elif self.prefix == PrefixEnum.attackingorblocking and not (other.attacking or other.blocking):
                return False
            elif isinstance(self.prefix, Stats) and not (other.damage == self.prefix[0] and other.health == self.prefix[1]):
                return False
            elif isinstance(self.prefix, ColorEnum) and self.prefix not in other.color:
                return False
        return True


class Suffix(BaseModel):
    suffix: SuffixEnum
    subj: Any = None

    def match(self, ctx: dict, other: Any) -> bool:
        if self.suffix == SuffixEnum.control:
            return self.subj.match(ctx, other.control)
        elif self.suffix == SuffixEnum.nocontrol:
            return not self.subj.match(ctx, other.control)
        elif self.suffix == SuffixEnum.own:
            return self.subj.match(ctx, other.owner)
        elif self.suffix == SuffixEnum.noown:
            return not self.subj.match(ctx, other.owner)
        elif self.suffix == SuffixEnum.inzone:
            for place in self.subj:
                if not place.match(ctx, other):
                    return False
        elif self.suffix == SuffixEnum.youplay:
            if "played" not in ctx or ctx["played"] != other:
                return False
            if ctx["controller"] != other.control:
                return False
        elif self.suffix == SuffixEnum.targets:
            if "targets" not in ctx or "targeting" not in ctx:
                return False
            if ctx["targeting"] != other:
                return False
            for o in ctx["targets"]:
                if self.subj.match(o):
                    return True
            return False
        elif self.suffix == SuffixEnum.targetsonly:
            if "targets" not in ctx or "targeting" not in ctx:
                return False
            if ctx["targeting"] != other:
                return False
            if len(ctx["targets"]) != 1:
                return False
            return self.subj.match(ctx["targets"][0])
        elif self.suffix == SuffixEnum.activatedthisway:
            if "activated" not in ctx or other not in ctx["activated"]:
                return False
        elif self.suffix == SuffixEnum.deactivatedthisway:
            if "deactivated" not in ctx or other not in ctx["deactivated"]:
                return False
        elif self.suffix == SuffixEnum.couldtarget:
            # TODO: implement couldtarget
            return False
        elif self.suffix == Suffix.chosentype:
            # TODO: implement chosentype
            return False
        elif self.suffix == SuffixEnum.amongthem:
            # TODO: implement amongthem
            return False
        return True


class Condition(BaseModel):
    condition: ConditonEnum
    until: bool = False


class EssenceCosts(BaseModel):
    costs: list[ColorEnum | NumberOrX] = []


class Object(BaseModel):
    def match(self, ctx: dict, other: Any) -> bool:
        pass


class Objects(BaseModel):
    objects: list[Object] = []
    each: bool = False

    def match(self, ctx: dict, other: Any) -> bool:
        for o in self.objects:
            if not o.match(ctx, other):
                return False
        return True


class Player(BaseModel):
    player: PlayerEnum
    ref: Reference | Objects | PlayerRef | None = None
    who_cant: bool = False

    def match(self, ctx: dict, other: Any) -> bool:
        if not isinstance(other, PlayerState):
            return False
        elif self.player == PlayerEnum.you and ctx["controller"] != other:
            return False
        elif self.player == PlayerEnum.opponent and ctx["controller"] == other:
            return False
        # TODO: add owner and controller checks
        elif self.player == PlayerEnum.attacking:
            if "attacking" not in ctx or ctx["attacking"] != other:
                return False
        elif self.player == PlayerEnum.defending:
            if "defending" not in ctx or ctx["defending"] != other:
                return False
        return True


class Zone(BaseModel):
    zones: list[ZoneEnum] = []
    ref: Object | Player | None = None
    op: OperatorEnum | None = None


class Into(Zone):
    place: PlaceEnum | None = None
    random: bool = False


class Effect(BaseEffect):
    effects: list[BaseEffect] = []
    op: OperatorEnum = OperatorEnum.AND

    def activate(self, ctx: dict):
        # TODO: add op == Operator.optional check
        for e in self.effects:
            e.activate(ctx)


class ActionCost(BaseModel):
    cost: list[BaseEffect] = []


class PlayedCondition(Condition):
    object: Objects
    duration: Condition


class NumberCondition(Condition):
    number: str
    compare: str   # TODO: implement compare


class PlayerCondition(Condition):
    player: Player
    phrase: str   # TODO: implement playerphrase


class ObjectCondition(Condition):
    object: Objects
    phrase: str   # TODO: implement objectphrase


class Phase(BaseModel):
    ref: TurnQualifierEnum | ObjectRef | Player | None = None
    phase: PhaseEnum
    

class Trigger(BaseModel):
    trigger: TriggerEnum
    objects: Objects | Player | Phase | None = None


class NumberDef(BaseModel):
    amount: Objects | PlayerRef
    property: NumbericalEnum | None = None


class TriggeredAbility(BaseModel):
    trigger: Trigger
    effect: Effect
    condition: Condition | None = None


class ActivatedAbility(BaseModel):
    costs: list[EssenceCosts | Activation | ActionCost] = []
    effect: Effect

    def pay_costs(self, ctx: dict):
        # TODO: check if costs can be paid and pay costs
        # TODO: add pyed costs to ctx including sacrificed units
        pass

    def activate(self, ctx: dict):
        self.pay_costs(ctx)
        self.effect.activate(ctx)


AquiredAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility | ActionCost | Effect | Literal["this"]


class PlayerEffect(BaseEffect):
    subj: Player = Player(player=PlayerEnum.you)
    effects: list[BaseEffect] = []

    def activate(self, ctx: dict):
        for player in ctx["game"].query(ctx, self.subj):
            ctx["subject"] = player
            for e in self.effects:
                e.activate(ctx)


class ObjectEffect(BaseEffect):
    subj: Object = Object(object=ObjectRef.it)
    effects: list[BaseEffect] = []
    
    def activate(self, ctx: dict):
        for player in ctx["game"].query(ctx, self.subj):
            ctx["subject"] = player
            for e in self.effects:
                e.activate(ctx)


class CreateTokenEffect(BaseEffect):
    number: NumberOrX = 1
    stats: Stats = (1, 1)
    abilities: list[AquiredAbilities] = []

    def activate(self, ctx: dict):
        player = ctx["subject"]
        # TODO: prompt for field place


class DestroyEffect(BaseEffect):
    objects: Objects

    def activate(self, ctx: dict):
        for d in ctx["game"].query(ctx, self.objects):
            d.destroy(ctx)


class CopyEffect(BaseEffect):
    objects: Objects


class PlayEffect(BaseEffect):
    objects: Objects
    free: bool = False


class DrawEffect(BaseEffect):
    number: NumberOrX = 1


class DiscardEffect(BaseEffect):
    number: NumberOrX = 1
    objects: Objects


class SearchEffect(BaseEffect):
    zones: Zone
    objects: Objects | None = None


class ShuffleEffect(BaseEffect):
    what: Zone | Objects | None = None
    zones: Zone


class CounterEffect(BaseEffect):
    objects: Objects


class ExtraTurnEffect(BaseEffect):
    turns: int = 1


class LookEffect(BaseEffect):
    number: NumberOrX = 1
    zones: Zone


class PutEffect(BaseEffect):
    objects: Objects
    into: Into
    deactivated: bool = False
    second_objects: Objects | None = None
    second_into: Into | None = None


class GainControlEffect(BaseEffect):
    objects: Objects
    until: Condition | None = None


class SwitchHpDmgEffect(BaseEffect):
    objects: Objects
    until: Condition | None = None


class AddEssenceEffect(BaseEffect):
    colors: list[str] = []
    amount: NumberOrX = 1


class ActivationEffect(BaseEffect):
    objects: Objects
    deactivate: bool = True


class SacrificeEffect(BaseEffect):
    objects: Objects


class PayessenceEffect(BaseEffect):
    costs: EssenceCosts


class PaylifeEffect(BaseEffect):
    costs: NumberOrX


class MoveEffect(BaseEffect):
    objects: Objects
    tozone: Zone
    fromzone: Zone | None = None


class ModAbility(BaseEffect):
    stats: Stats = (0, 0)
    foreach: Objects | None = None


class GetAbility(BaseEffect):
    abilities: list[AquiredAbilities | ModAbility | Literal["this"]] = []
    until: Condition | None = None


class CantAbility(BaseEffect):
    actions: list[ObjectActionEnum] = []
    until: Condition | None = None


class NoActivationAbility(BaseEffect):
    moment: Phase


class LoseAbilitiesAbility(BaseEffect):
    until: Condition | None = None


class CostsAbility(BaseEffect):
    costs: EssenceCosts
    more: bool = False
    foreach: Objects | None = None


class EntersAbility(BaseEffect):
    deactivate: bool = False
    control: Player | ObjectRef | None = None


class BecomesAbility(BaseEffect):
    what: list[ColorEnum | TypeEnum | Stats] = []
    additional: bool = False


class DealsAbility(BaseEffect):
    amount: NumberOrX | NumberDef = 1
    recipients: list[Player | Objects | DamageRef] = []
    spread: bool = False


class CardObject(Object):
    type: TypeEnum | None = None
    ref: Reference | ObjectRef | None = None
    extra: NumberOrX | None = None
    prefixes: list[Prefix] = []
    suffix: Suffix | None = None
    withwhat: AquiredAbilities | None = None
    without: KeywordEnum | None = None
    copies: bool = False

    def match(self, ctx: dict, other: Any) -> bool:
        if not isinstance(other, CardInstance):
            return False
        
        if self.type is not None and self.type not in other.card.type:
            return False
        
        if self.ref is not None:
            r = self.ref
            if r == ObjectRef.self and ctx["self"] != other:
                return False
            elif r in [ObjectRef.it, Reference.this, Reference.that] and ctx["this"] != other:
                return False
            elif r in [ObjectRef.rest, Reference.another]:
                if ctx["this"] == other:
                    return False
                elif "these" in ctx and other not in ctx["these"]:
                    return False
            elif r == ObjectRef.any and other not in ctx["these"]:
                return False
            elif r == ObjectRef.sac and other not in ctx["sacrificed"]:
                return False
            if r in [Reference.each, Reference.all]:
                if "these" in ctx and other not in ctx["these"]:
                    return False
            elif r == Reference.chosen and other not in ctx["chosen"]:
                return False
            elif r == Reference.target and other not in ctx["targets"]:
                # TODO: add test for "another"
                return False
            elif r in Countables and other in ctx["selected"]:
                return False
            else:
                raise RuntimeError(f"Unknown object reference: {r}")
        
        for prefix in self.prefixes:
            if not prefix.match(ctx, other.card):
                return False

        if self.suffix is not None and not self.suffix.match(ctx, other.card):
            return False
        
        if self.withwhat is not None:
            # TODO: implement more "with"
            if isinstance(self.without, AquiredAbilities) and r not in other.abilities:
                return False
        
        if self.without is not None and self.without in other.card.abilities:
            return False
        
        return True


class AbilityObject(Object):
    ref: Reference | ObjectRef | NumberOrX | None = None
    extra: NumberOrX | None = None
    prefixes: list[Prefix] = []
    suffix: Suffix | None = None

    def match(self, ctx: dict, other: Any) -> bool:
        if not isinstance(other, AquiredAbilities):
            return False
        # TODO: add prefixes, suffix and ref checks
        return True


class Card(BaseModel):
    name: str = ''
    cost: list[ColorEnum | NumberOrX] = [0]
    type: list[TypeEnum] = []
    subtype: list[str] = []
    abilities: list[AquiredAbilities] = []
    rule_texts: list[str] = []
    damage: int = 1
    health: int = 1

    @property
    def color(self) -> set[ColorEnum]:
        colors = list(set([c for c in self.cost if c in ColorEnum]))
        if len(colors) == 0:
            return set([ColorEnum.colorless])
        elif len(colors) == 1:
            return set(colors + [ColorEnum.monocolored])
        return set(colors + [ColorEnum.multicolored])


class CardInstance(BaseModel):
    owner: 'PlayerState'
    controller: 'PlayerState' | None = None
    card: Card
    mods: list = []
    damage: int = 1
    health: int = 1
    activated: bool = True
    attacking: bool = False
    blocking: bool = False
    side: bool = False
    field_index: int = -1

    @property
    def type(self) -> list[TypeEnum]:
        return self.card.type  # TODO: add modified types

    @property
    def abilities(self) -> list[AquiredAbilities]:
        return self.card.abilities  # TODO: add modifiers
    
    @property
    def color(self) -> set[ColorEnum]:
        # TODO: add modifiers
        return self.card.color
    
    def activate(self, ctx: dict, ability_index: int):
        ability = self.abilities[ability_index]
        assert isinstance(ability, ActivatedAbility)
        ctx["self"] = self
        ctx["owner"] = self.owner
        ctx["controller"] = self.controller
        ability.activate(ctx)

    def destroy(self, ctx: dict):
        assert self.field_index >= 0
        player = self.controller
        place = player.field[self.field_index]
        assert self in place
        player.pile.append(place.pop(place.index(self)))
        self.on_destroy(ctx)
        self.on_exit(ctx)
    
    def on_enter(self, ctx: dict):
        self.reset()
        # TODO: trigger on enter effects

    def on_exit(self, ctx: dict):
        self.reset()
        # TODO: trigger on exit effects

    def on_destroy(self, ctx: dict):
        # TODO: trigger on destory effects
        pass

    def reset(self):
        self.damage = self.card.damage
        self.health = self.card.health
        self.mods = []
        self.activated = True
        self.attacking = False
        self.blocking = False


class PlayerState(BaseModel):
    game: 'Game'
    deck: list[CardInstance] = []
    field: list[list[CardInstance]] = [[], [], [], [], []]
    pile: list[CardInstance] = []
    hand: list[CardInstance] = []
    side: list[Card] = []
    life: int = 20

    subscribed: dict[str, list[CardInstance]] = {}

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_cards(cls, game: 'Game', cards: list[Card], side_cards: list[Card]):
        p = cls(game=game, side=side_cards)
        p.deck=[CardInstance(owner=p, card=c) for c in cards]
        return p

    def draw(self, ctx: dict, n: int = 1, side: bool = False):
        assert side or n <= len(self.deck)
        cards = []
        for _ in range(n):
            if side:
                card = CardInstance(owner=self, card=random.choice(self.side), side=True)
            else:
                card = self.deck.pop()
            self.hand.append(card)
            cards.append(card)
        return cards
    
    def discard(self, ctx: dict, index: int = 0):
        assert index >= 0 and index < len(self.hand)
        self.pile.append(self.hand.pop(index))

    def place(self, ctx: dict, from_index: int, to_index: int):
        assert to_index >= 0 and to_index < len(self.field)
        assert from_index >= 0 and from_index < len(self.hand)
        card = self.hand.pop(from_index)
        self.field[to_index].append(card)
        card.controller = self
        card.field_index = to_index
        card.on_enter(ctx)
        return card
    
    def activate(self, index: int, ability_index: int, sub_index: int = 0):
        # TODO: add ability to activate from pile or hand or opponents field
        card = self.field[index][sub_index]
        ctx = {
            "game": self.game,
            "activator": self,
        }
        card.activate(ctx=ctx, ability_index=ability_index)

    def query(self, ctx: dict, obj: Player | Objects):
        found = []
        if obj.match(ctx, self):
            found.append(self)
        for place in self.field:
            for card in place:
                if obj.match(ctx, self):
                    found.append(card)
        # TODO: find in pile, deck, or hand?
        return found

class Game(BaseModel):
    players: list[PlayerState] = []
    turn: tuple[int, int] = (0, 0)
    phase: PhaseEnum = PhaseEnum.activation

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_cards(cls, *decks: list[tuple[list[Card], list[Card]]]):
        g = cls()
        g.players = [PlayerState.from_cards(g, d[0], d[1]) for d in decks]
        return g
    
    def query(self, ctx: dict, obj: Player | Objects):
        found = []
        for player in self.players:
            found.extend(player.query(ctx, obj))
        return found
