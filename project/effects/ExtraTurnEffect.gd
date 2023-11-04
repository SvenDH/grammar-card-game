extends BaseEffect

@export var number: int = 1

func activate(ctx: Dictionary):
	return [[getnumber(number, ctx)]]

func resolve(player: CardPlayer, n: int = 1):
	player.turnsafterthis += n
