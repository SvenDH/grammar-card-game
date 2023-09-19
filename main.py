from enum import Enum
from typing import Literal, Any
from pydantic import BaseModel
from llama_cpp import Llama, LlamaGrammar

from lark import Lark, Tree, Token


NumberOrX = int | Literal["X"] | Literal["-X"] | Literal["that"]
Stats = tuple[NumberOrX, NumberOrX]

class ColorEnum(str, Enum):
    white = "W"
    red = "R"
    green = "G"
    blue = "B"


class Activation(str, Enum):
    activate = "Q"
    deactivate = "T"


class TypeEnum(str, Enum):
    UNIT = "creature"
    SPELL = "sorcery"

    @classmethod
    def to_grammar(cls):
        return " | ".join([f'( /[{v.value[0].lower()}{v.value[0].upper()}]/ "{v.value[1:]}")' for v in cls])


class KeywordEnum(str, Enum):
    FLYING = "flying"
    SIEGE = "siege"
    POISON = "poison"

    @classmethod
    def to_grammar(cls):
        return " | ".join([f'( /[{v.value[0].lower()}{v.value[0].upper()}]/ "{v.value[1:]}")' for v in cls])


class ObjectActionEnum(str, Enum):
    attack = "attack"
    block = "block"
    attackorblock = "attack or block"
    beblocked = "be blocked"
    becountered = "be countered"
    activateability = "activate abilities"


class ConditonEnum(str, Enum):
    playedwhen = "played when"
    yourturn = "your turn"
    notyourturn = "not your turn"
    compare = "number compare"
    playercond = "player condition"
    objectcond = "object condition"
    thisturn = "thisturn"


class ObjectRef(str, Enum):
    self = "~"
    it = "it"
    they = "they"
    them = "them"
    one = "one"
    your = "your"
    their = "their"
    one_of_them = "one of them"
    rest = "the rest"


class Reference(str, Enum):
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


class PrefixEnum(str, Enum):
    activated = "activated"
    token = "token"
    attacking = "attacking"
    blocking = "blocking"
    attackingorblocking = "attackingorblocking"


class SuffixEnum(str, Enum):
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


class PureObject(str, Enum):
    ability = "ability"
    token = "token"
    card = "card"
    copies = "copies"


class ZoneEnum(str, Enum):
    deck = "deck"
    discard = "discard"
    hand = "hand"
    field = "field"
    it = "it"


class OperatorEnum(str, Enum):
    AND = "and"
    OR = "or"
    XOR = "xor"
    OPTIONAL = "optional"


class PlaceEnum(str, Enum):
    bottom = "bottom"
    top = "top"


class PlayerEnum(str, Enum):
    opponent = "opponent"
    player = "player"
    you = "you"
    they = "they"
    owner = "owner"
    controller = "controller"
    defending = "defending"
    attacking = "attacking"


class TriggerEnum(str, Enum):
    whenplay = "whenplay"
    whengainlife = "whengainlife"
    whenloselife = "whengainlife"
    whendamaged = "whendamaged"
    endofturn = "endofturn"
    beginningofphase = "beginningofphase"


class PhaseEnum(str, Enum):
    turn = "turn"
    activation = "activation"
    draw = "draw step"
    play = "play phase"
    fight = "fight phase"
    cleanup = "cleanup"


class TurnQualifierEnum(str, Enum):
    each = "each"
    this = "this"
    that = "that"
    the = "the"


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


class BaseEffect(BaseModel):
    pass


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


class ObjectEffect(BaseEffect):
    subj: Object = Object(object=ObjectRef.it)


class CreateTokenEffect(PlayerEffect):
    number: NumberOrX = 1
    stats: Stats = (1, 1)
    abilities: list[AquiredAbilities] = []


class DestroyEffect(PlayerEffect):
    objects: Objects


class CopyEffect(PlayerEffect):
    objects: Objects


class PlayEffect(PlayerEffect):
    objects: Objects
    free: bool = False


class DrawEffect(PlayerEffect):
    number: NumberOrX = 1


