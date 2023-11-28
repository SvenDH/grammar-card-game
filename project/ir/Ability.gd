extends Match
class_name AbilityMatch

@export var essence: bool = false

func match_query(ability: Ability, other) -> bool:
	if not other is CardInstance:
		return false
	
	if essence and not other.is_essence_ability():
		return false
	
	return true
