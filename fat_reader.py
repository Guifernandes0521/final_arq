class ReadFat():
    def __init__(self, lines_to_read=32, path: str = 'dump-pendrive-2024-1.txt'):
        self.dump_information = []
        with open(path) as dump:
            # pula a linha de offset e a linha vazia
            next(dump)
            next(dump)

            for i, row in enumerate(dump):
                # cria lista de bytes em formato hexadecimal e adiciona a uma lista maior
                linha = row.strip().split('  ')[1].split(' ')
                if lines_to_read != 'all' and i == lines_to_read:
                    break
                self.dump_information += linha

        # retorna os bytes em formato hexadecimal do dump como uma lista, ou como um inteiro
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

# lê o arquivo

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

# essa é a FAT12 pois a quantidade de cluster é menor que 4088! o resultado obtido foi de 4078

# fórmulas retiradas do manual da microsoft
CountofClusters = DataSec // BPB_SecPerClus
print('quantidade de clusters:', CountofClusters, '... Então é fat12')

# dentro do root haverá várias entradas que conterão informações sobre os arquivos e diretórios
# cada entrada possui 32 bytes, e os campos foram divididos de acordo com o offset na tabela da microsoft

FirstRootDirSecNum = BPB_ResvdSecCnt + (BPB_NumFATs * BPB_FATSz16)
FirstRootDirSecNumOffset = FirstRootDirSecNum * BPB_BytsPerSec
FirstDataSector = BPB_ResvdSecCnt + (BPB_NumFATs * FATSz) + RootDirSectors
FirstDataSectorOffset = FirstDataSector * BPB_BytsPerSec

#--------------------------------------------------------------------------------
# os atributos dos arquivos foram analisados seguindo o manual.
# o primeiro arquivo tem atributo 0x08, que indica que é um label de volume
# algunstem atributo 0xf, que indica que é um nome longo

# primeiro arquivo que é label do volume
short_name = dump.get_bytes(FirstRootDirSecNumOffset + 0*32, 11, string=True)
dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + 0*32 + 11, 1, inteiro=True)
DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + 0*32 + 26, 2, inteiro=True)
DIR_FileSize = dump.get_bytes(FirstRootDirSecNumOffset + 0*32 + 28, 4, inteiro=True)
FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
offset_of_file = FirstSectorofCluster * BPB_BytsPerSec 
# o tamanho deste arquivo é zero como deveria ser!
# os próximos dois arquivos têm o 0x0f no atributo, o que significa que é um nome longo
# o nome do rótulo da unidade é "KINGSTON DT InformationSystem Volume"
long_name = ''
for i in range(1,3):
    LDIR_Name1 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 1, 11, string=True)
    LDIR_Name2 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 14, 12, string=True)
    LDIR_Name3 = dump.get_bytes(FirstRootDirSecNumOffset + i*32 + 28, 4, string=True)
    long_name += LDIR_Name1 + LDIR_Name2 + LDIR_Name3

print('*' * 100)
print('nome do arquivo:',short_name + long_name)
print('atributo do arquivo:', hex(dir_attr))
print('tamanho do arquivo', DIR_FileSize)
#--------------------------------------------------------------------------------
# segundo arquivo
short_name = dump.get_bytes(FirstRootDirSecNumOffset + 3*32, 11, string=True)
dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + 3*32 + 11, 1, inteiro=True)
DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + 3*32 + 26, 2, inteiro=True)
DIR_FileSize = dump.get_bytes(FirstRootDirSecNumOffset + 3*32 + 28, 4, inteiro=True)
FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
offset_of_file = FirstSectorofCluster * BPB_BytsPerSec
# este arquivo tem atributos de ditetório, sistema e oculto
#	"A entrada de ponto é um diretório que aponta para si mesmo.
#	A entrada dotdot aponta para o cluster inicial do pai deste diretório (que é 0 se este
#	diretório pai é o diretório raiz)."

