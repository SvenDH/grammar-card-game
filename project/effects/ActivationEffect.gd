extends BaseEffect

@export var objects: ObjectMatch
@export var deactivate: bool = true

func activate(ctx: Dictionary):
	var results = []
	for d in await ctx["game"].pick(ctx, objects, deactivate):
		results.append([d])
	return results

func resolve(player: CardPlayer, card: CardInstance, deactivate: bool):
	if deactivate:
		card.deactivate()
	else:
		card.activate()
