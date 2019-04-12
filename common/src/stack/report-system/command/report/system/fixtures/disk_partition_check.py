import pytest
import testinfra
import paramiko
import socket
import math
from collections import namedtuple
from itertools import groupby


@pytest.fixture()
def get_partitions():

	# For a given testinfra host, return a list of all partitions across disks
	def find_partitions(testinfra_host):
		try:
			return testinfra_host.check_output(f'lsblk -r -n -o name').split('\n')

		# If we can't ssh, return a blank list
		except paramiko.ssh_exception.NoValidConnectionsError:
			return []

	return find_partitions

@pytest.fixture()
def get_part_label():

	# For a given partition and testinfra host, return the partition label
	# if it is has one, otherwise return 'no label'
	def find_label(testinfra_host, partition):
		try:
			labels = testinfra_host.check_output(f'lsblk -r -n -o name,label').split('\n')

		# If we can't ssh, return 'no label'
		except paramiko.ssh_exception.NoValidConnectionsError:
			return 'no label'

		# Try all labels on the host
		for label in labels:
			try:
				curr_part = label.split(' ')[0]
				curr_label = label.split(' ')[1]
				if curr_label == '':
					curr_label = 'no label'

			except IndexError:
				return 'no label'

			# If the partition matches the argument one, return the label
			if curr_part == partition:
				return curr_label

		# Otherwise return no label
		return 'no label'
	return find_label

@pytest.fixture()
def get_part_mountpoint():

	# For a given partition and testinfra host, return the partition mountpoint
	# if it is has one, otherwise return 'no mountpoint'
	def find_mountpoint(testinfra_host, partition):
		try:
			mounts = testinfra_host.check_output(f'lsblk -r -n -o name,mountpoint').split('\n')

		# If we can't ssh, return there is no mountpoint
		except paramiko.ssh_exception.NoValidConnectionsError:
			return 'no mountpoint'

		# Try all mountpoints on the host
		for mount in mounts:
			try:
				curr_part = mount.split(' ')[0]
				curr_mount = mount.split(' ')[1]
				if curr_mount == '':
					curr_mount = 'no mountpoint'

			except IndexError:
				return 'no mountpoint'

			# If the partition matches the argument one, return the mountpoint
			if curr_part == partition:
				return curr_mount

		# Otherwise return no mountpoint
		return 'no mountpoint'
	return find_mountpoint

@pytest.fixture()
def get_part_fs():

	# For a testinfra host and partition, return the partition
	# filesystem
	def find_fs(testinfra_host, partition):
		try:
			fstypes = testinfra_host.check_output(f'lsblk -r -n -o name,fstype').split('\n')

		# Return blank if we can't ssh into the host
		except paramiko.ssh_exception.NoValidConnectionsError:
			return ''

		# Go through all found partitions on the host
		for fs in fstypes:
			try:
				curr_part = fs.split(' ')[0]
				curr_fs = fs.split(' ')[1]

			except IndexError:
				return ''

			# If the current partition matches the the input one
			# return the file system
			if curr_part == partition:
				return curr_fs

		# Otherwise return blank
		return ''
	return find_fs

@pytest.fixture()
def get_part_size():

	# For a testinfra host and partition, return the partition's
	# size if it can be found
	def find_size(testinfra_host, partition):
		try:
			sizes = testinfra_host.check_output(f'lsblk -b -r -n -o name,size').split('\n')

		# If we can't ssh into the host, return an invalid size
		except paramiko.ssh_exception.NoValidConnectionsError:
			return -1

		# Go through all the partitions
		for size in sizes:
			try:
				curr_part = size.split(' ')[0]
				curr_size = size.split(' ')[1]

			except IndexError:
				return -1

			# If the current partition matches the input one
			# return the partition size in megabytes since
			# lsblk can only do bytes precisely
			if curr_part == partition:
				return int(curr_size) / math.pow(2,20)

		# Otherwise return an invalid size
		return -1
	return find_size
