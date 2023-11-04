extends Resource
class_name Condition

enum ConditionEnum {
	playedwhen,
	yourturn,
	notyourturn,
	compare,
	playercond,
	objectcond,
	thisturn
}

@export var condition: ConditionEnum
@export var until: bool = false
