extends BaseEffect

@export var number: int = 1
@export var objects: ObjectMatch

func targets(ability: Ability):
	return objects.targets(ability)

func has_target():
	return objects.has_target()

func activate(ability: Ability):
	return [[getnumber(number, ability)]]

func resolve(ability: Ability, player: CardPlayer, n: int = 1):
	await player.game.trigger(player.game.discarded, [player, n])
	if not player.hand.cards():
		return
		
	var choices
	if objects:
		choices = player.query(ability, objects, ZoneMatch.ZoneEnum.hand)
	else:
		choices = player.hand.cards()
	if choices:
		for card in await player.choose("discard", choices, n):
			await player.remove(card)
			await player.place(card, ZoneMatch.ZoneEnum.pile)
			await card.on_discard()
