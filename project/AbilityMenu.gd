extends PanelContainer

const card_text_scene := preload("res://CardText.tscn")

signal click(ability)

@onready var list := $List

func set_abilities(activated_abilities: Array):
	reset()
	for ability in activated_abilities:
		var text = card_text_scene.instantiate()
		text.append_text(ability.text)
		list.add_child(text)
		text.highlight(true)
		text.click.connect(_on_label_click.bind(ability))

func reset():
	for child in list.get_children():
		list.remove_child(child)

func _on_label_click(ability):
	click.emit(ability)
