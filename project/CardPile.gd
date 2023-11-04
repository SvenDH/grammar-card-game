extends Node
class_name CardPile

func add(card: CardInstance):
	add_child(card)

func insert(card: CardInstance, index: int):
	add_child(card)
	move_child(card, index)

func pop():
	var num = get_child_count()
	if num:
		var card = get_child(num-1)
		remove_child(card)
		return card
	return null

func remove(card: CardInstance):
	for child in get_children():
		if child == card:
			remove_child(child)
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
