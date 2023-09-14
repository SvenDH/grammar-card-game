from enum import Enum
from typing import Literal
from pydantic import BaseModel
from llama_cpp import Llama, LlamaGrammar

from lark import Lark, Token


NumberOrX = int | Literal["X"]


class Essence(str, Enum):
    white = "W"
    red = "R"
    green = "G"
    blue = "B"


class Activation(str, Enum):
    activate = "Q"
    deactivate = "T"


class TypeEnum(str, Enum):
    UNIT = 'creature'
    SPELL = 'sorcery'

    @classmethod
    def to_grammar(cls):
        return " | ".join([f'( /[{v.value[0].lower()}{v.value[0].upper()}]/ "{v.value[1:]}")' for v in cls])


class KeywordEnum(str, Enum):
    FLYING = 'flying'
    SIEGE = 'siege'
    POISON = 'poison'

    @classmethod
    def to_grammar(cls):
        return " | ".join([f'( /[{v.value[0].lower()}{v.value[0].upper()}]/ "{v.value[1:]}")' for v in cls])


def get_number(tree):
    if isinstance(tree, Token):
        return str(tree)
    match tree.data:
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
        case "smallnumber":
            return tree.children[0]
        case "number":
            return get_number(tree.children[0])
        case "numberorx":
            return get_number(tree.children[0])
        case "numberorxorthat":
            return get_number(tree.children[0])
        case _:
            return 1


class EssenceCosts(BaseModel):
    costs: list[Essence | NumberOrX]


class ImperativeCost(BaseModel):
    costs: list[str] = []
    
    @classmethod
    def from_tree(cls, tree):
        return cls(costs=[])


class Trigger(BaseModel):
    conditions: list[str] = []
    
    @classmethod
    def from_tree(cls, tree):
        return cls(conditions=[])


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


class Prefix(str, Enum):
    activated = "activated"
    deactivated = "deactivated"



class PureObject(str, Enum):
    ability = "ability"
    token = "token"
    card = "card"


class Object(BaseModel):
    referenceprefix: Reference
    object: PureObject
    type: TypeEnum | None = None
    without: KeywordEnum | None = None
    copyof: bool = False


class Objects(BaseModel):
    objects: list[str]

    @classmethod
    def from_tree(cls, tree):
        print([i for i in tree.children])
        print(tree.data)
        match tree.data:
            case "NAME":
                return ObjectRef.self
            case "refobject":
                return cls.from_tree(tree.children[0])
            case "object":
                return cls.from_tree(tree.children[0])
            case "objects":
                return cls(
                    objects=[cls.from_tree(i) for i in tree.children]
                )


class Effect(BaseModel):
    effects: list['Abilities'] = []
    optional: bool = False
    
    @classmethod
    def get_effect(cls, tree):
        match tree.data:
            case "composedeffect":
                return [e for c in tree.children for e in cls.get_effect(c)]
            case "effect":
                return cls.get_effect(tree.children[0])
            case "imperatives":
                return cls.get_effect(tree.children[0])
            case "imperative":
                return cls.get_effect(tree.children[0])
            case "createtoken":
                return [CreateTokenEffect.from_tree(tree)]
            case "destroy":
                return [DestroyEffect.from_tree(tree)]
            case _:
                return []

    @classmethod
    def from_tree(cls, tree):
        return cls(
            effects=[e for a in tree.children for e in cls.get_effect(a)],
            optional=tree.children[0].data == "may"
        )


class Ability(BaseModel):

    @classmethod
    def from_tree(cls, tree):
        t = tree.children[0].data
        c = tree.children[0]
        match t:
            case "keywords":
                return [i.children[0].lower() for i in c.children]
            case "activated":
                return [ActivatedAbility.from_tree(c)]
            case "triggered":
                return [TriggeredAbility.from_tree(c)]
            case "extracosts":
                return [ImperativeCost.from_tree(c)]
            case "effects":
                return [Effect.from_tree(c)]
            case _:
                raise Exception(f"Unexpected ability type {t}")


