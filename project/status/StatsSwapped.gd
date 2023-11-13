extends CardStatus
class_name StatsSwapped

func apply(card: CardInstance):
	var temp = card.power
	card.power = card.health
	card.health = temp

func remove(card: CardInstance):
	var temp = card.power
	card.power = card.health
	card.health = temp
