extends BaseEffect

@export var number: int = 1
@export var zones: ZoneMatch

func activate(ability: Ability):
	return [[zones, getnumber(number, ability)]]

func resolve(ability: Ability, player: CardPlayer, place: ZoneMatch, n: int):
	var cards = ability.game.query(ability, null, place, n)
	await player.choose("reveal", cards)
