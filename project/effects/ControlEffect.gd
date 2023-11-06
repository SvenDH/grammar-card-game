extends BaseEffect

@export var objects: ObjectMatch
@export var until: Condition

func activate(ctx: Dictionary):
	var results = []
	var res = await ctx.game.pick(ctx, objects)
	if res == null:
		return null
	for d in res:
		results.append([d, until])
	return results
