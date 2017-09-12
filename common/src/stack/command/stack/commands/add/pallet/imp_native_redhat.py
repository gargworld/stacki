# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import os
import sys
import stack
import stack.commands
from stack.exception import CommandError


class Implementation(stack.commands.Implementation):
	"""
	Copy a native Stacki roll.
	"""
	
	def run(self, args):

		(clean, prefix, info) = args

		name = info.getRollName()
		vers = info.getRollVersion()
		arch = info.getRollArch()
		release = info.getRollRelease()
		OS = info.getRollOS()

		roll_dir = os.path.join(prefix, name)
		new_roll_dir = os.path.join(roll_dir, vers, release, OS, arch)
		old_roll_dir = os.path.join(roll_dir, vers, OS, arch)

		#
		# Clean out the existing roll directory if asked
		#
		if clean and (os.path.exists(new_roll_dir) or 
				os.path.exists(old_roll_dir)):
			print('Cleaning %s %s-%s' %
				(name, vers, release), end=' ')
			print('for %s from the pallets directory' % arch)

			if os.path.exists(new_roll_dir):
				os.system('/bin/rm -rf %s' % new_roll_dir)
			elif os.path.exists(old_roll_dir):
				os.system('/bin/rm -rf %s' % old_roll_dir)

		#
		# copy the roll to the HD
		#
		sys.stdout.write('Copying %s %s-%s to pallets ...' %
			(name, vers, release))
		sys.stdout.flush()

		os.chdir(os.path.join(self.owner.mountPoint, name))

		old_format = os.path.join(vers, OS, arch)
		new_format = os.path.join(vers, release, OS, arch)
		if os.path.exists(old_format):
			os.chdir(old_format)
		elif os.path.exists(new_format):
			os.chdir(new_format)
		else:
			raise CommandError(self.owner, 'unrecognized pallet format')

		os.system('find . ! -name TRANS.TBL -print | cpio -mpud %s'
			% new_roll_dir)

		#
		# go back to the top of the pallet
		#
		os.chdir(os.path.join(self.owner.mountPoint, name))

		#
		# after copying the roll, make sure everyone (apache included)
		# can traverse the directories
		#
		os.system('find %s -type d -exec chmod a+rx {} \;' % roll_dir)

