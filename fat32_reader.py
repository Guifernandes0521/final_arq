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
#print('BPB_BytsPerSec',BPB_BytsPerSec)
BPB_RootEntCnt = dump.get_bytes(17,2,inteiro=True)
#print('BPB_RootEntCnt',BPB_RootEntCnt)
BPB_SecPerClus = dump.get_bytes(13,1,inteiro=True)
#print('BPB_SecPerClus',BPB_SecPerClus)

ClusterSize = BPB_BytsPerSec * BPB_SecPerClus
#the size of the cluster is 2048 bytes
#print('ClusterSize',ClusterSize)

RootDirSectors = round(((BPB_RootEntCnt * 32) + (BPB_BytsPerSec - 1)) / BPB_BytsPerSec)
#print('RootDirSectors', RootDirSectors)

BPB_FATSz16 = dump.get_bytes(22,2,inteiro=True)
#print('BPB_FATSz16',BPB_FATSz16)
BPB_TotSec16 = dump.get_bytes(19,2,inteiro=True)
#print('BPB_TotSec16',BPB_TotSec16)
BPB_ResvdSecCnt = dump.get_bytes(14,2,inteiro=True)
#print('BPB_ResvdSecCnt',BPB_ResvdSecCnt)
BPB_NumFATs = dump.get_bytes(16,1,inteiro=True)
#print('BPB_NumFATs',BPB_NumFATs)

FATSz = BPB_FATSz16
#print('FATSz',FATSz)
TotSec = BPB_TotSec16
DataSec = TotSec - (BPB_ResvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors);
#print('DataSec',DataSec)
# considering the CountOfClusters, this is FAT12
CountofClusters = DataSec // BPB_SecPerClus

#print('count of clusters', CountofClusters)
SectorsOccupiedByRoot = (BPB_RootEntCnt * 32) // BPB_BytsPerSec
#print('SectorsOccupiedByRoot',SectorsOccupiedByRoot)
FirstRootDirSecNum = BPB_ResvdSecCnt + (BPB_NumFATs * BPB_FATSz16)
#print('FirstRootDirSecNum',FirstRootDirSecNum)
FirstRootDirSecNumOffset = FirstRootDirSecNum * BPB_BytsPerSec
content_of_root_dir = dump.get_bytes(FirstRootDirSecNumOffset, 10, string=True)

# first data sector
FirstDataSector = BPB_ResvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors
FirstDataSectorOffset = FirstDataSector * BPB_BytsPerSec
print('FirstDataSectorOFFSET',hex(FirstDataSectorOffset))
ATTR_LONG_NAME = 0xf

# there are 8 entries of the root directory being used
for i in range(8):
	short_name = dump.get_bytes(FirstRootDirSecNumOffset + i*32, 11, string=True)
	dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 11, 1, inteiro=True)
	# 0xf = 15
	if dir_attr == 15 or dir_attr == 8:
		LDIR_Name1 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 1, 10, string=True)
		LDIR_Name2 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 14, 12, string=True)
		LDIR_Name3 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 28, 4, string=True)

	else:
		DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 26, 2, inteiro=True)
		print(hex(DIR_FstClusLO))
		#DIR_FstClusLO = hex(DIR_FstClusLO) & 0xffff
		print('DIR_FstClusLO',DIR_FstClusLO)
		FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
		
		offset_of_file = FirstSectorofCluster * BPB_BytsPerSec 
		
		print(hex(offset_of_file))
		print('conteudo do arquivo', dump.get_bytes(offset_of_file, 2048, string=True))
		print('#########################################################')
	
