extends BaseEffect

@export var amount: int
@export var recipients: Array
@export var spread: bool

func activate(ability: Ability):
	var results = []
	for recipient in recipients:
		var res
		if recipient == Match.Reference.anytarget:
			res = await ability.game.pick(ability, null, ZoneMatch.ZoneEnum.board)
		else:
			res = await ability.game.pick(ability, recipient, ZoneMatch.ZoneEnum.board)
		if res == null:
			return null
		for d in res:
			print(d, amount)
			results.append([d, getnumber(amount, ability)])
	return results

func resolve(_ability: Ability, source: CardInstance, obj, damage: int):
	print(obj, damage)
	obj.damage(damage, source)
