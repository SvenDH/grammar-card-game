from enum import Enum
from typing import Literal
from pydantic import BaseModel
from llama_cpp import Llama, LlamaGrammar

from lark import Lark, Tree, Token


NumberOrX = int | Literal["X"] | Literal["that"]


class Essence(str, Enum):
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


class ConditonEnum(str, Enum):
    playedwhen = "played when"
    yourturn = "your turn"
    notyourturn = "not your turn"
    compare = "number compare"
    playereffect = "player effect"
    objecteffect = "object effect"


class BaseEffect(BaseModel):
    pass


class Condition(BaseModel):
    condition: ConditonEnum


class EssenceCosts(BaseModel):
    costs: list[Essence | NumberOrX] = []


class ImperativeCost(BaseModel):
    cost: list[BaseEffect] = []


class ObjectRef(str, Enum):
    self = "~"
    it = "it"
    they = "they"
    them = "them"
    one = "one"
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
    a = "a"
    target = "target"
    exactly = "exactly"
    ormore = "or more"
    fewerthan = "fewer than"
    anynumberof = "any number of"
    upto = "up to"
    oneof = "one of"


class Prefix(str, Enum):
    activated = "activated"
    deactivated = "deactivated"


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


class OwnerEnum(str, Enum):
    your = "your"
    their = "their"


class PlaceEnum(str, Enum):
    bottom = "bottom"
    top = "top"


class PlayerEnum(str, Enum):
    opponent = "opponent"
    player = "player"
    you = "you"
    they = "they"
    owner = "owner"
    defending = "defending"
    attacking = "attacking"


class Player(BaseModel):
    player: PlayerEnum
    who_cant: bool = False


class Zone(BaseModel):
    ref: OwnerEnum | Player | None = None
    zones: list[ZoneEnum] = []
    op: OperatorEnum | None = None


class Into(Zone):
    place: PlaceEnum | None = None
    random: bool = False


class Object(BaseModel):
    object: PureObject | TypeEnum | ObjectRef
    ref: Reference | NumberOrX | None = None
    type: TypeEnum | None = None
    without: KeywordEnum | None = None
    copyof: bool = False


class Objects(BaseModel):
    objects: list[Object]
    op: OperatorEnum | None = None
    each: bool = False


class Effect(BaseModel):
    effects: list[BaseEffect] = []
    optional: bool = False


class PlayedCondition(Condition):
    object: Objects
    duration: str   # TODO: implement duration


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
    costs: list[EssenceCosts | Activation | ImperativeCost]
    effect: Effect


class TriggerEnum(BaseModel):
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


class Phase(BaseModel):
    ref: TurnQualifierEnum | OwnerEnum | Player | None = None
    phase: PhaseEnum
    

class Trigger(BaseModel):
    trigger: TriggerEnum
    objects: Objects | Player | Phase | None = None


class TriggeredAbility(BaseModel):
    trigger: Trigger
    effect: Effect
    condition: Condition | None = None


TokenAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility
AquiredAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility | ImperativeCost | Effect


class CreateTokenEffect(BaseEffect):
    number: NumberOrX = 1
    damage: NumberOrX = 1
    health: NumberOrX = 1
    abilities: list[TokenAbilities] = []


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


class ReturnEffect(BaseEffect):
    objects: Objects
    tozone: Zone
    fromzone: Zone | None = None


class SacrificeEffect(BaseEffect):
    objects: Objects


class PayessenceEffect(BaseEffect):
    costs: EssenceCosts


