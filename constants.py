from enum import Enum
from typing import Literal


NumberOrX = int | Literal["X"] | Literal["-X"] | Literal["that"]


class GrammarEnum(Enum):
    @classmethod
    def to_grammar(cls):
        notnones = [c for c in cls if c != ""]
        return " | ".join([f'( /[{v.value[0].lower()}{v.value[0].upper()}]/ "{v.value[1:]}")' for v in notnones])
    
    @classmethod
    def to_int(cls, value):
        if value is None:
            return 0
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
    item = "item"
    source = "source"
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
    none = ""
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
    none = ""
    turn = "turn"
    activation = "activation"
    draw = "draw step"
    play = "play phase"
    fight = "fight phase"
    cleanup = "cleanup"


class ObjectPhrase(str, GrammarEnum):
    blocked = "block"
    attacked = "attacks"
    targets = "targets"
    leaves = "leaves"
    dies = "dies"
    moveszone = "is put"
    whenenters = "enters"
    dealsdamage = "damage"


class TurnQualifierEnum(str, GrammarEnum):
    none = ""
    each = "each"
    this = "this"
    that = "that"
    the = "the"
