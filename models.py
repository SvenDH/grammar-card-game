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
    white = "W"
    red = "R"
    green = "G"
    blue = "B"


class Activation(str, GrammarEnum):
    activate = "Q"
    deactivate = "T"


class TypeEnum(str, GrammarEnum):
    UNIT = "creature"
    SPELL = "sorcery"


class KeywordEnum(str, GrammarEnum):
    FLYING = "flying"
    SIEGE = "siege"
    POISON = "poison"


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
    them = "them"
    one = "one"
    your = "your"
    their = "their"
    one_of_them = "one of them"
    rest = "the rest"


class Reference(str, GrammarEnum):
    sac = "the sacrificed"
    anyof = "any of"
    the = "the"
    this = "this"
    that = "that"
    another = "another"
    chosen = "the chosen"
    atleast = "atleast"
    each = "each"
    all = "all"
    target = "target"
    exactly = "exactly"
    ormore = "or more"
    fewerthan = "fewer than"
    anynumberof = "any number of"
    upto = "up to"
    oneof = "one of"


class PrefixEnum(str, GrammarEnum):
    activated = "activated"
    token = "token"
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
    pass


class Prefix(BaseModel):
    prefix: PrefixEnum | TypeEnum | Stats
    non: bool = False


class Suffix(BaseModel):
    suffix: SuffixEnum
    subj: Any = None


class Condition(BaseModel):
    condition: ConditonEnum
    until: bool = False


class EssenceCosts(BaseModel):
    costs: list[ColorEnum | NumberOrX] = []


class Object(BaseModel):
    object: PureObject | TypeEnum | ObjectRef
    ref: Reference | NumberOrX | None = None
    prefixes: list[Prefix] = []
    suffix: Suffix | None = None
    type: TypeEnum | None = None
    without: KeywordEnum | None = None
    copyof: bool = False


class Objects(BaseModel):
    objects: list[Object] = []
    op: OperatorEnum | None = None
    each: bool = False


class Player(BaseModel):
    player: PlayerEnum
    ref: Reference | Objects | ObjectRef | None = None
    who_cant: bool = False


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


class ActivatedAbility(BaseModel):
    costs: list[EssenceCosts | Activation | ActionCost] = []
    effect: Effect


class Phase(BaseModel):
    ref: TurnQualifierEnum | ObjectRef | Player | None = None
    phase: PhaseEnum
    

class Trigger(BaseModel):
    trigger: TriggerEnum
    objects: Objects | Player | Phase | None = None


class TriggeredAbility(BaseModel):
    trigger: Trigger
    effect: Effect
    condition: Condition | None = None


AquiredAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility | ActionCost | Effect | Literal["this"]


class PlayerEffect(BaseEffect):
    subj: Player = Player(player=PlayerEnum.you)
    effects: list[BaseEffect] = []


class ObjectEffect(BaseEffect):
    subj: Object = Object(object=ObjectRef.it)
    effects: list[BaseEffect] = []


class CreateTokenEffect(BaseEffect):
    number: NumberOrX = 1
    stats: Stats = (1, 1)
    abilities: list[AquiredAbilities] = []


class DestroyEffect(BaseEffect):
    objects: Objects


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


class ModAbility(ObjectEffect):
    stats: Stats = (0, 0)
    foreach: Objects | None = None


class GetAbility(ObjectEffect):
    abilities: list[AquiredAbilities | ModAbility] = []
    until: Condition | None = None


class CantAbility(ObjectEffect):
    actions: list[ObjectActionEnum] = []
    until: Condition | None = None


class NoActivationAbility(ObjectEffect):
    moment: Phase


class LoseAbilitiesAbility(ObjectEffect):
    until: Condition | None = None


class CostsAbility(ObjectEffect):
    costs: EssenceCosts
    more: bool = False
    foreach: Objects | None = None


class EntersAbility(ObjectEffect):
    deactivate: bool = False
    control: Player | ObjectRef | None = None


class BecomesAbility(ObjectEffect):
    what: list[ColorEnum | TypeEnum | Stats] = []
    additional: bool = False


class Card(BaseModel):
    name: str = ''
    cost: list[ColorEnum | NumberOrX] = [0]
    type: TypeEnum = ''
    subtype: str | None = None
    abilities: list[AquiredAbilities] = []
    damage: int = 1
    health: int = 1


class CardInstance:
    card: Card
    mods: list = []
    health: int = 1


class PlayerState(BaseModel):
    deck: list[CardInstance] = []
    field: list[list[CardInstance]] = [[], [], [], [], [], [], [], []]
    pile: list[CardInstance] = []
    hand: list[CardInstance] = []
    life: int = 25
    subscribed: dict[str, list[CardInstance]] = {}

    @classmethod
    def from_cards(cls, cards: list[Card]):
        return cls(deck=[CardInstance(card=c) for c in cards])

    def draw(self, n: int = 1):
        for _ in range(n):
            self.hand.append(self.deck.pop())
    
    def discard(self, index: int = 0):
        self.pile.append(self.hand.pop(index))

    def place(self, from_index: int, to_index: int):
        card = self.hand.pop(from_index)
        card.health = card.card.health
        card.mods = []
        self.field[to_index].append(card)


class Game(BaseModel):
    playerstates: list[PlayerState]