extends Resource
class_name Ability

@export var source: CardInstance
@export var controller: CardPlayer
@export var ability: CardAbility
@export var effects: Array

func resolve(ctx: Dictionary):
	for eff in effects:
		ctx.subject = eff[0]
		eff[0].ctx = ctx
		var params = [eff[0]]
		params.append_array(eff[2])
		# TODO: should targets be checked here?
		await eff[1].callv("resolve", params)

func on_counter():
	source.game.countered.emit(self)
