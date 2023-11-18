extends CardResource
class_name ModAbility

@export var stats: Array = []
@export var foreach: ObjectMatch

func get_stats(ability: Ability):
	var game = ability.game
	var n = 1
	if foreach != null:
		n = len(await game.pick(ability, foreach, ZoneMatch.ZoneEnum.board))
	return [stats[0] * n, stats[1] * n]
