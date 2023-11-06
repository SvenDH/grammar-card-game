extends Node
class_name CardGame

const START_CARDS := 5

enum PhaseEnum {
	turn,
	activation,
	draw,
	play,
	fight,
	cleanup
}

var players: Array[CardPlayer] = []
var turn: int = 0
var phase: PhaseEnum = PhaseEnum.activation
var stack: Array = []

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
		for _i in range(START_CARDS):
			player.draw()
	
	var player = players[randi() % players.size()]
	while true:
		await do_turn(player)
		print(turn)
		turn += 1
		if player.turnsafterthis == 0:
			var idx := players.find(player)
			player = players[(idx + 1) % len(players)]
		else:
			player.turnsafterthis -= 1
	
func do_turn(player: CardPlayer):
	# TODO: add phase to ctx
	player.ctx = {
		"game": self,
		"turn": turn,
		"current_player": player,
		"reaction": false,
		"priority": player
	}
	player.start()
	
	player.draw()

	var done = false
	while not done:
		done = await player.choose_action()
	
	# TODO: combat
	
	player.end()

func send(ctx: Dictionary, effects: Array):
	var ability = PlayedAbility.new()
	ability.source = ctx["self"]
	ability.controller = ctx["controller"]
	ability.ability = ctx.get("ability")
	ability.effects = effects
	stack.append(ability)
	ctx["reaction"] = true
	
	while len(stack) > 0:
		for priority in len(players):
			var player = players[(turn + priority) % len(players)]
			ctx["priority"] = player
			player.ctx = ctx
			var done = false
			while not done:
				done = await player.choose_action()
		ability = stack.pop_back()
		if ability:
			ability.resolve(ctx)
	
	ctx["reaction"] = false

func pick(ctx: Dictionary, obj, place = null) -> Array:
	var n = obj.targets(ctx)
	if n > 0:
		var player: CardPlayer = ctx["controller"]
		ctx["targets"] = []
		for _i in n:
			var found = query(ctx, obj, place)
			if len(found) == 0:
				return ctx["targets"]
			var choice = await player.choose("target", found)
			ctx["targets"].append(choice)
		return ctx["targets"]
	
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
