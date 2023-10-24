from string import ascii_uppercase as auc

from lark import Lark, Tree, Token, Transformer, v_args, Discard

from models import *


class DropLetters(Transformer):
    def __init__(self, visit_tokens: bool = True) -> None:
        for l in auc:
            setattr(self, l, self._drop_token.__func__)
        super().__init__(visit_tokens)

    def _drop_token(self):
        return Discard
    
@v_args(inline=True)
class NumberTransformer(Transformer):
    def smallnumber(self, item):
        try:
            return int(item)
        except:
            return str(item)
    def number(self, item):
        return item
    def numberorx(self, item):
        return item
    def numberorxorthat(self, item):
        return item
    def a(self):
        return 1
    def one(self):
        return 1
    def two(self):
        return 2
    def three(self):
        return 3
    def four(self):
        return 4
    def five(self):
        return 5
    def six(self):
        return 6
    def seven(self):
        return 7
    def eight(self):
        return 8
    def nine(self):
        return 9
    def ten(self):
        return 10
    def x(self):
        return "X"
    def thatmany(self):
        return "that"
    def plusminus(self, item):
        return (lambda x: -x if isinstance(x, int) else "-" + x) if item == "-" else (lambda x: x)
    def plusminusnumber(self, mod, num):
        return mod(num)


@v_args(inline=True)
class OperatorTransformer(Transformer):
    def opandorthen(self, item):
        return item
    def opandor(self, item):
        return item
    def andor(self):
        return OperatorEnum.OR
    def opand(self):
        return OperatorEnum.AND
    def opor(self):
        return OperatorEnum.XOR
    def then(self):
        return OperatorEnum.AND

@v_args(inline=True)
class BaseTransformer(Transformer):
    def COLOR(self, item):
        return ColorEnum(item)
    def TYPE(self, item):
        return TypeEnum(item.lower())
    def KEYWORD(self, item):
        return KeywordEnum(item.lower())
    def maintype(self, item):
        return item
    def subtype(self, item):
        return str(item)
    def types(self, *items):
        main_types = []
        sub_types = []
        for i in items:
            if i in TypeEnum.__members__:
                main_types.append(i)
            else:
                sub_types.append(i)
        return main_types, sub_types
    def type(self, item):
        return item
    def keyword(self, item):
        return item
    def stats(self, power, health):
        return Stats(power=power, health=health)


class PureObject(str, Enum):
    ability = "ability"
    token = "token"
    card = "card"
    copies = "copies"


@v_args(inline=True)
class KeywordTransformer(Transformer):
    def red(self):
        return ColorEnum.red
    def green(self):
        return ColorEnum.green
    def blue(self):
        return ColorEnum.blue
    def yellow(self):
        return ColorEnum.yellow
    def colorless(self):
        return ColorEnum.colorless
    def multicolored(self):
        return ColorEnum.multicolored
    
    def copies(self):
        return PureObject.copies
    def tokencard(self):
        return PureObject.token
    def abilityref(self):
        return PureObject.ability
    
    def field(self):
        return ZoneEnum.board
    def hand(self):
        return ZoneEnum.hand
    def deck(self):
        return ZoneEnum.deck
    def discardzone(self):
        return ZoneEnum.pile
    def top(self):
        return PlaceEnum.top
    def bottom(self):
        return PlaceEnum.bottom
    def random(self):
        return OrderEnum.random
    def ordered(self):
        return OrderEnum.ordered
    def zone(self, item):
        return item
    def orderedzone(self, item):
        return item
    
    def turn(self):
        return PhaseEnum.turn
    def activationphase(self):
        return PhaseEnum.activation
    def drawphase(self):
        return PhaseEnum.draw
    def playphase(self):
        return PhaseEnum.play
    def fightphase(self):
        return PhaseEnum.fight
    def cleanup(self):
        return PhaseEnum.cleanup
    
    def damage(self):
        return NumbericalEnum.damage
    def health(self):
        return NumbericalEnum.health
    def level(self):
        return NumbericalEnum.level
    def numberical(self, item):
        return item

    def owners(self):
        return PlayerEnum.owner
    def controllers(self):
        return PlayerEnum.controller
    def opponent(self):
        return PlayerEnum.opponent
    def anyplayer(self):
        return PlayerEnum.player
    def you(self):
        return PlayerEnum.you
    def they(self):
        return PlayerEnum.they
    def defending(self):
        return PlayerEnum.defending
    def attacking(self):
        return PlayerEnum.attacking
    
    def its(self):
        return PlayerRef.their
    def their(self):
        return PlayerRef.their
    def your(self):
        return PlayerRef.your
    
    def attack(self):
        return ObjectActionEnum.attack
    def block(self):
        return ObjectActionEnum.block
    def attackorblock(self):
        return ObjectActionEnum.attack, ObjectActionEnum.block
    def beblocked(self):
        return ObjectActionEnum.beblocked
    def becountered(self):
        return ObjectActionEnum.becountered
    def activateability(self):
        return ObjectActionEnum.activateability
    
    def anytarget(self):
        return DamageRef.anytarget
    def itself(self):
        return DamageRef.itself
    
    def phase(self, item):
        return item
    def pureplayer(self, item):
        return item
    def pureobject(self, item):
        return item
    def typecard(self, *items):
        if items:
            return items[0]
        return PureObject.card


