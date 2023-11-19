extends BaseEffect

@export var objects: ObjectMatch

func targets(ability: Ability):
	return objects.targets(ability)

func has_target():
	return objects.has_target()

func activate(ability: Ability):
	var results = []
	var res = await ability.game.pick(ability, objects, ZoneMatch.ZoneEnum.board)
	if res == null:
		return null
	for d in res:
		results.append([d])
	return results
	
func resolve(_ability: Ability, player: CardPlayer, card: CardInstance):
	if card.location == ZoneMatch.ZoneEnum.board:
		await card.controller.remove(card)
		await card.player_owner.place(card, ZoneMatch.ZoneEnum.pile)
		await card.on_destroy()
