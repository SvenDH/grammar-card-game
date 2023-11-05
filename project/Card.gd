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
@export var abilities: Array = []
@export var power: int = 1
@export var health: int = 1

func convert_keyword(keyword: String):
	match keyword.to_lower():
		"flying": return KeywordEnum.flying
		"siege": return KeywordEnum.siege
		"poison": return KeywordEnum.poison
		_: return ColorEnum.none
