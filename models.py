from typing import Literal, Any
from pydantic import BaseModel
from godot_parser import GDResource, GDSection, GDSectionHeader, GDExtResourceSection, GDSubResourceSection, ExtResource, SubResource

from constants import *


def encode_numberorx(num: NumberOrX):
    if num == "X":
        return 9999999999999999
    elif num == "-X":
        return -9999999999999999
    elif num == "that":
        return 8888888888888888
    return int(num)


class Stats(BaseModel):
    power: NumberOrX = 0
    health: NumberOrX = 0


class BaseEffect(BaseModel):
    pass


class Prefix(BaseModel):
    prefix: PrefixEnum | TypeEnum | ColorEnum | Stats = PrefixEnum.none
    non: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Prefix.gd", "Script").reference
        if isinstance(self.prefix, PrefixEnum):
            ability["prefix"] = PrefixEnum.to_int(self.prefix)
        elif isinstance(self.prefix, TypeEnum):
            ability["type"] = TypeEnum.to_int(self.prefix)
        elif isinstance(self.prefix, ColorEnum):
            ability["color"] = ColorEnum.to_int(self.prefix)
        elif isinstance(self.prefix, Stats):
            ability["stats"] = [self.prefix.power, self.prefix.health]
        ability["non"] = self.non
        return ability.reference


class Suffix(BaseModel):
    suffix: SuffixEnum = SuffixEnum.none
    subj: Any = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Suffix.gd", "Script").reference
        ability["suffix"] = SuffixEnum.to_int(self.suffix)
        if isinstance(self.suffix, ZoneMatch):
            ability["zones"] = [z.to_godot(resource) for z in self.subj]
        elif self.suffix is not None:
            ability["subj"] = self.suffix.to_godot(resource)
        return ability.reference


class BaseObject(BaseModel):
    def to_godot(self, resource: GDResource):
        pass


class ObjectMatch(BaseModel):
    objects: list[BaseObject] = []
    each: bool = False

    def to_godot(self, resource: GDResource):
        
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Object.gd", "Script").reference
        ability["objects"] = [o.to_godot(resource) for o in self.objects]
        ability["each"] = self.each
        return ability.reference


class PlayerMatch(BaseModel):
    player: PlayerEnum = PlayerEnum.none
    ref: Reference | ObjectMatch | None = None
    extra: NumberOrX = 0  # TODO: implement player extra (target count etc)
    who_cant: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Player.gd", "Script").reference
        ability["player"] = PlayerEnum.to_int(self.player)
        if isinstance(self.ref, ObjectMatch):
            ability["object"] = self.ref.to_godot(resource)
        elif self.ref is not None:
            ability["ref"] = Reference.to_int(self.ref)
        ability["extra"] = encode_numberorx(self.extra)
        ability["who_cant"] = self.who_cant
        return ability.reference

class ZoneMatch(BaseModel):
    zones: list[ZoneEnum] = []
    ref: PlayerMatch | None = None
    # Used for placement
    place: PlaceEnum = PlaceEnum.none
    random: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Zone.gd", "Script").reference
        ability["zones"] = [ZoneEnum.to_int(z) for z in self.zones]
        ability["ref"] = self.ref.to_godot(resource) if self.ref else None
        ability["place"] = PlaceEnum.to_int(self.place)
        ability["random"] = self.random
        return ability.reference


class Effect(BaseEffect):
    effects: list[BaseEffect] = []
    op: OperatorEnum = OperatorEnum.AND

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Effect.gd", "Script").reference
        ability["effects"] = [e.to_godot(resource) for e in self.effects]
        ability["optional"] = self.op == OperatorEnum.OPTIONAL
        return ability.reference


class DamageRecipients(BaseModel):
    recipients: list[PlayerMatch | ObjectMatch | Reference] = []
    targets: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/DamageRecipients.gd", "Script").reference
        ability["recipients"] = [Reference.to_int(r) if isinstance(r, Reference) else r.to_godot(resource) for r in self.recipients]
        ability["targets"] = self.targets
        return ability.reference


class NumberDef(BaseModel):
    amount: ObjectMatch | Reference
    property: NumbericalEnum | None = None


class Condition(BaseModel):
    condition: ConditonEnum
    until: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Condition.gd", "Script").reference
        ability["condition"] = ConditonEnum.to_int(self.condition)
        ability["until"] = self.until
        return ability.reference


