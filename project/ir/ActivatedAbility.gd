extends CardAbility
class_name ActivatedAbility

@export var costs: Array = []
@export var effect: Effect

func is_essence_ability() -> bool:
	if has_target():
		return false
	return effect.is_essence_ability()

func targets(ability: Ability) -> int:
	return effect.targets(ability)

func has_target() -> bool:
	return effect.has_target()

func can_activate(card: CardInstance):
	if card.location != ZoneMatch.ZoneEnum.board:
		# TODO: check if activatable from other place
		return false
	# TODO: add potential essence from essence sources
	var controller = card.controller
	return controller.can_pay(card, costs)

func activate(player, card):
	var ability = Ability.new()
	ability.game = player.game
	ability.source = card
	ability.controller = player
	ability.ability = self
	await effect.activate(ability)
	return ability
