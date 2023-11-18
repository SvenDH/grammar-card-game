extends CardResource
class_name Match

enum Reference {
	none,
	selfref,
	it,
	they,
	rest,
	sac,
	any,
	this,
	that,
	the,
	another,
	chosen,
	each,
	all,
	target,
	atleast,
	exactly,
	ormore,
	fewerthan,
	anynumberof,
	upto,
	oneof,
	your,
	their,
	itself,
	anytarget
}

enum NumbericalEnum {
	damage,
	health,
	level
}

const Countables = [Reference.exactly, Reference.atleast, Reference.ormore, Reference.fewerthan, Reference.upto, Reference.oneof, Reference.anynumberof]

func targets(_ctx: Dictionary) -> int:
	return -1

func has_target() -> bool:
	return false

func match_query(_ability: Ability, _other) -> bool:
	return false
