extends BaseEffect

@export var number: int = 1
@export var objects: ObjectMatch

func targets(ctx):
	return objects.targets(ctx)

func activate(ctx: Dictionary):
	return [[getnumber(number, ctx), objects]]

func resolve(player: CardPlayer, n: int = 1, query_match = null):
	for _i in n:
		if not player.hand.cards():
			return
			
		var choices
		if query_match:
			choices = player.query(player.ctx, query_match, ZoneMatch.ZoneEnum.hand)
		else:
			choices = player.hand.cards()
		if choices:
			var card = await player.choose("discard", choices)
			player.hand.remove(card)
			player.pile.add(card)
			card.location = ZoneMatch.ZoneEnum.pile
			card.on_discard()
