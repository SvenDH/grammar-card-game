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
                print(tree.children[3].children)
                return [CreateTokenEffect(
                    number=get_number(tree.children[1]),
                    damage=get_number(tree.children[2].children[0]),
                    health=get_number(tree.children[2].children[1]),

                )]
            case "destroy":
                return []
            case _:
                return []

    @classmethod
    def from_tree(cls, tree):
        #print(tree.children[0].children)
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
    with_abilities: list[TokenAbilities] = []

    @classmethod
    def from_tree(cls, tree):
        return cls(
            number=1,
            damage=1,
            health=1,
            with_abilities=[]
        )

Abilities = CreateTokenEffect
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

grammar_str = r'''
root: name " " cardcosts "\n" types "\n" abilities stats
name: {name} 
types: maintype (" - " subtype)?
maintype: TYPE
subtype: /[ a-zA-Z]+/
stats: numberorx "/" numberorx

cardcosts: essencecost
abilitycosts: essencecost ", " activationcost ", " imperativescost | activationcost ", " imperativescost | essencecost ", " imperativescost | essencecost ", " activationcost | activationcost | essencecost | imperativescost
essencecost: ("{{" COLOR "}}")* ("{{" numberorx "}}") | ("{{" COLOR "}}")+ | "{{0}}"
activationcost: activatecost | deactivatecost
deactivatecost: "{{T}}"
activatecost: "{{Q}}"

abilities: (ability "\n")*
ability: keywords | activated | triggered | extracosts | effects
keywords: keyword (", " keyword)*
keyword: KEYWORD
activated: abilitycosts ":" " " effects
extracosts: "Extra cost:" " " imperativescost
acquiredability: "\"" ability "\"" (" and \"" ability "\"")* | "this ability"
imperativescost: imperativecost (", " imperativecost)*
imperativecost: return | discard | sacrifice | paylife

triggered: triggerconditions ", " intervening? effects
triggerconditions: /[wW]/ ("hen " | "henever ") triggercondition | endofturn | beginningofphase
triggercondition: whenyouplay | whengainlife | whendamaged
whenyouplay: "you play " objects
whengainlife: players " gain" "s"? " life"
whendamaged: objects " is dealt damage"
intervening: "if " condition ", "

condition: playedwhen | yourturn | notyourturn | compare
playedwhen: "you've played " objects " " when
compare: numberdefinition " is " numbericalcompare

effects: composedeffect | may
may: ( /[yY]/ "ou ")? "may " imperatives (". " ("If" | "When") " you do, " composedeffect)?
composedeffect: effect (", " (("then" | "and")? " ")? effect)*
effect: imperatives | objecteffect | playereffect
objecteffect: objects " " objectphrases
playereffect: players " " playerphrases

imperatives: imperative (" for each " pureobject)? (", where X is " numberdefinition)? (" unless " condition)?
imperative: createtoken | destroy | copy | play | search | draw | shuffle | counter | activate | deactivate | extraturn | look | put | gaincontrol | switchdmghp | addmana | return | discard | sacrifice | payessence | paylife

createtoken: /[cC]/ "reate " number " " stats (" token" | " tokens") (" with " acquiredability)?
destroy: /[dD]/ "estroy " objects
copy: /[cC]/ "opy " objects
play: /[pP]/ "lay" "s"? " " objects (" without paying essence")?
search: /[sS]/ "earch " zone (" for " objects)?
draw: ( /[yY]/ "ou ")? /[dD]/ ("raw" | "raws") " " ("a card" | number " cards")
shuffle: /[sS]/ "huffle" "s"? (" " (objects | zone) " into ")? zone
counter: /[cC]/ "ounter " objects
extraturn: /[tT]/ "ake an extra turn after this one"
look: /[lL]/ "ook at the top " number " cards of " zone
put: /[pP]/ "ut " objects " " into (" deactivated")? (" and " objects " " into)?
gaincontrol: /[gG]/ "ain" "s"? " control of " objects
switchdmghp: /[sS]/ "witch the damage and health of " objects (" " until)?
addmana: /[aA]/ "dd one essence of any color" | "add " number " essence of any one color" | "add " COLOR (" or " COLOR)?

activate: /[aA]/ "ctivate " objects
deactivate: /[dD]/ "eactivate " objects
return: /[rR]/ "eturn " objects (" from " zones)? " to " zones
discard: /[dD]/ "iscard " objects
sacrifice: /[sS]/ "acrifice " objects
payessence: /[pP]/ "ay " essencecost
paylife: /[pP]/ "ay " numberorxorthat " life"

playerphrases: playerphrase
| playerphrase " for each " object
| playerphrase " for the first time each turn"
| playerphrase ", then " playerphrase
| playerphrase " this way"

playerphrase: ("gain " | "gains ") numberorx " life"
| ("gain " | "gains ") "life equal to " itspossesion " " numberical
| ("controls " | "control ") objects
| ("owns " | "own ") objects
| "puts " objects " " into
| "discards " objects
| "sacrifices " objects
| "reveals " possesion " hand"
| imperative
| "can't " imperative
| "doesn't" | "don't" | "does" | "do"
| "lose" "s"? " the game"

objectphrases: objectphrase ","? " and " objectphrase
| objectphrase " or " objectphrase
| objectphrase "," (" then")? " " objectphrase
| objectphrase " " foreach
| objectphrase " " duration
| objectphrase " if " condition

objectphrase: ("has" | "have") " " acquiredability (" as long as " condition)?
| ("gets " | "get ") mod (" and gains " acquiredability)? (" " until)?
| ("gets " | "get ") mod (" and gains " acquiredability)? (" " until)?
| "gains " acquiredability (" and gets " mod)? (" " until)?
| ("gets " | "get ") mod (" " foreach)? (" " until)?
| ("enter" | "enters") " the field" " deactivated"? (" under " possesion " control")?
| ("leave" | "leaves") " the field"
| ("die" | "dies")
| "is put " into " from " zone
| "can't " cant (" " duration)?
| "deals " deals
| "is " what
| ("attacks" | "attack") (" " ("this" | "each") " fight if able")?
| ("gains " | "gain ") acquiredability (" " until)?
| "doesn't activate during " moment
| "blocks or becomes blocked by " objects
| "targets " objects
| ("cost" | "costs") " " essencecost " less to play"
| ("lose" | "loses") " all abilities" (" " until)?


# "do so"
# "does so"
# "becomes " becomes
# ("is" | "are") " created"
# "is countered this way"
# "causes " players " to discard " objects

into: "onto the field"
| "into " zone
| "on top of " orderedzone
| "on the bottom of " orderedzone " in any order"
| "on the bottom of " orderedzone " in a random order"

place: "on the field" | "in " zone
zones: ((possesion | "a" ) " " (zone "s" | zone " or " zone | zone " and/or " zone | zone (", " "and "? zone)+)) | "the field" | "it"
zone: orderedzone | "hand"
orderedzone: "deck" | "discard"

referenceprefix: refsacrificed | anyof | the | reference | countable
reference: each | all | a | this | that | another | chosen | atleast | counted | countedtarget
counted: countable (" " reference)?
countedtarget: ( /[aA]/ "nother ")? (countable " ")? "target"

prefix: /[dD]/ "eactivated"
| /[nN]/ "on-" TYPE
| /[tT]/ "oken" | /[nN]/ "ontoken"
| stats
| /[aA]/ "ttacking"
| /[bB]/ "locking"
| /[aA]/ "ttacking or blocking"

suffix: player " " ("control" | "controls" | "don't control" | "doesn't control" | "own" | "owns" | "don't own" | "doesn't own")
| "in " zone (" and in " zone)?
| "from " zone
| "you play"
| "that targets only " objects
| "deactivated this way"
| "of the " TYPE " type of " possesion " choice"
| object " could target"
| "from among them"
| "you've played before it this turn"

itspossesion: objects "'s" | /[iI]/ "ts" | /[tT]/ "heir"
possesion: "your" | "their" | players "'s"
players: player
| player " who can't"
| itspossesion " " ("controller" | "owner" | "owners" | "controllers")
player: you | they | opponent | defending | attacking | refplayer
refplayer: reference " " pureplayer
pureplayer: "opponent" | "player" | "players"

objects: object ((", " | "and " | "or " | "and/or ") object)*
object: name | it | they | one | other | refobject | specifiedobject | copyof | withoutkeyword | objectwith

refobject: referenceprefix " " pureobject
specifiedobject: (prefix " ")+ pureobject  (" " suffix)?
copyof: /[cC]/ "opy" (" of " pureobject)?
withoutkeyword: pureobject " without " keyword
objectwith: pureobject " " with
pureobject: /[cC]/ "opies" | n
n: nn "s"?
nn: (TYPE " ")? "card" | /[tT]/ "oken" | /[aA]/ "bility"

deals: ("combat ")? "damage to " damagerecipient
| numberorxorthat " damage to " damagerecipient
| "damage equal to " numberdefinition " to " damagerecipient
| "damage to " damagerecipient " equal to " numberdefinition
| numberorxorthat " damage spread between any target"
damagerecipient: objects | players | "any target" | "itself"
| "target " damagerecipient " or " damagerecipient

with: numberical " " numbericalcompare
| "the highest " numberical " among " objects
| "level " numberorxorthat
| acquiredability
what: color | objects | place | TYPE (" in addition to its other types")?
becomes: "deactivated" | "activated" | "a copy of " objects (", except " copyexception (", " ("and ")? copyexception)*)?
copyexception: "its name is " name | "it is " what
cant: "attack"| "block" | "attack or block"
| "be blocked"
| "be countered"
| "be blocked by more than " number (" units" | " unit")
foreach: "for each " object
numberical: "damage" | "health" | "level"
numbericalcompare: numberorx " or greater"
| numberorx " or less"
| "less than or equal to " numberdefinition
| "greater than " numberdefinition
| numberorx
numberdefinition: itspossesion " " numberical | /[Tt]/ "he number of " objects
countable: /[Ee]/ "xactly " number
| number " or more"
| /[Ff]/ "ewer than " number
| /[Aa]/ "ny number of"
| /[Oo]/ "ne of"
| /[Uu]/ "p to " number
| number

until: "until " (condition | "end of turn")
duration: thisturn | "for as long as " condition | until
when: thisturn
thisturn: "this turn"
moment: turnqualifier " " phase | "fight on your turn" | "fight"
turnqualifier: (possesion | "the") (" next")?
| "the"
| "each"
| "this turn's"
| "that turn's"
phase: "turn"
| "activation"
| "draw step"
| "main phase"
| "fight phase"
| "end step"

refsacrificed: /[tT]/ "he sacrificed"
anyof: "any of"
the: /[tT]/ "he"
each: /[eE]/ "ach"
all: /[aA]/ "ll" (" the")?
this: /[tT]/ "his"
that: /[tT]/ ("hat" | "hese"| "hose")
a: /[aA]/ "n"?
another: /[aA]/ "nother"
chosen: /[tT]/ "he chosen"
atleast: /[aA]/ "t least " number
it: /[iI]/ "t"
other: /[tT]/ ("he rest" | "he other")
you: /[Yy]/ "ou"
they: /[Tt]/ "hey"
opponent: /[Yy]/ "our " ("opponent" | "opponents")
defending: /[Dd]/ "efending player"
attacking: /[Aa]/ "ttacking player"
beginningofphase: /[Aa]/ "t the beginning of " moment
endofturn: /[Aa]/ "t end of the turn"
yourturn: "it's your turn"
notyourturn: "it's not your turn"

mod: plusminus numberorx "/" plusminus numberorx
plusminus: "+" | "-"
numberorxorthat: numberorx | thatmany
numberorx: smallnumber | x
number:  one | two | three | four | five | six | seven | eight | nine | ten | x | thatmany | smallnumber
color: "red" | "green" | "blue" | "white" | "colorless"

thatmany: "that many" | "that much"
one: "a" | "an" | /[oO]/ "ne"
two: "two"
three: "three"
four: "four"
five: "five"
six: "six"
seven: "seven"
eight: "eight"
nine: "nine"
ten: "ten"
x: "X"

smallnumber: /[1]?[0-9]/
COLOR: "R" | "G" | "B" | "W"
TYPE: {types}
KEYWORD: {keywords}
'''

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


parser = Parser(grammar_str)

card = parser.parse("""Soldier {R}{1}
Creature
Flying, Siege
{2}: Create a 2/2 token with "Flying" and "Siege"
{T}: Draw a card, then you draw an cards for each creature card
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