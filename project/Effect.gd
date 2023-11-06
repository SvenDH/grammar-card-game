extends Resource
class_name Effect

@export var effects: Array[BaseEffect] = []
@export var optional: bool = false

func activate(ctx: Dictionary):
	# TODO: add optional check
	var played = []
	for e in effects:
		var res = await e.activate(ctx)
		if res == null:
			return null
		played.append_array(res)
	return await ctx.game.send(ctx, played)