@v_args(inline=True)
class ReferenceTransformer(Transformer):
    def refsacrificed(self):
        return ObjectRef.sac
    def anyof(self):
        return ObjectRef.any
    def self(self):
        return ObjectRef.self
    def it(self):
        return ObjectRef.it
    def they(self):
        return ObjectRef.they
    def other(self):
        return ObjectRef.rest
    
    def this(self):
        return Reference.this
    def that(self):
        return Reference.that
    def each(self):
        return Reference.each
    def all(self):
        return Reference.all
    def another(self):
        return Reference.another
    def chosen(self):
        return Reference.chosen
    def anynumberof(self):
        return Reference.anynumberof
    def oneof(self):
        return Reference.oneof
    
    def atleast(self, item):
        return (Reference.atleast, item)
    def exactly(self, item):
        return (Reference.exactly, item)
    def ormore(self, item):
        return (Reference.ormore, item)
    def fewerthan(self, item):
        return (Reference.fewerthan, item)
    def upto(self, item):
        return (Reference.upto, item)
    def atleast(self, item):
        return (Reference.atleast, item)
    def exactly(self, item):
        return (Reference.exactly, item)
    def ormore(self, item):
        return (Reference.ormore, item)
    def fewerthan(self, item):
        return (Reference.fewerthan, item)
    def upto(self, item):
        return (Reference.upto, item)
    
    def reference(self, item):
        return item
    
    def countable(self, item):
        return item
    
    def referenceprefix(self, item):
        if isinstance(item, int):
            return (Reference.exactly, item)
        return item
    
    def target(self, *items):
        return tuple([Reference.target] + items)


class PrefixMixin:
    def prefix(self, item):
        item = item[0]
        if isinstance(item, Stats):
            return Prefix(prefix=item)
        elif item == PlayerEnum.attacking:
            item = (PrefixEnum.attacking, False)
        return Prefix(prefix=item[0], non=item[1] if len(item) > 1 else False)
    def activated(self):
        return (PrefixEnum.activated, False)
    def deactivated(self):
        return (PrefixEnum.activated, True)
    def token(self):
        return (TypeEnum.TOKEN, False)
    def nontoken(self):
        return (TypeEnum.TOKEN, True)
    def blocking(self):
        return (PrefixEnum.blocking, False)
    def attackingorblocking(self):
        return (PrefixEnum.attackingorblocking, False)
    def nontype(self, item):
        return (item, True)
    def noncolor(self, item):
        return (item, True)
    def color(self, item):
        return (item, False)
    

