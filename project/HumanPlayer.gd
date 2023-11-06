extends CardPlayer

signal action_done(param)

@onready var pass_button = $PassButton

func choose(command: String, choices := []):
	print(command)
	if command == "action":
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
		board.highlight(board_cards)
		
		hand.show()
		var action = await action_done
		hand.highlight([])
		hand.hide()
		pass_button.hide()
		
		var card: CardInstance
		if action is String and action == "pass":
			# Skip
			return true
		
		elif action is int:
			if action == -1:
				return false
			card = board.get_card(action)
		elif action is CardInstance:
			card = action
		
		var activatable = []
		for ab in card.activated_abilities:
			if ab.can_activate(ctx):
				activatable.append(ab)
		if activatable:
			# Activate ability
			var ability
			if len(activatable) > 1:
				ability = await choose("ability", activatable)
			elif len(activatable) == 1:
				ability = activatable[0]
			print(ability.text)
			await card.activate_ability(ctx, ability)
		elif card.can_cast(ctx):
			# Cast card
			await card.cast(ctx)
		
		return false
	
	elif command == "field":
		hand.hide()
		pass_button.show()
		board.highlight(choices)
		var action = await action_done
		board.highlight([])
		hand.show()
		pass_button.hide()
		if action is String and action == "pass" or not action is int:
			return -1
		
		return action
	
	elif command == "target":
		print(choices)
		board.highlight(choices)
		var action = await action_done
		print(action)
		return action
		
	elif command == "ability":
		pass
	
	return choices[len(choices)-1]

func _on_pass_button_pressed():
	action_done.emit("pass")

func _on_hand_click(card: CardInstance):
	action_done.emit(card)

func _on_board_click(index):
	action_done.emit(index)
