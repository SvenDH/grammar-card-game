extends Match
class_name SuffixMatch

enum SuffixEnum {
	none,
	control,
	nocontrol,
	own,
	noown,
	inzone,
	youplay,
	targets,
	targetsonly,
	couldtarget,
	activatedthisway,
	deactivatedthisway,
	chosentype,
	amongthem
}

@export var suffix: SuffixEnum
@export var subj: Match = null
@export var zones: Array[ZoneMatch] = []

func match_query(ctx: Dictionary, other) -> bool:
	if suffix == SuffixEnum.control:
		return subj.match_query(ctx, other.control)
	elif suffix == SuffixEnum.nocontrol:
		return not subj.match_query(ctx, other.control)
	elif suffix == SuffixEnum.own:
		return subj.match_query(ctx, other.owner)
	elif suffix == SuffixEnum.noown:
		return not subj.match_query(ctx, other.owner)
	elif suffix == SuffixEnum.inzone:
		for place in zones:
			if not place.match_query(ctx, other):
				return false
	elif suffix == SuffixEnum.youplay:
		if "played" not in ctx or ctx["played"] != other:
			return false
		if ctx["controller"] != other.control:
			return false
	elif suffix == SuffixEnum.targets:
		if "targets" not in ctx or "targeting" not in ctx:
			return false
		if ctx["targeting"] != other:
			return false
		for o in ctx["targets"]:
			if subj.match_query(ctx, o):
				return true
		return false
	elif suffix == SuffixEnum.targetsonly:
		if "targets" not in ctx or "targeting" not in ctx:
			return false
		if ctx["targeting"] != other:
			return false
		if ctx["targets"].size() != 1:
			return false
		return subj.match_query(ctx, ctx["targets"][0])
	elif suffix == SuffixEnum.activatedthisway:
		if "activated" not in ctx or other not in ctx["activated"]:
			return false
	elif suffix == SuffixEnum.deactivatedthisway:
		if "deactivated" not in ctx or other not in ctx["deactivated"]:
			return false
	elif suffix == SuffixEnum.couldtarget:
		# TODO: implement couldtarget
		return false
	elif suffix == SuffixEnum.chosentype:
		# TODO: implement chosentype
		return false
	elif suffix == SuffixEnum.amongthem:
		# TODO: implement amongthem
		return false
	return true