class SuffixMixin:
    def suffix(self, item):
        return item
    def playercontrol(self, item):
        return Suffix(suffix=SuffixEnum.control, subj=item)
    def playernocontrol(self, item):
        return Suffix(suffix=SuffixEnum.nocontrol, subj=item)
    def playerown(self, item):
        return Suffix(suffix=SuffixEnum.own, subj=item)
    def playernoown(self, item):
        return Suffix(suffix=SuffixEnum.noown, subj=item)
    def inzones(self, items):
        return Suffix(suffix=SuffixEnum.inzone, subj=items)
    def thattargets(self, item):
        return Suffix( suffix=SuffixEnum.targets, subj=item)
    def thattargetsonly(self, item):
        return Suffix(suffix=SuffixEnum.targetsonly, subj=item)
    def couldtarget(self, item):
        return Suffix(suffix=SuffixEnum.couldtarget, subj=item)
    def chosentype(self, type, who):
        return Suffix(suffix=SuffixEnum.chosentype, subj=(type, who))
    def activatedthisway(self):
        return Suffix(suffix=SuffixEnum.activatedthisway)
    def deactivatedthisway(self):
        return Suffix(suffix=SuffixEnum.deactivatedthisway)
    def amongthem(self):
        return Suffix(suffix=SuffixEnum.amongthem)
    def youplay(self):
        return Suffix(suffix=SuffixEnum.youplay)


class ConditionMixin:
    def yourturn(self):
        return Condition(condition=ConditonEnum.yourturn)
    def notyourturn(self):
        return Condition(condition=ConditonEnum.notyourturn)
    def thisturn(self):
        return Condition(condition=ConditonEnum.thisturn)
    def until(self, items):
        if len(items):
            items[0].until = True
            return items[0]
        return Condition(condition=ConditonEnum.thisturn)
    def condition(self, item):
        return item
    def duration(self, item):
        return item


class ZoneMixin:
    def into(self, items):
        if items[0] == ZoneEnum.board:
            return Into(zones=[ZoneEnum.board])
        elif isinstance(items[0], Zone):
            return Into(**items[0].dict())
        return Into(
            place=items[0],
            zones=[items[1]],
            random=len(items) > 2 and items[2] == OrderEnum.random
        )
    
    def zones(self, items):
        if items[0] == ObjectRef.it:
            return Zone(zones=[ZoneEnum.it])
        elif items[0] == ZoneEnum.board:
            return Zone(zones=[ZoneEnum.board])
        return Zone(
            ref=None if items[0] == 1 else items[0],
            zones=[i for i in items[1:] if isinstance(i, ZoneEnum)]
        )


class PlayerMixin:
    def refplayer(self, items):
        return tuple(items)
    
    def player(self, items):
        if len(items) == 1:
            return items[0]
        return items
    
    def possesion(self, item):
        if isinstance(item, Player):
            return item
        elif item == PlayerRef.their:
            return Player(player=PlayerEnum.they)
        return Player(player=PlayerEnum.you)
    
    def players(self, items):
        p = items[0]
        ref = None
        if isinstance(p, tuple):
            ref = p[0]
            p = p[1]
        return Player(player=p, ref=ref, who_cant=len(items) > 1)