class PlayedCondition(Condition):
    object: ObjectMatch
    duration: Condition

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/PlayedCondition.gd", "Script").reference
        ability["condition"] = ConditonEnum.to_int(self.condition)
        ability["until"] = self.until
        ability["object"] = self.object.to_godot(resource)
        ability["duration"] = self.duration.to_godot(resource)
        return ability.reference


class ObjectCondition(Condition):
    subject: ObjectMatch
    phrase: ObjectPhraseEnum
    object: ObjectMatch | None = None
    possesion: PlayerMatch | None = None
    into_zone: ZoneMatch | None = None
    from_zone: ZoneMatch | None = None
    damagerecipients: DamageRecipients | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/ObjectCondition.gd", "Script").reference
        ability["condition"] = ConditonEnum.to_int(self.condition)
        ability["until"] = self.until
        ability["subject"] = self.subject.to_godot(resource)
        ability["phrase"] = ObjectPhraseEnum.to_int(self.phrase)
        ability["object"] = self.object.to_godot(resource) if self.object else None
        ability["possesion"] = self.possesion.to_godot(resource) if self.possesion else None
        ability["into"] = self.into_zone.to_godot(resource) if self.into_zone else None
        ability["from"] = self.from_zone.to_godot(resource) if self.from_zone else None
        ability["damagerecipients"] = self.damagerecipients.to_godot(resource) if self.damagerecipients else None
        return ability.reference


class NumberCondition(Condition):
    number: str
    compare: str   # TODO: implement compare


class PlayerCondition(Condition):
    subject: PlayerMatch
    phrase: str   # TODO: implement playerphrase


class Phase(BaseModel):
    phase: PhaseEnum
    turn: TurnQualifierEnum = TurnQualifierEnum.none
    ref: Reference = Reference.none
    player: PlayerMatch | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Trigger.gd", "Script").reference
        ability["phase"] = PhaseEnum.to_int(self.phase)
        ability["turn"] = TurnQualifierEnum.to_int(self.turn)
        ability["ref"] = Reference.to_int(self.ref)
        ability["player"] = self.player.to_godot(resource) if self.player else None
        return ability.reference
    

class Trigger(BaseModel):
    trigger: TriggerEnum
    objects: ObjectMatch | PlayerMatch | None = None
    condition: Condition | None = None
    phase: Phase | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Trigger.gd", "Script").reference
        ability["trigger"] = TriggerEnum.to_int(self.trigger)
        ability["objects"] = self.objects.to_godot(resource) if isinstance(self.objects, ObjectMatch) else None
        ability["players"] = self.objects.to_godot(resource) if isinstance(self.objects, PlayerMatch) else None
        ability["condition"] = self.condition.to_godot(resource) if isinstance(self.condition, Condition) else None
        ability["phase"] = self.phase.to_godot(resource) if self.phase else None
        return ability.reference


class TriggeredAbility(BaseModel):
    trigger: Trigger
    effect: Effect
    condition: Condition | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/TriggeredAbility.gd", "Script").reference

        return ability.reference


class ActivatedAbility(BaseModel):
    costs: list[ColorEnum | NumberOrX | Activation | BaseEffect] = []
    effect: Effect

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/ActivatedAbility.gd", "Script").reference
        ability["costs"] = [c.to_godot(resource) if isinstance(c, BaseEffect) else c for c in self.costs]
        ability["effect"] = self.effect.to_godot(resource)
        return ability.reference

AquiredAbilities = KeywordEnum | TriggeredAbility | ActivatedAbility | BaseEffect | Effect | Literal["this"]


def ability_to_godot(resource: GDResource, ability: AquiredAbilities | None = None):
    if ability is None:
        return None
    if isinstance(ability, BaseModel):
        return ability.to_godot(resource)
    # TODO: keyword to resource
    return ability.capitalize()


