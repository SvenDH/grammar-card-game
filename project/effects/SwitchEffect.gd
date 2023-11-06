extends BaseEffect

@export var objects: ObjectMatch
@export var until: Condition

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
		var status = StatsChanged.new()
		status.until = until
		status.original_power = card.power
		status.original_health = card.health
		var temp = card.health
		card.health = card.power
		card.power = temp
		card.add_status(status)
