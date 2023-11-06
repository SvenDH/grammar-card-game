extends BaseEffect
class_name SubjectEffect

@export var effects: Array = []
@export var subject: Match

func activate(ctx: Dictionary):
	var game = ctx.game
	var played = []
	var subj = await game.pick(ctx, subject)
	if subj == null:
		return null
	
	for player in subj:
		ctx.subject = player
		for e in effects:
			var res = await e.activate(ctx)
			if res == null:
				return null
			
			for action in res:
				played.append([player, e, action])
	return played