class ObjectMixin:
    def selfref(self, n):
        return CardObject(ref=ObjectRef.self)
    
    def object(self, item):
        if isinstance(item, PureObject):
            return self._from_pureobject(item)
        elif isinstance(item, TypeEnum):
            return CardObject(type=item)
        return item
    
    def objects(self, items):
        items = items[0]
        each = False
        if len(items) > 1 and items[0] == Reference.each:
            items = items[1:]
            each = True
        return Objects(objects=items, each=each)
    
    def opwith(self, item):
        # TODO: implement more with clauses (numbercompare, highestnumber, whatlevel)
        return ("with", item)
    
    def specifiedobject(self, items):
        r = items[0] if not isinstance(items[0], Prefix) and not isinstance(items[0], PureObject) and not isinstance(items[0], TypeEnum) else None
        e = None
        if r and isinstance(r, tuple):
            if len(r) > 1:
                e = r[1]
            r = r[0]
        
        suffix = items[-1] if isinstance(items[-1], Suffix) else None
        prefixes = [c for c in items if isinstance(c, Prefix)]
        wo = [c for c in items if isinstance(c, KeywordEnum)]
        w = [c for c in items if isinstance(c, tuple) and c[0] == "with"]
        o = items[-2] if suffix else items[-1]
        return self._from_pureobject(
            o,
            ref=r,
            prefixes=prefixes,
            suffix=suffix,
            extra=e,
            withwhat=w[0] if w else None,
            without=wo[0] if wo else None
        )
    def foreach(self, item):
        return item
    def itspossesion(self, item):
        return item
    def _from_pureobject(
        self,
        o: PureObject,
        ref: Reference | ObjectRef | NumberOrX | None = None,
        prefixes: list[Prefix] = [],
        suffix: Suffix | None = None,
        extra: Any = None,
        withwhat: Any = None,
        without: Any = None
    ):
        if o == PureObject.ability:
            return AbilityObject(ref=ref, prefixes=prefixes, suffix=suffix, extra=extra)
        elif o == PureObject.copies:
            return CardObject(ref=ref, prefixes=prefixes, suffix=suffix, extra=extra, copies=True, without=without, withwhat=withwhat)
        elif o == PureObject.token:
            return CardObject(ref=ref, prefixes=prefixes, suffix=suffix, type=TypeEnum.TOKEN, extra=extra, without=without, withwhat=withwhat)
        return CardObject(ref=ref, prefixes=prefixes, extra=extra, without=without, withwhat=withwhat)


@v_args(inline=True)
class ObjectTransformer(PrefixMixin, SuffixMixin, ZoneMixin, PlayerMixin, ObjectMixin, ConditionMixin, Transformer):
    def numberdefinition(self, items):
        o = [c for c in items if isinstance(c, Objects)]
        n = [c for c in items if isinstance(c, NumbericalEnum)]
        return NumberDef(amount=o[0] if len(o) > 0 else items[0], property=n[0] if len(n) > 0 else None)
    
    def objectcant(self, item):
        if not isinstance(item, tuple):
            item = (item, )
        return item
    
    def moment(self, items):
        if items:
            return Phase(ref=items[0], phase=items[1])
        return Phase(ref=PlayerRef.your, phase=PhaseEnum.fight)
    
    def beginningofphase(self, item):
        return item
    
    def turnqualifier(self, items):
        t = items[0]
        if t == Reference.each:
            return (TurnQualifierEnum.each, False)
        elif t == Reference.this:
            return (TurnQualifierEnum.this, False)
        elif t == Reference.that:
            return (TurnQualifierEnum.that, False)
        elif t == Reference.the:
            return (TurnQualifierEnum.the, len(items) > 1)
        return (t, len(items) > 1)


grammar = open("grammars/game.lark", "r").read()

lark = Lark(grammar.format(name=f'"~"', types=TypeEnum.to_grammar(), keywords=KeywordEnum.to_grammar()), start="root")

drop_tf = DropLetters()
number_tf = NumberTransformer()
op_tf = OperatorTransformer()
base_tf = BaseTransformer()
keyword_tf = KeywordTransformer()
ref_tf = ReferenceTransformer()
obj_tf = ObjectTransformer()


card = """~ {Y}{B}
Unit
{2}: Attacking unit cards in your hand get -3/-3 until end of turn.
{B}: Attacking unit cards in your deck get -2/-2 until end of turn.
{1}, Sacrifice ~: Draw two cards, then each player discards two cards.
2/0"""

tree = lark.parse(card)
tree = drop_tf.transform(tree)
tree = number_tf.transform(tree)
tree = op_tf.transform(tree)
tree = base_tf.transform(tree)
tree = keyword_tf.transform(tree)
tree = ref_tf.transform(tree)
tree = obj_tf.transform(tree)

print(tree)