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
	controller.can_pay(card, costs)
	return true

func activate(ctx: Dictionary):
	await effect.activate(ctx)
	return true
