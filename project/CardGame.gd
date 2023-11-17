extends Node
class_name CardGame

const START_CARDS := 5

signal drawn(player: CardPlayer, amount: int)
signal discarded(player: CardPlayer, amount: int)
signal play(player: CardPlayer, what: CardInstance)
signal lifechanged(player: CardPlayer, value: int, source)
signal phasechanged(player: CardPlayer, phase: Phase.PhaseEnum)
signal entered(card: CardInstance)
signal left(card: CardInstance)
signal destroyed(card: CardInstance)
signal healthchanged(card: CardInstance, value: int, source)
signal countered(thing)

var players: Array[CardPlayer] = []
var turn := 0
var phase: Phase.PhaseEnum = Phase.PhaseEnum.activation
var stack := []
var current_player = null
var priority = null
var reaction := false
var ctx

func _ready():
	for child in get_children():
		if child is CardPlayer:
			add_player(child)
	start()

func add_player(player: CardPlayer):
	player.game = self
	players.append(player)
	return player

func start():
	# TODO: add muligan
	for player in players:
		for _i in START_CARDS:
			player.draw()
	var player = players[randi() % players.size()]
	while true:
		await do_turn(player)
		turn += 1
		if player.turnsafterthis == 0:
			var idx := players.find(player)
			player = players[(idx + 1) % len(players)]
		else:
			player.turnsafterthis -= 1
	
func do_turn(player: CardPlayer):
	# TODO: add phase to ctx
	current_player = player
	reaction = false
	priority = player
	
	phase = Phase.PhaseEnum.activation
	player.start_turn()
	phase = Phase.PhaseEnum.draw
	player.draw()
	phase = Phase.PhaseEnum.play
	var done = false
	while not done:
		var choices = player.get_playable_cards()
		done = await player.choose("action", choices)
	phase = Phase.PhaseEnum.cleanup
	player.end_turn()

func send(ctx: Dictionary, effects: Array, use_stack := true):
	var ability = PlayedAbility.new()
	ability.source = ctx.self
	ability.controller = ctx.controller
	ability.ability = ctx.get("ability")
	ability.effects = effects
	if use_stack:
		stack.append(ability)
		reaction = true
		
		while len(stack) > 0:
			for i in len(players):
				var player = players[(turn + i) % len(players)]
				priority = player
				var done = false
				while not done:
					var choices = player.get_playable_cards()
					done = await player.choose("action", choices)
			ability = stack.pop_back()
			if ability:
				await ability.resolve(ctx)
		
		reaction = false
	else:
		await ability.resolve(ctx)

func pick(ctx: Dictionary, obj, place = null):
	var n = obj.targets(ctx)
	if n > 0:
		var player: CardPlayer = priority
		for _i in n:
			var found = query(ctx, obj, place)
			if len(found) == 0:
				return ctx.targets
			var choice = await player.choose("target", found)
			if choice == null:
				return null
			ctx.targets.append(choice)
		return ctx.targets
	
	return query(ctx, obj, place)

func query(ctx: Dictionary, obj, place = null, n: int = -1) -> Array:
	var found := []
	for player in players:
		if obj.match_query(ctx, player):
			found.append(player)
		found.append_array(player.query(ctx, obj, place))
	if n > 0:
		return found.slice(0, n)
	return found
