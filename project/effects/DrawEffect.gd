extends BaseEffect

@export var number: int = 1
@export var side: bool = false
	
func activate(ctx: Dictionary):
	return [[getnumber(number, ctx), side]]

func resolve(player: CardPlayer, n: int = 1, side_: bool = false):
	# TODO: draw specific matched card
	# TODO: lose game when deck is empty
	assert(side_ or n <= player.board.num_fields)
	player.draw(n, side_)
