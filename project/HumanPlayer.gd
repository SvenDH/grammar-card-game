extends CardPlayer

signal action_done(param)

@onready var pass_button = $PassButton

func choose(command: String, choices: Array):
	print(command)
	if command == "field":
		hand.hide()
		pass_button.show()
		board.highlight(choices)
		var action = await action_done
		print(action)
		board.highlight([])
		hand.show()
		pass_button.hide()
		if action is String and action == "pass" or not action is int:
			return -1
		return action
	
	return choices[len(choices)-1]

func choose_action():
	pass_button.show()
	# TODO: get castable cards and abilities from other places
	var castable_cards = []
	for card in hand.cards():
		if card.can_cast(ctx):
			castable_cards.append(card)
	hand.highlight(castable_cards)
	
	var board_cards = []
	for card in board.cards():
		if card.can_activate(ctx):
			board_cards.append(card)
	print(board_cards)
	board.highlight(board_cards)
	
	hand.show()
	var action = await action_done
	print(action)
	hand.highlight([])
	hand.hide()
	pass_button.hide()
	if action is int:
		if action == -1:
			return false
		# Activate ability
		var card: CardInstance = board.get_card(action)
		var activatable = []
		for ab in card.activated_abilities:
			if ab.can_activate(ctx):
				activatable.append(ab)
		var ability
		if len(activatable) > 1:
			ability = await choose("ability", activatable)
		elif len(activatable) == 1:
			ability = activatable[0]
		else:
			return false
		card.activate_ability(ctx, ability)
	elif action is CardInstance:
		# Cast card
		await action.cast(ctx)
	elif action == "pass":
		# Skip
		return true
	return false

func _on_pass_button_pressed():
	action_done.emit("pass")

func _on_hand_click(card: CardInstance):
	action_done.emit(card)

func _on_board_click(index):
	action_done.emit(index)
