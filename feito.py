class ReadFat():
	def __init__(self, lines_to_read=32, path: str = '/content/dump-pendrive-2024-1.txt'):
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

# os offsets foram pegos na referência da microsoft

BPB_BytsPerSec = dump.get_bytes(11,2,inteiro=True)
BPB_RootEntCnt = dump.get_bytes(17,2,inteiro=True)
BPB_SecPerClus = dump.get_bytes(13,1,inteiro=True)
BPB_FATSz16 = dump.get_bytes(22,2,inteiro=True)
BPB_TotSec16 = dump.get_bytes(19,2,inteiro=True)
BPB_ResvdSecCnt = dump.get_bytes(14,2,inteiro=True)
BPB_NumFATs = dump.get_bytes(16,1,inteiro=True)

# o tamanho do cluster é de 2048 bytes
ClusterSize = BPB_BytsPerSec * BPB_SecPerClus
print('tamanho dos clusters:', ClusterSize)

# o manual da microsoft estava enganado! não é necessário usar roundup
RootDirSectors = BPB_RootEntCnt*32 // BPB_BytsPerSec
TotSec = BPB_TotSec16
FATSz = BPB_FATSz16
DataSec = TotSec - (BPB_ResvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors);

# essa é a FAT12 pois a quantidade de cluster é menor que 4088! o resultado obtido
# foi de 4077
CountofClusters = DataSec // BPB_SecPerClus
print('quantidade de clusters:', CountofClusters, '... Então é fat12')
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
	LDIR_Name1 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 1, 11, string=True)
	LDIR_Name2 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 14, 12, string=True)
	LDIR_Name3 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 28, 4, string=True)
	long_name += LDIR_Name1 + LDIR_Name2 + LDIR_Name3

print('*' * 100)
print('file name:',short_name + long_name)
print('attribute of file:', hex(dir_attr))
print('tamanho do arquivo', DIR_FileSize)
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
long_name = ''
for i in range(4,6):
	LDIR_Name1 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 1, 10, string=True)
	LDIR_Name2 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 14, 12, string=True)
	LDIR_Name3 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 28, 4, string=True)
 
print('*' * 100)
print('name of directory:',short_name + long_name)
print('attribute of file:', hex(dir_attr))
print('size of the file:', DIR_FileSize)
print('offset_of_file:', offset_of_file)
print('tamanho do arquivo', DIR_FileSize)

for i in range(0,2):
    short_name = dump.get_bytes(offset_of_file + i*32, 11, string=True)
    print('   dot and dotdot pointers:',short_name)

# já que os atributos das files são 0x42, isso indica que há duas entradas que formam o nome longo
# essas entradas são referentes a file abaixo, logo fazemos o looping na ordem inversa

long_name = ''
for i in range(3,1,-1):
  LDIR_Name1 = dump.get_bytes(offset_of_file + i*32 + 1, 10, string=True)
  LDIR_Name2 = dump.get_bytes(offset_of_file + i*32 + 14, 12, string=True)
  LDIR_Name3 = dump.get_bytes(offset_of_file + i*32 + 28, 4, string=True)
  long_name += LDIR_Name1 + LDIR_Name2 + LDIR_Name3
print('   name of file in subdirectory',long_name)
long_name = ''
for i in range(6,4,-1):
  LDIR_Name1 = dump.get_bytes(offset_of_file + i*32 + 1, 10, string=True)
  LDIR_Name2 = dump.get_bytes(offset_of_file + i*32 + 14, 12, string=True)
  LDIR_Name3 = dump.get_bytes(offset_of_file + i*32 + 28, 4, string=True)
  long_name += LDIR_Name1 + LDIR_Name2 + LDIR_Name3
print('   name of file in subdirectory',long_name)
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
print('tamanho do arquivo', DIR_FileSize)
print('content of file:',dump.get_bytes(offset_of_file, DIR_FileSize, string=True))
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
print('tamanho do arquivo', DIR_FileSize)
print('content of file:',dump.get_bytes(offset_of_file, DIR_FileSize, string=True))
print('*' * 100)
#################################################################################