class CardObject(BaseObject):
    ref: Reference = Reference.none
    type: TypeEnum = TypeEnum.none
    extra: NumberOrX = 0
    prefixes: list[Prefix] = []
    suffixes: list[Suffix] = []
    withwhat: AquiredAbilities | None = None
    without: KeywordEnum = KeywordEnum.none
    copies: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/Card.gd", "Script").reference
        ability["ref"] = Reference.to_int(self.ref)
        ability["type"] = TypeEnum.to_int(self.type)
        ability["extra"] = encode_numberorx(self.extra)
        ability["prefixes"] = [p.to_godot(resource) for p in self.prefixes]
        ability["suffixes"] = [s.to_godot(resource) for s in self.suffixes]
        ability["withwhat"] = ability_to_godot(resource, self.withwhat)
        ability["without"] = KeywordEnum.to_int(self.without)
        ability["copies"] = self.copies
        return ability.reference


class AbilityObject(BaseObject):
    ref: Reference | NumberOrX | None = None
    extra: NumberOrX = 0


class SubjEffect(BaseEffect):
    effects: list[BaseEffect] = []
    foreach: ObjectMatch | None = None
    condition: Condition | None = None
    
    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/SubjectEffect.gd", "Script").reference
        ability["effects"] = [o.to_godot(resource) for o in self.effects]
        ability["subject"] = self.subj.to_godot(resource)
        ability["foreach"] = self.foreach.to_godot(resource) if self.foreach else None
        ability["condition"] = self.condition.to_godot(resource) if self.condition else None
        return ability.reference


class PlayerEffect(SubjEffect):
    subj: PlayerMatch = PlayerMatch(player=PlayerEnum.you)


class ObjectEffect(SubjEffect):
    subj: ObjectMatch = ObjectMatch(objects=[BaseObject(object=Reference.it)])


class CreateTokenEffect(BaseEffect):
    number: NumberOrX = 1
    stats: Stats = Stats()
    abilities: list[AquiredAbilities] = []

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/TokenEffect.gd", "Script").reference
        ability["number"] = encode_numberorx(self.number)
        ability["stats"] = [self.stats.power, self.stats.health]
        ability["abilities"] = [ability_to_godot(resource, a) for a in self.abilities]
        return ability.reference


class DestroyEffect(BaseEffect):
    objects: ObjectMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/DestroyEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        return ability.reference


class CopyEffect(BaseEffect):
    objects: ObjectMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/CopyEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        return ability.reference
    

class PlayEffect(BaseEffect):
    objects: ObjectMatch
    free: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/PlayEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        ability["free"] = self.free
        return ability.reference


class DrawEffect(BaseEffect):
    number: NumberOrX = 1

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/DrawEffect.gd", "Script").reference
        ability["number"] = encode_numberorx(self.number)
        return ability.reference


class DiscardEffect(BaseEffect):
    number: NumberOrX = 1
    objects: ObjectMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/DiscardEffect.gd", "Script").reference
        ability["number"] = encode_numberorx(self.number)
        ability["objects"] = self.objects.to_godot(resource)
        return ability.reference


class SearchEffect(BaseEffect):
    number: NumberOrX = 1
    zones: ZoneMatch
    objects: ObjectMatch | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/SearchEffect.gd", "Script").reference
        ability["number"] = encode_numberorx(self.number)
        ability["zones"] = self.zones.to_godot(resource)
        ability["objects"] = self.objects.to_godot(resource) if self.objects else None
        return ability.reference


class ShuffleEffect(BaseEffect):
    what: ZoneMatch | ObjectMatch | None = None
    zones: ZoneMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/ShuffleEffect.gd", "Script").reference
        ability["what"] = self.what.to_godot(resource) if self.what else None
        ability["zones"] = self.zones.to_godot(resource)
        return ability.reference


class CounterEffect(BaseEffect):
    objects: ObjectMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/CounterEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        return ability.reference


class ExtraTurnEffect(BaseEffect):
    number: NumberOrX = 1

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/ExtraTurnEffect.gd", "Script").reference
        ability["number"] = encode_numberorx(self.number)
        return ability.reference


class LookEffect(BaseEffect):
    number: NumberOrX = 1
    zones: ZoneMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/LookEffect.gd", "Script").reference
        ability["number"] = encode_numberorx(self.number)
        ability["zones"] = self.zones.to_godot(resource)
        return ability.reference


class PutEffect(BaseEffect):
    objects: ObjectMatch
    into: ZoneMatch
    deactivated: bool = False
    second_objects: ObjectMatch | None = None
    second_into: ZoneMatch | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/PutEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        ability["into"] = self.into.to_godot(resource)
        ability["deactivated"] = self.deactivated
        ability["second_objects"] = self.second_objects.to_godot(resource) if self.second_objects else None
        ability["second_into"] = self.second_into.to_godot(resource) if self.second_into else None
        return ability.reference


