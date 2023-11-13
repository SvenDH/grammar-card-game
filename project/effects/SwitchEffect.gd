extends BaseEffect

@export var objects: ObjectMatch
@export var until: Condition

func targets(ctx):
	return objects.targets(ctx)

func activate(ctx: Dictionary):
	var results = []
	var res = await ctx.game.pick(ctx, objects)
	if res == null:
		return null
	for d in res:
		results.append([d, until])
	return results

func resolve(player: CardPlayer, card: CardInstance, until = null):
	if card.location == ZoneMatch.ZoneEnum.board:
		var status = StatsSwapped.new()
		status.until = until
		card.add_status(status)
