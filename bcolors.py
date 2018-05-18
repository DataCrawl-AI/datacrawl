
class bcolors:          # for colord output, looks pretty.
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	def _print(self, *text):
		if len(text) >1:
			iter_text = iter(text)
			next(iter_text)

			for _str in iter_text:
				print(" ",_str)
		else:
			print("\n")

	def succes(self, *text):
		print(bcolors.OKGREEN + text[0] + self.ENDC, end=''),
		self._print(*text)
	
	def error(self, *text):
		print(self.FAIL + text[0] + self.ENDC, end=''),
		self._print(*text)


	def info(self, *text):
		print(self.INFO + text[0] + self.ENDC, end=''),
		self._print(*text)


	def warning(self, *text):
		print(self.WARNING + text[0] + self.ENDC, end=''),
		self._print(*text)

	def bold(self, *text):
		print(self.BOLD + text[0] + self.ENDC, end=''),
		self._print(*text)



