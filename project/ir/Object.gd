extends Match
class_name ObjectMatch

@export var objects: Array[Match] = []
@export var each: bool = false

func targets(ctx: Dictionary) -> int:
	for obj in objects:
		var n = obj.targets(ctx)
		if n > 0:
			return n
	return -1

func match_query(ctx: Dictionary, other) -> bool:
	for o in objects:
		if not o.match_query(ctx, other):
			return false
	return true
