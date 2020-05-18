#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *
import sys

cpu = CPU()

cpu.load(sys.argv)
cpu.run()
