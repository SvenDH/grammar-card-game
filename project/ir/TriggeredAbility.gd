extends CardAbility
class_name TriggeredAbility

@export var trigger: Trigger
@export var effect: Effect

func activate(player, card):
	var game: CardGame = player.game
	var ability = Ability.new()
	ability.game = game
	ability.source = card
	ability.controller = player
	ability.ability = self
	
	if trigger.trigger == Trigger.TriggerEnum.whenplay:
		game.played.connect(on_play.bind(ability))
	elif trigger.trigger == Trigger.TriggerEnum.whengainlife:
		game.lifechanged.connect(on_lifegained.bind(ability))
	elif trigger.trigger == Trigger.TriggerEnum.whenloselife:
		game.lifechanged.connect(on_lifelost.bind(ability))
	elif trigger.trigger == Trigger.TriggerEnum.whendamaged:
		game.healthchanged.connect(on_damaged.bind(ability))
	elif trigger.trigger == Trigger.TriggerEnum.endofturn:
		game.phasechanged.connect(on_endofturn.bind(ability))
	elif trigger.trigger == Trigger.TriggerEnum.beginningofphase:
		game.phasechanged.connect(on_beginningofphase.bind(ability))
	elif trigger.trigger == Trigger.TriggerEnum.condition:
		if trigger.condition.condition == Condition.ConditionEnum.objectcond:
			var objcond: ObjectCondition = trigger.condition
			if objcond.phrase == ObjectCondition.ObjectPhraseEnum.whenenters:
				game.entered.connect(on_entered.bind(ability))
			elif objcond.phrase == ObjectCondition.ObjectPhraseEnum.leaves:
				game.left.connect(on_left.bind(ability))
			elif objcond.phrase == ObjectCondition.ObjectPhraseEnum.dies:
				game.destroyed.connect(on_died.bind(ability))
				
	return ability

func on_entered(card: CardInstance, ability: Ability):
	if card in ability.game.query(ability, trigger.condition.subject):
		if trigger.condition.possesion and card.controller not in \
			ability.game.query(ability, trigger.condition.possesion):
			return ability.game.triggered.emit()
		await effect.activate(ability)
	ability.game.triggered.emit()

func on_left(card: CardInstance, ability: Ability):
	if card in ability.game.query(ability, trigger.condition.subject):
		await effect.activate(ability)
	ability.game.triggered.emit()

func on_died(card: CardInstance, ability: Ability):
	if card in ability.game.query(ability, trigger.condition.subject):
		await effect.activate(ability)
	ability.game.triggered.emit()

func on_play(player: CardPlayer, card: CardInstance, ability: Ability):
	if ability.controller == player and card in player.query(ability, trigger.objects):
		await effect.activate(ability)
	ability.game.triggered.emit()

func on_lifegained(player: CardPlayer, value: int, source, ability: Ability):
	if value > 0 and player in ability.game.query(ability, trigger.players):
		await effect.activate(ability)
	ability.game.triggered.emit()

func on_lifelost(player: CardPlayer, value: int, source, ability: Ability):
	if value < 0 and player in ability.game.query(ability, trigger.players):
		await effect.activate(ability)
	ability.game.triggered.emit()

func on_damaged(card: CardInstance, value: int, source, ability: Ability):
	if value < 0 and card in card.game.query(ability, trigger.objects):
		await effect.activate(ability)
	ability.game.triggered.emit()

func on_endofturn(player: CardPlayer, phase: Phase.PhaseEnum, ability: Ability):
	if phase == Phase.PhaseEnum.cleanup:
		await effect.activate(ability)
	ability.game.triggered.emit()

func on_beginningofphase(player: CardPlayer, phase: Phase.PhaseEnum, ability: Ability):
	if phase == Phase.PhaseEnum.cleanup:
		await effect.activate(ability)
	ability.game.triggered.emit()
