extends Node
class_name CardFields

signal click(index: int)

@export var num_fields := 4
@export var field_scene: PackedScene

var player

func _ready():
	for i in num_fields:
		var field = field_scene.instantiate()
		field.index = i
		add_child(field)

func highlight(fields: Array):
	for field in get_children():
		field.highlight(field.index in fields)
		if field.card:
			field.card.highlight(field.card in fields)

func free_fields(card: CardInstance):
	# TODO: check card stacking
	var fields = []
	for i in num_fields:
		if get_child(i).card == null:
			fields.append(i)
	return fields

func place(card: CardInstance, index: int):
	var field = get_child(index)
	if not field.card:
		field.card = card
		card.click.connect(_on_field_click.bind(card))
	# TODO: check card stacking

func remove(index: int):
	var field = get_child(index)
	if field.card:
		field.card.hightlight(false)
		field.card.click.disconnect(_on_field_click.bind(field.card))
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

func _on_field_click(card):
	click.emit(card.field_index)
