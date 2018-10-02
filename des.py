import re
from flask import Flask, abort, request, redirect, render_template, jsonify
import copy
from werkzeug.utils import secure_filename
import os
from flask_uploads import UploadSet, IMAGES
from flask_uploads import configure_uploads, patch_request_class


IP_table=[58, 50, 42, 34, 26, 18, 10,  2,
  60, 52, 44, 36, 28, 20, 12,  4,
  62, 54, 46, 38, 30, 22, 14,  6,
  64, 56, 48, 40, 32, 24, 16,  8,
  57, 49, 41, 33, 25, 17,  9,  1,
  59, 51, 43, 35, 27, 19, 11,  3,
  61, 53, 45, 37, 29, 21, 13,  5,
  63, 55, 47, 39, 31, 23, 15,  7
]
#逆IP置换表
_IP_table=[40,  8, 48, 16, 56, 24, 64, 32,
  39,  7, 47, 15, 55, 23, 63, 31,
  38,  6, 46, 14, 54, 22, 62, 30,
  37,  5, 45, 13, 53, 21, 61, 29,
  36,  4, 44, 12, 52, 20, 60, 28,
  35,  3, 43, 11, 51, 19, 59, 27,
  34,  2, 42, 10, 50, 18, 58, 26,
  33,  1, 41,  9, 49, 17, 57, 25
]
#S盒中的S1盒
S1=[14,  4, 13,  1,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7,
0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8,
4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0,
  15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13
]
#S盒中的S2盒
S2=[15,  1,  8, 14,  6, 11,  3,  4,  9,  7,  2, 13, 12,  0,  5, 10,
3, 13,  4,  7, 15,  2,  8, 14, 12,  0,  1, 10,  6,  9, 11,  5,
0, 14,  7, 11, 10,  4, 13,  1,  5,  8, 12,  6,  9,  3,  2, 15,
  13,  8, 10,  1,  3, 15,  4,  2, 11,  6,  7, 12,  0,  5, 14,  9
]
#S盒中的S3盒
S3=[10,  0,  9, 14,  6,  3, 15,  5,  1, 13, 12,  7, 11,  4,  2,  8,
  13,  7,  0,  9,  3,  4,  6, 10,  2,  8,  5, 14, 12, 11, 15,  1,
  13,  6,  4,  9,  8, 15,  3,  0, 11,  1,  2, 12,  5, 10, 14,  7,
1, 10, 13,  0,  6,  9,  8,  7,  4, 15, 14,  3, 11,  5,  2, 12
]
#S盒中的S4盒
S4=[7, 13, 14,  3,  0,  6,  9, 10,  1,  2,  8,  5, 11, 12,  4, 15,
  13,  8, 11,  5,  6, 15,  0,  3,  4,  7,  2, 12,  1, 10, 14,  9,
  10,  6,  9,  0, 12, 11,  7, 13, 15,  1,  3, 14,  5,  2,  8,  4,
3, 15,  0,  6, 10,  1, 13,  8,  9,  4,  5, 11, 12,  7,  2, 14
]
#S盒中的S5盒
S5=[2, 12,  4,  1,  7, 10, 11,  6,  8,  5,  3, 15, 13,  0, 14,  9,
  14, 11,  2, 12,  4,  7, 13,  1,  5,  0, 15, 10,  3,  9,  8,  6,
4,  2,  1, 11, 10, 13,  7,  8, 15,  9, 12,  5,  6,  3,  0, 14,
  11,  8, 12,  7,  1, 14,  2, 13,  6, 15,  0,  9, 10,  4,  5,  3
]
#S盒中的S6盒
S6=[12,  1, 10, 15,  9,  2,  6,  8,  0, 13,  3,  4, 14,  7,  5, 11,
  10, 15,  4,  2,  7, 12,  9,  5,  6,  1, 13, 14,  0, 11,  3,  8,
9, 14, 15,  5,  2,  8, 12,  3,  7,  0,  4, 10,  1, 13, 11,  6,
4,  3,  2, 12,  9,  5, 15, 10, 11, 14,  1,  7,  6,  0,  8, 13
]
#S盒中的S7盒
S7=[4, 11,  2, 14, 15,  0,  8, 13,  3, 12,  9,  7,  5, 10,  6,  1,
  13,  0, 11,  7,  4,  9,  1, 10, 14,  3,  5, 12,  2, 15,  8,  6,
1,  4, 11, 13, 12,  3,  7, 14, 10, 15,  6,  8,  0,  5,  9,  2,
6, 11, 13,  8,  1,  4, 10,  7,  9,  5,  0, 15, 14,  2,  3, 12
]
#S盒中的S8盒
S8=[13,  2,  8,  4,  6, 15, 11,  1, 10,  9,  3, 14,  5,  0, 12,  7,
1, 15, 13,  8, 10,  3,  7,  4, 12,  5,  6, 11,  0, 14,  9,  2,
7, 11,  4,  1,  9, 12, 14,  2,  0,  6, 10, 13, 15,  3,  5,  8,
2,  1, 14,  7,  4, 10,  8, 13, 15, 12,  9,  0,  3,  5,  6, 11
]
# S盒
S=[S1,S2,S3,S4,S5,S6,S7,S8]
#P盒
P_table=[16,  7, 20, 21,
  29, 12, 28, 17,
1, 15, 23, 26,
5, 18, 31, 10,
2,  8, 24, 14,
  32, 27,  3,  9,
  19, 13, 30,  6,
  22, 11,  4, 25
]
#压缩置换表1，不考虑每字节的第8位，将64位密钥减至56位。然后进行一次密钥置换。
swap_table1=[ 57, 49, 41, 33, 25, 17,  9,
1, 58, 50, 42, 34, 26, 18,
  10,  2, 59, 51, 43, 35, 27,
  19, 11,  3, 60, 52, 44, 36,
  63, 55, 47, 39, 31, 23, 15,
7, 62, 54, 46, 38, 30, 22,
  14,  6, 61, 53, 45, 37, 29,
  21, 13,  5, 28, 20, 12,  4
]


