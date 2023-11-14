extends Condition
class_name ObjectCondition

enum ObjectPhraseEnum {
	blocked,
	attacked,
	targets,
	leaves,
	dies,
	moveszone,
	whenenters,
	dealsdamage
}

@export var phrase: ObjectPhraseEnum
@export var subject: ObjectMatch
@export var object: ObjectMatch
@export var possesion: PlayerMatch
@export var into: ZoneMatch
@export var from: ZoneMatch
@export var damagerecipients: DamageRecipients

