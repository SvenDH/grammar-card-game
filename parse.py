from string import ascii_uppercase

from lark import Lark, Transformer, v_args, Discard

from models import *


class DropLetters(Transformer):
    def __init__(self, visit_tokens: bool = True) -> None:
        for l in ascii_uppercase:
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
    def stats(self, power, health):
        return Stats(power=power, health=health)
    def essencecost(self, *args):
        return list(args)
    def activatecost(self):
        return Activation.activate
    def deactivatecost(self):
        return Activation.deactivate
    def activationcost(self, item):
        return item
    def keywords(self, *args):
        return args


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
        return Reference.their
    def their(self):
        return Reference.their
    def your(self):
        return Reference.your
    
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
        return Reference.anytarget
    def itself(self):
        return Reference.itself
    
    def endofturn(self):
        return TriggerEnum.endofturn
    
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
        return Reference.sac
    def anyof(self):
        return Reference.any
    def self(self):
        return Reference.self
    def it(self):
        return Reference.it
    def they(self):
        return Reference.they
    def other(self):
        return Reference.rest
    
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
        return Reference.atleast, item
    def exactly(self, item):
        return Reference.exactly, item
    def ormore(self, item):
        return Reference.ormore, item
    def fewerthan(self, item):
        return Reference.fewerthan, item
    def upto(self, item):
        return Reference.upto, item
    def atleast(self, item):
        return Reference.atleast, item
    def exactly(self, item):
        return Reference.exactly, item
    def ormore(self, item):
        return Reference.ormore, item
    def fewerthan(self, item):
        return Reference.fewerthan, item
    def upto(self, item):
        return Reference.upto, item
    
    def reference(self, item):
        return item
    
    def countable(self, item):
        return item
    
    def referenceprefix(self, item):
        if isinstance(item, int):
            return Reference.exactly, item
        return item
    
    def target(self, *items):
        return tuple([Reference.target] + list(items))


class PrefixMixin:
    def prefix(self, item):
        item = item[0]
        if isinstance(item, Stats):
            return Prefix(prefix=item)
        elif item == PlayerEnum.attacking:
            item = PrefixEnum.attacking, False
        return Prefix(prefix=item[0], non=item[1] if len(item) > 1 else False)
    def activated(self, _):
        return PrefixEnum.activated, False
    def deactivated(self, _):
        return PrefixEnum.activated, True
    def token(self):
        return TypeEnum.token, False
    def nontoken(self):
        return TypeEnum.token, True
    def blocking(self):
        return PrefixEnum.blocking, False
    def attackingorblocking(self):
        return PrefixEnum.attackingorblocking, False
    def nontype(self, item):
        return item[0], True
    def noncolor(self, item):
        return item[0], True
    def color(self, item):
        return item[0], False
    def esscolor(self, item):
        return item[0]
    

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
        return item[0]
    def duration(self, item):
        return item
    def playedwhen(self, object, duration):
        return PlayedCondition(
            condition=ConditonEnum.playedwhen,
            object=object,
            duration=duration
        )
    def compare(self, number, compare):
        return NumberCondition(
            condition=ConditonEnum.compare,
            number=number,
            compare=compare
        )


class ZoneMixin:
    def into(self, items):
        if items[0] == ZoneEnum.board:
            return ZoneMatch(zones=[ZoneEnum.board])
        elif isinstance(items[0], ZoneMatch):
            return ZoneMatch(**items[0].dict())
        return ZoneMatch(
            place=items[0],
            zones=[items[1]],
            random=len(items) > 2 and items[2] == OrderEnum.random
        )
    
    def zones(self, items):
        if items[0] == Reference.it:
            return ZoneMatch(zones=[ZoneEnum.it])
        elif items[0] == ZoneEnum.board:
            return ZoneMatch(zones=[ZoneEnum.board])
        return ZoneMatch(
            ref=None if items[0] == 1 else items[0],
            zones=[i for i in items[1:] if isinstance(i, ZoneEnum)]
        )


class PlayerMixin:
    def refplayer(self, items):
        return tuple(items)
    
    def player(self, items):
        if len(items) == 1:
            return items[0]
        return items[0][0], items[1]
    
    def players(self, items):
        p = items[0]
        ref = None
        if isinstance(p, tuple):
            ref = p[0]
            p = p[1]
        return PlayerMatch(player=p, ref=ref, who_cant=len(items) > 1)
    
    def possesion(self, item):
        if isinstance(item, PlayerMatch):
            return item
        elif item == Reference.their:
            return PlayerMatch(player=PlayerEnum.they)
        return PlayerMatch(player=PlayerEnum.you)


