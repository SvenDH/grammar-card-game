extends BaseEffect

@export var objects: ObjectMatch

func targets(ability: Ability):
	return objects.targets(ability)

func has_target():
	return objects.has_target()

func activate(ability: Ability):
	var player = ability.subject
	var results = []
	var res = await ability.game.pick(ability, objects, ZoneMatch.ZoneEnum.board)
	if res == null:
		return null
	for d in res:
		results.append([d])
	return results

func resolve(_ability: Ability, player: CardPlayer, card: CardInstance):
	# Check to see if card has changed location?
	await player.remove(card)
	await player.place(card, ZoneMatch.ZoneEnum.pile)
