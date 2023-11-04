extends BaseEffect

@export var number: int = 1
@export var zones: ZoneMatch

func activate(ctx: Dictionary):
	return [[zones, getnumber(number, ctx)]]

func resolve(player: CardPlayer, place: ZoneMatch, n: int):
	var cards = player.game.query(player.ctx, null, place, n)
	player.callback.show("reveal", cards)
