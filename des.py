
def str2bin(text):
	if text.isdigit() or text.isalpha():
		return '0'*(8-len(bin(ord(text))[2:]))+bin(ord(text))[2:]
	else:
		str_hex = text.encode('utf8')
		return bin(int(str_hex.hex(),16))[2:]  #hex to bin

def _str2bin(texts):
	_bin = ''
	for t in texts:
		_bin += str2bin(t)
	return _bin

print(_str2bin('b'))

# 现在计算机中，在内存中采用unicode编码方式。
# 这是因为t是采用utf-8来编码，而utf-8与unicode编码中的字符部分的编码方式是一样的，
# 在显示t的时候，在内存中采用unicode解码，而两种编码方式的字符部分一样，因此显示并没有什么区别。
# utf-8与unicode汉字部分的编码是不一样的，unicode无法进行解码，因此只能用0，1串来显示。