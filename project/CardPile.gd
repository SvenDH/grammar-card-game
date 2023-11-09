extends Node
class_name CardPile

signal click(card: CardInstance)

var player

func reset():
	for card in get_children():
		card.highlight(false)

func highlight(highlighted_cards: Array):
	for card in get_children():
		card.highlight(card in highlighted_cards)

func add(card: CardInstance):
	add_child(card)
	_add_card(card)

func insert(card: CardInstance, index: int):
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

func remove(card: CardInstance):
	for child in get_children():
		if child == card:
			remove_child(child)
			_remove_card(card)
			return child
	return null

func shuffle():
	var temp = []
	for child in get_children():
		if child is CardInstance:
			temp.append(child)
			remove_child(child)
	temp.shuffle()
	for card in temp:
		add_child(card)

func cards():
	var temp = []
	for child in get_children():
		if child is CardInstance:
			temp.append(child)
	return temp

func _add_card(card: CardInstance):
	card.click.connect(_on_click.bind(card))
	
func _remove_card(card: CardInstance):
	card.click.disconnect(_on_click.bind(card))

func _on_click(card: CardInstance):
	click.emit(card)
