extends RichTextLabel

const essence_image := preload("res://textures/essence.png")

signal click

var highlighted := false
var selected := false

func highlight(enable: bool):
	highlighted = enable
	if enable:
		mouse_default_cursor_shape = CURSOR_POINTING_HAND
		focus_mode = Control.FOCUS_ALL
		mouse_filter = Control.MOUSE_FILTER_STOP
	else:
		mouse_default_cursor_shape = CURSOR_ARROW
		focus_mode = Control.FOCUS_NONE
		mouse_filter = Control.MOUSE_FILTER_PASS

func add_icon(chr):
	var pos = null
	if chr == "R":
		pos = Vector2.ZERO
	elif chr == "B":
		pos = Vector2(16, 0)
	elif chr == "Y":
		pos = Vector2(32, 0)
	elif chr == "G":
		pos = Vector2(48, 0)
	elif chr == "T":
		pos = Vector2(0, 16)
	elif chr == "Q":
		pos = Vector2(16, 16)
	if pos != null:
		add_image(essence_image, 12, 12, Color.WHITE, 5, Rect2(pos, Vector2(16, 16)))
	else:
		push_color(Color("9badb7"))
		add_text(convert_chr(chr))
		pop()

func convert_chr(chr):
	match chr:
		"0": return "⓿"
		"1": return "❶"
		"2": return "❷"
		"3": return "❸"
		"4": return "❹"
		"5": return "❺"
		"6": return "❻"
		"7": return "❼"
		"8": return "❽"
		"9": return "❾"
		"10": return "❿"
		"10": return "⓫"
		"11": return "⓬"
		"12": return "⓬"
		"13": return "⓭"
		"14": return "⓮"
		"15": return "⓯"
		"16": return "⓰"
		"17": return "⓱"
		"18": return "⓲"
		"19": return "⓳"
		"20": return "⓴"

func add_format_text(txt):
	for t in txt.split("{"):
		var p = t.split("}")
		if len(p) == 1:
			append_text(t)
		else:
			add_icon(p[0])
			append_text(p[1])

func _input(event):
	if highlighted and selected and event.is_action_pressed("ui_accept"):
		click.emit()

func _on_input(event):
	if highlighted and \
	  (event is InputEventMouseButton and \
	   event.button_index == MOUSE_BUTTON_LEFT and \
	   event.pressed):
		click.emit()

func _on_focus_entered():
	selected = true

func _on_focus_exited():
	selected = false

func _on_mouse_entered():
	if highlighted:
		grab_focus()
