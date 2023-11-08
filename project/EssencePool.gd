extends VBoxContainer
	
const card_text_scene := preload("res://CardText.tscn")

signal click(ability)

func set_essence(essence: Array):
	reset()
	for c in Card.COLORS:
		var i := 0
		for es in essence:
			if es == c:
				i += 1
		if i > 0:
			var text = card_text_scene.instantiate()
			text.append_text(str(i) + "x {" + c + "}")
			add_child(text)
			text.highlight(true)
			text.click.connect(_on_label_click.bind(c))

func reset():
	for child in get_children():
		remove_child(child)

func _on_label_click(ability):
	click.emit(ability)