class DiscardEffect(PlayerEffect):
    objects: Objects


class SearchEffect(PlayerEffect):
    zones: Zone
    objects: Objects | None = None


class ShuffleEffect(PlayerEffect):
    what: Zone | Objects | None = None
    zones: Zone


class CounterEffect(PlayerEffect):
    objects: Objects


class ExtraTurnEffect(PlayerEffect):
    turns: int = 1


class LookEffect(PlayerEffect):
    number: NumberOrX = 1
    zones: Zone


class PutEffect(PlayerEffect):
    objects: Objects
    into: Into
    deactivated: bool = False
    second_objects: Objects | None = None
    second_into: Into | None = None


class GainControlEffect(PlayerEffect):
    objects: Objects
    until: Condition | None = None


class SwitchHpDmgEffect(PlayerEffect):
    objects: Objects
    until: Condition | None = None


class AddEssenceEffect(PlayerEffect):
    colors: list[str] = []
    amount: NumberOrX = 1


class ActivationEffect(PlayerEffect):
    objects: Objects
    deactivate: bool = True


class SacrificeEffect(PlayerEffect):
    objects: Objects


class PayessenceEffect(PlayerEffect):
    costs: EssenceCosts


class PaylifeEffect(PlayerEffect):
    costs: NumberOrX


class MoveEffect(PlayerEffect):
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