class GainControlEffect(BaseEffect):
    objects: ObjectMatch
    until: Condition | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/ControlEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        ability["until"] = self.until.to_godot(resource) if self.until else None
        return ability.reference


class SwitchStatsEffect(BaseEffect):
    objects: ObjectMatch
    until: Condition | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/SwitchEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        ability["until"] = self.until.to_godot(resource) if self.until else None
        return ability.reference


class AddEssenceEffect(BaseEffect):
    colors: list[str] = []
    amount: NumberOrX = 1

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/EssenceEffect.gd", "Script").reference
        ability["colors"] = self.colors
        ability["amount"] = self.amount
        return ability.reference


class ActivationEffect(BaseEffect):
    objects: ObjectMatch
    deactivate: bool = True

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/ActivationEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        ability["deactivate"] = self.deactivate
        return ability.reference


class SacrificeEffect(BaseEffect):
    objects: ObjectMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/SacrificeEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        return ability.reference


class PayessenceEffect(BaseEffect):
    costs: list[ColorEnum | NumberOrX]

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/PayessenceEffect.gd", "Script").reference
        ability["costs"] = [c if isinstance(c, ColorEnum) else encode_numberorx(c) for c in self.costs]
        return ability.reference


class PaylifeEffect(BaseEffect):
    costs: NumberOrX

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/PaylifeEffect.gd", "Script").reference
        ability["costs"] = encode_numberorx(self.costs)
        return ability.reference


class RevealEffect(BaseEffect):
    player: PlayerMatch

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/RevealEffect.gd", "Script").reference
        ability["player"] = self.player.to_godot(resource)
        return ability.reference


class MoveEffect(BaseEffect):
    objects: ObjectMatch
    tozone: ZoneMatch
    fromzone: ZoneMatch | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/MoveEffect.gd", "Script").reference
        ability["objects"] = self.objects.to_godot(resource)
        ability["tozone"] = self.tozone.to_godot(resource)
        ability["fromzone"] = self.fromzone.to_godot(resource) if self.fromzone else None
        return ability.reference


class ModAbility(BaseEffect):
    stats: Stats = Stats()
    foreach: ObjectMatch | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://ir/ModAbility.gd", "Script").reference
        ability["stats"] = [self.stats.power, self.stats.health]
        ability["foreach"] = self.foreach.to_godot(resource) if self.foreach else None
        return ability.reference


class GetAbility(BaseEffect):
    abilities: list[AquiredAbilities | ModAbility] = []
    until: Condition | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/GetAbility.gd", "Script").reference
        ability["abilities"] = [ability_to_godot(resource, a) for a in self.abilities]
        ability["until"] = self.until.to_godot(resource) if self.until else None
        return ability.reference


class CantAbility(BaseEffect):
    actions: list[ObjectActionEnum] = []
    until: Condition | None = None

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/CantAbility.gd", "Script").reference
        ability["actions"] = [ObjectActionEnum.to_int(a) for a in self.actions]
        ability["until"] = self.until.to_godot(resource) if self.until else None
        return ability.reference


class NoActivationAbility(BaseEffect):
    moment: Phase
    
    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/NoActivationAbility.gd", "Script").reference
        ability["moment"] = self.moment.to_godot(resource)
        return ability.reference


class LoseAbilitiesAbility(BaseEffect):
    until: Condition | None = None
    
    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/LoseAbilitiesAbility.gd", "Script").reference
        ability["until"] = self.until.to_godot(resource) if self.until else None
        return ability.reference


class CostsAbility(BaseEffect):
    costs: list[ColorEnum | NumberOrX]
    more: bool = False
    foreach: ObjectMatch | None = None


class EntersAbility(BaseEffect):
    deactivate: bool = False
    control: PlayerMatch | Reference | None = None


class BecomesAbility(BaseEffect):
    what: list[ColorEnum | TypeEnum | Stats] = []
    additional: bool = False


