extends Node
class_name CardInstance

var player_owner
var card: Card
var power := 1
var health := 1
var controller
var status: Array[CardStatus] = []
var activated: bool = true
var attacking: bool = false
var blocking: bool = false
var side: bool = false
var location: ZoneMatch.ZoneEnum = ZoneMatch.ZoneEnum.deck
var field_index: int = -1
var ctx: Dictionary

var types: get = _get_types
var abilities: get = _get_abilities
var activated_abilities: get = _get_activated_abilities
var color: get = _get_color

func _get_types() -> Array[Card.TypeEnum]:
	return card.types  # TODO: add modified types

func _get_abilities() -> Array:
	return card.abilities  # TODO: add modifiers

func _get_activated_abilities() -> Array[ActivatedAbility]:
	# TODO: add modifiers
	var abs = []
	for c in _get_abilities():
		if c is ActivatedAbility:
			abs.append(c)
	return abs

func _get_color() -> Array[Card.ColorEnum]:
	# TODO: add modifiers
	return card.color
	
func activate():
	if not activated:
		activated = true
		on_activate()

func deactivate():
	if activated:
		activated = false
		on_deactivate()

func add_status(status: CardStatus):
	# TODO: subscribe for 'until' condition check
	status.append(status)

func cast(ctx: Dictionary) -> bool:
	if not can_cast(ctx):
		return false

	location = ZoneMatch.ZoneEnum.stack
	ctx["self"] = self
	ctx["owner"] = player_owner
	ctx["controller"] = player_owner
	var to_index = player_owner.pick_free_field(self)
	if to_index == -1:
		return false
	# TODO: pay card costs
	player_owner.game.send(ctx, [[player_owner, "play", [self, to_index]]])
	return true

func activate_ability(ctx: Dictionary, index: int):
	var ability = activated_abilities[index]
	if not ability.can_activate(ctx):
		return false

	ctx["self"] = self
	ctx["owner"] = player_owner
	ctx["controller"] = controller
	ctx["ability"] = ability
	return ability.activate(ctx)

func reset():
	power = card.power
	health = card.health
	status = []
	activated = true
	attacking = false
	blocking = false
	field_index = -1

func can_react(ctx: Dictionary):
	# TODO: Check if card has flash or is an instant
	return false

func can_cast(ctx: Dictionary):
	var react = can_react(ctx)
	if ctx["current_player"] != player_owner and not react:
		return false
	if ctx["reaction"] and not react:
		return false
	return true

func can_activate(ctx: Dictionary):
	for ability in activated_abilities:
		if ability.can_activate(ctx):
			return true
	return false

func on_activate():
	pass

func on_deactivate():
	pass
