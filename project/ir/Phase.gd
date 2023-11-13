extends CardResource
class_name Phase

enum PhaseEnum {
	none,
	turn,
	activation,
	draw,
	play,
	fight,
	cleanup
}

enum TurnQualifierEnum {
	none,
	each,
	this,
	that,
	the
}

@export var phase: PhaseEnum
@export var turn: TurnQualifierEnum
@export var ref: Match.Reference
@export var player: PlayerMatch
