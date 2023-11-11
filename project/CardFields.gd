extends Node
class_name CardFields

signal click(index: int)

@export var max_card_size: Vector2
@export var num_fields := 4
@export var field_scene: PackedScene

var player

func _ready():
	var last = null
	for i in num_fields:
		var field = field_scene.instantiate()
		field.index = i
		add_child(field)
		if last:
			field.focus_neighbor_left = last.get_path()
			last.focus_neighbor_right = field.get_path()
		last = field

func reset():
	for field in get_children():
		field.highlight(false)
		if field.card:
			field.card.highlight(false)

func highlight(fields: Array):
	var first = false
	for field in get_children():
		var isin = field.index in fields
		field.highlight(isin)
		if not first and isin:
			field.grab_focus()
			first = true
		if field.card:
			isin = field.card in fields
			field.card.highlight(isin)
			if not first and isin:
				field.grab_focus()
				first = true

func free_fields(card):
	# TODO: check card stacking
	var fields = []
	for i in num_fields:
		if get_child(i).card == null:
			fields.append(i)
	return fields

func place(card: CardInstance, field_index: int):
	var field = get_child(field_index)
	if not field.card:
		field.card = card
		card.click.connect(_on_field_click.bind(card))
	# TODO: check card stacking

func remove(field_index: int):
	var field = get_child(field_index)
	if field.card:
		field.card.highlight(false)
		field.card.click.disconnect(_on_field_click.bind(field.card))
	field.card = null

func index(card: CardInstance):
	for i in get_child_count():
		if get_child(i).card == card:
			return i
	return -1

func get_card(field_index: int):
	return get_child(field_index).card

func cards():
	var results := []
	for child in get_children():
		if child.card:
			results.append(child.card)
	# TODO: check card stacking
	return results

func _on_field_click(card):
	click.emit(card)
