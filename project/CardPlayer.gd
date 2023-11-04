extends Node
class_name CardPlayer

@export var player_name: String
@export var life: int = 20
@export var cards: Array[Card] = []
@export var side: Array[Card] = []

var game = null
var callback
var turnsafterthis: int = 0
var essence := []
var ctx := {}

@onready var board: CardFields = $Board
@onready var deck: CardPile = $Deck
@onready var pile: CardPile = $Pile
@onready var hand: CardPile = $Hand

func _ready():
	for card in cards:
		var inst = CardInstance.new()
		inst.player_owner = self
		inst.card = card
		deck.add(inst)

func can_cast():
	# TODO: get castable cards not in hand
	for card in hand.cards():
		if card.can_cast(ctx):
			return true
	return false

func can_activate():
	# TODO: get activatable cards not on board
	for card in board.cards():
		if card != null and card.can_activate(ctx):
			return true
	return false

func choose_action():
	# TODO: get possible actions
	var idx = await callback.choose("action", callback.choices)
	match callback.choices[idx]:
		"play":
			cast()
		"activate":
			activate()
		"pass":
			return true
	return false
	
func start():
	essence = []
	# TODO: activate cards
	on_startturn()

func end():
	on_endturn()
	essence = []

func cast():
	var card = await callback.choose("hand", hand.cards())
	hand.remove(card)
	card.cast(ctx)
	on_cast(card)

func draw(side_: bool = false):
	var card: CardInstance
	if side_:
		card = CardInstance.new()
		card.player_owner = self
		card.card = side[randi() % len(side)]
		card.side = true
	else:
		card = deck.pop()
	place(card, ZoneMatch.ZoneEnum.hand)
	on_draw(card)

func activate():
	# TODO: get payable and playable abilities
	# TODO: include enemy abilities
	# TODO: include abilities from other places
	var card_options = []
	for card in board.cards():
		if card.activated_abilities():
			card_options.append(card)
	var index = await callback.choose("Activate ability of:", card_options)
	var card: CardInstance = board.get_card(index)
	
	
	var abilities = []
	for ability in card.activated_abilities:
		if ability.can_activate():
			abilities.append(ability)
	var idx = await callback.choose("Choose ability:", abilities)
	card.activate_ability(ctx, idx)

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
		assert(to_index != null and 0 <= to_index < deck.num_fields)
		assert(board.get_card(to_index) == null)     # TODO: should this be allowed?
		board.place(card, to_index)
		card.location = ZoneMatch.ZoneEnum.board
		card.field_index = to_index
		card.controller = self
		on_enter(card)

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
		on_exit(card)

func query(ctx: Dictionary, obj = null, place = null) -> Array[CardInstance]:
	var found = []
	if _match_field(ctx, ZoneMatch.ZoneEnum.board, place):
		for card in board.cards():
			if card and (obj == null or obj.match_query(ctx, card)):
				found.append(card)
	if _match_field(ctx, ZoneMatch.ZoneEnum.hand, place):
		for card in hand.cards():
			if obj == null or obj.match_query(ctx, card):
				found.append(card)
	if _match_field(ctx, ZoneMatch.ZoneEnum.pile, place):
		for card in pile.cards():
			if obj == null or obj.match_query(ctx, card):
				found.append(card)
	if _match_field(ctx, ZoneMatch.ZoneEnum.deck, place):
		for card in deck.cards():
			if obj == null or obj.match_query(ctx, card):
				found.append(card)
	if _match_field(ctx, ZoneMatch.ZoneEnum.stack, place):
		for card in game.stack:
			if card.controller == self:
				if obj == null or obj.match_query(ctx, card):
					found.append(card)
	return found

func _match_field(ctx: Dictionary, place: ZoneMatch.ZoneEnum, match_query) -> bool:
	if match_query == null:
		return true
	if match_query is ZoneMatch:
		return match_query.match_query(ctx, place, self)
	return place == match_query

func on_startturn():
	pass

func on_enter(card: CardInstance):
	pass

func on_exit(card: CardInstance):
	pass

func on_draw(card: CardInstance):
	pass

func on_discard(card: CardInstance):
	pass

func on_cast(card: CardInstance):
	pass

func on_destroy(card: CardInstance):
	pass

func on_counter(ability):
	pass

func on_endturn():
	pass
