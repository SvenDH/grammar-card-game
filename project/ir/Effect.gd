extends Resource
class_name Effect

@export var effects: Array[BaseEffect] = []
@export var optional: bool = false

func is_essence_ability():
	if has_target():
		return false
	for eff in effects:
		if not eff.is_essence_ability():
			return false
	return true

func targets(ctx):
	var total = 0
	var has_targets = false
	for eff in effects:
		var efftargets = eff.targets(ctx)
		if efftargets >= 0:
			total += efftargets
			has_targets = true
	if has_targets:
		return total
	return -1

func has_target() -> bool:
	for eff in effects:
		if eff.has_target():
			return true
	return false

func activate(ability: Ability):
	# TODO: add optional check
	var played = []
	for e in effects:
		var res = await e.activate(ability)
		if res == null:
			return null
		played.append_array(res)
	await ability.game.send(ability, played, not is_essence_ability())
