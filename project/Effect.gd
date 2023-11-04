extends Resource
class_name Effect

@export var effects: Array[BaseEffect] = []
@export var optional: bool = false

func activate(ctx: Dictionary):
	# TODO: add optional check
	for e in effects:
		e.activate(ctx)
