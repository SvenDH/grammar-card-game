from enum import Enum
from typing import Literal, Any
from pydantic import BaseModel

from godot_parser import GDResource


NumberOrX = int | Literal["X"] | Literal["-X"] | Literal["that"]

def encode_numberorx(num: NumberOrX):
    if num == "X":
        return 9999999999999999
    elif num == "-X":
        return -9999999999999999
    elif num == "that":
        return 8888888888888888
    return int(num)


class GrammarEnum(Enum):
    @classmethod
    def to_grammar(cls):
        return " | ".join([f'( /[{v.value[0].lower()}{v.value[0].upper()}]/ "{v.value[1:]}")' for v in cls])
    
    @classmethod
    def to_int(cls, value):
        vals = list(cls.__members__.values())
        return vals.index(value)


class ColorEnum(str, GrammarEnum):
    none = ""
    colorless = "U"
    yellow = "Y"
    red = "R"
    green = "G"
    blue = "B"
    multicolored = "M"
    monocolored = "O"


class Activation(str, GrammarEnum):
    activate = "Q"
    deactivate = "T"


class TypeEnum(str, GrammarEnum):
    none = ""
    unit = "unit"
    spell = "spell"
    token = "token"


class KeywordEnum(str, GrammarEnum):
    none = ""
    flying = "flying"
    siege = "siege"
    poison = "poison"


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


class Reference(str, GrammarEnum):
    none = ""
    self = "~"
    it = "it"
    they = "they"
    rest = "the rest"
    sac = "the sacrificed"
    any = "any of"
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
    itself = "itself"
    anytarget = "any target"


Countables = [Reference.exactly, Reference.atleast, Reference.ormore, Reference.fewerthan, Reference.upto, Reference.oneof, Reference.anynumberof]


class PrefixEnum(str, GrammarEnum):
    none = ""
    activated = "activated"
    attacking = "attacking"
    blocking = "blocking"
    attackingorblocking = "attacking or blocking"


class SuffixEnum(str, GrammarEnum):
    none = ""
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
    none = ""
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
    top = "top"
    bottom = "bottom"


class OrderEnum(str, GrammarEnum):
    ordered = "ordered"
    random = "random"


class PlayerEnum(str, GrammarEnum):
    none = ""
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


class BaseEffect(BaseModel):
    pass


class Prefix(BaseModel):
    prefix: PrefixEnum | TypeEnum | ColorEnum | Stats = PrefixEnum.none
    non: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_ext_resource("res://ir/Prefix.gd", "Script")
        if isinstance(self.prefix, PrefixEnum):
            ability["prefix"] = PrefixEnum.to_int(self.prefix)
        elif isinstance(self.prefix, TypeEnum):
            ability["type"] = TypeEnum.to_int(self.prefix)
        elif isinstance(self.prefix, ColorEnum):
            ability["color"] = ColorEnum.to_int(self.prefix)
        elif isinstance(self.prefix, Stats):
            ability["stats"] = [self.prefix.power, self.prefix.health]
        ability["non"] = self.non
        return ability


class Suffix(BaseModel):
    suffix: SuffixEnum = SuffixEnum.none
    subj: Any = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_ext_resource("res://ir/Suffix.gd", "Script")
        ability["suffix"] = SuffixEnum.to_int(self.suffix)
        if isinstance(self.suffix, ZoneMatch):
            ability["zones"] = [z.to_godot(resource) for z in self.subj]
        elif self.suffix is not None:
            ability["subj"] = self.suffix.to_godot(resource)
        return ability


class BaseObject(BaseModel):
    def to_godot(self, resource: GDResource):
        pass


class ObjectMatch(BaseModel):
    objects: list[BaseObject] = []
    each: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_ext_resource("res://ir/Object.gd", "Script")
        ability["objects"] = [o.to_godot(resource) for o in self.objects]
        ability["each"] = self.each
        return ability


class PlayerMatch(BaseModel):
    player: PlayerEnum = PlayerEnum.none
    ref: Reference | ObjectMatch | None = None
    extra: NumberOrX | None = None  # TODO: implement player extra (target count etc)
    who_cant: bool = False


class ZoneMatch(BaseModel):
    zones: list[ZoneEnum] = []
    ref: PlayerMatch | None = None
    # Used for placement
    place: PlaceEnum | None = None
    random: bool = False


class Effect(BaseEffect):
    effects: list[BaseEffect] = []
    op: OperatorEnum = OperatorEnum.AND

    def to_godot(self, resource: GDResource):
        ability = resource.add_ext_resource("res://Effect.gd", "Script")
        ability["effects"] = [e.to_godot(resource) for e in self.effects]
        ability["optional"] = self.op == OperatorEnum.OPTIONAL
        return ability


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

    def to_godot(self, resource: GDResource):
        ability = resource.add_ext_resource("res://TriggeredAbility.gd", "Script")

        return ability


class ActivatedAbility(BaseModel):
    costs: list[ColorEnum | NumberOrX | Activation | ActionCost] = []
    effect: Effect

    def to_godot(self, resource: GDResource):
        ability = resource.add_ext_resource("res://ActivatedAbility.gd", "Script")
        ability["costs"] = [c.to_godot(resource) if isinstance(c, ActionCost) else c for c in self.costs]
        ability["effect"] = self.effect.to_godot(resource)
        return ability

AquiredAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility | ActionCost | Effect | Literal["this"]


