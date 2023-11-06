extends BaseEffect

@export var objects: ObjectMatch
@export var deactivate: bool = true

func activate(ctx: Dictionary):
	var results = []
	var res = await ctx.game.pick(ctx, objects)
	if res == null:
		return null
	for d in res:
		results.append([d])
	return results

func resolve(player: CardPlayer, card: CardInstance, deactivate: bool):
	if card.location == ZoneMatch.ZoneEnum.board:
		if deactivate:
			card.deactivate()
		else:
			card.activate()
