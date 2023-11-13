extends PanelContainer

@export var spread := false
@export var can_focus := false

var card = null : set = _set_card, get = _get_card
var highlighted := false
var selected := false
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

func _on_focus_entered():
	selected = true
	modulate = Color.WHITE

func _on_focus_exited():
	selected = false
	modulate = Color(.7, .7, .7)

func _on_mouse_entered():
	grab_focus()

func _input(event):
	if selected and event.is_action_pressed("ui_accept"):
		if highlighted:
			board.click.emit(index)
		elif card and card.highlighted:
			board.click.emit(card)

func _on_gui_input(event):
	if event is InputEventMouseButton and \
	   event.button_index == MOUSE_BUTTON_LEFT and \
	   event.pressed:
		if highlighted:
			board.click.emit(index)
		elif card and card.highlighted:
			board.click.emit(card)