class DealsAbility(BaseEffect):
    amount: NumberOrX | NumberDef = 1
    recipients: list[PlayerMatch | ObjectMatch | Reference] = []
    spread: bool = False

    def to_godot(self, resource: GDResource):
        ability = resource.add_sub_resource("Resource")
        ability["script"] = resource.add_ext_resource("res://effects/DealsAbility.gd", "Script").reference
        ability["amount"] = self.amount.to_godot(resource) if isinstance(self.amount, NumberDef) else self.amount
        ability["recipients"] = [r.to_godot(resource) if isinstance(r, (PlayerMatch, ObjectMatch)) else Reference.to_int(r) for r in self.recipients]
        ability["spread"] = self.spread
        return ability.reference


class Godot4Resource(GDResource):
    def add_ext_resource(self, path: str, type: str) -> GDExtResourceSection:
        next_id = 1 + max([s.id for s in self.get_ext_resources()] + [s.id for s in self.get_sub_resources()] + [0])
        section = GDExtResourceSection(path, type, next_id)
        self.add_section(section)
        return section

    def add_sub_resource(self, type: str, **kwargs) -> GDSubResourceSection:
        next_id = 1 + max([s.id for s in self.get_ext_resources()] + [s.id for s in self.get_sub_resources()] + [0])
        section = GDSubResourceSection(type, next_id, **kwargs)
        self.add_section(section)
        return section
    
    def renumber_resource_ids(self):
        """Refactor all resource IDs to be sequential with no gaps"""
        self._renumber_resource_ids(self.get_ext_resources() + self.get_sub_resources(), (ExtResource, SubResource))

    def get_subresource_refs(self, section: GDSubResourceSection):
        refs = []
        for val in section.properties.values():
            if isinstance(val, SubResource):
                refs.append(val.id)
            elif isinstance(val, list):
                for i in val:
                    if isinstance(i, SubResource):
                        refs.append(i.id)
            elif isinstance(val, dict):
                for i in val.keys():
                    if isinstance(i, SubResource):
                        refs.append(i.id)
                for i in val.values():
                    if isinstance(i, SubResource):
                        refs.append(i.id)
        return refs

    def sort_subsections(self):
        subresources = self.get_sub_resources()
        graph = {}
        visited = {}
        idmap = {}
        for sub in subresources:
            self.remove_section(sub)
            graph[sub.id] = self.get_subresource_refs(sub)
            idmap[sub.id] = sub
            visited[sub.id] = False
        
        stack = []
        for i in idmap.keys():
            if visited[i] == False:
                self.topological_sort(graph, i, visited, stack)
        for i in reversed(stack):
            self.add_section(idmap[i])
    
    def topological_sort(self, graph, v, visited, stack):
        visited[v] = True
        for i in graph[v]:
            if visited[i] == False:
                self.topological_sort(graph, i, visited, stack)

        stack.insert(0, v)


class Card(BaseModel):
    name: str = ''
    cost: list[ColorEnum | NumberOrX] = [0]
    types: list[TypeEnum] = []
    subtypes: list[str] = []
    abilities: list[AquiredAbilities] = []
    rule_texts: list[str] = []
    power: int = 1
    health: int = 1
    
    def __str__(self) -> str:
        costs = "}{".join([str(c) for c in self.cost])
        t = " ".join([t.capitalize() for t in self.types])
        if self.subtypes:
            t += " - " + " ".join([t.capitalize() for t in self.subtypes])
        a = "\n".join(self.rule_texts)
        return f"{self.name} {{{costs}}}\n{t}\n{a}\n{self.power}/{self.health}"

    def to_godot(self, path):
        resource = Godot4Resource()
        head = resource.get_sections()[0]
        # For godot 4 add type and script to resource
        head.header["type"] = "Resource"
        head.header["script_class"] = "Card"
        
        card = GDSection(GDSectionHeader("resource"))
        card["script"] = resource.add_ext_resource("res://Card.gd", "Script").reference
        card["name"] = self.name
        card["costs"] = self.cost
        card["types"] = [TypeEnum.to_int(t) for t in self.types]
        card["subtypes"] = self.subtypes
        card["abilities"] = [ability_to_godot(resource, a) for a in self.abilities]
        for text, ref in zip(self.rule_texts, card["abilities"]):
            if isinstance(ref, SubResource):
                resource.find_section(id=ref.id)["text"] = text

        card["power"] = encode_numberorx(self.power)
        card["health"] = encode_numberorx(self.health)
        resource.add_section(card)
        
        resource.sort_subsections()
        resource.write(path)
        return resource
