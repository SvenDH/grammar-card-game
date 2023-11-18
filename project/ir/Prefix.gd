extends Match
class_name PrefixMatch

enum PrefixEnum {
	none,
	activated,
	attacking,
	blocking,
	attackingorblocking
}

@export var prefix: PrefixEnum
@export var type: Card.TypeEnum
@export var color: Card.ColorEnum
@export var stats: Array
@export var non: bool = false

func match_query(ability: Ability, other) -> bool:
	if non:
		if type and other.type == type:
			return false
		elif prefix:
			if prefix == PrefixEnum.activated and other.activated:
				return false
			elif prefix == PrefixEnum.attacking and other.attacking:
				return false
			elif prefix == PrefixEnum.blocking  and other.blocking:
				return false
			elif prefix == PrefixEnum.attackingorblocking and (other.attacking or other.blocking):
				return false
		elif stats and other.damage == stats[0] and other.health == stats[1]:
			return false
		elif color and color in other.color:
			return false
	else:
		if type and other.type != type:
			return false
		elif prefix:
			if prefix == PrefixEnum.activated and not other.activated:
				return false
			elif prefix == PrefixEnum.attacking and not other.attacking:
				return false
			elif prefix == PrefixEnum.blocking  and not other.blocking:
				return false
			elif prefix == PrefixEnum.attackingorblocking and not (other.attacking or other.blocking):
				return false
		elif stats and not (other.damage == stats[0] and other.health == stats[1]):
			return false
		elif color and color not in other.color:
			return false
	return true
