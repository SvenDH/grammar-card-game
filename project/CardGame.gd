extends Node
class_name CardGame

const START_CARDS := 5
const ability_scene := preload("res://AbilityInstance.tscn")

signal triggered

signal drawn(player: CardPlayer, amount: int)
signal discarded(player: CardPlayer, amount: int)
signal play(player: CardPlayer, what: CardInstance)
signal lifechanged(player: CardPlayer, value: int, source)
signal phasechanged(player: CardPlayer, phase: Phase.PhaseEnum)
signal entered(card: CardInstance)
signal left(card: CardInstance)
signal played(card: CardInstance)
signal destroyed(card: CardInstance)
signal activated(card: CardInstance)
signal deactivated(card: CardInstance)
signal healthchanged(card: CardInstance, value: int, source)
signal countered(thing)

var players: Array[CardPlayer] = []
var turn := 0
var phase: Phase.PhaseEnum = Phase.PhaseEnum.activation
var current_player = null
var priority = null
var reaction := false

@onready var stack := $Stack

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
	reaction = false
	current_player = player
	priority = player
	phase = Phase.PhaseEnum.activation
	await player.start_turn()
	phase = Phase.PhaseEnum.draw
	await player.draw()
	phase = Phase.PhaseEnum.play
	var done = false
	while not done:
		priority = player
		var choices = player.get_playable_cards()
		done = await player.choose("action", choices)
	phase = Phase.PhaseEnum.cleanup
	await player.end_turn()

func send(ability: Ability, effects: Array, use_stack := true):
	var new_ability := ability_scene.instantiate()
	ability.copy(new_ability)
	new_ability.effects = effects
	if use_stack:
		stack.add(new_ability)
		reaction = true
		
		while len(stack.cards()) > 0:
			for i in len(players):
				var player = players[(turn + i) % len(players)]
				priority = player
				var done = false
				while not done:
					var choices = player.get_playable_cards()
					done = await player.choose("action", choices)
			var other_ability = stack.pop()
			if other_ability:
				await other_ability.resolve()
		
		reaction = false
	else:
		await new_ability.resolve()

func pick(ability: Ability, obj, place = null):
	var n = obj.targets(ability)
	if n > 0:
		var player: CardPlayer = priority
		for _i in n:
			var found = query(ability, obj, place)
			if len(found) == 0:
				return ability.targets
			var choice = await player.choose("target", found)
			if choice == null:
				return null
			ability.targets.append(choice)
		return ability.targets
	
	return query(ability, obj, place)

func query(ability: Ability, obj, place = null, n: int = -1) -> Array:
	var found := []
	for player in players:
		if obj.match_query(ability, player):
			found.append(player)
		found.append_array(player.query(ability, obj, place))
	if n > 0:
		return found.slice(0, n)
	return found

func trigger(sig: Signal, params: Array):
	var n = len(sig.get_connections())
	emit_signal.bindv([sig.get_name()] + params).call_deferred()
	for _i in n:
		await triggered
