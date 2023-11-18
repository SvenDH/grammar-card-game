extends BaseEffect

@export var number: int = 1
@export var objects: ObjectMatch

func targets(ctx):
	return objects.targets(ctx)

func has_target():
	return objects.has_target()

func activate(ability: Ability):
	return [[getnumber(number, ability), objects]]

func resolve(ability: Ability, player: CardPlayer, n: int = 1, query_match = null):
	await player.game.trigger(player.game.discarded, [player, n])
	for _i in n:
		if not player.hand.cards():
			return
			
		var choices
		if query_match:
			choices = player.query(ability, query_match, ZoneMatch.ZoneEnum.hand)
		else:
			choices = player.hand.cards()
		if choices:
			var card = await player.choose("discard", choices)
			await player.remove(card)
			await player.place(card, ZoneMatch.ZoneEnum.pile)
			await card.on_discard()
