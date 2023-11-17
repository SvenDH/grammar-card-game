extends BaseEffect

@export var objects: ObjectMatch
@export var deactivate: bool = true

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ctx: Dictionary):
	var results = []
	var res = await ctx.game.pick(ctx, objects)
	if res == null:
		return null
	for d in res:
		results.append([d])
	return results

func resolve(_player: CardPlayer, card: CardInstance):
	if card.location == ZoneMatch.ZoneEnum.board:
		if deactivate:
			await card.deactivate()
		else:
			await card.activate()
