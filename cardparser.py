from lark import Lark, Tree, Token

from models import *


class PureObject(str, GrammarEnum):
    ability = "ability"
    token = "token"
    card = "card"
    copies = "copies"


def to_numberorx(x):
    try:
        return int(x)
    except:
        return str(x)


def from_pureobject(
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


def from_tree(tree: Tree | Token):
    if isinstance(tree, Token):
        t = tree
        if t in list(ObjectRef):
            return ObjectRef(tree)
        return t
    
    match tree.data:
        case "root":
            types = tree.children[2].children[0].children
            return Card(
                cost=[from_tree(c.children[0]) for c in tree.children[1].children],
                type=[types[0].lower()],   # TODO: add more types and subtypes
                subtype=[types[1].lower()] if len(types) > 1 else [],
                abilities=[i for a in tree.children[3].children for i in from_tree(a)],
                damage=from_tree(tree.children[4].children[0]),
                health=from_tree(tree.children[4].children[1]),
            )
        case "essencecost":
            if isinstance(tree.children[0], Token):
                return EssenceCosts(costs=[from_tree(e) for e in tree.children])
            return EssenceCosts(costs=[from_tree(e) for e in tree.children[0].children])
        case "activationcost":
            if tree.children[0].data == "deactivatecost":
                return Activation.deactivate
            return Activation.activate
        case "referenceprefix":
            r = from_tree(tree.children[0])
            if isinstance(r, int):
                return (Reference.exactly, r)
            return r
        case "pureobject":
            return from_tree(tree.children[0])
        case "object":
            r = from_tree(tree.children[0])
            if isinstance(r, PureObject):
                return from_pureobject(r)
            elif isinstance(r, TypeEnum):
                return CardObject(type=r)
            return r
        case "selfref":
            return CardObject(ref=ObjectRef.self)
        case "objects":
            each = False
            objs = [from_tree(i) for i in tree.children]
            if len(objs) > 1 and objs[0] == Reference.each:
                objs = objs[1:]
                each = True
            return Objects(objects=objs, each=each)
        case "specifiedobject":
            r = from_tree(tree.children[0]) if tree.children[0].data == "referenceprefix" else None
            e = None
            if r and isinstance(r, tuple):
                if len(r) > 1:
                    e = r[1]
                r = r[0]
            suffix = from_tree(tree.children[-1]) if tree.children[-1].data == "suffix" else None
            prefixes = [from_tree(c) for c in tree.children if c.data == "prefix"]
            w = [from_tree(c) for c in tree.children if c.data == "with"]
            wo = [from_tree(c) for c in tree.children if c.data == "keyword"]
            o = from_tree(tree.children[-2] if suffix else tree.children[-1])
            return from_pureobject(
                o,
                ref=r,
                prefixes=prefixes,
                suffix=suffix,
                extra=e,
                withwhat=w[0] if w else None,
                without=wo[0] if wo else None
            )
        case "with":
            # TODO: implement more with clauses (numbercompare, highestnumber, whatlevel)
            return from_tree(tree.children[0])
        case "keyword":
            return from_tree(tree.children[0])
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
            t = from_tree(tree.children[0])
            if isinstance(t, Player):
                return t
            elif t == PlayerRef.their:
                return Player(player=PlayerEnum.they)
            return Player(player=PlayerEnum.you)
        case "ability":
            return from_tree(tree.children[0])
        case "keywords":
            return [i.children[0].lower() for i in tree.children]
        case "activatedability":
            return [ActivatedAbility(
                costs=[from_tree(t) for t in tree.children[0].children],
                effect=Effect(effects=from_tree(tree.children[1]))
            )]
        case "triggeredability":
            return [TriggeredAbility(
                trigger=from_tree(tree.children[0]),
                effect=Effect(effects=from_tree(tree.children[-1])),
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
        case "noncolor":
            return (from_tree(tree.children[0].children[0]), True)
        case "color":
            return (from_tree(tree.children[0]), False)
        case "red":
            return ColorEnum.red
        case "green":
            return ColorEnum.green
        case "blue":
            return ColorEnum.blue
        case "yellow":
            return ColorEnum.yellow
        case "colorless":
            return ColorEnum.colorless
        case "multicolored":
            return ColorEnum.multicolored
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
            return [from_tree(c) for c in tree.children if isinstance(c, Tree) and c.data == "effect"]
        case "effect":
            return from_tree(tree.children[0])
        case "imperative":
            return PlayerEffect(
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
            return ObjectEffect(effects=p, op=o[0] if o else None)  # TODO: add condition
        case "playerphrase":
            return PlayerEffect(
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
                abilities=[from_tree(tree.children[0])] + m,
                until=u[0] if u else None
            )
        case "getsmod":
            m = [from_tree(c) for c in tree.children if c.data == "acquiredability"]
            u = [from_tree(c) for c in tree.children if c.data == "until"]
            return GetAbility(
                abilities=[from_tree(tree.children[0])] + m,
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
        case "dealswhat":
            return from_tree(tree.children[0])
        case "deals":
            r = [i for c in tree.children if c.data == "damagerecipients" for i in from_tree(c)]
            n = [from_tree(c) for c in tree.children if c.data == "numberorxorthat" or c.data == "numberdefinition"]
            return DealsAbility(
                amount=n[0],
                recipients=r if r else [DamageRef.anytarget],
                spread=len(r) == 0
            )
        case "damagerecipients":
            return [from_tree(c) for c in tree.children if c.data == "damagerecipient"]
        case "numberdefinition":
            o = [from_tree(c) for c in tree.children if c.data == "objects"]
            n = [from_tree(c) for c in tree.children if c.data == "numberical"]
            return NumberDef(
                amount=o[0] if len(o) > 0 else from_tree(tree.children[0]),
                property=n[0] if len(n) > 0 else None
            )
        case "numberical":
            return from_tree(tree.children[0])
        case "damage":
            return NumbericalEnum.damage
        case "health":
            return NumbericalEnum.health
        case "level":
            return NumbericalEnum.level
        case "anytarget":
            return DamageRef.anytarget
        case "itself":
            return DamageRef.itself
        case "objectcant":
            a = from_tree(tree.children[0])
            if not isinstance(a, tuple):
                a = (a, )
            return a
        case "into":
            if tree.children[0].data == "field":
                return Into(zones=[ZoneEnum.board])
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
                return Zone(zones=[ZoneEnum.board])
            return Zone(
                ref=from_tree(t) if t.data == "possesion" else None,
                zones=[from_tree(i) for i in tree.children if i.data == "zone"]
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
            return DiscardEffect(
                number=from_tree(tree.children[1]) if len(tree.children) > 1 else 1,
                objects=from_tree(tree.children[1]) if len(tree.children) > 2 else Objects(objects=[CardObject()])
            )
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
            ref = None
            if isinstance(p, tuple):
                ref = p[0]
                p = p[1]
            return Player(
                player=p,
                ref=ref,
                who_cant=len(tree.children) > 1
            )
        case "p":
            t = tree.children[0]
            if t.data == "defending":
                return PlayerEnum.defending
            elif t.data == "attacking":
                return PlayerEnum.attacking
            elif t.data == "itspossesion":
                return (from_tree(tree.children[0]), from_tree(tree.children[1]))
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
            return (TypeEnum.TOKEN, False)
        case "nontoken":
            return (TypeEnum.TOKEN, True)
        case "attacking":
            return (PrefixEnum.attacking, False)
        case "blocking":
            return (PrefixEnum.blocking, False)
        case "attackingorblocking":
            return (PrefixEnum.attackingorblocking, False)
        case "nontype":
            return (from_tree(tree.children[1]), True)
        case "stats":
            return (to_numberorx(from_tree(tree.children[0])), to_numberorx(from_tree(tree.children[1])))
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
                return TypeEnum(tree.children[0].children[0].lower())
            return PureObject.card
        case "hand":
            return ZoneEnum.hand
        case "deck":
            return ZoneEnum.deck
        case "discardzone":
            return ZoneEnum.pile
        case "refsacrificed":
            return ObjectRef.sac
        case "anyof":
            return ObjectRef.any
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
        case "target":
            return tuple([Reference.target] + [from_tree(c) for c in tree.children])
        case "countable":
            return from_tree(tree.children[0])
        case "reference":
            return from_tree(tree.children[0])
        case "opandorthen":
            return from_tree(tree.children[0])
        case "opandor":
            return from_tree(tree.children[0])
        case "its":
            return PlayerRef.their
        case "their":
            return PlayerRef.their
        case "your":
            return PlayerRef.your
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


class Parser:
    def __init__(self, grammar_path: str = "grammars/game.lark", debug: bool = True) -> None:
        self.grammar = open(grammar_path, "r").read()
        self.lark = Lark(self.grammar.format(name=f'"~"', types=TypeEnum.to_grammar(), keywords=KeywordEnum.to_grammar()), start="root", debug=debug)
        self.debug = debug

    def parse(self, card: str, name: str | None = None):
        if name is None:
            name = " ".join(card.split("\n", 1)[0].split(" ")[:-1])
        card_txt = card.split("\n\n", 1)[0].replace(name, "~")
        t = self.lark.parse(card_txt)
        c = from_tree(t)
        c.name = name
        c.rule_texts = card_txt.split("\n")[2:-1]
        return c
