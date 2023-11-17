extends BaseEffect

@export var objects: ObjectMatch

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ctx: Dictionary):
	var results = []
	var res = await ctx.game.pick(ctx, objects, ZoneMatch.ZoneEnum.board)
	if res == null:
		return null
	for d in res:
		results.append([d])
	return results
	
func resolve(player: CardPlayer, card: CardInstance):
	if card.location == ZoneMatch.ZoneEnum.board:
		await card.controller.remove(card)
		await card.player_owner.place(card, ZoneMatch.ZoneEnum.pile)
		await card.on_destroy()
