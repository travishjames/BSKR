import numpy as np 

typelist= ['violinist', 'flautist', 'singer_songwriter', 
			'singer_songwriter','cellist', 
			'saxaphoner', 'saxaphoner','guitarist','rap_crew','beatboxer', 'beatboxer', 
			'trashcan_percussionist', 'guitarist','guitarist','guitarist','one_man_band']

for x in range(0,150):
	x = np.random.random_integers(1,14)
	if x>=6:
		print('musician')
	if x == 6:
		print('juggler')
	if x == 5:
		print('mime')
	if x == 4:
		print('artist')
	if x == 3:
		print('living statue')
	if x == 2:
		print('magician')
	if x == 1:
		print('psychic')

print(len(typelist))
for x in range(0,150):
	x= np.random.random_integers(0,15)
	print(typelist[x])
	# if x >= 15:
	# 	print(typel)


