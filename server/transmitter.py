# This file is part of Fail2Ban.
#
# Fail2Ban is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Fail2Ban is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fail2Ban; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Author: Cyril Jaquier
# 
# $Revision$

__author__ = "Cyril Jaquier"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2004 Cyril Jaquier"
__license__ = "GPL"

from threading import Lock
import logging, time

# Gets the instance of the logger.
logSys = logging.getLogger("fail2ban.comm")

class Transmitter:
	
	def __init__(self, server):
		self.__lock = Lock()
		self.__server = server
		
	def proceed(self, action):
		# Deserialize object
		try:
			self.__lock.acquire()
			logSys.debug("Action: " + `action`)
			try:
				ret = self.__actionHandler(action)
				ack = 0, ret
			except Exception, e:
				logSys.warn("Invalid command: " + `action`)
				ack = 1, e
			return ack
		finally:
			self.__lock.release()
	
	##
	# Handle an action.
	#
	# 
	
	def __actionHandler(self, action):
		if action[0] == "ping":
			return "pong"
		elif action[0] == "add":
			name = action[1]
			if name == "all":
				raise Exception("Reserved name")
			self.__server.addJail(name)
			return name
		elif action[0] == "start":
			name = action[1]
			self.__server.startJail(name)
			return None
		elif action[0] == "stop":
			if len(action) == 1:
				self.__server.quit()
			elif action[1] == "all":
				self.__server.stopAllJail()
			else:
				name = action[1]
				self.__server.stopJail(name)
			return None
		elif action[0] == "sleep":
			value = action[1]
			time.sleep(int(value))
			return None
		elif action[0] == "set":
			return self.__actionSet(action[1:])
		elif action[0] == "get":
			return self.__actionGet(action[1:])
		elif action[0] == "status":
			return self.status(action[1:])			
		raise Exception("Invalid command")
	
	def __actionSet(self, action):
		name = action[0]
		# Logging
		if name == "loglevel":
			value = int(action[1])
			self.__server.setLogLevel(value)
			return self.__server.getLogLevel()
		elif name == "logtarget":
			value = action[1]
			self.__server.setLogTarget(value)
			return self.__server.getLogTarget()
		# Jail
		elif action[1] == "idle":
			if action[2] == "on":
				self.__server.setIdleJail(name, True)
			elif action[2] == "off":
				self.__server.setIdleJail(name, False)
			return self.__server.getIdleJail(name)
		# Filter
		elif action[1] == "addignoreip":
			value = action[2]
			self.__server.addIgnoreIP(name, value)
			return self.__server.getIgnoreIP(name)
		elif action[1] == "delignoreip":
			value = action[2]
			self.__server.delIgnoreIP(name, value)
			return self.__server.getIgnoreIP(name)
		elif action[1] == "addlogpath":
			value = action[2:]
			for path in value:
				self.__server.addLogPath(name, path)
			return self.__server.getLogPath(name)
		elif action[1] == "dellogpath":
			value = action[2]
			self.__server.delLogPath(name, value)
			return self.__server.getLogPath(name)
		elif action[1] == "timeregex":
			value = action[2]
			self.__server.setTimeRegex(name, value)
			return self.__server.getTimeRegex(name)
		elif action[1] == "timepattern":
			value = action[2]
			self.__server.setTimePattern(name, value)
			return self.__server.getTimePattern(name)
		elif action[1] == "failregex":
			value = action[2]
			self.__server.setFailRegex(name, value)
			return self.__server.getFailRegex(name)
		elif action[1] == "maxtime":
			value = action[2]
			self.__server.setMaxTime(name, int(value))
			return self.__server.getMaxTime(name)
		elif action[1] == "findtime":
			value = action[2]
			self.__server.setFindTime(name, int(value))
			return self.__server.getFindTime(name)
		elif action[1] == "maxretry":
			value = action[2]
			self.__server.setMaxRetry(name, int(value))
			return self.__server.getMaxRetry(name)
		# Action
		elif action[1] == "bantime":
			value = action[2]
			self.__server.setBanTime(name, int(value))
			return self.__server.getBanTime(name)
		elif action[1] == "addaction":
			value = action[2]
			self.__server.addAction(name, value)
			return self.__server.getLastAction(name).getName()
		elif action[1] == "delaction":
			self.__server.delAction(name, value)
			return None
		elif action[1] == "setcinfo":
			act = action[2]
			key = action[3]
			value = action[4]
			self.__server.setCInfo(name, act, key, value)
			return self.__server.getCInfo(name, act, key)
		elif action[1] == "delcinfo":
			act = action[2]
			key = action[3]
			self.__server.delCInfo(name, act, key)
			return None
		elif action[1] == "actionstart":
			act = action[2]
			value = action[3]
			self.__server.setActionStart(name, act, value)
			return self.__server.getActionStart(name, act)
		elif action[1] == "actionstop":
			act = action[2]
			value = action[3]
			self.__server.setActionStop(name, act, value)
			return self.__server.getActionStop(name, act)
		elif action[1] == "actioncheck":
			act = action[2]
			value = action[3]
			self.__server.setActionCheck(name, act, value)
			return self.__server.getActionCheck(name, act)
		elif action[1] == "actionban":
			act = action[2]
			value = action[3]
			self.__server.setActionBan(name, act, value)
			return self.__server.getActionBan(name, act)
		elif action[1] == "actionunban":
			act = action[2]
			value = action[3]
			self.__server.setActionUnban(name, act, value)
			return self.__server.getActionUnban(name, act)
		raise Exception("Invalid command (no set action or not yet implemented)")
	
	def __actionGet(self, action):
		name = action[0]
		# Logging
		if name == "loglevel":
			return self.__server.getLogLevel()
		elif name == "logtarget":
			return self.__server.getLogTarget()
		# Filter
		elif action[1] == "logpath":
			return self.__server.getLogPath(name)
		elif action[1] == "ignoreip":
			return self.__server.getIgnoreIP(name)
		elif action[1] == "timeregex":
			return self.__server.getTimeRegex(name)
		elif action[1] == "timepattern":
			return self.__server.getTimePattern(name)
		elif action[1] == "failregex":
			return self.__server.getFailRegex(name)
		elif action[1] == "maxtime":
			return self.__server.getMaxTime(name)
		elif action[1] == "findtime":
			return self.__server.getFindTime(name)
		elif action[1] == "maxretry":
			return self.__server.getMaxRetry(name)
		# Action
		elif action[1] == "bantime":
			return self.__server.getBanTime(name)
		elif action[1] == "addaction":
			return self.__server.getLastAction(name).getName()
		elif action[1] == "actionstart":
			act = action[2]
			return self.__server.getActionStart(name, act)
		elif action[1] == "actionstop":
			act = action[2]
			return self.__server.getActionStop(name, act)
		elif action[1] == "actioncheck":
			act = action[2]
			return self.__server.getActionCheck(name, act)
		elif action[1] == "actionban":
			act = action[2]
			return self.__server.getActionBan(name, act)
		elif action[1] == "actionunban":
			act = action[2]
			return self.__server.getActionUnban(name, act)
		raise Exception("Invalid command (no get action or not yet implemented)")
	
	def status(self, action):
		if len(action) == 0:
			return self.__server.status()
		else:
			name = action[0]
			return self.__server.statusJail(name)
		raise Exception("Invalid command (no status)")
	