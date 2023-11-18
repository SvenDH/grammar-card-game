extends BaseEffect

@export var objects: ObjectMatch
@export var until: Condition

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ability: Ability):
	var results = []
	var res = await ability.game.pick(ability, objects)
	if res == null:
		return null
	for d in res:
		results.append([d, until])
	return results
