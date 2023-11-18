extends BaseEffect

@export var objects: ObjectMatch
@export var into: ZoneMatch
@export var deactivated: bool = false
@export var second_objects: ObjectMatch
@export var second_into: ZoneMatch

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ability: Ability):
	var player = ability.subject
	var results = []
	var res = await ability.game.pick(ability, objects)
	if res == null:
		return null
	for d in res:
		var zone = ZoneMatch.ZoneEnum.board
		var index = await player.pick_free_field(d)
		if index == -1:
			break
		elif index == null:
			return null
		elif into.place == ZoneMatch.PlaceEnum.bottom:
			index = -index
		# TODO: Fix zone and relative place picking
		results.append([d, zone, index, deactivated])
	# TODO: add second put effect
	if into.random:
		# TODO: is this correct random order?
		results.shuffle()
	return results

func resolve(
	_ability: Ability, 
	player: CardPlayer,
	card: CardInstance,
	zone: ZoneMatch.ZoneEnum,
	to_index = null,
	deactivated = false
):
	# Check to see if card has changed location?
	await player.remove(card)
	await player.place(card, zone, to_index)
