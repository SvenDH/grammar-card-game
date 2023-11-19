extends Match
class_name ObjectMatch

@export var objects: Array = []
@export var each: bool = false

func targets(ability: Ability):
	for o in objects:
		var n = o.targets(ability)
		if n > 0:
			return n
	return -1

func has_target() -> bool:
	for o in objects:
		if o.has_target():
			return true
	return false

func match_query(ability: Ability, other) -> bool:
	for o in objects:
		if not o.match_query(ability, other):
			return false
	return true
