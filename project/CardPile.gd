extends Node
class_name CardPile

signal click(card)

@export var max_card_size: Vector2
@export var can_focus := false
@export var spread := false

var player

func reset():
	for card in get_children():
		card.highlight(false)

func highlight(highlighted_cards: Array):
	var first = false
	for card in get_children():
		var isin = card in highlighted_cards
		card.highlight(isin)
		if not first and isin:
			card.grab_focus()
			first = true

func add(card):
	add_child(card)
	_add_card(card)

func insert(card, index: int):
	add_child(card)
	move_child(card, index)
	_add_card(card)

func pop():
	var num = get_child_count()
	if num:
		var card = get_child(num-1)
		remove_child(card)
		_remove_card(card)
		return card
	return null

func remove(card):
	for child in get_children():
		if child == card:
			remove_child(child)
			_remove_card(card)
			return child
	return null

func shuffle():
	var temp = []
	for child in get_children():
		temp.append(child)
		remove_child(child)
	temp.shuffle()
	for card in temp:
		add_child(card)

func cards():
	var temp = []
	for child in get_children():
		temp.append(child)
	return temp

func _reset_focus():
	var last_card = null
	for child in get_children():
		if last_card:
			child.focus_neighbor_left = last_card.get_path()
			last_card.focus_neighbor_right = child.get_path()
		last_card = child

func _add_card(card):
	if can_focus:
		_reset_focus()
	card.can_focus = can_focus
	card.click.connect(_on_click.bind(card))
	
func _remove_card(card):
	if can_focus:
		_reset_focus()
	card.click.disconnect(_on_click.bind(card))

func _on_click(card):
	click.emit(card)
