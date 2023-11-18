extends BaseEffect

@export var colors: Array[String] = []
@export var amount: int = 1

func is_essence_ability():
	return true

func activate(ability: Ability):
	var player = ability.subject
	if len(colors) > 1:
		return [[await player.choose("essence", colors), amount]]
	elif len(colors) == 1:
		return [[colors[0], amount]]
	return [["U", amount]]

func resolve(_ability: Ability, player: CardPlayer, color, amount):
	for _i in amount:
		player.add_essence(color)
