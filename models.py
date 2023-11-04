from enum import Enum
from typing import Literal, Any
from pydantic import BaseModel


NumberOrX = int | Literal["X"] | Literal["-X"] | Literal["that"]


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


class Reference(str, GrammarEnum):
    this = "this"
    that = "that"
    the = "the"
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
    your = "your"
    their = "their"


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


class ZoneEnum(str, GrammarEnum):
    deck = "deck"
    pile = "pile"
    hand = "hand"
    board = "board"
    stack = "stack"
    it = "it"


class OperatorEnum(str, GrammarEnum):
    AND = "and"
    OR = "or"
    XOR = "xor"
    OPTIONAL = "optional"


class PlaceEnum(str, GrammarEnum):
    bottom = "bottom"
    top = "top"


class OrderEnum(str, GrammarEnum):
    ordered = "ordered"
    random = "random"


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


class Stats(BaseModel):
    power: NumberOrX = 0
    health: NumberOrX = 0


def getnumber(n: NumberOrX, ctx: dict):
    if isinstance(n, int):
        return n
    elif n == "X":
        # TODO: find value of X
        # TODO: ask player for X
        return ctx["X"]
    else:
        raise RuntimeError(F"n can't be {n}")


class BaseEffect(BaseModel):
    async def activate(self, ctx: dict):
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
        elif self.suffix == SuffixEnum.chosentype:
            # TODO: implement chosentype
            return False
        elif self.suffix == SuffixEnum.amongthem:
            # TODO: implement amongthem
            return False
        return True


class BaseObject(BaseModel):
    def targets(self, ctx: dict) -> int:
        return -1
    
    def match(self, ctx: dict, other: Any) -> bool:
        pass


class ObjectMatch(BaseModel):
    objects: list[BaseObject] = []
    each: bool = False

    def targets(self, ctx: dict) -> int:
        for obj in self.objects:
            n = obj.targets(ctx)
            if n > 0:
                return n
        return -1

    def match(self, ctx: dict, other: Any) -> bool:
        for o in self.objects:
            if not o.match(ctx, other):
                return False
        return True


class PlayerMatch(BaseModel):
    player: PlayerEnum
    ref: Reference | ObjectMatch | None = None
    extra: NumberOrX | None = None  # TODO: implement player extra (target count etc)
    who_cant: bool = False

    def targets(self, ctx: dict) -> int:
        if self.ref == Reference.target:
            if self.extra is not None:
                # TODO: implement get X
                return self.extra
            return 1
        return -1

    def match(self, ctx: dict, other: Any) -> bool:
        if type(other).__name__ != "PlayerState":
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


class ZoneMatch(BaseModel):
    zones: list[ZoneEnum] = []
    ref: PlayerMatch | None = None
    # Used for placement
    place: PlaceEnum | None = None
    random: bool = False

    def match(self, ctx: dict, field: ZoneEnum, player: Any = None):
        if isinstance(self.ref, PlayerMatch):
            if not self.ref.match(ctx, player):
                return False
        return field in self.zones


class Effect(BaseEffect):
    effects: list[BaseEffect] = []
    op: OperatorEnum = OperatorEnum.AND

    async def activate(self, ctx: dict):
        # TODO: add op == Operator.optional check
        for e in self.effects:
            await e.activate(ctx)


class EssenceCosts(BaseModel):
    costs: list[ColorEnum | NumberOrX] = []


class ActionCost(BaseModel):
    cost: list[BaseEffect] = []


class Condition(BaseModel):
    condition: ConditonEnum
    until: bool = False


class PlayedCondition(Condition):
    object: ObjectMatch
    duration: Condition


class NumberCondition(Condition):
    number: str
    compare: str   # TODO: implement compare


class PlayerCondition(Condition):
    player: PlayerMatch
    phrase: str   # TODO: implement playerphrase


class ObjectCondition(Condition):
    object: ObjectMatch
    phrase: str   # TODO: implement objectphrase


class Phase(BaseModel):
    ref: TurnQualifierEnum | Reference | PlayerMatch | None = None
    phase: PhaseEnum
    

class Trigger(BaseModel):
    trigger: TriggerEnum
    objects: ObjectMatch | PlayerMatch | Phase | None = None


class NumberDef(BaseModel):
    amount: ObjectMatch | Reference
    property: NumbericalEnum | None = None


class TriggeredAbility(BaseModel):
    trigger: Trigger
    effect: Effect
    condition: Condition | None = None


class ActivatedAbility(BaseModel):
    costs: list[EssenceCosts | Activation | ActionCost] = []
    effect: Effect

    def can_activate(self, ctx: dict):
        # TODO: check if costs can be paid
        return True

    async def pay_costs(self, ctx: dict):
        # TODO: check if costs can be paid and pay costs
        # TODO: add pyed costs to ctx including sacrificed units
        pass

    async def activate(self, ctx: dict):
        await self.pay_costs(ctx)
        await self.effect.activate(ctx)
        return True


AquiredAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility | ActionCost | Effect | Literal["this"]


class CardObject(BaseObject):
    type: TypeEnum | None = None
    ref: Reference | ObjectRef | None = None
    extra: NumberOrX | None = None
    prefixes: list[Prefix] = []
    suffix: Suffix | None = None
    withwhat: AquiredAbilities | None = None
    without: KeywordEnum | None = None
    copies: bool = False

    def targets(self, ctx: dict) -> int:
        if self.ref == Reference.target:
            if self.extra is not None:
                return getnumber(self.extra, ctx)
            return 1
        return -1

    def match(self, ctx: dict, other: Any) -> bool:
        if type(other).__name__ != 'CardInstance':
            return False
        
        if self.type is not None and self.type not in other.card.type:
            return False
        
        if self.ref is not None:
            r = self.ref
            if r == ObjectRef.self and ctx["self"] != other:
                return False
            elif r in [ObjectRef.it, Reference.this, Reference.that]:
                if ctx["this"] != other:
                    return False
            elif r in [ObjectRef.rest, Reference.another]:
                if ctx["this"] == other:
                    return False
                elif "these" in ctx and other not in ctx["these"]:
                    return False
            elif r == ObjectRef.any:
                if other not in ctx["these"]:
                    return False
            elif r == ObjectRef.sac:
                if other not in ctx["sacrificed"]:
                    return False
            if r in [Reference.each, Reference.all]:
                if "these" in ctx and other not in ctx["these"]:
                    return False
            elif r == Reference.chosen:
                if other in ctx["chosen"]:
                    # TODO: add choose action
                    return False
            elif r == Reference.target:
                if other in ctx["targets"]:
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
            if isinstance(self.withwhat, AquiredAbilities) and self.withwhat not in other.abilities:
                return False
        
        if self.without is not None and self.without in other.card.abilities:
            return False
        
        return True


class AbilityObject(BaseObject):
    ref: Reference | ObjectRef | NumberOrX | None = None
    extra: NumberOrX | None = None
    prefixes: list[Prefix] = []
    suffix: Suffix | None = None

    def match(self, ctx: dict, other: Any) -> bool:
        if type(other).__name__ != 'PlayedAbility':
            return False
        # TODO: add prefixes, suffix and ref checks
        return True


class SubjEffect(BaseEffect):
    effects: list[BaseEffect] = []

    async def activate(self, ctx: dict):
        game = ctx["game"]
        effects = []
        for player in await game.pick(ctx, self.subj):
            ctx["subject"] = player
            for e in self.effects:
                async for action in e.activate(ctx):
                    effects.append((player, e.action, action))
        await game.send(ctx, effects)


class PlayerEffect(SubjEffect):
    subj: PlayerMatch = PlayerMatch(player=PlayerEnum.you)
    

class ObjectEffect(SubjEffect):
    subj: ObjectMatch = ObjectMatch(objects=[BaseObject(object=ObjectRef.it)])


class CreateTokenEffect(BaseEffect):
    action: str = "create"
    number: NumberOrX = 1
    stats: Stats = Stats()
    abilities: list[AquiredAbilities] = []

    async def activate(self, ctx: dict):
        player = ctx["subject"]
        for _ in range(getnumber(self.number, ctx)):
            card = Card(
                name="Token",
                damage=self.stats.power,
                health=self.stats.health,
                types=[TypeEnum.UNIT],
            )
            index = await player.pick_free_field(ctx, card)
            if index == -1:
                # TODO: No field places available, should it stop creeating tokens?
                return
            yield card, index


class DestroyEffect(BaseEffect):
    action: str = "destroy"
    objects: ObjectMatch

    async def activate(self, ctx: dict):
        for d in await ctx["game"].pick(ctx, self.objects, place=ZoneEnum.board):
            yield d


class CopyEffect(BaseEffect):
    action: str = "copy"
    objects: ObjectMatch

    async def activate(self, ctx: dict):
        player = ctx["subject"]
        for d in await ctx["game"].pick(ctx, self.objects, place=ZoneEnum.board):
            index = await player.pick_free_field(ctx, d)
            if index == -1:
                # TODO: No field places available, should it stop creating tokens?
                return
            yield d


class PlayEffect(BaseEffect):
    action: str = "play"
    objects: ObjectMatch
    free: bool = False
    
    async def activate(self, ctx: dict):
        for d in await ctx["game"].pick(ctx, self.objects):
            yield d, self.free


class DrawEffect(BaseEffect):
    action: str = "draw"
    number: NumberOrX = 1
    
    async def activate(self, ctx: dict):
        yield getnumber(self.number, ctx)


