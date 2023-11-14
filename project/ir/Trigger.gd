extends CardResource
class_name Trigger

enum TriggerEnum {
	whenplay,
	whengainlife,
	whenloselife,
	whendamaged,
	endofturn,
	beginningofphase,
	condition
}

@export var trigger: TriggerEnum
@export var objects: ObjectMatch
@export var players: PlayerMatch
@export var condition: Condition
@export var phase: Phase
