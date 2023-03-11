import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from bisa_kitchen import app, config as CFG

if __name__ == '__main__':
	app.run(port=CFG.PORT)

