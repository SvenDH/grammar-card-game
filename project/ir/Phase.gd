extends CardResource
class_name Phase

enum PhaseEnum {
	none,
	turn,
	activation,
	draw,
	play,
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

func check(card: CardInstance):
	var ctx = card.ctx
	var game = ctx.game
	var cardstate = ctx.state[card]
	if phase != PhaseEnum.none and phase != PhaseEnum.turn:
		if phase != game.phase:
			return false
	if turn == TurnQualifierEnum.this:
		if cardstate[ctx.ability].turn != game.turn:
			return false
	if player and ctx.current_player not in game.query(ctx, player):
		return false
	return true
