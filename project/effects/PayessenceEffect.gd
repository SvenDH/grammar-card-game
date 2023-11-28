extends BaseEffect

@export var costs: Array

func activate(ability: Ability):
	var objects = ObjectMatch.new()
	objects.
	var res = await ability.game.pick(ability, objects)
	if res == null:
		return null
	for d in res:
		await d[0].activate_ability(d[1])
	return []

func resolve(_ability: Ability, player: CardPlayer):
	pass
