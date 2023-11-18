extends RefCounted
class_name Ability

var source: CardInstance
var controller: CardPlayer
var ability: CardAbility
var ctx := {}
var effects := []
var targets := []
var game
var subject = null

func resolve():
	for eff in effects:
		ctx.subject = eff[0]
		var params = [self, eff[0]]
		params.append_array(eff[2])
		# TODO: should targets be checked here?
		await eff[1].callv("resolve", params)

func on_counter():
	await game.trigger(game.countered, [self])

func copy(ability):
	ability.source = source
	ability.controller = controller
	ability.ability = ability
	ability.ctx = ctx
	ability.effects = effects
	ability.targets = targets
	ability.game = game
	ability.subject = subject
