extends CardAbility
class_name ActivatedAbility

@export var costs: Array = []
@export var effect: Effect

func is_essence_ability(ctx: Dictionary):
	if targets(ctx) != -1:
		return false
	return effect.is_essence_ability(ctx)

func targets(ctx: Dictionary):
	return effect.targets(ctx)

func can_activate(ctx: Dictionary):
	if ctx.self.location != ZoneMatch.ZoneEnum.board:
		# TODO: check if activatable from other place
		return false
	# TODO: add potential essence from essence sources
	var card = ctx.self
	var controller = card.controller
	return controller.can_pay(card, costs)

func activate(ctx: Dictionary):
	await effect.activate(ctx)
	return true
