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

BPB_BytsPerSec = dump.get_bytes(11,2,inteiro=True)
BPB_RootEntCnt = dump.get_bytes(17,2,inteiro=True)
BPB_SecPerClus = dump.get_bytes(13,1,inteiro=True)
BPB_FATSz16 = dump.get_bytes(22,2,inteiro=True)
BPB_TotSec16 = dump.get_bytes(19,2,inteiro=True)
BPB_ResvdSecCnt = dump.get_bytes(14,2,inteiro=True)
BPB_NumFATs = dump.get_bytes(16,1,inteiro=True)

# The size of a cluster is 2048 bytes
ClusterSize = BPB_BytsPerSec * BPB_SecPerClus
# The count of root dirs was wrong in the microsoft documentation, it is 32, no need to roundup!!!!!
RootDirSectors = BPB_RootEntCnt*32 // BPB_BytsPerSec
TotSec = BPB_TotSec16
FATSz = BPB_FATSz16
DataSec = TotSec - (BPB_ResvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors);
# Count of clusters determines the size of the FAT, in this case is FAT12 because there are less than 4085 clusters -> 4077
CountofClusters = DataSec // BPB_SecPerClus
FirstRootDirSecNum = BPB_ResvdSecCnt + (BPB_NumFATs * BPB_FATSz16)
FirstRootDirSecNumOffset = FirstRootDirSecNum * BPB_BytsPerSec
FirstDataSector = BPB_ResvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors
FirstDataSectorOffset = FirstDataSector * BPB_BytsPerSec

#################################################################################
# File attributes:
# ATTR_READ_ONLY 0x01
# ATTR_HIDDEN 0x02
# ATTR_SYSTEM 0x04
# ATTR_VOLUME_ID 0x08
# The or of the four above indicates that the file is a unit label
# ATTR_DIRECTORY 0x10
# ATTR_ARCHIVE 0x20
#################################################################################
# primeiro arquivo que é label do volume
short_name = dump.get_bytes(FirstRootDirSecNumOffset + 0*32, 11, string=True)
dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + 0*32 + 11, 1, inteiro=True)
long_name = ''
DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + 0*32 + 26, 2, inteiro=True)
DIR_FileSize = dump.get_bytes(FirstRootDirSecNumOffset + 0*32 + 28, 4, inteiro=True)
FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
offset_of_file = FirstSectorofCluster * BPB_BytsPerSec 
# the size of this file is zero as it should!
# the next two files have the 0x0f in the attribute, which means that it is a long name
# the name of the unit label is "KINGSTON DT InformationSystem Volume"
for i in range(1,3):
	LDIR_Name1 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 1, 10, string=True)
	LDIR_Name2 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 14, 12, string=True)
	LDIR_Name3 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 28, 4, string=True)
	long_name += LDIR_Name1 + LDIR_Name2 + LDIR_Name3

print('*' * 100)
print('file name:',short_name + long_name)
print('attribute of file:', dir_attr)
print('size of the file:', DIR_FileSize)
print('offset_of_file:', offset_of_file)

#################################################################################
# segundo arquivo
short_name = dump.get_bytes(FirstRootDirSecNumOffset + 3*32, 11, string=True)
dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + 3*32 + 11, 1, inteiro=True)
DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + 3*32 + 26, 2, inteiro=True)
DIR_FileSize = dump.get_bytes(FirstRootDirSecNumOffset + 3*32 + 28, 4, inteiro=True)
FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
offset_of_file = FirstSectorofCluster * BPB_BytsPerSec
# this file has system, hidden and directory attributes
#	"The dot entry is a directory that points to itself.
#	The dotdot entry points to the starting cluster of the parent of this directory (which is 0 if this
#	directories parent is the root directory)."
for i in range(4,6):
	dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 11, 1, inteiro=True)
	print('dir_attr',dir_attr)
	LDIR_Name1 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 1, 10, string=True)
	LDIR_Name2 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 14, 12, string=True)
	LDIR_Name3 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 28, 4, string=True)

print('*' * 100)
print('file name:',short_name + long_name)
print('attribute of file:', hex(dir_attr))
print('size of the file:', DIR_FileSize)
print('offset_of_file:', offset_of_file)
print('content of file:',dump.get_bytes(offset_of_file, 2048, string=True))

#################################################################################
# terceiro arquivo
short_name = dump.get_bytes(FirstRootDirSecNumOffset + 6*32, 11, string=True)
dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + 6*32 + 11, 1, inteiro=True)
DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + 6*32 + 26, 2, inteiro=True)
DIR_FileSize = dump.get_bytes(FirstRootDirSecNumOffset + 6*32 + 28, 4, inteiro=True)
FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
offset_of_file = FirstSectorofCluster * BPB_BytsPerSec
print('*' * 100)
print('file name:',short_name)
print('attribute of file:', hex(dir_attr))
print('size of the file:', DIR_FileSize)
print('offset_of_file:', offset_of_file)
print('content of file:',dump.get_bytes(offset_of_file, 2048, string=True))
#################################################################################
# quarto arquivo
short_name = dump.get_bytes(FirstRootDirSecNumOffset + 7*32, 11, string=True)
dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + 7*32 + 11, 1, inteiro=True)
DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + 7*32 + 26, 2, inteiro=True)
DIR_FileSize = dump.get_bytes(FirstRootDirSecNumOffset + 7*32 + 28, 4, inteiro=True)
FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
offset_of_file = FirstSectorofCluster * BPB_BytsPerSec
print('*' * 100)
print('file name:',short_name)
print('attribute of file:', hex(dir_attr))
print('size of the file:', DIR_FileSize)
print('offset_of_file:', offset_of_file)
print('content of file:',dump.get_bytes(offset_of_file, 2048, string=True))
print('*' * 100)
#################################################################################



# there are 8 entries of the root directory being used

for i in range(8):
	DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 26, 2, inteiro=True)
	short_name = dump.get_bytes(FirstRootDirSecNumOffset + i*32, 11, string=True)
	print('short_name',short_name)
	dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 11, 1, inteiro=True)
	print('dir_attr',dir_attr)
#	# 0xf = 15
#	if dir_attr == 15 or dir_attr == 8:
#		LDIR_Name1 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 1, 10, string=True)
#		LDIR_Name2 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 14, 12, string=True)
#		LDIR_Name3 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 28, 4, string=True)
#
#	else:
#		print(hex(DIR_FstClusLO))
#		print('DIR_FstClusLO',DIR_FstClusLO)
#		
#		print('conteudo do arquivo', dump.get_bytes(offset_of_file, 2048, string=True))	
#