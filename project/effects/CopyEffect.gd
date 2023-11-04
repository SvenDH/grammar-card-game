extends BaseEffect

@export var objects: ObjectMatch

func activate(ctx: Dictionary):
	var player = ctx["subject"]
	var results = []
	for d in ctx["game"].pick(ctx, objects, ZoneMatch.ZoneEnum.board):
		var index = player.pick_free_field(d)
		if index == -1:
			# TODO: No field places available, should it stop creating tokens?
			return []
		results.append([d])
	return results

func resolve(player: CardPlayer, card: CardInstance, to_index: int):
	# TODO: add 'token' and 'copy' modifier
	var inst = CardInstance.new()
	inst.card = card.card
	inst.controller = self
	inst.player_owner = self
	inst.field_index = to_index
	player.place(inst, ZoneMatch.ZoneEnum.board, to_index)
