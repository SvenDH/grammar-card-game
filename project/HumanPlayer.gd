extends CardPlayer

signal action_done(param)

@onready var pass_button := $PassButton
@onready var submit_button := $SubmitButton
@onready var essence_pool := $Control3/EssencePool
@onready var ability_menu := $Control4/AbilityMenu

func choose(command: String, choices := [], n := 1):
	get_viewport().set_input_as_handled()
	pass_button.hide()
	submit_button.hide()
	ability_menu.hide()
	ability_menu.reset()
	hand.reset()
	board.reset()
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
			if card.can_attack():
				activatable.append("{T}: Attack")
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
				if ability is String and ability == "{T}: Attack":
					await card.attack()
				else:
					await card.activate_ability(ability)
		
		elif card.is_source():
			# Play card
			await card.play()
		
		elif card.can_cast():
			# Cast card
			await card.cast()
		
		return false
	
	elif command == "discard":
		hand.show()
		var selected := []
		while true:
			if len(selected) == n:
				submit_button.show()
				hand.highlight(selected)
				var card = await action_done
				if card is String and card == "submit":
					return selected
				
				selected.erase(card)
				card.deselect()
			else:
				submit_button.hide()
				hand.highlight(choices)
				var card = await action_done
				if card in selected:
					selected.erase(card)
					card.deselect()
				else:
					selected.append(card)
					card.select()
	
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
		var selected := []
		while true:
			if len(selected) == n:
				submit_button.show()
				for player in game.players:
					player.board.highlight(selected)
				var card = await action_done
				if card is String and card == "submit":
					return selected
				
				selected.erase(card)
				card.deselect()
			else:
				submit_button.hide()
				for player in game.players:
					player.board.highlight(choices)
				var card = await action_done
				if card in selected:
					selected.erase(card)
					card.deselect()
				else:
					selected.append(card)
					card.select()
		
	elif command == "ability":
		ability_menu.show()
		ability_menu.set_abilities(choices)
		
		var ability = await action_done
		if ability is String and ability == "pass":
			return null
		
		return ability
	
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

func _on_submit_button_pressed():
	action_done.emit("submit")

func _on_hand_click(card: CardInstance):
	action_done.emit(card)

func _on_board_click(index):
	action_done.emit(index)

func _on_ability_menu_click(ability):
	action_done.emit(ability)
