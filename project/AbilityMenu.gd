extends PanelContainer

const card_text_scene := preload("res://CardText.tscn")

signal click(ability)

@onready var list := $List

func set_abilities(activated_abilities: Array):
	reset()
	var last = null
	var first = false
	for ability in activated_abilities:
		var text = card_text_scene.instantiate()
		if ability is String:
			text.add_format_text(ability)
		else:
			text.add_format_text(ability.text)
		list.add_child(text)
		text.highlight(true)
		if not first:
			text.grab_focus()
			first = true
		text.click.connect(_on_label_click.bind(ability))
		if last:
			text.focus_neighbor_top = last.get_path()
			last.focus_neighbor_bottom = text.get_path()
		last = text

func reset():
	for child in list.get_children():
		list.remove_child(child)

func _on_label_click(ability):
	click.emit(ability)
