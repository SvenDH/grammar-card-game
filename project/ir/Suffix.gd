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

func match_query(ability: Ability, other) -> bool:
	if suffix == SuffixEnum.control:
		return subj.match_query(ability, other.controller)
	elif suffix == SuffixEnum.nocontrol:
		return not subj.match_query(ability, other.controller)
	elif suffix == SuffixEnum.own:
		return subj.match_query(ability, other.player_owner)
	elif suffix == SuffixEnum.noown:
		return not subj.match_query(ability, other.player_owner)
	elif suffix == SuffixEnum.inzone:
		for place in zones:
			if not place.match_query(ability, other):
				return false
	elif suffix == SuffixEnum.youplay:
		if "played" not in ability.ctx or ability.ctx.played != other:
			return false
		if ability.ctx.self.controller != other.controller:
			return false
	elif suffix == SuffixEnum.targets:
		if "targeting" not in ability.ctx:
			return false
		if ability.ctx.targeting != other:
			return false
		for o in ability.targets:
			if subj.match_query(ability, o):
				return true
		return false
	elif suffix == SuffixEnum.targetsonly:
		if "targeting" not in ability.ctx:
			return false
		if ability.ctx.targeting != other:
			return false
		if len(ability.targets) != 1:
			return false
		return subj.match_query(ability, ctx.targets[0])
	elif suffix == SuffixEnum.activatedthisway:
		if "activated" not in ctx or other not in ability.ctx.activated:
			return false
	elif suffix == SuffixEnum.deactivatedthisway:
		if "deactivated" not in ctx or other not in ability.ctx.deactivated:
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
