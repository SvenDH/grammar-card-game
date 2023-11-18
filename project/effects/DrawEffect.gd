extends BaseEffect

@export var number: int = 1
@export var side: bool = false
	
func activate(ability: Ability):
	return [[getnumber(number, ability), side]]

func resolve(_ability: Ability, player: CardPlayer, n: int = 1, side_: bool = false):
	# TODO: draw specific matched card
	# TODO: lose game when deck is empty
	assert(side_ or n <= player.board.num_fields)
	await player.draw(n, side_)
