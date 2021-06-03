from macros_wrapper import Launchpad, get_input_port_names, get_output_port_names, Brightness, TargetRegion
import keyboard, json, os

os.system("clear")

lp = Launchpad("Launchpad Mini", "Launchpad Mini")
for i in range(8):
	lp.change_led(TargetRegion.COMMAND_ROW, i, Brightness.OFF, Brightness.OFF)
	lp.change_led(TargetRegion.COMMAND_COLUMN, i, Brightness.OFF, Brightness.OFF)

for i in range(64):
	lp.change_led(TargetRegion.GRID, i, Brightness.OFF, Brightness.OFF)

def _process_press(index: int, key: str):
	keyboard.press(key)

def _process_release(index: int, key: str):
	keyboard.release(key)

def key_press(target: TargetRegion, index: int, char: str):
	lp.on_press(target, index, lambda: _process_press(index, char))
	lp.on_release(target, index, lambda: _process_release(index, char))

def read():
	with open("/Users/promandan/Onedrive/Code/Launchpad macros/macros.json", "r+") as file:
		keybinds = json.load(file)
		return {int(k): v for k, v  in keybinds["grid_keybinds"].items()}, {int(k): v for k, v  in keybinds["row_keybinds"].items()}, {int(k): v for k, v  in keybinds["column_keybinds"].items()}

print("Processes defined")

if __name__ == "__main__":

	grid_keybinds, row_keybinds, column_keybinds = read()

	for k, v in grid_keybinds.items():
		key_press(TargetRegion.GRID, k, v)
		lp.change_led(TargetRegion.GRID, k, Brightness.HIGH, Brightness.HIGH)

	for k, v in row_keybinds.items():
		key_press(TargetRegion.COMMAND_ROW, k, v)
		lp.change_led(TargetRegion.COMMAND_ROW, k, Brightness.OFF, Brightness.HIGH)


	for k, v in column_keybinds.items():
		key_press(TargetRegion.COMMAND_COLUMN, k, v)
		lp.change_led(TargetRegion.COMMAND_COLUMN, k, Brightness.OFF, Brightness.HIGH)

	print("Running central process")
	lp.run()
