extends Control
class_name Ability

const card_text_scene := preload("res://CardText.tscn")

signal click

@export var highlight_color := Color.WHITE
@export var disabled_color := Color.LIGHT_SLATE_GRAY
@export var can_focus := false

var source
var controller: CardPlayer
var ability: CardAbility
var ctx := {}
var effects := []
var targets := []
var game = null
var subject = null
var highlighted := false
var selected := false

@onready var panel = $Panel
@onready var picture = $Panel/Margin/Parts/Picture
@onready var ability_text = $Panel/Margin/Parts/Scroll/Abilities
@onready var name_label = $Panel/Margin/Parts/Name

func _ready():
	picture.texture = source.picture.texture
	name_label.text = source.card.name
	if ability is CardAbility:
		var text = card_text_scene.instantiate()
		text.add_format_text(ability.text)
		ability_text.add_child(text)

func resolve():
	for eff in effects:
		ctx.subject = eff[0]
		var params = [self, eff[0]]
		params.append_array(eff[2])
		# TODO: should targets be checked here?
		await eff[1].callv("resolve", params)

func on_counter():
	await game.trigger(game.countered, [self])

func copy(new_ability):
	new_ability.source = source
	new_ability.controller = controller
	new_ability.ability = ability
	new_ability.ctx = ctx
	new_ability.effects = effects
	new_ability.targets = targets
	new_ability.game = game
	new_ability.subject = subject

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
