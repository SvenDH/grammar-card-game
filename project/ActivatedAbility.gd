extends CardAbility
class_name ActivatedAbility

@export var costs: Array = []
@export var effect: Effect

func can_activate(ctx: Dictionary):
	if ctx.self.location != ZoneMatch.ZoneEnum.board:
		# TODO: check if activatable from other place
		return false
	# TODO: add potential essence from essence sources
	var card = ctx.self
	var controller = card.controller
	var pool := Array(controller.essence)
	for symbol in costs:
		if symbol is String:
			if symbol == "T" and not card.activated:
				return false
			elif symbol == "Q" and card.activated:
				return false
			elif symbol in Card.COLORS:
				if symbol not in pool:
					return false
				pool.erase(symbol)
		elif symbol is int:
			if len(pool) < symbol:
				return false
			for _i in symbol:
				if "U" in pool:
					pool.erase("U")
				else:
					pool.pop_back()
	return true

func pay_costs(ctx: Dictionary):
	# TODO: check if costs can be paid and pay costs
	# TODO: add pyed costs to ctx including sacrificed units
	pass

func activate(ctx: Dictionary):
	await pay_costs(ctx)
	await effect.activate(ctx)
	return true