class ObjectMixin:
    def selfref(self, _):
        return CardObject(ref=Reference.self)
    
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
        return ObjectMatch(objects=items, each=each)
    
    def opwith(self, item):
        # TODO: implement more with clauses (numbercompare, highestnumber, whatlevel)
        return ("with", item)
    
    def specifiedobject(self, items):
        r = items[0] if not isinstance(items[0], Prefix) and not isinstance(items[0], PureObject) and not isinstance(items[0], TypeEnum) else Reference.none
        e = 0
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
            without=wo[0] if wo else KeywordEnum.none
        )
    def foreach(self, item):
        return item
    def itspossesion(self, item):
        return item
    def _from_pureobject(
        self,
        o: PureObject,
        ref: Reference | NumberOrX | None = None,
        prefixes: list[Prefix] = [],
        suffix: Suffix | None = None,
        extra: Any = None,
        withwhat: Any = None,
        without: Any = None
    ):
        suffixes = [suffix] if suffix else []
        if o == PureObject.ability:
            return AbilityObject(ref=ref, prefixes=prefixes, suffixes=suffixes, extra=extra)
        elif o == PureObject.copies:
            return CardObject(ref=ref, prefixes=prefixes, suffixes=suffixes, extra=extra, copies=True, without=without, withwhat=withwhat)
        elif o == PureObject.token:
            return CardObject(ref=ref, prefixes=prefixes, suffixes=suffixes, type=TypeEnum.token, extra=extra, without=without, withwhat=withwhat)
        return CardObject(ref=ref, prefixes=prefixes, extra=extra, without=without, withwhat=withwhat)


