extends BaseEffect

@export var objects: ObjectMatch
@export var until: Condition

func activate(ctx: Dictionary):
	var results = []
	for d in ctx["game"].pick(ctx, objects):
		results.append([d, until])
	return results