#压缩置换表2，用于将循环左移和右移后的56bit密钥压缩为48bit
swap_table2=[14, 17, 11, 24,  1,  5,
3, 28, 15,  6, 21, 10,
  23, 19, 12,  4, 26,  8,
  16,  7, 27, 20, 13,  2,
  41, 52, 31, 37, 47, 55,
  30, 40, 51, 45, 33, 48,
  44, 49, 39, 56, 34, 53,
  46, 42, 50, 36, 29, 32
]


#用于对数据进行扩展置换，将32bit数据扩展为48bit
extend_table=[32,  1,  2,  3,  4,  5,
4,  5,  6,  7,  8,  9,
8,  9, 10, 11, 12, 13,
  12, 13, 14, 15, 16, 17,
  16, 17, 18, 19, 20, 21,
  20, 21, 22, 23, 24, 25,
  24, 25, 26, 27, 28, 29,
  28, 29, 30, 31, 32,1
]

move_table=[1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]

def str2bin(text):
	i_by = bytes(text, encoding = "utf-8")
	_bin = ''
	for i_bin in i_by:
		i_b = bin(i_bin)
		i_b = i_b.replace('0b','')
		i_b = '0' * (8-len(i_b)) + i_b
		_bin += i_b
	space_num= int((64-len(_bin))/8)
	_bin += '00000000'* space_num	
	return _bin
	# str转为utf8编码的二进制
	# 由于des加密是64位一加密，中文字节24位，字符18位，为了方便将一个编码统一补全位64位
	# str_hex = text.encode('utf8')
	# return bin(int(str_hex.hex(),16))[2:]  #hex to bin

def _str2bin(texts):
	_bin = ''
	for t in texts:
		_bin += str2bin(t)
	# space_num= int((len(_bin)%64)/8)
	# _bin += '00100000'* space_num
	return _bin


def bin2str(text):
	t = '0b'+str(text)
	t2 = hex(int(t,2))
	t3 = t2.replace('0x','')
	t4 = bytes().fromhex(t3)
	return t4.decode('utf-8')

def swap(text,table):
	text = [t for t in text]
	_text = []
	for i in table:
		_text.append(text[i-1])
	return _text

def move(text,direction,steps):
	for step in range(0,steps):
		if direction == 'right':
			l = []
			for t in range(0,len(text)-1):
				l.append(text[t])
			r = text[len(text)-1:]
			text = ''
			for t in l:
				text += t
			for t in r:
				text = t + text
		elif direction == 'left':
			l = []
			for t in range(0,len(text)-1):
				l.append(text[len(text)-t-1])
			r = text[0]
			text = ''	
			for t in r:
				text += t
			for t in l:
				text = t + text
		else:
			raise RuntimeError('parameter mistake')
	return text


def rm_parity(text):
	text = [t for t in text]
	if len(text) != 64:
		raise RuntimeError('parity not found')
	for i in [7,14,21,28,35,42,49,56]:
		del text[i]
	return ''.join(text)

