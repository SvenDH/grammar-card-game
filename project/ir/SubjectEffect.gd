extends BaseEffect
class_name SubjectEffect

@export var effects: Array = []
@export var subject: Match
@export var foreach: Match
@export var condition: Condition

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
	var game = ctx.game
	var subj = await game.pick(ctx, subject)
	if subj == null:
		return null
	var n = 1
	if foreach != null:
		n = len(await game.pick(ctx, foreach, ZoneMatch.ZoneEnum.board))
	var played = []
	for _i in n:
		for player in subj:
			ctx.subject = player
			for e in effects:
				var res = await e.activate(ctx)
				if res == null:
					return null
				
				for action in res:
					played.append([player, e, action])
	return played
