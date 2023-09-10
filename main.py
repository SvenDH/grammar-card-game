from enum import Enum
from typing import Literal
from pydantic import BaseModel
from llama_cpp import LlamaGrammar
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from lark import Lark

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


NumberOrX = int | Literal["X"]


class Essence(str, Enum):
    white = "W"
    red = "R"
    green = "G"
    blue = "B"


class Activation(str, Enum):
    activate = "Q"
    deactivate = "T"

    def to_text(self):
        return f"{{{self}}}"


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


class EssenceCosts(BaseModel):
    costs: list[Essence | NumberOrX]
    
    def to_text(self):
        return "".join([f"{{{c}}}" for c in self.costs])


class ImperativeCost(BaseModel):
    costs: list[str] = []

    def to_text(self):
        return ""
    
    @classmethod
    def from_tree(cls, tree):
        return cls(costs=[])


class Trigger(BaseModel):
    conditions: list[str] = []

    def to_text(self):
        return ""
    
    @classmethod
    def from_tree(cls, tree):
        return cls(conditions=[])


class Effect(BaseModel):
    effects: list['Abilities'] = []
    optional: bool = False

    def to_text(self):
        return ""
    
    @staticmethod
    def get_effect(tree):
        print(tree)
        return 

    @classmethod
    def from_tree(cls, tree):
        print(tree.children[0].children)
        return cls(
            effects=[cls.get_effect(a) for a in tree.children[0].children],
            optional=tree.children[0].data == "may"
        )


class ActivatedAbility(BaseModel):
    costs: list[EssenceCosts | Activation | ImperativeCost]
    effect: Effect

    def to_text(self):
        costs = ", ".join([c.to_text() for c in self.costs])
        return f"{costs}: {self.effect.to_text()}"
    
    @staticmethod
    def get_cost(tree):
        match tree.data:
            case "essencecost":
                return EssenceCosts(costs=tree.children[0].children)
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


class TriggeredAbility(BaseModel):
    trigger: Trigger
    effect: Effect

    def to_text(self):
        costs = ", ".join([c.to_text() for c in self.costs])
        return f"{costs}: {self.effect.to_text()}"
    
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

    @staticmethod
    def process_abilities(ability):
        t = ability.children[0].data
        c = ability.children[0]
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
    
    @classmethod
    def from_tree(cls, tree):
        types = tree.children[2].children[0].children
        return cls(
            name=tree.children[0].children[0].value,
            cost=[c.children[0].value for c in tree.children[1].children],
            type=types[0].lower(),
            subtype=types[1].value if len(types) > 1 else None,
            abilities=[i for a in tree.children[3].children for i in cls.process_abilities(a)],
            damage=tree.children[4].children[0],
            health=tree.children[4].children[1],
        )


grammar_str = fr'''
root: card ("\n\n" card)*
card: name " " cardcosts "\n" types "\n" abilities stats

name: /[A-Z][a-z]*(" " [A-Z][a-z]*)*/
types: maintype (" - " subtype)?
maintype: TYPE
subtype: /[ a-zA-Z]+/
stats: SNUMBER "/" SNUMBER

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
imperative: destroy | createtoken | copy | play | search | draw | shuffle | counter | activate | deactivate | extraturn | look | put | gaincontrol | switchdmghp | addmana | return | discard | sacrifice | payessence | paylife

destroy: /[dD]/ "estroy " objects
createtoken: /[cC]/ "reate " number " " stats (" token" | " tokens") (" with " with)?
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
object: it | they | one | other | refobject | specifiedobject | copyof | withoutkeyword | objectwith

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
one: /[oO]/ "ne"
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
numberorxorthat: numberorx | "that much"
numberorx: SNUMBER | "X"
number:  "a" | "an" | "one" | "two" | "three" | "four" | "five" | "six" | "seven" | "eight" | "nine" | "ten" | "X" | "that many" | SNUMBER
color: "red" | "green" | "blue" | "white" | "colorless"

SNUMBER: /[1]?[0-9]/
COLOR: "R" | "G" | "B" | "W"
TYPE: {TypeEnum.to_grammar()}
KEYWORD: {KeywordEnum.to_grammar()}
'''

new_grammar = grammar_str.replace(" /", " ").replace("/ ", " ").replace("/\n", "\n").replace("\n|", " |").replace(": ", " ::= ")
llm_grammar = LlamaGrammar.from_string(new_grammar)

g = Lark(grammar_str, start="root", debug=True)

p = g.parse("""Soldier {R}{1}
Creature
Flying, Siege
{2}: Create a 2/2 token with the highest level among all creature cards
{T}: Draw a card, then you draw an cards for each creature card
1/1""")

cards = [Card.from_tree(c) for c in p.children]

print(cards)


n_gpu_layers = 128
n_batch = 512

llm = LlamaCpp(
    model_path="C:\\Users\\denha\\Bureaublad\\oobabooga\\text-generation-webui\\models\\llama-2-7b-chat.ggmlv3.q4_K_M.bin",
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    f16_kv=True,
    #callback_manager=callback_manager,
    temperature=1.0,
)
llm.grammar = llm_grammar

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

Advisor {W}{1}
Creature
{T}: Activate any target
0/2

"""
output = llm(prompt)
for c in output.split("\n\n"):
    if c:
        print(c)
        print(Card.from_tree(g.parse(c).children[0]))