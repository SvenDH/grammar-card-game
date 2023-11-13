extends BaseEffect

@export var abilities: Array
@export var until: Condition

func activate(ctx: Dictionary):
	var status = AbilitiesAdded.new()
	status.until = until
	status.abilities = []
	for ability in abilities:
		if ability is ModAbility:
			status.abilities.append(ability.get_stats(ctx))
		else:
			status.abilities.append(ability)
	return [[status]]

func resolve(card: CardInstance, status):
	card.add_status(status)
