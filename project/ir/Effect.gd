extends Resource
class_name Effect

@export var effects: Array[BaseEffect] = []
@export var optional: bool = false

func is_essence_ability(ctx):
	if targets(ctx) != -1:
		return false
	for eff in effects:
		if not eff.is_essence_ability(ctx):
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

func activate(ctx: Dictionary):
	# TODO: add optional check
	var played = []
	for e in effects:
		var res = await e.activate(ctx)
		if res == null:
			return null
		played.append_array(res)
	return await ctx.game.send(ctx, played, not is_essence_ability(ctx))
