extends Match
class_name PlayerMatch

enum PlayerEnum {
	none,
	opponent,
	player,
	you,
	they,
	owner,
	controller,
	defending,
	attacking
}

@export var player: PlayerEnum
@export var ref: Reference
@export var object: ObjectMatch
@export var extra: int  # TODO: implement player extra (target count etc)
@export var who_cant: bool = false

func targets(_ctx: Dictionary) -> int:
	if ref == Reference.target:
		if extra != null:
			# TODO: implement get X
			return extra
		return 1
	return -1

func match_query(ability: Ability, other) -> bool:
	if not other is CardPlayer:
		return false
	elif player == PlayerEnum.you and ability.ctx.controller != other:
		return false
	elif player == PlayerEnum.opponent and ability.ctx.controller == other:
		return false
	# TODO: add owner and controller checks
	elif player == PlayerEnum.attacking:
		if "attacking" not in ability.ctx or ability.ctx.attacking != other:
			return false
	elif player == PlayerEnum.defending:
		if "defending" not in ability.ctx or ability.ctx.defending != other:
			return false
	return true
