extends BaseEffect
class_name SubjectEffect

@export var effects: Array = []
@export var subject: Match
@export var foreach: Match
@export var condition: Condition

func is_essence_ability():
	if has_target():
		return false
	for eff in effects:
		if not eff.is_essence_ability():
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

func has_target() -> bool:
	for eff in effects:
		if eff.has_target():
			return true
	return false

func activate(ability: Ability):
	var game = ability.game
	var subj = await game.pick(ability, subject)
	if subj == null:
		return null
	var n = 1
	if foreach != null:
		n = len(await game.pick(ability, foreach, ZoneMatch.ZoneEnum.board))
	var played = []
	for _i in n:
		for player in subj:
			ability.subject = player
			for e in effects:
				var res = await e.activate(ability)
				if res == null:
					return null
				
				for action in res:
					played.append([player, e, action])
	return played