class DiscardEffect(BaseEffect):
    action: str = "discard"
    number: NumberOrX = 1
    objects: ObjectMatch

    async def activate(self, ctx: dict):
        yield getnumber(self.number, ctx), self.objects


class SearchEffect(BaseEffect):
    action: str = "search"
    number: NumberOrX = 1
    zones: ZoneMatch
    objects: ObjectMatch | None = None

    async def activate(self, ctx: dict):
        for _ in range(getnumber(self.number, ctx)):
            yield self.objects, self.zones


class ShuffleEffect(BaseEffect):
    action: str = "shuffle"
    what: ZoneMatch | ObjectMatch | None = None
    zones: ZoneMatch

    async def activate(self, ctx: dict):
        player = ctx["subject"]
        for zone in self.zones.zones:
            if isinstance(self.what, ObjectMatch):
                what = player.query(ctx, self.what)
            elif isinstance(self.what, ZoneMatch):
                what = player.query(ctx, None, self.what)
            else:
                what = player.query(ctx, None, ZoneMatch(zones=[zone], ref=self.zones.ref))
            yield what, zone


class CounterEffect(BaseEffect):
    action: str = "counter"
    objects: ObjectMatch

    async def activate(self, ctx: dict):
        for d in await ctx["game"].pick(ctx, self.objects, place=ZoneEnum.stack):
            yield d


class ExtraTurnEffect(BaseEffect):
    action: str = "extraturn"
    number: NumberOrX = 1

    async def activate(self, ctx: dict):
        yield getnumber(self.number, ctx)


class LookEffect(BaseEffect):
    action: str = "look"
    number: NumberOrX = 1
    zones: ZoneMatch

    async def activate(self, ctx: dict):
        yield self.zones, getnumber(self.number, ctx)


class PutEffect(BaseEffect):
    action: str = "put"
    objects: ObjectMatch
    into: ZoneMatch
    deactivated: bool = False
    second_objects: ObjectMatch | None = None
    second_into: ZoneMatch | None = None

    async def activate(self, ctx: dict):
        for d in await ctx["game"].pick(ctx, self.objects):
            yield d, self.into, {"deactivated": self.deactivated}


class GainControlEffect(BaseEffect):
    action: str = "control"
    objects: ObjectMatch
    until: Condition | None = None

    async def activate(self, ctx: dict):
        for d in await ctx["game"].pick(ctx, self.objects):
            yield d, self.until


class SwitchStatsEffect(BaseEffect):
    action: str = "switchstats"
    objects: ObjectMatch
    until: Condition | None = None

    async def activate(self, ctx: dict):
        for d in await ctx["game"].pick(ctx, self.objects):
            yield d, self.until


class AddEssenceEffect(BaseEffect):
    action: str = "essence"
    colors: list[str] = []
    amount: NumberOrX = 1

    async def activate(self, ctx: dict):
        player = ctx["subject"]
        if len(self.colors) > 1:
            yield await player.callback.choose("Choose essence color:", self.colors), self.amount
        elif len(self.colors) == 1:
            yield self.colors[0], self.amount
        else:
            yield None, self.amount


class ActivationEffect(BaseEffect):
    objects: ObjectMatch
    deactivate: bool = True


class SacrificeEffect(BaseEffect):
    objects: ObjectMatch


class PayessenceEffect(BaseEffect):
    costs: EssenceCosts


class PaylifeEffect(BaseEffect):
    costs: NumberOrX


class RevealEffect(BaseEffect):
    player: PlayerMatch


class MoveEffect(BaseEffect):
    objects: ObjectMatch
    tozone: ZoneMatch
    fromzone: ZoneMatch | None = None


class ModAbility(BaseEffect):
    stats: Stats = Stats()
    foreach: ObjectMatch | None = None


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
    foreach: ObjectMatch | None = None


class EntersAbility(BaseEffect):
    deactivate: bool = False
    control: PlayerMatch | ObjectRef | None = None


class BecomesAbility(BaseEffect):
    what: list[ColorEnum | TypeEnum | Stats] = []
    additional: bool = False


class DealsAbility(BaseEffect):
    amount: NumberOrX | NumberDef = 1
    recipients: list[PlayerMatch | ObjectMatch | DamageRef] = []
    spread: bool = False


class Card(BaseModel):
    name: str = ''
    cost: list[ColorEnum | NumberOrX] = [0]
    types: list[TypeEnum] = []
    subtypes: list[str] = []
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
    
    def __str__(self) -> str:
        costs = "}{".join([str(c) for c in self.cost])
        t = " ".join([t.capitalize() for t in self.types])
        if self.subtypes:
            t += " - " + " ".join([t.capitalize() for t in self.subtypes])
        a = "\n".join(self.rule_texts)
        return f"{self.name} {{{costs}}}\n{t}\n{a}\n{self.damage}/{self.health}"
