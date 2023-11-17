extends CardPlayer

signal action_done(param)

@onready var pass_button := $PassButton
@onready var essence_pool := $Control3/EssencePool
@onready var ability_menu := $Control4/AbilityMenu

func choose(command: String, choices := []):
	get_viewport().set_input_as_handled()
	pass_button.hide()
	ability_menu.hide()
	print(command)
	if command == "action":
		if len(choices) == 0:
			if game.reaction:
				# TODO: make auto pass optional for multiplayer
				return true
		for player in game.players:
			player.board.highlight(choices)
		hand.highlight(choices)
		pass_button.show()
		hand.show()
		var card = await action_done
		hand.reset()
		hand.hide()
		pass_button.hide()
		
		if card is String and card == "pass":
			# Skip
			return true
		# Can cast and can activate add another menu
		if card.can_activate():
			var activatable = []
			for ab in card.activated_abilities:
				if ab.can_activate(card):
					activatable.append(ab)
			if activatable:
				# Activate ability
				var ability
				if len(activatable) > 1:
					ability = await choose("ability", activatable)
				elif len(activatable) == 1:
					ability = activatable[0]
				if ability == null:
					return false
				await card.activate_ability(ability)
		
		elif card.is_source():
			# Play card
			await card.play()
		
		elif card.can_cast():
			# Cast card
			await card.cast()
		
		return false
	
	elif command == "discard":
		board.reset()
		hand.highlight(choices)
		hand.show()
		pass_button.hide()
		var card = await action_done
		return card
	
	elif command == "field":
		hand.hide()
		pass_button.show()
		for player in game.players:
			player.board.highlight(choices)
		
		var action = await action_done
		board.reset()
		hand.show()
		pass_button.hide()
		if action is String and action == "pass" or not action is int:
			return -1
		
		return action
	
	elif command == "target":
		pass_button.show()
		for player in game.players:
			player.board.highlight(choices)
		
		var card = await action_done
		board.reset()
		pass_button.hide()
		if card is String and card == "pass":
			return null
		
		return card
		
	elif command == "ability":
		ability_menu.show()
		ability_menu.set_abilities(choices)
		var ability = await action_done
		ability_menu.reset()
		ability_menu.hide()
		if ability is ActivatedAbility:
			return ability
		
		return null
	
	return choices[len(choices)-1]

func clear_essence():
	essence = []
	essence_pool.set_essence(essence)

func add_essence(color):
	essence.append(color)
	essence_pool.set_essence(essence)

func remove_essence(color):
	essence.erase(color)
	essence_pool.set_essence(essence)

func _on_pass_button_pressed():
	action_done.emit("pass")

func _on_hand_click(card: CardInstance):
	action_done.emit(card)

func _on_board_click(index):
	action_done.emit(index)

func _on_ability_menu_click(ability):
	action_done.emit(ability)
