extends RichTextLabel

signal click

var highlighted := false

func highlight(enable: bool):
	highlighted = enable
	if enable:
		mouse_default_cursor_shape = CURSOR_POINTING_HAND
	else:
		mouse_default_cursor_shape = CURSOR_ARROW

func _on_input(event):
	if highlighted:
		if event is InputEventMouseButton:
			if event.pressed:
				click.emit()
