extends BaseEffect

@export var objects: ObjectMatch

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
		player.remove(card)
		player.place(card, ZoneMatch.ZoneEnum.pile)
		card.on_destroy()