def exclusive_or(text1,text2):
	text = ''
	if len(text1) != len(text2):
		raise RuntimeError('exclusive_or error')
	else:
		for i in range(0,len(text1)):
			if text1[i] == text2[i]:
				text += '0'
			else:
				text += '1'
		return text

def my_bin(num):
	la = []
	if num < 0:
		return '-' + my_bin(abs(num))
	while True:
		num, remainder = divmod(num, 2)
		la.append(str(remainder))
		if num == 0:
			return ''.join(la[::-1])

def processkey(swaped_ciphertext):
	leftKey = ''.join(swaped_ciphertext[:28])
	rightKey = ''.join(swaped_ciphertext[28:])
	resultKey = []
	for num in move_table:
		leftKey = move(leftKey,'left',num)
		rightKey = move(rightKey,'left',num)
		tempKey = leftKey + rightKey
		result = swap(tempKey,swap_table2)
		resultKey.append(result)
	return resultKey

def des(plaintext,ciphertext):
	# if encyrpt:
	# 	plaintext = _str2bin(plaintext)
	ciphertext = _str2bin(ciphertext)
	# plaintext = '0000000100100011010001010110011110001001101010111100110111101111'
	swaped_plaintext = swap(plaintext,IP_table)
	l0 = swaped_plaintext[:32]

	r0 = swaped_plaintext[32:]
	l_list = []
	r_list = []
	l_list.append(''.join(l0))
	r_list.append(''.join(r0))

	swaped_ciphertext = swap(ciphertext,swap_table1)

	k_list = processkey(swaped_ciphertext)
	# k_list = [] # 48位
	for step in move_table:
		idx = move_table.index(step)
		l = r_list[idx-1]
		# r = l_list[idx-1]
		e = swap(r_list[idx-1],extend_table) # 48
		# e 
		eo = exclusive_or(e,k_list[idx])
		# exclusive_or
		s_fragment = re.findall(r'.{6}', eo)
		s_result = ''
		for s in s_fragment:
			index = s_fragment.index(s)
			s1 = int(s[0] + s[5],2)
			s2 = int(s[1:5],2)
			b = my_bin(S[index][s1*16+s2])	
			s_result += '0'*(4-len(b)) + b
		# s
		p_result = ''.join(swap(s_result,P_table))
		p_result = exclusive_or(l_list[idx-1],p_result)
		# p
		r = p_result
		l_list.append(l)
		r_list.append(r)
	r16l16 = r_list[16] + l_list[16]
	ciphertext = ''.join(swap(r16l16,_IP_table)) 
	return ciphertext
# encrypted_ciphertext = hex(int(ciphertext))

def _des(text,key,action):
	result = ''
	if action == 1:
		for t in re.findall(r'.{64}',_str2bin(text)):
			t = des(t,key)
			result += t
		return result
	else:
		for t in re.findall(r'.{64}',text):
			t = des(t,key)
			result += bin2str(t)
			new_result = ''
			for r in result:
				if r != '\x00':         # 因为我用空字符补全每个字符，所以解密时候实际上是有空字符存在，只是仅在内存中看到
					new_result += r
			result = new_result
		return result

 

app = Flask('des')
 
@app.route('/upload', methods=['POST', 'GET'])
def upload():
	if request.method == 'POST':
		act = request.form.get('encrypt')
		key = request.form.get('key')
		f = request.files['file']
		fname = secure_filename(f.filename)
		ext = fname.rsplit('.',1)[1]  # 获取文件后缀
		new_filename = '11'+'.'+ext  # 修改了上传的文件名
		abspath = os.path.join('static/upload',new_filename)
		f.save(abspath)  #保存文件到upload目录
		f = open(abspath)
		text = ''
		for line in f.readlines():
			text += line
		if act == '加密':
			t = _des(text,key,1)
			result = t
		else:
			act = '解密'
			result = _des(text,key,0)
		return render_template('upload.html',action=act+'结果',result=result)
	return render_template('upload.html')


if __name__ == '__main__':
	app.run(debug=True,port=5000)

# 现在计算机中，在内存中采用unicode编码方式。
# 这是因为t是采用utf-8来编码，而utf-8与unicode编码中的字符部分的编码方式是一样的，
# 在显示t的时候，在内存中采用unicode解码，而两种编码方式的字符部分一样，因此显示并没有什么区别。
# utf-8(汉字3字节)与unicode(汉字2字节)汉字部分的编码是不一样的，unicode无法进行解码，因此只能用0，1串来显示。
