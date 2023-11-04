extends BaseEffect

@export var number: int = 1
@export var zones: ZoneMatch
@export var objects: ObjectMatch

func activate(ctx: Dictionary):
	var results = []
	for _i in getnumber(number, ctx):
		results.append([objects, zones])
	return results

func resolve(player: CardPlayer, zones: ZoneMatch, query_match = null):
	var choices = player.game.query(player.ctx, query_match, zones)
	# TODO: search own fields if not otherwise specified
	var card = player.callback.choose("Choose a card:", choices)
	player.remove(card)
	player.place(card, ZoneMatch.ZoneEnum.hand)
