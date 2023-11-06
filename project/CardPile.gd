extends Node
class_name CardPile

signal click(card: CardInstance)

var player

func highlight(cards: Array):
	for card in get_children():
		card.highlight(card in cards)

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
	var cards = []
	for child in get_children():
		if child is CardInstance:
			cards.append(child)
			remove_child(child)
	cards.shuffle()
	for card in cards:
		add_child(card)

func cards():
	var cards = []
	for child in get_children():
		if child is CardInstance:
			cards.append(child)
	return cards

func _add_card(card: CardInstance):
	card.click.connect(_on_click.bind(card))
	
func _remove_card(card: CardInstance):
	card.click.disconnect(_on_click.bind(card))

func _on_click(card: CardInstance):
	click.emit(card)