def from_tree(tree: Tree | Token):
    if isinstance(tree, Token):
        t = str(tree)
        if t in list(ObjectRef):
            return ObjectRef(tree)
        return t
    
    match tree.data:
        case "essencecost":
            if isinstance(tree.children[0], Token):
                return EssenceCosts(costs=[from_tree(e) for e in tree.children])
            return EssenceCosts(costs=[from_tree(e) for e in tree.children[0].children])
        case "activationcost":
            if tree.children[0].data == "deactivatecost":
                return Activation.deactivate
            return Activation.activate
        case "referenceprefix":
            return from_tree(tree.children[0])
        case "pureobject":
            return from_tree(tree.children[0])
        case "object":
            r = from_tree(tree.children[0])
            if isinstance(r, (TypeEnum, PureObject)):
                return Object(object=r)
            return r
        case "selfref":
            return Object(object=ObjectRef.self)
        case "objects":
            op = None
            each = False
            objs = [from_tree(i) for i in tree.children]
            if len(objs) > 1:
                if objs[0] == Reference.each:
                    objs = objs[1:]
                    each = True
                else:
                    op = objs.pop(len(objs) - 2)
            return Objects(objects=objs, each=each, op=op)
        case "refobject":
            r = from_tree(tree.children[0])  # TODO: add more complex references
            if isinstance(r, tuple):
                return Object(
                    ref=r[0],
                    object=from_tree(tree.children[1])
                )
            return Object(ref=r, object=from_tree(tree.children[1]))
        case "specifiedobject":
            suffix = from_tree(tree.children[-1]) if tree.children[-1].data == "suffix" else None
            return Object(
                object=from_tree(tree.children[-2] if suffix else tree.children[-1]),
                suffix=suffix,
                prefixes=[from_tree(c) for c in tree.children if c.data == "prefix"]
            )
        case "prefix":
            if tree.children[0].data == "stats":
                return Prefix(prefix=from_tree(tree.children[0]))
            t = from_tree(tree.children[0])
            return Prefix(prefix=t[0], non=t[1])
        case "suffix":
            return from_tree(tree.children[0])
        case "playercontrol":
            return Suffix(
                suffix=SuffixEnum.control,
                subj=from_tree(tree.children[0])
            )
        case "playernocontrol":
            return Suffix(
                suffix=SuffixEnum.nocontrol,
                subj=from_tree(tree.children[0])
            )
        case "playerown":
            return Suffix(
                suffix=SuffixEnum.own,
                subj=from_tree(tree.children[0])
            )
        case "playernoown":
            return Suffix(
                suffix=SuffixEnum.noown,
                subj=from_tree(tree.children[0])
            )
        case "inzones":
            return Suffix(
                suffix=SuffixEnum.inzone,
                subj=[from_tree(c) for c in tree.children if isinstance(c, Tree) and c.data == "zones"]
            )
        case "fromzones":
            return Suffix(
                suffix=SuffixEnum.inzone,
                subj=[from_tree(tree.children[0])]
            )
        case "thattargets":
            return Suffix(
                suffix=SuffixEnum.targets,
                subj=from_tree(tree.children[0])
            )
        case "thattargetsonly":
            return Suffix(
                suffix=SuffixEnum.targetsonly,
                subj=from_tree(tree.children[0])
            )
        case "couldtarget":
            return Suffix(
                suffix=SuffixEnum.couldtarget,
                subj=from_tree(tree.children[0])
            )
        case "chosentype":
            return Suffix(
                suffix=SuffixEnum.chosentype,
                subj=(from_tree(tree.children[0]), from_tree(tree.children[0]))
            )
        case "activatedthisway":
            return Suffix(suffix=SuffixEnum.activatedthisway)
        case "deactivatedthisway":
            return Suffix(suffix=SuffixEnum.deactivatedthisway)
        case "amongthem":
            return Suffix(suffix=SuffixEnum.amongthem)
        case "youplay":
            return Suffix(suffix=SuffixEnum.youplay)
        case "possesion":
            return from_tree(tree.children[0])
        case "ability":
            return from_tree(tree.children[0])
        case "keywords":
            return [i.children[0].lower() for i in tree.children]
        case "activatedability":
            return [ActivatedAbility(
                costs=[from_tree(t) for t in tree.children[0].children],
                effect=from_tree(tree.children[1])
            )]
        case "triggeredability":
            return [TriggeredAbility(
                trigger=from_tree(tree.children[0]),
                effect=from_tree(tree.children[-1]),
                condition=from_tree(tree.children[1]) if len(tree.children) > 2 else None
            )]
        case "triggercondition":
            if tree.children[0].data == "endofturn":
                return Trigger(trigger=TriggerEnum.endofturn)
            elif tree.children[0].data == "beginningofphase":
                return Trigger(
                    trigger=TriggerEnum.beginningofphase, 
                    objects=from_tree(tree.children[0])
                )
            return from_tree(tree.children[1])
        case "whenyouplay":
            return Trigger(
                trigger=TriggerEnum.whenplay, 
                objects=from_tree(tree.children[0])
            )
        case "whengainlife":
            return Trigger(
                trigger=TriggerEnum.whengainlife, 
                objects=from_tree(tree.children[0])
            )
        case "whenloselife":
            return Trigger(
                trigger=TriggerEnum.whenloselife, 
                objects=from_tree(tree.children[0])
            )
        case "whendamaged":
            return Trigger(
                trigger=TriggerEnum.whendamaged, 
                objects=from_tree(tree.children[0])
            )
        case "moment":
            if tree.children:
                return Phase(
                    ref=from_tree(tree.children[0]),
                    phase=from_tree(tree.children[1])
                )
            return Phase(ref=ObjectRef.your, phase=PhaseEnum.fight)
        case "foreach":
            return from_tree(tree.children[0])
        case "mod":
            return ModAbility(
                stats=(
                    from_tree(tree.children[0])(from_tree(tree.children[1])),
                    from_tree(tree.children[2])(from_tree(tree.children[3]))
                ),
                foreach=from_tree(tree.children[4]) if len(tree.children) > 4 else None
            )
        case "beginningofphase":
            return from_tree(tree.children[1])
        case "phase":
            return from_tree(tree.children[0])
        case "turn":
            return PhaseEnum.turn
        case "activationphase":
            return PhaseEnum.activation
        case "drawphase":
            return PhaseEnum.draw
        case "playphase":
            return PhaseEnum.play
        case "fightphase":
            return PhaseEnum.fight
        case "cleanup":
            return PhaseEnum.cleanup
        case "turnqualifier":
            t = tree.children[0]
            if t.data == "each":
                return (TurnQualifierEnum.each, False)
            elif t.data == "this":
                return (TurnQualifierEnum.this, False)
            elif t.data == "that":
                return (TurnQualifierEnum.that, False)
            elif t.data == "the":
                return (TurnQualifierEnum.the, len(tree.children) > 1)
            return (from_tree(t), len(tree.children) > 1)
        case "extracosts":
            return ActionCost(costs=[from_tree(c) for c in tree.children[0].children])
        case "imperativescost":
            return ActionCost(costs=[from_tree(c) for c in tree.children])
        case "imperativecost":
            return from_tree(tree.children[0])
        case "acquiredability":
            return [i for c in tree.children for i in from_tree(c)] if tree.children else ["this"]
        case "tokenability":
            return from_tree(tree.children[0])
        case "effects":
            return from_tree(tree.children[0])
        case "may":
            return Effect(
                effects=[e for a in tree.children for e in from_tree(a)],
                op=OperatorEnum.OPTIONAL
            )
        case "composedeffect":
            return Effect(
                effects=[from_tree(c) for c in tree.children if isinstance(c, Tree) and c.data == "effect"],
                op=OperatorEnum.AND
            )
        case "effect":
            return from_tree(tree.children[0])
        case "imperative":
            return Effect(
                effects=[from_tree(tree.children[0])]
            )  # TODO: add for each, conditional and where X
        case "i":
            return from_tree(tree.children[0])
        case "objecteffect":
            p = from_tree(tree.children[1])
            p.subj = from_tree(tree.children[0])
            return p
        case "playereffect":
            p = from_tree(tree.children[1])
            p.subj = from_tree(tree.children[0])
            return p
        case "objectphrase":
            p = [from_tree(c) for c in tree.children if isinstance(c, Tree) and c.data == "op"]
            o = [from_tree(c) for c in tree.children if isinstance(c, Tree) and c.data == "opandorthen"]
            return Effect(effects=p, op=o[0] if o else None)  # TODO: add condition
        case "playerphrase":
            return Effect(
                effects=[from_tree(c) for c in tree.children if isinstance(c, Tree) and c.data == "pp"]
            )  # TODO: add for each
        case "hasability":
            return GetAbility(
                abilities=from_tree(tree.children[0]),
                until=from_tree(tree.children[1]) if len(tree.children) > 1 else None
            )
        case "getsability":
            m = [from_tree(c) for c in tree.children if c.data == "mod"]
            u = [from_tree(c) for c in tree.children if c.data == "until"]
            return GetAbility(
                abilities=from_tree(tree.children[0]) + m,
                until=u[0] if u else None
            )
        case "getsmod":
            m = [from_tree(c) for c in tree.children if c.data == "acquiredability"]
            u = [from_tree(c) for c in tree.children if c.data == "until"]
            return GetAbility(
                abilities=from_tree(tree.children[0]) + m,
                until=u[0] if u else None
            )
        case "objectcantdo":
            return CantAbility(
                actions=from_tree(tree.children[0]),
                until=from_tree(tree.children[1]) if len(tree.children) > 1 else None
            )
        case "noactivate":
            return NoActivationAbility(moment=from_tree(tree.children[0]))
        case "losesabilities":
            return LoseAbilitiesAbility(until=from_tree(tree.children[0]) if tree.children else None)
        case "costsless":
            return CostsAbility(
                costs=from_tree(tree.children[0]),
                foreach=from_tree(tree.children[1]) if len(tree.children) > 1 else None
            )
        case "costsmore":
            return CostsAbility(
                costs=from_tree(tree.children[0]),
                more=True,
                foreach=from_tree(tree.children[1]) if len(tree.children) > 1 else None
            )
        case "entersdeactivated":
            return EntersAbility(
                deactivate=True,
                control=from_tree(tree.children[0]) if tree.children else None
            )
        case "becomeswhat":
            return BecomesAbility(
                what=from_tree(tree.children[0]),
                additional=len(tree.children) > 1
            )
        case "objectcant":
            a = from_tree(tree.children[0])
            if not isinstance(a, tuple):
                a = (a, )
            return a
        case "into":
            if tree.children[0].data == "field":
                return Into(zones=[ZoneEnum.field])
            elif tree.children[0] == "zones":
                return Into(**from_tree(tree.children[0]))
            return Into(
                place=tree.children[0].data,
                zones=[from_tree(tree.children[1])],
                random=len(tree.children) > 2 and tree.children[2].data == "random"
            )
        case "zones":
            t = tree.children[0]
            if t.data == "it":
                return Zone(zones=[ZoneEnum.it])
            elif t.data == "field":
                return Zone(zones=[ZoneEnum.field])
            op = [c for c in tree.children if isinstance(c, Tree) and c.data == "op"]
            return Zone(
                ref=from_tree(t) if t.data == "possesion" else None,
                zones=[from_tree(i) for i in tree.children if i.data == "zone"],
                op=from_tree(op[0]) if op else None
            )
        case "zone":
            return from_tree(tree.children[0])
        case "orderedzone":
            return from_tree(tree.children[0])
        case "createtoken":
            return CreateTokenEffect(
                number=from_tree(tree.children[1]),
                stats=from_tree(tree.children[2]),
                abilities=from_tree(tree.children[3]) if len(tree.children) > 3 else []
            )
        case "destroy":
            return DestroyEffect(objects=from_tree(tree.children[1]))
        case "copy":
            return CopyEffect(objects=from_tree(tree.children[1]))
        case "play":
            return PlayEffect(
                objects=from_tree(tree.children[1]),
                free="free" in [c.data for c in tree.children if isinstance(c, Tree)]
            )
        case "draw":
            c = [t for t in tree.children if isinstance(t, Tree)]
            return DrawEffect(number=from_tree(c[0]) if c else 1)
        case "discard":
            return DiscardEffect(objects=from_tree(tree.children[1]))
        case "search":
            return SearchEffect(
                zones=from_tree(tree.children[1]),
                objects=from_tree(tree.children[2]) if len(tree.children) > 2 else None
            )
        case "shuffle":
            return ShuffleEffect(
                what=from_tree(tree.children[1]) if len(tree.children) > 2 else None,
                zones=from_tree(tree.children[-1])
            )
        case "counter":
            return CounterEffect(objects=from_tree(tree.children[1]))
        case "extraturn":
            return ExtraTurnEffect()
        case "look":
            return LookEffect(
                number=from_tree(tree.children[1]),
                zones=from_tree(tree.children[2])
            )
        case "put":
            objs = [c for c in tree.children if isinstance(c, Tree) and c.data == "objects"]
            intos = [c for c in tree.children if isinstance(c, Tree) and c.data == "into"]
            return PutEffect(
                objects=from_tree(objs[0]),
                into=from_tree(intos[0]),
                deactivated=len(tree.children) > 3 and tree.children[3].data == "deactivated",
                second_objects=from_tree(objs[1]) if len(objs) > 1 else None,
                second_into=from_tree(intos[1]) if len(intos) > 1 else None,
            )
        case "gaincontrol":
            return GainControlEffect(
                objects=from_tree(tree.children[1]),
                until=from_tree(tree.children[2]) if len(tree.children) > 2 else None
            )
        case "switchdmghp":
            return SwitchHpDmgEffect(
                objects=from_tree(tree.children[1]),
                until=from_tree(tree.children[2]) if len(tree.children) > 2 else None
            )
        case "addessence":
            a = [from_tree(c) for c in tree.children if isinstance(c, Tree) and c.data == "number"]
            return AddEssenceEffect(
                colors=[c.children[0] for c in tree.children if isinstance(c, Tree) and c.data == "esscolor"],
                amount=a[0] if a else 1
            )
        case "activate":
            return ActivationEffect(objects=from_tree(tree.children[1]), deactivate=False)
        case "deactivate":
            return ActivationEffect(objects=from_tree(tree.children[1]), deactivate=True)
        case "return":
            return MoveEffect(
                objects=from_tree(tree.children[1]),
                tozone=from_tree(tree.children[-1]),
                fromzone=from_tree(tree.children[-2]) if len(tree.children) > 3 else None,
            )
        case "sacrifice":
            return SacrificeEffect(objects=from_tree(tree.children[1]))
        case "payessence":
            return PayessenceEffect(costs=from_tree(tree.children[1]))
        case "paylife":
            return PaylifeEffect(costs=from_tree(tree.children[1]))
        case "players":
            p = from_tree(tree.children[0])
            if isinstance(p, tuple):
                return Player(
                    player=p[1],
                    ref=p[0],
                    who_cant=len(tree.children) > 1
                )
            return Player(player=p, who_cant=len(tree.children) > 1)
        case "p":
            t = tree.children[0]
            if t.data == "defending":
                return PlayerEnum.defending
            elif t.data == "attacking":
                return PlayerEnum.attacking
            elif t.data == "itspossesion":
                return (from_tree(tree.children[0], from_tree(tree.children[1])))
            return from_tree(t)
        case "owners":
            return PlayerEnum.owner
        case "controllers":
            return PlayerEnum.controller
        case "itspossesion":
            return from_tree(tree.children[0])
        case "refplayer":
            return (from_tree(tree.children[0]), from_tree(tree.children[1]))
        case "pureplayer":
            return from_tree(tree.children[0])
        case "opponent":
            return PlayerEnum.opponent
        case "player":
            return PlayerEnum.player
        case "condition":
            return from_tree(tree.children[0])
        case "playedwhen":
            return PlayedCondition(
                condition=ConditonEnum.playedwhen,
                object=from_tree(tree.children[0]),
                duration=from_tree(tree.children[1])
            )
        case "compare":
            return NumberCondition(
                condition=ConditonEnum.compare,
                number=from_tree(tree.children[0]),
                compare=from_tree(tree.children[1])
            )
        case "playercondition":
            return PlayerCondition(
                condition=ConditonEnum.playercond,
                player=from_tree(tree.children[0]),
                phrase=from_tree(tree.children[1])
            )
        case "objectcondition":
            return ObjectCondition(
                condition=ConditonEnum.objectcond,
                object=from_tree(tree.children[0]),
                phrase=from_tree(tree.children[1])
            )
        case "pc":
            return from_tree(tree.children[0])
        case "oc":
            return from_tree(tree.children[0])
        case "pp":
            return from_tree(tree.children[0])
        case "op":
            return from_tree(tree.children[0])
        case "yourturn":
            return Condition(condition=ConditonEnum.yourturn)
        case "notyourturn":
            return Condition(condition=ConditonEnum.notyourturn)
        case "duration":
            return from_tree(tree.children[0])
        case "thisturn":
            return Condition(condition=ConditonEnum.thisturn)
        case "until":
            if len(tree.children):
                c = from_tree(tree.children[0])
                c.until = True
                return c
            return Condition(condition=ConditonEnum.thisturn)
        case "attack":
            return ObjectActionEnum.attack
        case "block":
            return ObjectActionEnum.block
        case "attackorblock":
            return ObjectActionEnum.attack, ObjectActionEnum.block
        case "beblocked":
            return ObjectActionEnum.beblocked
        case "becountered":
            return ObjectActionEnum.becountered
        case "activateability":
            return ObjectActionEnum.activateability
        case "activated":
            return (PrefixEnum.activated, False)
        case "deactivated":
            return (PrefixEnum.activated, True)
        case "token":
            return (PrefixEnum.token, False)
        case "nontoken":
            return (PrefixEnum.token, True)
        case "attacking":
            return (PrefixEnum.attacking, False)
        case "blocking":
            return (PrefixEnum.blocking, False)
        case "attackingorblocking":
            return (PrefixEnum.attackingorblocking, False)
        case "nontype":
            return (from_tree(tree.children[1], True))
        case "stats":
            return (from_tree(tree.children[0]), from_tree(tree.children[1]))
        case "you":
            return PlayerEnum.you
        case "they":
            return PlayerEnum.they
        case "copies":
            return PureObject.copies
        case "tokencard":
            return PureObject.token
        case "abilityref":
            return PureObject.ability
        case "typecard":
            if tree.children:
                return TypeEnum(tree.children[0].children[0])
            return PureObject.card
        case "hand":
            return ZoneEnum.hand
        case "deck":
            return ZoneEnum.deck
        case "discardzone":
            return ZoneEnum.discard
        case "refsacrificed":
            return Reference.sac
        case "anyof":
            return Reference.anyof
        case "the":
            return Reference.the
        case "this":
            return Reference.this
        case "that":
            return Reference.that
        case "each":
            return Reference.each
        case "all":
            return Reference.all
        case "another":
            return Reference.another
        case "chosen":
            return Reference.chosen
        case "anynumberof":
            return Reference.anynumberof
        case "oneof":
            return Reference.oneof
        case "atleast":
            return (Reference.atleast, from_tree(tree.children[1]))
        case "exactly":
            return (Reference.exactly, from_tree(tree.children[1]))
        case "ormore":
            return (Reference.ormore, from_tree(tree.children[0]))
        case "fewerthan":
            return (Reference.fewerthan, from_tree(tree.children[1]))
        case "upto":
            return (Reference.upto, from_tree(tree.children[1]))
        case "counted":
            return [from_tree(c) for c in tree.children]
        case "target":
            return tuple([from_tree(c) for c in tree.children] + [Reference.target])
        case "countable":
            return from_tree(tree.children[0])
        case "reference":
            return from_tree(tree.children[0])
        case "opandorthen":
            return from_tree(tree.children[0])
        case "opandor":
            return from_tree(tree.children[0])
        case "its":
            return ObjectRef.their
        case "their":
            return ObjectRef.their
        case "your":
            return ObjectRef.your
        case "and":
            return OperatorEnum.AND
        case "or":
            return OperatorEnum.XOR
        case "then":
            return OperatorEnum.AND
        case "andor":
            return OperatorEnum.OR
        case "smallnumber":
            return tree.children[0]
        case "number":
            return from_tree(tree.children[0])
        case "numberorx":
            return from_tree(tree.children[0])
        case "numberorxorthat":
            return from_tree(tree.children[0])
        case "a":
            return 1
        case "one":
            return 1
        case "two":
            return 2
        case "three":
            return 3
        case "four":
            return 4
        case "five":
            return 5
        case "six":
            return 6
        case "seven":
            return 7
        case "eight":
            return 8
        case "nine":
            return 9
        case "ten":
            return 10
        case "x":
            return "X"
        case "thatmany":
            return "that"
        case "plusminus":
            return (lambda x: -x if isinstance(x, int) else "-" + x) if tree.children[0] == "-" else (lambda x: x)
        case _:
            print(tree.data)
            return ""


