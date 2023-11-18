extends BaseEffect

@export var objects: ObjectMatch

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ability: Ability):
	var player = ability.subject
	var results = []
	var res = await ability.game.pick(ability, objects, ZoneMatch.ZoneEnum.board)
	if res == null:
		return null
	for d in res:
		var index = await player.pick_free_field(d)
		if index == -1:
			# TODO: No field places available, should it stop creating tokens?
			return []
		elif index == null:
			return null
		results.append([d])
	return results

func resolve(_ability: Ability, player: CardPlayer, card: CardInstance, to_index: int):
	# TODO: add 'token' and 'copy' modifier
	# TODO: check if card is valid target?
	var inst = CardInstance.new()
	inst.game = player.game
	inst.card = card.card
	inst.controller = self
	inst.player_owner = self
	inst.field_index = to_index
	await player.place(inst, ZoneMatch.ZoneEnum.board, to_index)
