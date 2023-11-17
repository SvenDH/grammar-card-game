extends BaseEffect

@export var objects: ObjectMatch

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ctx: Dictionary):
	var results = []
	var res = await ctx.game.pick(ctx, objects, ZoneMatch.ZoneEnum.stack)
	if res == null:
		return null
	for d in res:
		results.append([d])
	return results

func resolve(player: CardPlayer, obj):
	if obj in player.game.stack:
		await obj.on_counter()
		player.game.stack.remove(obj)
