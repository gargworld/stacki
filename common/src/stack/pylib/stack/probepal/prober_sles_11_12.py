import pathlib

from common import PalletInfo, Prober

class SLES_11_12_Prober(Prober):
	'''
	This prober is intended to look for and parse a `content` file which indicates a sles11/12 pallet.

	The contents of such a file look like this, though the keys change between sles11 and 12:

	CONTENTSTYLE     11
	DATADIR          suse
	DESCRDIR         suse/setup/descr
	DISTRO           cpe:/o:suse:sles:12:sp3,SUSE Linux Enterprise Server 12 SP3
	LINGUAS          cs da de en en_GB en_US es fi fr hu it ja nb nl pl pt pt_BR ru sv zh zh_CN zh_TW
	REGISTERPRODUCT  true
	REPOID           obsproduct://build.suse.de/SUSE:SLE-12-SP3:GA/SLES/12.3/DVD/x86_64
	VENDOR           SUSE
	META SHA256 2213a47eb194729bc965dabb6ea18c44b4b29a0f77c478afc384ab0d7e8907eb  appdata-icons.tar.gz
	META SHA256 ac56f9278a8da255de5fb63408e56848f0ac6597ba10dfbed221cf0f4330c056  appdata-screenshots.tar
	META SHA256 be5fd8aeb4cdf272b4b0cc0b5e519bd3a781207f29775e4be17d64674631c7e9  appdata.xml.gz

	'''



	def __init__(self, weight=30, desc='sles 11-12'):
		super().__init__(weight, desc)

	def probe(self, pallet_root):
		if not pathlib.Path(f'{pallet_root}/content').exists():
			return None

		with open(f'{pallet_root}/content', 'r') as fi:
			lines = fi.readlines()

		name, version, release, arch, distro_family = [None] * 5

		for line in lines:
			l = line.split(None, 1)
			if len(l) > 1:
				key = l[0].strip()
				value = l[1].strip()

				# SLES11 ISO's
				if key == 'NAME':
					if value == 'SUSE_SLES':
						name = 'SLES'
						distro_family = 'sles'
					elif value == 'sle-sdk':
						name = 'SLE-SDK'
						distro_family = 'sles'
				elif key == 'VERSION':
					version = value
				elif key == 'RELEASE':
					release = value
				elif key == 'BASEARCHS':
					arch = value

				# SLES12 ISO's
				elif key == 'DISTRO':
					arch = 'x86_64'
					a = value.split(',')
					v = a[0].split(':')

					if v[3] == 'sles':
						name = 'SLES'
					elif v[3] == 'sle-sdk':
						name = 'SLE-SDK'
					elif v[3] == 'ses':
						name = 'SUSE-Enterprise-Storage'

					if name:
						distro_family = 'sles'
						version = v[4]
						if len(v) > 5:
							release = v[5]
						break

		return PalletInfo(name, version, release, arch, distro_family)
