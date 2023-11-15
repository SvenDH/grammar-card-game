extends Control
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
var selected := false
var can_focus := false
var types: get = _get_types
var abilities: get = _get_abilities
var activated_abilities: get = _get_activated_abilities
var keyword_abilities: get = _get_keyword_abilities
var color: get = _get_color

@onready var panel = $Panel
@onready var picture = $Panel/Control/Picture
@onready var ability_text = $Panel/Control/Scroll/Abilities
@onready var name_label = $Panel/Control/Name
@onready var cost_label = $Panel/Control/Essence

func _ready():
	if card:
		name_label.text = card.name
		for c in card.costs:
			if c in Card.COLORS:
				cost_label.add_icon(c)
			else:
				cost_label.append_text(str(c))
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
				text.add_format_text(ability.text)
			if not text.get_parent():
				ability_text.add_child(text)

func _process(_delta):
	var container = get_parent()
	if container.spread:
		var bound = container.get_parent().size
		var new_size = bound / container.get_child_count()
		if container is VBoxContainer:
			custom_minimum_size.y = min(new_size.y, container.max_card_size.y)
		elif container is HBoxContainer:
			custom_minimum_size.x = min(new_size.x, container.max_card_size.x)

func highlight(enable: bool):
	highlighted = enable
	if enable:
		panel.mouse_default_cursor_shape = CURSOR_POINTING_HAND
		panel.modulate = Color.WHITE
	else:
		panel.mouse_default_cursor_shape = CURSOR_ARROW
		panel.modulate = Color(.7, .7, .7)

func activate():
	if not activated:
		activated = true
		on_activate()

func deactivate():
	if activated:
		activated = false
		on_deactivate()

func add_status(new_status: CardStatus):
	# TODO: subscribe for 'until' condition check
	status.append(new_status)
	new_status.apply(self)

func cast() -> bool:
	if not can_cast():
		return false
	
	var game = player_owner.game
	var player = game.priority
	var to_index = await player.pick_free_field(self)
	if to_index == -1:
		return false

	player.remove(self)
	location = ZoneMatch.ZoneEnum.stack
	
	var ctx = {
		'self': self,
		'controller': player,
		'ability': card,
	}
	# TODO: add additional costs (from status etc)
	await player.pay_costs(self, card.costs)
	player.game.send(ctx, [[player, self, [self, to_index]]])
	on_cast()
	return true

func resolve(player: CardPlayer, card: CardInstance, to_index: int):
	player.remove(card)
	player.place(card, ZoneMatch.ZoneEnum.board, to_index)

func activate_ability(ability):
	if not ability.can_activate(self):
		return false
	var game = player_owner.game
	var player = game.priority
	var ctx = {
		'self': self,
		'controller': player,
		'ability': ability,
		'targets': []
	}
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

func is_source():
	for type in types:
		if type == Card.TypeEnum.source:
			return true
	return false

func can_react():
	# TODO: Check if card has flash or is an instant
	return false

func can_cast():
	if location != ZoneMatch.ZoneEnum.hand:
		# TODO: check castable from other locations
		return false
	var react = can_react()
	var game = player_owner.game
	if game.current_player != player_owner and not react:
		return false
	if game.reaction and not react:
		return false
	
	return player_owner.can_pay(self, card.costs)

func can_activate():
	var game = player_owner.game
	for ability in activated_abilities:
		if ability.can_activate(self):
			if not ability.is_essence_ability() or not game.reaction:
				return true
	return false

func on_activate():
	pass

func on_deactivate():
	pass

func on_enter():
	player_owner.game.entered.emit(self)

func on_exit():
	player_owner.game.left.emit(self)

func on_draw():
	pass

func on_discard():
	pass

func on_cast():
	pass

func on_destroy():
	pass

func on_counter():
	player_owner.game.countered.emit(self)

func _get_types() -> Array:
	return card.types  # TODO: add modified types

func _get_abilities() -> Array:
	return card.abilities  # TODO: add modifiers

func _get_activated_abilities() -> Array:
	# TODO: add modifiers
	var results = []
	for c in _get_abilities():
		if c is ActivatedAbility:
			results.append(c)
	return results

func _get_keyword_abilities() -> Array:
	var results = []
	for c in _get_abilities():
		if c is String:
			results.append(card.convert_keyword(c))
	return results

func _get_color() -> Array:
	var colors = []
	if card:
		for c in card.cost:
			if not c is int:
				var color_id = card.convert_color(c)
				if color_id not in colors:
					colors.append(color_id)
	# TODO: add modifiers
	if len(colors) == 0:
		return [Card.ColorEnum.colorless]
	elif len(colors) == 1:
		colors.append(Card.ColorEnum.monocolored)
		return colors
	colors.append(Card.ColorEnum.multicolored)
	return colors

func _input(event):
	if highlighted and selected and event.is_action_pressed("ui_accept"):
		click.emit()

func _on_focus_entered():
	selected = true
	z_index = 1
	var container = get_parent()
	if container.can_focus:
		if container is VBoxContainer:
			panel.position.x = 20
		elif container is HBoxContainer:
			panel.position.y = -20

func _on_focus_exited():
	selected = false
	z_index = 0
	var container = get_parent()
	if container.can_focus:
		panel.position = Vector2.ZERO

func _on_panel_mouse_entered():
	grab_focus()

func _on_panel_gui_input(event):
	if highlighted and \
	  (event is InputEventMouseButton and \
	   event.button_index == MOUSE_BUTTON_LEFT and event.pressed):
		click.emit()