@v_args(inline=True)
class ObjectTransformer(PrefixMixin, SuffixMixin, ZoneMixin, PlayerMixin, ObjectMixin, ConditionMixin, Transformer):
    def blocked(self):
        return (ObjectPhraseEnum.blocked,)
    def attacked(self):
        return (ObjectPhraseEnum.attacked,)
    def leaves(self):
        return (ObjectPhraseEnum.leaves,)
    def dies(self):
        return (ObjectPhraseEnum.dies,)
    def whenenters(self, *args):
        return (ObjectPhraseEnum.whenenters, args[0] if args else None)
    def dealsdamage(self, item):
        return (ObjectPhraseEnum.dealsdamage, item)
    def moveszone(self, into, *args):
        return (ObjectPhraseEnum.moveszone, into, args[0] if args else None)
    def targets(self, item):
        return (ObjectActionEnum.targets, item)

    def numberdefinition(self, items):
        o = [c for c in items if isinstance(c, ObjectMatch)]
        n = [c for c in items if isinstance(c, NumbericalEnum)]
        return NumberDef(amount=o[0] if len(o) > 0 else items[0], property=n[0] if len(n) > 0 else None)
    
    def objectcant(self, item):
        if not isinstance(item, tuple):
            item = (item, )
        return item
    
    def moment(self, items):
        if isinstance(items[0], PlayerMatch):
            return Phase(phase=items[1], player=items[0])
        return Phase(phase=items[1], turn=items[0])
    
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
    
    def createtoken(self, number, stats, *args):
        return CreateTokenEffect(number=number, stats=stats, abilities=args[0] if args else [])
    def destroy(self, objects):
        return DestroyEffect(objects=objects)
    def copy(self, objects):
        return CopyEffect(objects=objects)
    def play(self, objects, *args):
        return PlayEffect(objects=objects, free=len(args) > 0)
    def draw(self, *args):
        return DrawEffect(number=args[0] if args else 1)
    def discard(self, *args):
        return DiscardEffect(
            number=args[0] if args else 1,
            objects=args[1] if len(args) > 1 else ObjectMatch(objects=[CardObject()])
        )
    def search(self, zones, *args):
        return SearchEffect(zones=zones, objects=args[0] if args else None)
    def shuffle(self, *args):
        return ShuffleEffect(what=args[0] if len(args) > 1 else None, zones=args[-1])
    def counter(self, objects):
        return CounterEffect(objects=objects)
    def extraturn(self):
        return ExtraTurnEffect()
    def look(self, number, zones):
        return LookEffect(number=number, zones=zones)
    def put(self, objects, into, *args):
        objs = [c for c in args if isinstance(c, ObjectMatch)]
        intos = [c for c in args if isinstance(c, ZoneMatch)]
        return PutEffect(
            objects=objects,
            into=into,
            deactivated=(PrefixEnum.activated, True) in args,
            second_objects=objs[0] if objs else None,
            second_into=intos[0] if intos else None,
        )
    def gaincontrol(self, objects, *args):
        return GainControlEffect(objects=objects, until=args[0] if args else None)
    def switchdmghp(self, objects, *args):
        return SwitchStatsEffect(objects=objects, until=args[0] if args else None)
    def addessence(self, *args):
        a = [c for c in args if isinstance(c, int) or c == "X"]
        colors = [c for c in args if isinstance(c, ColorEnum)]
        if not colors:
            colors = [ColorEnum.yellow, ColorEnum.red, ColorEnum.green, ColorEnum.blue]
        return AddEssenceEffect(colors=colors, amount=a[0] if a else 1)
    def activate(self, objects):
        return ActivationEffect(objects=objects, deactivate=False)
    def deactivate(self, objects):
        return ActivationEffect(objects=objects, deactivate=True)
    def returncard(self, objects, *args):
        return MoveEffect(objects=objects, tozone=args[-1], fromzone=args[-2] if len(args) > 1 else None)
    def sacrifice(self, objects):
        return SacrificeEffect(objects=objects)
    def reveals(self, possesion):
        return RevealEffect(player=possesion)
    
    def payessence(self, costs):
        return PayessenceEffect(costs=costs)
    def paylife(self, costs):
        return PaylifeEffect(costs=costs)
    
    def ability(self, item):
        return item
    def activatedability(self, abilitycosts, effects):
        return [ActivatedAbility(costs=abilitycosts, effect=Effect(effects=effects))]
    def abilitycosts(self, *args):
        items = []
        for a in args:
            if isinstance(a, list):
                items.extend(a)
            else:
                items.append(a)
        return items
    def triggeredability(self, triggercondition, *args):
        return [TriggeredAbility(
            trigger=triggercondition,
            effect=Effect(effects=args[-1]),
            condition=args[0] if len(args) > 1 else None
        )]
    def triggercondition(self, item):
        if item == TriggerEnum.endofturn:
            return Trigger(trigger=TriggerEnum.endofturn)
        elif isinstance(item, Phase):
            return Trigger(trigger=TriggerEnum.beginningofphase, phase=item)
        elif isinstance(item, Condition):
            return Trigger(trigger=TriggerEnum.condition, condition=item)
        return item
    def whenyouplay(self, item):
        return Trigger(trigger=TriggerEnum.whenplay, objects=item)
    def whengainlife(self, item):
        return Trigger(trigger=TriggerEnum.whengainlife, objects=item)
    def whenloselife(self, item):
        return Trigger(trigger=TriggerEnum.whenloselife, objects=item)
    def whendamaged(self, item):
        return Trigger(trigger=TriggerEnum.whendamaged, objects=item)
    def mod(self, power, health, *args):
        return ModAbility(stats=Stats(power=power, health=health), foreach=args[0] if args else None)
    def extracosts(self, *args):
        return list(args)
    def imperativescost(self, *args):
        return list(args)
    def imperativecost(self, item):
        return item
    def effects(self, item):
        return item
    def may(self, item, *args):
        # TODO: implement "When you do"
        return Effect(effects=item, op=OperatorEnum.OPTIONAL)
    def composedeffect(self, *args):
        return [c for c in args if isinstance(c, BaseEffect)]
    def effect(self, item):
        return item
    def imperative(self, item, *args):
        foreach = [c for c in args if isinstance(c, ObjectMatch)]
        # TODO: add conditional and where X
        return PlayerEffect(effects=[item], foreach=foreach[0] if foreach else None)
    def action(self, item):
        return item
    def objecteffect(self, obj, effect):
        effect.subj = obj
        return effect
    def playereffect(self, obj, effect):
        effect.subj = obj
        return effect
    def objectphrase(self, *args):
        condition = [c for c in args if isinstance(c, Condition)]
        foreach = [c for c in args if isinstance(c, ObjectMatch)]
        return ObjectEffect(
            effects=[c for c in args if isinstance(c, BaseEffect)],
            foreach=foreach[0] if foreach else None,
            condition=condition[0] if condition else None
        )  # TODO: add condition
    def playerphrase(self, *args):
        if isinstance(args[0], PlayerEffect):
            # TODO: add other modifiers or seconds effect
            return args[0]
        condition = [c for c in args if isinstance(c, Condition)]
        return PlayerEffect(
            effects=[c for c in args if isinstance(c, BaseEffect)],
            condition=condition[0] if condition else None
        )  # TODO: add for each
    def hasability(self, abilities, *args):
        return GetAbility(abilities=abilities, until=args[0] if args else None)
    def getsability(self, acquiredability, *args):
        m = [c for c in args if isinstance(c, ModAbility)]
        u = [c for c in args if isinstance(c, Condition)]
        return GetAbility(abilities=acquiredability + m, until=u[0] if u else None)
    def getsmod(self, mod, *args):
        m, u = [], []
        for a in args:
            if isinstance(a, Condition):
                u.append(a)
            else:
                m.append(a)
        return GetAbility(abilities=[mod] + m, until=u[0] if u else None)
    def objectcantdo(self, item, *args):
        return CantAbility(actions=item, until=args[0] if args else None)
    def noactivate(self, item):
        return NoActivationAbility(moment=item)
    def losesabilities(self, *args):
        return LoseAbilitiesAbility(until=args[0] if args else None)
    def costsless(self, item, *args):
        return CostsAbility(costs=item, foreach=args[0] if args else None)
    def costsmore(self, item, *args):
        return CostsAbility(costs=item, more=True, foreach=args[0] if args else None)
    def entersdeactivated(self, *args):
        return EntersAbility(deactivate=True, control=args[0] if args else None)
    def becomeswhat(self, item, *args):
        return BecomesAbility(what=item, additional=args)
    def deals(self, *args):
        r = [i for c in args if isinstance(c, tuple) for i in c]
        n = [c for c in args if not isinstance(c, tuple)]
        return DealsAbility(amount=n[0], recipients=r if r else [Reference.anytarget], spread=len(r) == 0)
    
    def damagerecipients(self, *args):
        return args
    def damagerecipient(self, item):
        return item
    def playercondition(self, player, phrase):
        return PlayerCondition(condition=ConditonEnum.playercond, subject=player, phrase=phrase)
    def objectcondition(self, object, phrase):
        kwargs = {'phrase': phrase}
        if isinstance(phrase, tuple):
            t = phrase[0]
            kwargs['phrase'] = t
            if t == ObjectPhraseEnum.blocked or t == ObjectPhraseEnum.targets:
                kwargs['object'] = phrase[1]
            elif t == ObjectPhraseEnum.whenenters:
                kwargs['possesion'] = phrase[1]
            elif t == ObjectPhraseEnum.moveszone:
                kwargs['into_zone'] = phrase[1]
                kwargs['from_zone'] = phrase[2]
            elif t == ObjectPhraseEnum.dealsdamage:
                kwargs['damagerecipients'] = phrase[1]
        return ObjectCondition(condition=ConditonEnum.objectcond, subject=object, **kwargs)
    def pc(self, item):
        return item
    def oc(self, item):
        return item
    def pp(self, item):
        return item
    def op(self, item):
        return item
    def acquiredability(self, *args):
        return [c for a in args for c in a] if args else ["this"]
    def tokenability(self, item):
        return item


