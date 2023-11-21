extends CardPlayer

var actions := [
	{"action": [0, 0, 0, 0], "field": [2, 0], "ability": [0]}
]
var current_actions = {}

func _start():
	current_actions = actions.pop_front()
	if current_actions == null:
		current_actions = {}

func choose(command: String, choices := [], n := 1):
	var index = current_actions.get(command, []).pop_front()
	if index == null: index = -1
	if command == "action":
		if len(choices) == 0:
			return true
		if index == -1:
			return true
		var card = choices[index]
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
			await card.play()
		elif card.can_cast():
			# Cast card
			await card.cast()
		return false
	
	return choices[index]

func _on_board_click(card):
	for player in game.players:
		if player != self:
			player.action_done.emit(card)
