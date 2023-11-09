extends PanelContainer
class_name CardInstance

const card_text_scene := preload("res://CardText.tscn")

signal click

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
var highlighted := false
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

func _get_types() -> Array:
	return card.types  # TODO: add modified types

func _get_abilities() -> Array:
	return card.abilities  # TODO: add modifiers

func _get_activated_abilities() -> Array:
	# TODO: add modifiers
	var abs = []
	for c in _get_abilities():
		if c is ActivatedAbility:
			abs.append(c)
	return abs

func _get_keyword_abilities() -> Array:
	var abs = []
	for c in _get_abilities():
		if c is String:
			abs.append(card.convert_keyword(c))
	return abs

func _get_color() -> Array:
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

func highlight(enable: bool):
	highlighted = enable
	if enable:
		mouse_default_cursor_shape = CURSOR_POINTING_HAND
	else:
		mouse_default_cursor_shape = CURSOR_ARROW

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
	
	var player = ctx.priority
	var to_index = await player.pick_free_field(self)
	if to_index == -1:
		return false

	player.remove(self)
	location = ZoneMatch.ZoneEnum.stack
	ctx.self = self
	ctx.owner = player_owner
	ctx.controller = player
	ctx.ability = card
	# TODO: add additional costs (from status etc)
	await player.pay_costs(self, card.cost)
	player.game.send(ctx, [[player, self, [self, to_index]]])
	on_cast()
	return true

func resolve(player: CardPlayer, card: CardInstance, to_index: int):
	player.remove(card)
	player.place(card, ZoneMatch.ZoneEnum.board, to_index)

func activate_ability(ctx: Dictionary, ability):
	if not ability.can_activate(ctx):
		return false

	var player = ctx.priority
	ctx.self = self
	ctx.owner = player_owner
	ctx.controller = player
	ctx.ability = ability
	ctx.targets = []
	await player.pay_costs(self, ability.costs)
	return await ability.activate(ctx)

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
	if location != ZoneMatch.ZoneEnum.hand:
		# TODO: check castable from other locations
		return false
	
	ctx.self = self
	var react = can_react(ctx)
	if ctx.current_player != player_owner and not react:
		return false
	if ctx.reaction and not react:
		return false
	player_owner.can_pay(self, card.cost)
	return true

func can_activate(ctx: Dictionary):
	ctx.self = self
	for ability in activated_abilities:
		if ability.can_activate(ctx):
			return true
	return false

func on_activate():
	pass

func on_deactivate():
	pass

func on_enter():
	pass

func on_exit():
	pass

func on_draw():
	pass

func on_discard():
	pass

func on_cast():
	pass

func on_destroy():
	pass

func on_counter():
	pass

func _on_gui_input(event):
	if highlighted:
		if event is InputEventMouseButton:
			if event.pressed:
				click.emit()
