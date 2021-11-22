# -*- coding: utf-8 -*-
"""
This example demonstrates many of the 2D plotting capabilities
in pyqtgraph. All of the plots may be panned/scaled by dragging with
the left/right mouse buttons. Right click on any plot to show a context menu.
"""

#import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
import pyqtgraph.examples

# pyqtgraph.examples.run()

import logging
# создаем логгер с именем 'log'
logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
# установим уровень логирования
stream.setLevel(logging.INFO)
logger.addHandler(stream)
logger.debug('debug message')
# вызов logger.debug() не возвращает
# никакого сообщения
logger.warning('info message')

