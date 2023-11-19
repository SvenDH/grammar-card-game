extends CardAbility
class_name ActivatedAbility

@export var costs: Array = []
@export var effect: Effect

func is_essence_ability() -> bool:
	if has_target():
		return false
	return effect.is_essence_ability()

func targets(ctx: Dictionary) -> int:
	return effect.targets(ctx)

func has_target() -> bool:
	return effect.has_target()

func can_activate(card: CardInstance):
	if card.location != ZoneMatch.ZoneEnum.board:
		# TODO: check if activatable from other place
		return false
	# TODO: add potential essence from essence sources
	var controller = card.controller
	return controller.can_pay(card, costs)

func activate(ctx: Dictionary):
	var ability = Ability.new()
	ability.ctx = ctx
	ability.game = ctx.game
	ability.source = ctx.self
	ability.controller = ctx.controller
	ability.ability = ctx.ability
	await effect.activate(ability)
