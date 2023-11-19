extends CardResource
class_name BaseEffect

func targets(_ability: Ability):
	return -1

func has_target():
	return false

func is_essence_ability():
	return false

func activate(_ability: Ability):
	pass
