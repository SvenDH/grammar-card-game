extends BaseEffect

@export var objects: ObjectMatch

func activate(ctx: Dictionary):
	var results = []
	for d in ctx["game"].pick(ctx, objects, ZoneMatch.ZoneEnum.stack):
		results.append([d])
	return results

func resolve(player: CardPlayer, obj):
	assert(obj in player.game.stack)
	player.game.stack.remove(obj)
	player.on_counter(obj)