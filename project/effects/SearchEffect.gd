extends BaseEffect

@export var number: int = 1
@export var zones: ZoneMatch
@export var objects: ObjectMatch

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ctx: Dictionary):
	var results = []
	for _i in getnumber(number, ctx):
		results.append([zones, objects])
	return results

func resolve(player: CardPlayer, zones: ZoneMatch, query_match = null):
	var choices = player.game.query(player.ctx, query_match, zones)
	# TODO: search own fields if not otherwise specified
	var card = await player.choose("search", choices)
	await player.remove(card)
	await player.place(card, ZoneMatch.ZoneEnum.hand)
	await player.on_search()
