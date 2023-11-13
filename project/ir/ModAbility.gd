extends CardResource
class_name ModAbility

@export var stats: Array = []
@export var foreach: ObjectMatch

func get_stats(ctx: Dictionary):
	var game = ctx.game
	var n = 1
	if foreach != null:
		n = len(await game.pick(ctx, foreach, ZoneMatch.ZoneEnum.board))
	return [stats[0] * n, stats[1] * n]
