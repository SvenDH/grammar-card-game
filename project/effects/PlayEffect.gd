extends BaseEffect

@export var objects: ObjectMatch
@export var free: bool = false

func targets(ability: Ability):
	return objects.targets(ability)

func has_target():
	return objects.has_target()

func activate(ability: Ability):
	var player = ability.subject
	var results = []
	var res = await ability.game.pick(ability, objects)
	if res == null:
		return null
	for d in res:
		var index = await player.pick_free_field(d)
		if index == -1:
			# TODO: No field places available, should it stop creating tokens?
			break
		elif index == null:
			return null
		# TODO: Pay essence if not free
		results.append([d, index])
	return results

func resolve(_ability: Ability, player: CardPlayer, card: CardInstance, to_index: int):
	await player.remove(card)
	await player.place(card, ZoneMatch.ZoneEnum.board, to_index)
	await card.on_play()
