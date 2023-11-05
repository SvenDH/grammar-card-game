extends CardPlayer

signal action_done(param)

@onready var pass_button = $PassButton

func choose(command: String, choices: Array):
	if command == "action":
		pass_button.show()
		var action = await action_done
		print(action)
		print(hand.cards())
		pass_button.hide()
		return action
	
	print(command)
	return choices[len(choices)-1]


func _on_pass_button_pressed():
	action_done.emit("pass")
