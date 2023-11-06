extends BaseEffect

@export var number: int = 1
@export var stats: Array = [1, 1]
@export var abilities: Array = []

func activate(ctx: Dictionary):
	var player = ctx["subject"]
	var results = []
	for _i in getnumber(number, ctx):
		var card = Card.new()
		card.name = "Token"
		card.power = stats[0]
		card.health = stats[1]
		card.types = [Card.TypeEnum.unit, Card.TypeEnum.token]
		var index = await player.pick_free_field(card)
		if index == -1:
			# TODO: No field places available, should it stop creeating tokens?
			break
		results.append([card, index])
	return results

func resolve(player: CardPlayer, card: Card, to_index: int):
	assert(to_index >= 0 and to_index < len(player.board.cards()))
	assert(player.board.get_card(to_index) == null)  # TODO: should this be allowed?
	var inst = CardInstance.new()
	inst.card = card
	inst.controller = self
	inst.player_owner = self
	inst.field_index = to_index
	player.place(inst, ZoneMatch.ZoneEnum.board, to_index)