def ability_to_godot(resource: GDResource, ability: AquiredAbilities | None = None):
    if ability is None:
        return None
    if isinstance(ability, BaseModel):
        return ability.to_godot(resource)
    # TODO: keyword to resource
    return str(ability)


class CardObject(BaseObject):
    ref: Reference = Reference.none
    type: TypeEnum = TypeEnum.none
    extra: NumberOrX = 0
    prefixes: list[Prefix] = []
    suffixes: list[Suffix] = []
    withwhat: AquiredAbilities | None = None
    without: KeywordEnum = KeywordEnum.none
    copies: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_ext_resource("res://ir/Card.gd", "Script")
        ability["ref"] = Reference.to_int(self.ref)
        ability["type"] = TypeEnum.to_int(self.type)
        ability["extra"] = encode_numberorx(self.extra)
        ability["prefixes"] = [p.to_godot(resource) for p in self.prefixes]
        ability["suffixes"] = [s.to_godot(resource) for s in self.suffixes]
        ability["withwhat"] = ability_to_godot(resource, self.withwhat)
        ability["without"] = KeywordEnum.to_int(self.without)
        ability["copies"] = self.copies
        return ability


class AbilityObject(BaseObject):
    ref: Reference | NumberOrX | None = None
    extra: NumberOrX = 0
    prefixes: list[Prefix] = []
    suffixes: list[Suffix] = []


class SubjEffect(BaseEffect):
    effects: list[BaseEffect] = []


class PlayerEffect(SubjEffect):
    subj: PlayerMatch = PlayerMatch(player=PlayerEnum.you)
    

class ObjectEffect(SubjEffect):
    subj: ObjectMatch = ObjectMatch(objects=[BaseObject(object=Reference.it)])


class CreateTokenEffect(BaseEffect):
    number: NumberOrX = 1
    stats: Stats = Stats()
    abilities: list[AquiredAbilities] = []


class DestroyEffect(BaseEffect):
    objects: ObjectMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_ext_resource("res://effects/DestroyEffect.gd", "Script")
        ability["objects"] = [o.to_godot(resource) for o in self.objects]
        return ability


class CopyEffect(BaseEffect):
    objects: ObjectMatch


class PlayEffect(BaseEffect):
    objects: ObjectMatch
    free: bool = False


class DrawEffect(BaseEffect):
    number: NumberOrX = 1


class DiscardEffect(BaseEffect):
    number: NumberOrX = 1
    objects: ObjectMatch


class SearchEffect(BaseEffect):
    number: NumberOrX = 1
    zones: ZoneMatch
    objects: ObjectMatch | None = None


class ShuffleEffect(BaseEffect):
    what: ZoneMatch | ObjectMatch | None = None
    zones: ZoneMatch


class CounterEffect(BaseEffect):
    objects: ObjectMatch


class ExtraTurnEffect(BaseEffect):
    number: NumberOrX = 1


class LookEffect(BaseEffect):
    number: NumberOrX = 1
    zones: ZoneMatch


class PutEffect(BaseEffect):
    objects: ObjectMatch
    into: ZoneMatch
    deactivated: bool = False
    second_objects: ObjectMatch | None = None
    second_into: ZoneMatch | None = None


class GainControlEffect(BaseEffect):
    objects: ObjectMatch
    until: Condition | None = None


class SwitchStatsEffect(BaseEffect):
    objects: ObjectMatch
    until: Condition | None = None


class AddEssenceEffect(BaseEffect):
    colors: list[str] = []
    amount: NumberOrX = 1


class ActivationEffect(BaseEffect):
    objects: ObjectMatch
    deactivate: bool = True


class SacrificeEffect(BaseEffect):
    objects: ObjectMatch


class PayessenceEffect(BaseEffect):
    costs: list[ColorEnum | NumberOrX]


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
    costs: list[ColorEnum | NumberOrX]
    more: bool = False
    foreach: ObjectMatch | None = None


class EntersAbility(BaseEffect):
    deactivate: bool = False
    control: PlayerMatch | Reference | None = None


class BecomesAbility(BaseEffect):
    what: list[ColorEnum | TypeEnum | Stats] = []
    additional: bool = False


class DealsAbility(BaseEffect):
    amount: NumberOrX | NumberDef = 1
    recipients: list[PlayerMatch | ObjectMatch | Reference] = []
    spread: bool = False


class Card(BaseModel):
    name: str = ''
    cost: list[ColorEnum | NumberOrX] = [0]
    types: list[TypeEnum] = []
    subtypes: list[str] = []
    abilities: list[AquiredAbilities] = []
    rule_texts: list[str] = []
    power: int = 1
    health: int = 1
    
    def __str__(self) -> str:
        costs = "}{".join([str(c) for c in self.cost])
        t = " ".join([t.capitalize() for t in self.types])
        if self.subtypes:
            t += " - " + " ".join([t.capitalize() for t in self.subtypes])
        a = "\n".join(self.rule_texts)
        return f"{self.name} {{{costs}}}\n{t}\n{a}\n{self.power}/{self.health}"

    def to_godot(self):
        resource = GDResource()
        card = resource.add_ext_resource("res://Card.gd", "Script")
        card["cost"] = self.cost
        card["types"] = [TypeEnum.to_int(t) for t in self.types]
        card["subtypes"] = self.subtypes
        card["abilities"] = [ability_to_godot(resource, a) for a in self.abilities]
        card["power"] = encode_numberorx(self.power)
        card["health"] = encode_numberorx(self.health)
        return resource
