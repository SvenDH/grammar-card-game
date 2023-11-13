extends CardResource
class_name Card

enum TypeEnum {
	none,
	unit,
	item,
	source,
	spell,
	token
}

enum KeywordEnum {
	none,
	flying,
	siege,
	poison
}

@export var name: String
@export var costs: Array = []
@export var types: Array = []
@export var subtypes: Array = []
@export var abilities: Array = []
@export var power: int = 1
@export var health: int = 1

func convert_keyword(keyword: String):
	match keyword.to_lower():
		"flying": return KeywordEnum.flying
		"siege": return KeywordEnum.siege
		"poison": return KeywordEnum.poison
		_: return ColorEnum.none
