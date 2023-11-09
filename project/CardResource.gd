extends Resource
class_name CardResource

enum ColorEnum {
	none,
	colorless,
	yellow,
	red,
	green,
	blue,
	multicolored,
	monocolored
}

const XNUM := 9999999999999999
const THATNUM := 8888888888888888

const COLORS := ["Y", "R", "G", "B"]

func getnumber(n, ctx: Dictionary):
	if n is int:
		if n == XNUM:
			# TODO: find value of X
			# TODO: ask player for X
			return ctx["X"]
		return n
	else:
		assert(false, "n can't be " + str(n))

func convert_color(color: String):
	match color:
		"Y": return ColorEnum.yellow
		"R": return ColorEnum.red
		"G": return ColorEnum.green
		"B": return ColorEnum.blue
		"U": return ColorEnum.colorless
		"M": return ColorEnum.multicolored
		"O": return ColorEnum.monocolored
		_: return ColorEnum.none
