extends BaseEffect

@export var objects: ObjectMatch

func activate(ctx: Dictionary):
	var results = []
	for d in ctx["game"].pick(ctx, objects, ZoneMatch.ZoneEnum.board):
		results.append([d])
	return results
	
func resolve(player: CardPlayer, card: CardInstance):
	player.remove(card)
	player.place(card, ZoneMatch.ZoneEnum.pile)
	player.on_destroy(card)
