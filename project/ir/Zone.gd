extends Match
class_name ZoneMatch

enum ZoneEnum {
	none,
	deck,
	pile,
	hand,
	board,
	stack,
	it
}

enum PlaceEnum {
	none,
	top,
	bottom,
}

@export var zones: Array[ZoneEnum] = []
@export var ref: PlayerMatch
# Only used for placement
@export var place: PlaceEnum
@export var random: bool = false

func match_query(ability: Ability, field: ZoneEnum, player = null):
	if ref is PlayerMatch:
		if not ref.match_query(ability, player):
			return false
	return field in zones
