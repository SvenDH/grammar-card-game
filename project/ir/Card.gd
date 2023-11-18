extends Match
class_name CardMatch

@export var ref: Reference
@export var type: Card.TypeEnum
@export var extra: int
@export var prefixes: Array = []
@export var suffixes: Array = []
@export var withwhat: Resource = null
@export var without: Card.KeywordEnum
@export var copies: bool = false

func targets(ctx: Dictionary) -> int:
	if ref == Reference.target:
		if extra != 0:
			return getnumber(extra, ctx)
		return 1
	return -1
	
func has_target() -> bool:
	return ref == Reference.target

func match_query(ability: Ability, other) -> bool:
	if not other is CardInstance:
		return false
	
	if type and type not in other.card.types:
		return false
	
	if ref == Reference.selfref and ability.ctx.self != other:
		return false
	elif ref in [Reference.it, Reference.this, Reference.that]:
		if ability.ctx.this != other:
			return false
	elif ref in [Reference.rest, Reference.another]:
		if ability.ctx.this == other:
			return false
		elif "these" in ability.ctx and other not in ability.ctx.these:
			return false
	elif ref == Reference.any:
		if other not in ability.ctx.these:
			return false
	elif ref == Reference.sac:
		if other not in ability.ctx.sacrificed:
			return false
	if ref in [Reference.each, Reference.all]:
		if "these" in ability.ctx and other not in ability.ctx.these:
			return false
	elif ref == Reference.chosen:
		if other in ability.ctx.chosen:
			# TODO: add choose action
			return false
	elif ref == Reference.target:
		if other in ability.ctx.targets:
			# TODO: add test for "another"
			return false
	elif ref in Countables and other in ability.ctx.selected:
		return false
	
	for prefix in prefixes:
		if not prefix.match_query(ability, other.card):
			return false
	for suffix in suffixes:
		if not suffix.match_query(ability, other.card):
			return false
	
	if withwhat != null:
		# TODO: implement more "with"
		if without not in other.abilities:
			return false
	
	if without and without in other.card.keyword_abilities:
		return false
	
	return true

