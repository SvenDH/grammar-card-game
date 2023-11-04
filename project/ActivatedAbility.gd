extends CardAbility
class_name ActivatedAbility

@export var costs: Array = []
@export var effect: Effect

func can_activate(ctx: Dictionary):
	# TODO: check if costs can be paid
	return true

func pay_costs(ctx: Dictionary):
	# TODO: check if costs can be paid and pay costs
	# TODO: add pyed costs to ctx including sacrificed units
	pass

func activate(ctx: Dictionary):
	pay_costs(ctx)
	effect.activate(ctx)
	return true
