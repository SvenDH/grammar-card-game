extends Node
class_name CardInstance

const card_text_scene := preload("res://CardText.tscn")

signal on_click

var card: Card
var power := 1
var health := 1
var player_owner
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
var keyword_abilities: get = _get_keyword_abilities
var color: get = _get_color

@onready var picture = $Control/Picture
@onready var ability_text = $Control/Scroll/Abilities

func _ready():
	if card:
		var text = null
		for ability in card.abilities:
			if ability is String:
				if text == null:
					text = card_text_scene.instantiate()
				else:
					text.append_text(", ")
				text.append_text(ability)
			else:
				text = card_text_scene.instantiate()
				text.append_text(ability.text)
			if not text.get_parent():
				ability_text.add_child(text)

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

func _get_keyword_abilities() -> Array[Card.KeywordEnum]:
	var abs = []
	for c in _get_abilities():
		if c is String:
			abs.append(card.convert_keyword(c))
	return abs

func _get_color() -> Array[Card.ColorEnum]:
	var colors = []
	if card:
		for c in card.cost:
			if not c is int:
				var color = card.convert_color(c)
				if color not in colors:
					colors.append(color)
	# TODO: add modifiers
	if len(colors) == 0:
		return [Card.ColorEnum.colorless]
	elif len(colors) == 1:
		colors.append(Card.ColorEnum.monocolored)
		return colors
	colors.append(Card.ColorEnum.multicolored)
	return colors

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

func _on_gui_input(event):
	if event is InputEventMouseButton:
		if event.pressed:
			on_click.emit()
