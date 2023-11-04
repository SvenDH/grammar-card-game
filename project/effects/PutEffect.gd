extends BaseEffect

@export var objects: ObjectMatch
@export var into: ZoneMatch
@export var deactivated: bool = false
@export var second_objects: ObjectMatch
@export var second_into: ZoneMatch

func activate(ctx: Dictionary):
	var player = ctx["subject"]
	var results = []
	for d in ctx["game"].pick(ctx, objects):
		var zone = ZoneMatch.ZoneEnum.board
		var index = player.pick_free_field(d)
		if into.place == ZoneMatch.PlaceEnum.bottom:
			index = -index
		# TODO: Fix zone and relative place picking
		results.append([d, zone, index, into.random, deactivated])
	# TODO: add second put effect
	return results

func resolve(
	player: CardPlayer,
	card: CardInstance,
	zone: ZoneMatch.ZoneEnum,
	to_index = null,
	random: bool = false,
	deactivated = false
):
	player.remove(card)
	player.place(card, zone, to_index)
	if random:
		player.shuffle(zone)