class PaylifeEffect(BaseEffect):
    costs: NumberOrX


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
            return Phase(ref=OwnerEnum.your, phase=PhaseEnum.fight)
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
            if tree.children[0].data == "each":
                return (TurnQualifierEnum.each, False)
            elif tree.children[0].data == "this":
                return (TurnQualifierEnum.this, False)
            elif tree.children[0].data == "that":
                return (TurnQualifierEnum.that, False)
            elif tree.children[0].data == "the":
                return (TurnQualifierEnum.the, len(tree.children) > 1)
            return (from_tree(tree.children[0]), len(tree.children) > 1)
        case "extracosts":
            return ImperativeCost(costs=[from_tree(c) for c in tree.children[0].children])
        case "imperativescost":
            return ImperativeCost(costs=[from_tree(c) for c in tree.children])
        case "imperativecost":
            return from_tree(tree.children[0])
        case "effects":
            if tree.children[0].data == "may":
                return Effect(
                    effects=[e for a in tree.children[0].children for e in from_tree(a)],
                    optional=True
                )
            return Effect(
                effects=[e for a in tree.children for e in from_tree(a)],
                optional=False
            )
        case "composedeffect":
            return [e for c in tree.children for e in from_tree(c)]
        case "effect":
            return from_tree(tree.children[0])
        case "imperatives":
            return from_tree(tree.children[0])
        case "imperative":
            return [from_tree(tree.children[0])]
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
            if tree.children[0].data == "it":
                return Zone(zones=[ZoneEnum.it])
            elif tree.children[0].data == "field":
                return Zone(zones=[ZoneEnum.field])
            op = [i for i in tree.children if i.data == "op"]
            return Zone(
                ref=from_tree(tree.children[0]) if tree.children[0].data == "possesion" else None,
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
                damage=from_tree(tree.children[2].children[0]),
                health=from_tree(tree.children[2].children[1]),
                abilities=[i for a in tree.children[3].children for i in from_tree(a)]
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
            objs = [c for c in tree.children if c.data == "objects"]
            intos = [c for c in tree.children if c.data == "into"]
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
                colors=[c.children[0] for c in tree.children if isinstance(c, Tree) and c.data == "colort"],
                amount=a[0] if a else 1
            )
        case "activate":
            return ActivationEffect(objects=from_tree(tree.children[1]), deactivate=False)
        case "deactivate":
            return ActivationEffect(objects=from_tree(tree.children[1]), deactivate=True)
        case "return":
            return ReturnEffect(
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
        case "condition":
            t = tree.children[0]
            if t == "playedwhen":
                return PlayedCondition(
                    condition=ConditonEnum.playedwhen,
                    object=from_tree(t.children[0]),
                    duration=from_tree(t.children[1])
                )
            if t == "yourturn":
                return Condition(condition=ConditonEnum.yourturn)
            elif t == "notyourturn":
                return Condition(condition=ConditonEnum.notyourturn)
            elif t == "compare":
                return NumberCondition(
                    condition=ConditonEnum.compare,
                    number=from_tree(t.children[0]),
                    compare=from_tree(t.children[1])
                )
            elif t == "playereffect":
                return PlayerCondition(
                    condition=ConditonEnum.playereffect,
                    player=from_tree(t.children[0]),
                    phrase=from_tree(t.children[1])
                )
            elif t == "objecteffect":
                return ObjectCondition(
                    condition=ConditonEnum.objecteffect,
                    object=from_tree(t.children[0]),
                    phrase=from_tree(t.children[1])
                )
        case "until":
            return Condition()  # TODO: implement until
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
        case "atleast":
            return Reference.atleast
        case "chosen":
            return Reference.chosen
        case "anynumberof":
            return Reference.anynumberof
        case "oneof":
            return Reference.oneof
        case "exactly":
            return (Reference.exactly, from_tree(tree.children[0]))
        case "ormore":
            return (Reference.ormore, from_tree(tree.children[0]))
        case "fewerthan":
            return (Reference.fewerthan, from_tree(tree.children[0]))
        case "upto":
            return (Reference.upto, from_tree(tree.children[0]))
        case "counted":
            return [from_tree(c) for c in tree.children]
        case "target":
            return tuple([from_tree(c) for c in tree.children] + [Reference.target])
        case "countable":
            return from_tree(tree.children[0])
        case "reference":
            return from_tree(tree.children[0])
        case "op":
            return from_tree(tree.children[0])
        case "your":
            return OwnerEnum.your
        case "their":
            return OwnerEnum.their
        case "and":
            return OperatorEnum.AND
        case "or":
            return OperatorEnum.XOR
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
        case _:
            print(tree.data)
            return ""


class Card(BaseModel):
    name: str = ''
    cost: list[Essence | NumberOrX] = [0]
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
        t = self.lark.parse(card.replace(name, "~"))
        c = Card.from_tree(t.children[0])
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


card = parser.parse("""Graverobber {B}{R}{2}
Creature
{T}: Destroy Graverobber and target card
{B}, Sacrifice Graverobber: Return target creature card from your deck or hand to the field, and add 3 essence of any one color unless you've played an ability this turn
0/1""")

#print(card)

llm = Generator(
    model_path="C:\\Users\\denha\\Bureaublad\\oobabooga\\text-generation-webui\\models\\llama-2-7b-chat.ggmlv3.q4_K_M.bin",
    grammar=grammar_str,
    temperature=2.0
)

prompt = """Soldier {R}{1}
Creature - Human
1/1

Wizard {B}{2}
Creature
{T}: Deals 1 damage to any target
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

"""
output = llm.generate(prompt)
print(output)
print(parser.parse(output))