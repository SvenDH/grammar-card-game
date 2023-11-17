extends BaseEffect

@export var objects: ObjectMatch

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ctx: Dictionary):
	var results = []
	var res = await ctx.controller.game.pick(ctx, objects, ZoneMatch.ZoneEnum.board)
	if res == null:
		return null
	for d in res:
		results.append([d])
	return results
	
func resolve(player: CardPlayer, card: CardInstance):
	if card.location == ZoneMatch.ZoneEnum.board:
		card.controller.remove(card)
		card.player_owner.place(card, ZoneMatch.ZoneEnum.pile)
		card.on_destroy()
