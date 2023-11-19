extends BaseEffect

@export var where: ZoneMatch
@export var what: ObjectMatch
@export var zones: ZoneMatch

func targets(ability: Ability):
	return what.targets(ability) if what else -1

func has_target():
	return what.has_target()

func activate(ability: Ability):
	var player = ability.subject
	var results = []
	for zone in zones.zones:
		var w
		if what != null:
			w = player.query(ability, what)
		elif where != null:
			w = player.query(ability, null, where)
		else:
			var q = ZoneMatch.new()
			q.zones = [zone]
			q.ref = zones.ref
			w = player.query(ability, null, q)
		results.append([w, zone])
	return results

func resolve(_ability: Ability, player: CardPlayer, cards: Array, zone: ZoneMatch.ZoneEnum):
	assert(zone != ZoneMatch.ZoneEnum.hand and zone != ZoneMatch.ZoneEnum.board)
	for card in cards:
		# TODO: Check to see if cards have changed location
		await player.remove(card)
		await player.place(card, zone)
	await player.shuffle(zone)
