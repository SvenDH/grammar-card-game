extends CardAbility
class_name ActivatedAbility

@export var costs: Array = []
@export var effect: Effect

func can_activate(ctx: Dictionary):
	if ctx.self.location != ZoneMatch.ZoneEnum.board:
		# TODO: check if activatable from other place
		return false
	# TODO: check if costs can be paid
	return true

func pay_costs(ctx: Dictionary):
	# TODO: check if costs can be paid and pay costs
	# TODO: add pyed costs to ctx including sacrificed units
	pass

func activate(ctx: Dictionary):
	await pay_costs(ctx)
	await effect.activate(ctx)
	return true
