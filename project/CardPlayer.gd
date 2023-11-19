extends Node
class_name CardPlayer

@export var player_name: String
@export var life: int = 20
@export var cards: Array[Card] = []
@export var side: Array[Card] = []
@export var card_scene: PackedScene
@export var board_path: NodePath
@export var deck_path: NodePath
@export var pile_path: NodePath
@export var hand_path: NodePath

var turnsafterthis: int = 0
var essence := []

@onready var game = get_parent()
@onready var board: CardFields = get_node(board_path)
@onready var deck: CardPile = get_node(deck_path)
@onready var pile: CardPile = get_node(pile_path)
@onready var hand: CardPile = get_node(hand_path)

func _ready():
	board.player = self
	deck.player = self
	pile.player = self
	hand.player = self
	
	for card in cards:
		deck.add(create_card_instance(card))

func _start():
	pass

func _end():
	pass

func create_card_instance(card):
	var inst = card_scene.instantiate()
	inst.player_owner = self
	inst.card = card
	inst.game = game
	return inst

func get_playable_cards():
	# TODO: get castable cards and abilities from other places
	var castable_cards = []
	for card in hand.cards():
		if card.can_cast():
			castable_cards.append(card)
	var board_cards = []
	for card in board.cards():
		if card.can_activate():
			board_cards.append(card)
	return castable_cards + board_cards

func choose(command: String, choices := []):
	if command == "action":
		return true
	# Overwrite with something smarter/ controlled by the player
	return choices[len(choices)-1]

func pick_free_field(card) -> int:
	var fields = board.free_fields(card)
	if not fields:
		return -1
	return await choose("field", fields)

func pay_costs(card: CardInstance, costs: Array):
	# TODO: Pay action costs
	# TODO: add choice of mana sources etc
	for symbol in costs:
		if symbol is String:
			if symbol == "T":
				await card.deactivate()
			elif symbol == "Q":
				await card.activate()
			elif symbol in Card.COLORS:
				remove_essence(symbol)
	for symbol in costs:
		if symbol is int:
			for _i in symbol:
				if "U" in essence:
					remove_essence("U")
				elif len(essence) > 0:
					remove_essence(essence[0])

func can_pay(card: CardInstance, costs: Array) -> bool:
	# TODO: add potential essence from essence sources
	# TODO: add extra costs
	var pool := essence.duplicate()
	for symbol in costs:
		if symbol is String:
			if symbol == "T" and not card.activated:
				return false
			elif symbol == "Q" and card.activated:
				return false
			elif symbol in Card.COLORS:
				if symbol not in pool:
					return false
				pool.erase(symbol)
	for symbol in costs:
		if symbol is int:
			if len(pool) < symbol:
				return false
			for _i in symbol:
				if "U" in pool:
					pool.erase("U")
				else:
					pool.pop_back()
	return true

func can_cast() -> bool:
	# TODO: get castable cards not in hand
	for card in hand.cards():
		if card.can_cast():
			return true
	return false

func can_activate() -> bool:
	# TODO: get activatable cards not on board
	for card in board.cards():
		if card != null and card.can_activate():
			return true
	return false
	
func start_turn():
	_start()
	clear_essence()
	for card in board.cards():
		await card.activate()
	await on_startturn()

func end_turn():
	await on_endturn()
	clear_essence()
	_end()

func clear_essence():
	essence = []

func add_essence(color):
	essence.append(color)

func remove_essence(color):
	essence.erase(color)

func draw(amount: int = 1, side_: bool = false):
	var card: CardInstance
	await game.trigger(game.drawn, [self, amount])
	for _i in amount:
		if side_:
			card = CardInstance.new()
			card.player_owner = self
			card.card = side[randi() % len(side)]
			card.side = true
		else:
			card = deck.pop()
		if card:
			await place(card, ZoneMatch.ZoneEnum.hand)
			await card.on_draw()
		else:
			# TODO: Lose the game
			pass

func shuffle(zone: ZoneMatch.ZoneEnum = ZoneMatch.ZoneEnum.deck):
	match zone:
		ZoneMatch.ZoneEnum.deck:
			deck.shuffle()
		ZoneMatch.ZoneEnum.pile:
			pile.shuffle()
		_: assert(false)

func place(card: CardInstance, place: ZoneMatch.ZoneEnum, to_index = null, relative = null):
	if place == ZoneMatch.ZoneEnum.deck:
		if relative == null or relative == ZoneMatch.PlaceEnum.top:
			if to_index == null:
				deck.add(card)
			else:
				deck.insert(card, len(deck.cards()) - to_index)
		else:
			if to_index == null:
				deck.insert(card, 0)
			else:
				deck.insert(card, to_index)
		card.location = ZoneMatch.ZoneEnum.deck
		card.field_index = -1
	elif place == ZoneMatch.ZoneEnum.pile:
		pile.add(card)
		card.location = ZoneMatch.ZoneEnum.pile
		card.field_index = -1
	elif place == ZoneMatch.ZoneEnum.hand:
		hand.add(card)
		card.location = ZoneMatch.ZoneEnum.hand
		card.field_index = -1
	elif place == ZoneMatch.ZoneEnum.board:
		assert(to_index != null and 0 <= to_index and to_index < board.num_fields)
		assert(board.get_card(to_index) == null)     # TODO: should this be allowed?
		board.place(card, to_index)
		card.location = ZoneMatch.ZoneEnum.board
		card.field_index = to_index
		card.controller = self
		await card.on_enter()

func remove(card: CardInstance):
	card.reset()
	if card.location == ZoneMatch.ZoneEnum.deck:
		assert(card in deck.cards())
		deck.remove(card)
	elif card.location == ZoneMatch.ZoneEnum.pile:
		assert(card in pile.cards())
		pile.remove(card)
	elif card.location == ZoneMatch.ZoneEnum.hand:
		assert(card in hand.cards())
		hand.remove(card)
	elif card.location == ZoneMatch.ZoneEnum.board:
		assert(card in board.cards())
		board.remove(board.index(card))
		await card.on_exit()

func query(ability: Ability, obj = null, place = null) -> Array:
	var found = []
	if _match_field(ability, ZoneMatch.ZoneEnum.board, place):
		for card in board.cards():
			if card and (obj == null or obj.match_query(ability, card)):
				found.append(card)
	if _match_field(ability, ZoneMatch.ZoneEnum.hand, place):
		for card in hand.cards():
			if obj == null or obj.match_query(ability, card):
				found.append(card)
	if _match_field(ability, ZoneMatch.ZoneEnum.pile, place):
		for card in pile.cards():
			if obj == null or obj.match_query(ability, card):
				found.append(card)
	if _match_field(ability, ZoneMatch.ZoneEnum.deck, place):
		for card in deck.cards():
			if obj == null or obj.match_query(ability, card):
				found.append(card)
	if _match_field(ability, ZoneMatch.ZoneEnum.stack, place):
		for item in game.stack.cards():
			if item.controller == self:
				if obj == null or obj.match_query(ability, item):
					found.append(item)
	return found

func _match_field(ability: Ability, place: ZoneMatch.ZoneEnum, match_query) -> bool:
	if match_query == null:
		return true
	if match_query is ZoneMatch:
		return match_query.match_query(ability, place, self)
	return place == match_query

func on_startturn():
	pass

func on_search():
	pass

func on_endturn():
	pass