class ActivatedAbility(Ability):
    costs: list[EssenceCosts | Activation | ImperativeCost]
    effect: Effect
    
    @staticmethod
    def get_cost(tree):
        match tree.data:
            case "essencecost":
                if isinstance(tree.children[0], Token):
                    return EssenceCosts(costs=[get_number(e) for e in tree.children])
                else:
                    return EssenceCosts(costs=[get_number(e) for e in tree.children[0].children])
            case "activationcost":
                if tree.children[0].data == "deactivatecost":
                    return Activation.deactivate
                else:
                    return Activation.activate
            case "imperativescost":
                return ImperativeCost.from_tree(tree)
            case _:
                raise Exception(f"Unexpected cost {tree.data}")

    @classmethod
    def from_tree(cls, tree):
        return cls(
            costs=[cls.get_cost(t) for t in tree.children[0].children],
            effect=Effect.from_tree(tree.children[1])
        )


class TriggeredAbility(Ability):
    trigger: Trigger
    effect: Effect
    
    @classmethod
    def from_tree(cls, tree):
        return cls(
            trigger=Trigger.from_tree(tree.children[0]),
            effect=Effect.from_tree(tree.children[1])
        )

TokenAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility
AquiredAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility | ImperativeCost | Effect


class CreateTokenEffect(BaseModel):
    number: NumberOrX = 1
    damage: NumberOrX
    health: NumberOrX
    abilities: list[TokenAbilities] = []

    @classmethod
    def from_tree(cls, tree):
        return cls(
            number=get_number(tree.children[1]),
            damage=get_number(tree.children[2].children[0]),
            health=get_number(tree.children[2].children[1]),
            abilities=[i for a in tree.children[3].children for i in Ability.from_tree(a)]
        )


class DestroyEffect(BaseModel):
    objects: Objects

    @classmethod
    def from_tree(cls, tree):
        return cls(
            objects=Objects.from_tree(tree.children[1])
        )


Abilities = CreateTokenEffect | DestroyEffect
Effect.update_forward_refs()

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
            cost=[get_number(c.children[0]) for c in tree.children[1].children],
            type=types[0].lower(),
            subtype=types[1].value if len(types) > 1 else None,
            abilities=[i for a in tree.children[3].children for i in Ability.from_tree(a)],
            damage=get_number(tree.children[4].children[0]),
            health=get_number(tree.children[4].children[1]),
        )


class Parser:
    def __init__(self, grammar: str, debug: bool = True) -> None:
        self.grammar = grammar
        self.debug = debug

    def parse(self, card: str, name: str | None = None):
        if name is None:
            name = " ".join(card.split("\n", 1)[0].split(" ")[:-1])
        g = Lark(self.grammar.format(name=f'"{name}"', types=TypeEnum.to_grammar(), keywords=KeywordEnum.to_grammar()), start="root", debug=self.debug)
        t = g.parse(card)
        card = Card.from_tree(t)
        card.name = name
        return card


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
        g = self.parser.grammar.format(name=f'"{name}"', types=TypeEnum.to_grammar(), keywords=KeywordEnum.to_grammar())
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
{T}: Draw a card, then you draw an cards for each creature card
{Q}: Destroy target card
1/1""")

#print(card)


card = parser.parse("""Graverobber {B}{R}{2}
Creature
{B}, Sacrifice Graverobber: Return target creature card from your deck or hand to the field, and add 3 essence of any one color unless you've played an ability this turn
0/1""")

#print(card)

#llm = Generator(
#    model_path="C:\\Users\\denha\\Bureaublad\\oobabooga\\text-generation-webui\\models\\llama-2-7b-chat.ggmlv3.q4_K_M.bin",
#    grammar=grammar_str,
#    temperature=2.0
#)

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
#output = llm.generate(prompt)
#print(output)
#print(parser.parse(output))