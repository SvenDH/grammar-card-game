extends BaseEffect

@export var number: int = 1
@export var objects: ObjectMatch

func activate(ctx: Dictionary):
	return [[getnumber(number, ctx), objects]]

func resolve(player: CardPlayer, n: int = 1, query_match = null):
	for _i in n:
		if player.hand.cards():
			return
			
		var choices
		if query_match:
			choices = player.query(player.ctx, query_match, ZoneMatch.ZoneEnum.hand)
		else:
			choices = player.hand.cards()
		var card = player.callback.choose("Discard a card:", choices)
		player.hand.remove(card)
		player.pile.add(card)
		card.location = ZoneMatch.ZoneEnum.pile
		player.on_discard(card)
