extends Control
class_name CardInstance

const card_text_scene := preload("res://CardText.tscn")

signal click

@export var highlight_color := Color.WHITE
@export var disabled_color := Color.LIGHT_SLATE_GRAY

var game = null
var card: Card
var player_owner
var controller
var status: Array[CardStatus] = []
var triggers: Array[Ability] = []
var activated: bool = true
var attacking: bool = false
var blocking: bool = false
var side: bool = false
var location: ZoneMatch.ZoneEnum = ZoneMatch.ZoneEnum.deck
var field_index: int = -1
var highlighted := false
var can_focus := false
var types: get = _get_types
var power: get = _get_power, set = _set_power
var health: get = _get_health, set = _set_health
var abilities: get = _get_abilities
var activated_abilities: get = _get_activated_abilities
var triggered_abilities: get = _get_triggered_abilities
var keyword_abilities: get = _get_keyword_abilities
var color: get = _get_color

@onready var panel = $Panel
@onready var outline = $Outline
@onready var picture = $Panel/Margin/Parts/Picture
@onready var ability_text = $Panel/Margin/Parts/Scroll/Abilities
@onready var name_label = $Panel/Margin/Parts/Header/Name
@onready var cost_label = $Panel/Margin/Parts/Header/Essence
@onready var power_label = $Panel/Margin/Parts/Footer/Power
@onready var health_label = $Panel/Margin/Parts/Footer/Health

func _ready():
	if card:
		power = self.power
		health = self.health
		name_label.text = card.name
		for i in len(card.costs):
			var c = card.costs[len(card.costs)-1-i]
			cost_label.add_format_text("{"+str(c)+"}")
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
		panel.modulate = highlight_color
	else:
		panel.mouse_default_cursor_shape = CURSOR_ARROW
		panel.modulate = disabled_color

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
	await new_status.apply(self)
	await _check_dead()

func attack():
	assert(location == ZoneMatch.ZoneEnum.board and field_index != -1)
	var opponents = game.get_opponents(controller)
	# TODO: choose opponentn is there are multiple
	assert(len(opponents) > 0)
	# TODO: choose field if card has reach
	var card = game.get_field(opponents[0], field_index)
	await deactivate()
	if card:
		await card.damage(power)
	else:
		await opponents[0].damage(power)

func damage(amount: int):
	health -= amount
	await _check_dead()

func play() -> bool:
	# Check if playable
	var player = game.priority
	var to_index = await player.pick_free_field(self)
	if to_index == -1:
		return false
	await player.remove(self)
	await player.place(self, ZoneMatch.ZoneEnum.board, to_index)
	await _check_dead()
	return true

func cast() -> bool:
	if not can_cast():
		return false
	
	var player = game.priority
	var to_index = await player.pick_free_field(self)
	if to_index == -1:
		return false

	await player.remove(self)
	location = ZoneMatch.ZoneEnum.stack
	var ability = Ability.new()
	ability.game = game
	ability.source = self
	ability.controller = player
	ability.ability = card
	# TODO: add additional costs (from status etc)
	await player.pay_costs(self, card.costs)
	await game.send(ability, [[player, self, [self, to_index]]])
	await on_play()
	return true

func resolve(ability: Ability, player: CardPlayer, _card: CardInstance, to_index: int):
	assert(ability.source == self)
	await player.remove(self)
	for a in triggered_abilities:
		triggers.append(await a.activate(player, self))
	
	await player.place(self, ZoneMatch.ZoneEnum.board, to_index)
	await _check_dead()

func activate_ability(ability):
	if not ability.can_activate(self):
		return false
	
	var player = game.priority
	await player.pay_costs(self, ability.costs)
	await ability.activate(player, self)

func reset():
	power = card.power
	health = card.health
	status = []
	triggers = []
	activated = true
	attacking = false
	blocking = false
	field_index = -1

func is_source():
	for type in types:
		if type == Card.TypeEnum.source:
			return true
	return false

func can_attack():
	if location != ZoneMatch.ZoneEnum.board:
		return false
	if game.current_player != player_owner:
		return false
	if game.reaction:
		return false
	return activated

func can_react():
	# TODO: Check if card has flash or is an instant
	return false

func can_cast():
	if location != ZoneMatch.ZoneEnum.hand:
		# TODO: check castable from other locations
		return false
	var react = can_react()
	if game.current_player != player_owner and not react:
		return false
	if game.reaction and not react:
		return false
	
	return game.priority.can_pay(self, card.costs)

func can_activate():
	for ability in activated_abilities:
		if ability.can_activate(self):
			if not ability.is_essence_ability() or not game.reaction:
				return true
	return false

func on_activate():
	await game.trigger(game.activated, [self])

func on_deactivate():
	await game.trigger(game.deactivated, [self])

func on_enter():
	await game.trigger(game.entered, [self])

func on_exit():
	await game.trigger(game.left, [self])

func on_play():
	await game.trigger(game.played, [self])

func on_destroy():
	await game.trigger(game.destroyed, [self])

func on_counter():
	await game.trigger(game.countered, [self])

func on_draw():
	pass

func on_discard():
	pass

func _set_power(new_power):
	power = new_power
	power_label.text = str(power)

func _set_health(new_health):
	health = new_health
	health_label.text = str(health)

func _get_power():
	return power  # TODO: add modified types

func _get_health():
	return health  # TODO: add modified types

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

func _get_triggered_abilities() -> Array:
	# TODO: add modifiers
	var results = []
	for c in _get_abilities():
		if c is TriggeredAbility:
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
		for c in card.costs:
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
	if highlighted and has_focus() and event.is_action_pressed("ui_accept"):
		click.emit()

func select():
	outline.show()

func deselect():
	outline.hide()

func _check_dead():
	if location == ZoneMatch.ZoneEnum.board and health <= 0:
		await controller.remove(self)
		await player_owner.place(self, ZoneMatch.ZoneEnum.pile)
		await on_destroy()

func _on_focus_entered():
	z_index = 1
	var container = get_parent()
	if container.can_focus:
		if container is VBoxContainer:
			panel.position.x = 20
			outline.position.x = 20
		elif container is HBoxContainer:
			panel.position.y = -20
			outline.position.y = -20

func _on_focus_exited():
	z_index = 0
	var container = get_parent()
	if container.can_focus:
		panel.position = Vector2.ZERO
		outline.position = Vector2.ZERO

func _on_panel_mouse_entered():
	grab_focus()

func _on_panel_gui_input(event):
	if highlighted and \
	  (event is InputEventMouseButton and \
	   event.button_index == MOUSE_BUTTON_LEFT and event.pressed):
		click.emit()
