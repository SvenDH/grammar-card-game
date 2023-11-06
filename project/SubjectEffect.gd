extends BaseEffect
class_name SubjectEffect

@export var effects: Array = []
@export var subject: Match

func activate(ctx: Dictionary):
	var game = ctx["game"]
	var played = []
	for player in await game.pick(ctx, subject):
		ctx["subject"] = player
		for e in effects:
			for action in await e.activate(ctx):
				played.append([player, e, action])
	await game.send(ctx, played)
