extends BaseEffect

@export var where: ZoneMatch
@export var what: ObjectMatch
@export var zones: ZoneMatch

func targets(ctx):
	return what.targets(ctx) if what else -1

func has_target():
	return what.has_target()

func activate(ctx: Dictionary):
	var player = ctx.subject
	var results = []
	for zone in zones.zones:
		var w
		if what != null:
			w = player.query(ctx, what)
		elif where != null:
			w = player.query(ctx, null, where)
		else:
			var q = ZoneMatch.new()
			q.zones = [zone]
			q.ref = zones.ref
			w = player.query(ctx, null, q)
		results.append([w, zone])
	return results

func resolve(player: CardPlayer, cards: Array, zone: ZoneMatch.ZoneEnum):
	assert(zone != ZoneMatch.ZoneEnum.hand and zone != ZoneMatch.ZoneEnum.board)
	for card in cards:
		# TODO: Check to see if cards have changed location
		player.remove(card)
		player.place(card, zone)
	player.shuffle(zone)
