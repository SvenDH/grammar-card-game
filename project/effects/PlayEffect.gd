extends BaseEffect

@export var objects: ObjectMatch
@export var free: bool = false

func activate(ctx: Dictionary):
	var player = ctx["subject"]
	var results = []
	for d in await ctx["game"].pick(ctx, objects):
		var index = await player.pick_free_field(d)
		if index == -1:
			# TODO: No field places available, should it stop creating tokens?
			break
		# TODO: Pay essence if not free
		results.append([d, index])
	return results

func resolve(player: CardPlayer, card: CardInstance, to_index: int):
	player.remove(card)
	player.place(card, ZoneMatch.ZoneEnum.board, to_index)