print('*' * 100)
print('nome do diretório:',short_name)
print('atributo do arquivo:', hex(dir_attr))
print('tamanho do arquivo:', DIR_FileSize)
print('offset do arquivo:', offset_of_file)
print('tamanho do arquivo', DIR_FileSize)
print('\nconteúdo do diretório:')
for i in range(0,2):
    short_name = dump.get_bytes(offset_of_file + i*32, 11, string=True)
    print('ponteiros dot e dotdot:',short_name)
# já que os atributos dos arquivos são 0x42, isso indica que há duas entradas que formam o nome longo
# essas entradas são referentes ao arquivo abaixo, logo fazemos o looping na ordem inversa
long_name = ''
for i in range(3,1,-1):
  LDIR_Name1 = dump.get_bytes(offset_of_file + i*32 + 1, 10, string=True)
  LDIR_Name2 = dump.get_bytes(offset_of_file + i*32 + 14, 12, string=True)
  LDIR_Name3 = dump.get_bytes(offset_of_file + i*32 + 28, 4, string=True)
  long_name += LDIR_Name1 + LDIR_Name2 + LDIR_Name3
  
long_name = long_name.strip('ÿ')
print('nome do arquivo no subdiretório',long_name)
long_name = ''
for i in range(6,4,-1):
  LDIR_Name1 = dump.get_bytes(offset_of_file + i*32 + 1, 10, string=True)
  LDIR_Name2 = dump.get_bytes(offset_of_file + i*32 + 14, 12, string=True)
  LDIR_Name3 = dump.get_bytes(offset_of_file + i*32 + 28, 4, string=True)
  long_name += LDIR_Name1 + LDIR_Name2 + LDIR_Name3

long_name = long_name.strip('ÿ')
print('nome do arquivo no subdiretório',long_name, end='')
#--------------------------------------------------------------------------------
# terceiro arquivo
short_name = dump.get_bytes(FirstRootDirSecNumOffset + 6*32, 11, string=True)
dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + 6*32 + 11, 1, inteiro=True)
DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + 6*32 + 26, 2, inteiro=True)
DIR_FileSize = dump.get_bytes(FirstRootDirSecNumOffset + 6*32 + 28, 4, inteiro=True)
FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
offset_of_file = FirstSectorofCluster * BPB_BytsPerSec
long_name = ''
for i in range(6,3):
  LDIR_Name1 = dump.get_bytes(FirstDataSectorOffset + i*32 + 1, 10, string=True)
  LDIR_Name2 = dump.get_bytes(FirstDataSectorOffset + i*32 + 14, 12, string=True)
  LDIR_Name3 = dump.get_bytes(FirstDataSectorOffset + i*32 + 28, 4, string=True)
  long_name += LDIR_Name1 + LDIR_Name2 + LDIR_Name3
print(long_name)
print('*' * 100)
print('nome do arquivo:',short_name + long_name)
print('atributo do arquivo:', hex(dir_attr))
print('tamanho do arquivo:', DIR_FileSize)
print('offset do arquivo:', offset_of_file)
print('tamanho do arquivo', DIR_FileSize)
print('conteúdo do arquivo:',dump.get_bytes(offset_of_file, DIR_FileSize, string=True))
#--------------------------------------------------------------------------------
# quarto arquivo
short_name = dump.get_bytes(FirstRootDirSecNumOffset + 7*32, 11, string=True)
dir_attr = dump.get_bytes(FirstRootDirSecNumOffset + 7*32 + 11, 1, inteiro=True)
DIR_FstClusLO = dump.get_bytes(FirstRootDirSecNumOffset + 7*32 + 26, 2, inteiro=True)
DIR_FileSize = dump.get_bytes(FirstRootDirSecNumOffset + 7*32 + 28, 4, inteiro=True)
FirstSectorofCluster = ((DIR_FstClusLO - 2) * BPB_SecPerClus) + FirstDataSector
offset_of_file = FirstSectorofCluster * BPB_BytsPerSec
print('*' * 100)
print('nome do arquivo:',short_name)
print('atributo do arquivo:', hex(dir_attr))
print('tamanho do arquivo:', DIR_FileSize)
print('offset do arquivo:', offset_of_file)
print('tamanho do arquivo', DIR_FileSize)
print('conteúdo do arquivo:',dump.get_bytes(offset_of_file, DIR_FileSize, string=True))
print('*' * 100)
