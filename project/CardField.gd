extends Node

var card = null : set = _set_card, get = _get_card

func _set_card(new_card):
	card = new_card
	
func _get_card():
	return card
