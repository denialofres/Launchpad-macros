import threading, enum
import mido
from collections import defaultdict

class Brightness(enum.Enum):
	OFF = 0
	LOW = 1
	MEDIUM = 2
	HIGH = 3


def _get_command_row_led_message(index: int, green: Brightness, red: Brightness) -> mido.Message:
	if not 0 <= index < 8:
		raise IndexError("Index out of range")
	return mido.Message.from_hex(f"B0 {hex(104 + index)[2:].zfill(2)} {green.value}{red.value}")

def _get_command_column_led_message(index: int, green: Brightness, red: Brightness) -> mido.Message:
	if not 0 <= index < 8:
		raise IndexError("Index out of range")
	return mido.Message.from_hex(f"90 {hex(index)[2:].zfill(1)}8 {green.value}{red.value}")

def _get_grid_led_message(index: int, green: Brightness, red: Brightness) -> mido.Message:
	if not 0 <= index < 64:
		raise IndexError("Index out of range")
	return mido.Message.from_hex(f"90 {hex(16 * (index // 8) + (index % 8))[2:].zfill(2)} {green.value}{red.value}")

def _get_grid_coordinates_led_message(row: int, col: int, green: Brightness, red: Brightness) -> mido.Message:
	if (not 0 <= row < 8) or (not 0 <= col < 8):
		raise IndexError("Coordinates out of range")
	return _get_grid_led_message(row * 8 + col, green, red)

class TargetRegion(enum.Enum):
	COMMAND_ROW = 0
	COMMAND_COLUMN = 1
	GRID = 2

def get_input_port_names():
	return mido.get_input_names()

def get_output_port_names():
	return mido.get_output_names()

class Launchpad:
	def __init__(self, input_port_name: str, output_port_name: str) -> None:
		self.thread = threading.Thread(target=self._execute_thread, daemon=False)
		self.input_port = mido.open_input(input_port_name)
		self.output_port = mido.open_output(output_port_name)
		self.map = defaultdict(lambda: {
			"on_press": [],
			"on_release": [],
		})
		# self.map will take a tuple as a key: (TargetRegion, Index)


	def on_press(self, target: TargetRegion, index: int, fn) -> None:
		self._add_action(target, index, fn, "on_press")

	def on_release(self, target: TargetRegion, index: int, fn) -> None:
		self._add_action(target, index, fn, "on_release")

	def _add_action(self, target: TargetRegion, index: int, fn, action_type: str) -> None:
		if target not in TargetRegion:
			raise AttributeError(f"{target} not in TargetRegion")
		if target == TargetRegion.COMMAND_COLUMN or target == TargetRegion.COMMAND_ROW:
			if not 0 <= index < 8:
				raise IndexError
		elif target == TargetRegion.GRID:
			if not 0 <= index < 64:
				raise IndexError
		self.map[(target, index)][action_type].append(fn)

	def run(self) -> None:
		self.thread.start()

	def _execute_thread(self) -> None:
		while True:
			for msg in self.input_port.iter_pending():
				if msg.type == "control_change":
					index = msg.control - 104
					for fn in self.map[(TargetRegion.COMMAND_ROW, index)]["on_press" if msg.value == 127 else "on_release"]:
						fn()
				else:
					if (msg.note - 8) % 16 == 0:
						index = (msg.note - 8) // 16
						for fn in self.map[(TargetRegion.COMMAND_COLUMN, index)]["on_press" if msg.velocity == 127 else "on_release"]:
							fn()
					else:
						index = (msg.note // 16) * 8 + (msg.note % 8)
						for fn in self.map[(TargetRegion.GRID, index)]["on_press" if msg.velocity == 127 else "on_release"]:
							fn()
	
	def change_led(self, target: TargetRegion, index: int, red: Brightness, green: Brightness) -> None:
		if target not in TargetRegion:
			raise AttributeError(f"{target} not in TargetRegion")
		if target == TargetRegion.COMMAND_COLUMN:
			self.output_port.send(_get_command_column_led_message(index, green, red))
		elif target == TargetRegion.COMMAND_ROW:
			self.output_port.send(_get_command_row_led_message(index, green, red))
		elif target == TargetRegion.GRID:
			self.output_port.send(_get_grid_led_message(index, green, red))
				

"""

What next?

Add methods to discover and connect a launchpad to ports (investigate Mido multiports)

Prettify CLI interface (to see messages with verbose flag and to assist debugging)

"""