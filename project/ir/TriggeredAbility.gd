extends CardAbility
class_name TriggeredAbility

@export var trigger: Trigger
@export var effect: Effect

func activate(ctx: Dictionary):
	var game: CardGame = ctx.game
	var controller = ctx.priority
	if trigger.trigger == Trigger.TriggerEnum.whenplay:
		game.played.connect(on_play.bind(controller))
	elif trigger.trigger == Trigger.TriggerEnum.whengainlife:
		game.lifechanged.connect(on_lifegained.bind(controller))
	elif trigger.trigger == Trigger.TriggerEnum.whenloselife:
		game.lifechanged.connect(on_lifelost.bind(controller))
	elif trigger.trigger == Trigger.TriggerEnum.whendamaged:
		game.healthchanged.connect(on_damaged.bind(controller))
	elif trigger.trigger == Trigger.TriggerEnum.endofturn:
		game.phasechanged.connect(on_endofturn.bind(controller))
	elif trigger.trigger == Trigger.TriggerEnum.beginningofphase:
		game.phasechanged.connect(on_beginningofphase.bind(controller))

func on_play(player: CardPlayer, card: CardInstance, controller: CardPlayer):
	if controller == player and card in player.query(controller.ctx, trigger.objects):
		await effect.activate(controller.ctx)

func on_lifegained(player: CardPlayer, value: int, source, controller: CardPlayer):
	if value > 0 and player in player.game.query(controller.ctx, trigger.players):
		await effect.activate(controller.ctx)

func on_lifelost(player: CardPlayer, value: int, source, controller: CardPlayer):
	if value < 0 and player in player.game.query(controller.ctx, trigger.players):
		await effect.activate(controller.ctx)

func on_damaged(card: CardInstance, value: int, source, controller: CardPlayer):
	if value < 0 and card in card.game.query(controller.ctx, trigger.objects):
		await effect.activate(controller.ctx)

func on_endofturn(player: CardPlayer, phase: Phase.PhaseEnum, controller: CardPlayer):
	if phase == Phase.PhaseEnum.cleanup:
		await effect.activate(controller.ctx)

func on_beginningofphase(player: CardPlayer, phase: Phase.PhaseEnum, controller: CardPlayer):
	if phase == Phase.PhaseEnum.cleanup:
		await effect.activate(controller.ctx)