class Card(BaseModel):
    name: str = ''
    cost: list[ColorEnum | NumberOrX] = [0]
    type: TypeEnum = ''
    subtype: str | None = None
    abilities: list[AquiredAbilities] = []
    damage: int = 1
    health: int = 1
    
    @classmethod
    def from_tree(cls, tree):
        types = tree.children[2].children[0].children
        return cls(
            cost=[from_tree(c.children[0]) for c in tree.children[1].children],
            type=types[0].lower(),
            subtype=types[1].value if len(types) > 1 else None,
            abilities=[i for a in tree.children[3].children for i in from_tree(a)],
            damage=from_tree(tree.children[4].children[0]),
            health=from_tree(tree.children[4].children[1]),
        )


class Parser:
    def __init__(self, grammar: str, debug: bool = True) -> None:
        self.grammar = grammar
        self.lark = Lark(grammar.format(name=f'"~"', types=TypeEnum.to_grammar(), keywords=KeywordEnum.to_grammar()), start="root", debug=debug)
        self.debug = debug

    def parse(self, card: str, name: str | None = None):
        if name is None:
            name = " ".join(card.split("\n", 1)[0].split(" ")[:-1])
        t = self.lark.parse(card.split("\n\n", 1)[0].replace(name, "~"))
        c = Card.from_tree(t)
        c.name = name
        return c


