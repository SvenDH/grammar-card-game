extends Match
class_name ObjectMatch

@export var objects: Array[Match] = []
@export var each: bool = false

func targets(ctx: Dictionary) -> int:
	for o in objects:
		var n = o.targets(ctx)
		if n > 0:
			return n
	return -1

func has_target() -> bool:
	for o in objects:
		if o.has_target():
			return true
	return false

func match_query(ctx: Dictionary, other) -> bool:
	for o in objects:
		if not o.match_query(ctx, other):
			return false
	return true
