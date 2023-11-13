extends CardStatus
class_name ControllerChanged

var original: CardPlayer
var new: CardPlayer

func apply(card: CardInstance):
	var index = await new.pick_free_field(card)
	card.controller.remove(card)
	if index == -1:
		card.player_owner.place(card, ZoneMatch.ZoneEnum.pile)
	else:
		card.controller = new
		new.place(card, ZoneMatch.ZoneEnum.board, index)

func remove(card: CardInstance):
	var index = await original.pick_free_field(card)
	card.controller.remove(card)
	if index == -1:
		card.player_owner.place(card, ZoneMatch.ZoneEnum.pile)
	else:
		card.controller = original
		new.place(card, ZoneMatch.ZoneEnum.board, index)