@v_args(inline=True)
class CardTransformer(Transformer):
    def types(self, *items):
        main_types = []
        sub_types = []
        for i in items:
            if i in TypeEnum.__members__.values():
                main_types.append(i)
            else:
                sub_types.append(i)
        return main_types, sub_types
    
    def abilities(self, *args):
        return [i for a in args for i in a]
    
    def cardcost(self, *items):
        if items:
            return items[0]
        return []
    
    def root(self, _, cardcosts, types, abilities, *items):
        return Card(
            cost=cardcosts,
            types=[t.lower() for t in types[0]],   # TODO: add more types and subtypes
            subtypes=[t.lower() for t in types[1]],
            abilities=abilities,
            power=items[0].power if items else 0,
            health=items[0].health if items else 0,
        )


def is_keyword_line(text: str):
    for t in text.split(","):
        if t.strip().lower() not in KeywordEnum.__members__:
            return False
    return True


class Parser:
    def __init__(self, transformers: list[Transformer], grammar_path: str = "grammars/game.lark", debug: bool = True) -> None:
        self.grammar = open(grammar_path, "r").read()
        self.lark = Lark(self.grammar.format(name=f'"~"', types=TypeEnum.to_grammar(), keywords=KeywordEnum.to_grammar()), start="root", debug=debug)
        self.transformers = transformers
        self.debug = debug

    def parse(self, card: str, name: str | None = None):
        if name is None:
            name = card.split("\n", 1)[0].split(" {", 1)[0]
        card_txt = card.split("\n\n", 1)[0].replace(name, "~")
        t = self.lark.parse(card_txt)
        for tf in self.transformers:
            t = tf.transform(t)
        t.name = name
        rule_texts = []
        for line in card_txt.split("\n")[2:]:
            if is_keyword_line(line):
                for l in line.split(", "):
                    rule_texts.append(l)
            else:
                rule_texts.append(line)
        t.rule_texts = rule_texts
        return t
