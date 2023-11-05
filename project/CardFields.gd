extends Node
class_name CardFields

@export var num_fields := 4
@export var field_scene: PackedScene

@onready var player = get_parent()

func _ready():
	for _i in num_fields:
		var field = field_scene.instantiate()
		add_child(field)

func place(card: CardInstance, index: int):
	var field = get_child(index)
	if not field.card:
		field.card = card
	# TODO: check card stacking

func remove(index: int):
	var field = get_child(index)
	field.card = null

func index(card: CardInstance):
	for i in get_child_count():
		if get_child(i).card == card:
			return i
	return -1

func get_card(index: int):
	return get_child(index).card

func cards():
	var cards := []
	for child in get_children():
		if child.card:
			cards.append(child.card)
	# TODO: check card stacking
	return cards

func pick_free_field(card: CardInstance) -> int:
	# TODO: check card stacking
	var fields := []
	for i in get_child_count():
		var field = get_child(i)
		if not field.card:
			fields.append(i)
	if not fields:
		return -1
	var idx = await player.callback.choose("Choose field position:", fields)
	return idx
