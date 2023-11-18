extends BaseEffect

@export var number: int = 1

func activate(ability: Ability):
	return [[getnumber(number, ability)]]

func resolve(_ability: Ability, player: CardPlayer, n: int = 1):
	player.turnsafterthis += n