class Generator:
    def __init__(self, model_path: str, grammar: str, temperature: float = 1.0, debug: bool = True) -> None:
        self.temperature = temperature
        self.model = Llama(
            model_path,
            seed=-1,
            n_ctx=512,
            n_gpu_layers=128,
            n_batch=512,
            f16_kv=True,
            logits_all=False,
            vocab_only=False,
            use_mlock=False,
        )
        self.parser = Parser(grammar, debug)
        self.name_grammar = LlamaGrammar.from_string(r'root ::= [A-Z][a-z]*(" " [A-Z][a-z]*)* " {"')

    def generate(self, prompt: str, name: str | None = None):
        if name is None:
            result = self.model(prompt=prompt, grammar=self.name_grammar, temperature=self.temperature)
            name = result["choices"][0]["text"].strip(" {")
        
        g = self.parser.grammar.format(
            name=f'"{name}"',
            types=TypeEnum.to_grammar(),
            keywords=KeywordEnum.to_grammar()
        )
        g = g.replace(" /", " ").replace("/ ", " ").replace("/\n", "\n").replace("\n|", " |").replace(": ", " ::= ")
        g = LlamaGrammar.from_string(g)
        result = self.model(
            prompt=prompt,
            grammar=g,
            temperature=self.temperature,
            max_tokens=256
        )
        return result["choices"][0]["text"]


