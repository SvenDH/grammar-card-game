extends CardResource
class_name Card

enum TypeEnum {
	none,
	unit,
	spell,
	token
}

enum KeywordEnum {
	none,
	flying,
	siege,
	poison
}

@export var cost: Array = [0]
@export var types: Array[TypeEnum] = []
@export var subtypes: Array[String] = []
@export var abilities: Array[CardAbility] = []
@export var power: int = 1
@export var health: int = 1

var color : get = _get_color

func _get_color() -> Array[ColorEnum]:
	var colors = []
	for c in cost:
		if not c is int:
			var color = convert_color(c)
			if color not in colors:
				colors.append(color)
	if len(colors) == 0:
		return [ColorEnum.colorless]
	elif len(colors) == 1:
		colors.append(ColorEnum.monocolored)
		return colors
	colors.append(ColorEnum.multicolored)
	return colors
