class ReadFat():
	def __init__(self, lines_to_read=32, path: str = 'dump-pendrive-2024-1.txt'):
		self.dump_information = []
		with open(path) as dump:
			#skips offset line and empty line
			next(dump)
			next(dump)

			for i, row in enumerate(dump):
				# creates list of bytes in hexadecimal format and adds to bigger list
				linha = row.strip().split('  ')[1].split(' ')
				if lines_to_read != 'all' and i == lines_to_read:
					break
				self.dump_information += linha

		# returns the bytes in hexadecimal format from the dump as a list, or as an integer
	def get_bytes(self, offset, length=1, inteiro = False, string = False):
		if inteiro:
			hex_bytes =  self.dump_information[offset:offset+length]
			hex_bytes = ''.join(hex_bytes[::-1])
			hex_bytes = int(hex_bytes, 16)

		elif string:
			string = ''
			for character in self.dump_information[offset:offset+length]:
				string += chr(int(character, 16))
			return string

		else:
			hex_bytes =  self.dump_information[offset:offset+length]

		return hex_bytes

dump = ReadFat('all')

# getting boot sector
BPB_BytsPerSec = dump.get_bytes(11,2,inteiro=True)
print('BPB_BytsPerSec',BPB_BytsPerSec)
BPB_RootEntCnt = dump.get_bytes(17,2,inteiro=True)
print('BPB_RootEntCnt',BPB_RootEntCnt)
BPB_SecPerClus = dump.get_bytes(13,1,inteiro=True)
print('BPB_SecPerClus',BPB_SecPerClus)
ClusterSize = BPB_BytsPerSec * BPB_SecPerClus
print('ClusterSize',ClusterSize)
# getting root_dir_sector
RootDirSectors = round(((BPB_RootEntCnt * 32) + (BPB_BytsPerSec - 1)) / BPB_BytsPerSec)
print('RootDirSectors', RootDirSectors)

# explanations so far
BPB_FATSz16 = dump.get_bytes(22,2,inteiro=True)
print('BPB_FATSz16',BPB_FATSz16)
BPB_TotSec16 = dump.get_bytes(19,2,inteiro=True)
print('BPB_TotSec16',BPB_TotSec16)
BPB_ResvdSecCnt = dump.get_bytes(14,2,inteiro=True)
print('BPB_ResvdSecCnt',BPB_ResvdSecCnt)
BPB_NumFATs = dump.get_bytes(16,1,inteiro=True)
print('BPB_NumFATs',BPB_NumFATs)

# explanations so far
FATSz = BPB_FATSz16
print('FATSz',FATSz)
TotSec = BPB_TotSec16
DataSec = TotSec - (BPB_ResvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors);
print('DataSec',DataSec)
CountofClusters = DataSec // BPB_SecPerClus
print('count of clusters', CountofClusters)
# windows will consider this unit as FAT12, but it was formatted as FAT16
SectorsOccupiedByRoot = (BPB_RootEntCnt * 32) // BPB_BytsPerSec
print('SectorsOccupiedByRoot',SectorsOccupiedByRoot)
FirstRootDirSecNum = BPB_ResvdSecCnt + (BPB_NumFATs * BPB_FATSz16)
print('FirstRootDirSecNum',FirstRootDirSecNum)
FirstRootDirSecNumOffset = FirstRootDirSecNum * BPB_BytsPerSec
content_of_root_dir = dump.get_bytes(FirstRootDirSecNumOffset, 10, string=True)
print('content_of_root_dir',content_of_root_dir)

for i in range(10):
	print('content_of_root_dir',dump.get_bytes(FirstRootDirSecNumOffset + i*32, 32, string=True))
	print('content_of_root_dir_hex',' '.join(dump.get_bytes(FirstRootDirSecNumOffset + i*32, 32)))