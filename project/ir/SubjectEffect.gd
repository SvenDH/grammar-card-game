extends BaseEffect
class_name SubjectEffect

@export var effects: Array = []
@export var subject: Match
@export var foreach: Match
@export var condition: Condition

func activate(ctx: Dictionary):
	var game = ctx.game
	var subj = await game.pick(ctx, subject)
	if subj == null:
		return null
	var n = 1
	if foreach != null:
		n = len(await game.pick(ctx, foreach))
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