grammar_str = open("grammars/game.lark", "r").read()
parser = Parser(grammar_str)

card = parser.parse("""Soldier {R}{1}
Creature
Flying, Siege
{2}: Create a 2/2 token with "Flying" and "Siege"
{1}: Play creature cards without paying essence
{T}: Draw a card, then you draw a card for each creature card
{Q}: Destroy target card
1/1""")

#print(card)
#card = parser.parse("""Jacks Steadfast Pendant {W}{B}
#Creature
#{2}: Attacking creature cards in your hand get -3/-3 until end of turn
#{B}: Attacking creature cards in your deck get -2/-2 until end of turn
#{1}, Sacrifice Jacks Steadfast Pendant: Draw two cards, then each player discards two cards, exactly one at least one creature card, tokens, they or the other creature and loses all abilities
#2/0""")

#card = parser.parse("""Looking Glass {B}{1}
#Sorcery
#Look at the top five cards of your deck. If you control more creatures than each other player, put two of those cards into your hand. Otherwise, put one of them into your hand. Then put the rest on the bottom of your library in any order.
#0/0""")

#print(card)

llm = Generator(
    model_path="C:\\Users\\denha\\Bureaublad\\oobabooga\\text-generation-webui\\models\\llama-2-7b-chat.ggmlv3.q4_K_M.bin",
    grammar=grammar_str,
    temperature=10.0
)

prompt = """Soldier {R}{1}
Creature - Human
1/1

Looking Glass {B}
Sorcery
Look at the top five cards of your deck. If you control more creatures than each other player, put two of those cards into your hand. Otherwise, put one of them into your hand. Then put the rest on the bottom of your library in any order.
0/0

Wizard {B}{2}
Creature
{T}: Wizard deals 1 damage to any target
1/2

Knight {R}{2}
Creature
Siege
2/2

Crackleburr {1}{R}{B}
Creature — Elemental
{R}{B}, {T}, Tap two untapped red creatures you control: Crackleburr deals 3 damage to any target.
{R}{B}, {Q}, Untap two tapped blue creatures you control: Return target creature to its owner's hand. ({Q} is the untap symbol.)
2/2

Advisor {W}{1}
Creature
{T}: Activate any target
0/2

Dark Council {B}{3}
Creature
Flying, Siege
{2}: Create a 2/2 token with "Flying" and "Siege"
{1}: Play creature cards without paying essence
{T}: Draw a card, then you draw a card for each creature card
{Q}: Destroy target card
1/1

"""
output = llm.generate(prompt)
print(output)
print(parser.parse(output))