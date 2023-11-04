extends BaseEffect
class_name SubjectEffect

@export var effects: Array[BaseEffect] = []
@export var subject: Match

func activate(ctx: Dictionary):
	var game = ctx["game"]
	var effects = []
	for player in game.pick(ctx, subject):
		ctx["subject"] = player
		for e in effects:
			for action in e.activate(ctx):
				effects.append([player, e, action])
	game.send(ctx, effects)
