extends PanelContainer

var card = null : set = _set_card, get = _get_card
var highlighted := false
var index := -1

@onready var board = get_parent()

func _set_card(new_card):
	if card:
		remove_child(card)
	if new_card:
		add_child(new_card)
	card = new_card
	
func _get_card():
	return card

func highlight(enable: bool):
	highlighted = enable
	if enable:
		mouse_default_cursor_shape = CURSOR_POINTING_HAND
	else:
		mouse_default_cursor_shape = CURSOR_ARROW

func _on_gui_input(event):
	if highlighted:
		if event is InputEventMouseButton:
			if event.is_pressed() or event.is_released():
				board.click.emit(index)
