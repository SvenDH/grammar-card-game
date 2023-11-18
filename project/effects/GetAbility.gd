extends BaseEffect

@export var abilities: Array
@export var until: Condition

func activate(ability: Ability):
	var status = AbilitiesAdded.new()
	status.until = until
	status.abilities = []
	for a in abilities:
		if a is ModAbility:
			status.abilities.append(a.get_stats(ability))
		else:
			status.abilities.append(a)
	return [[status]]

func resolve(_ability: Ability, card: CardInstance, status):
	card.add_status(status)
