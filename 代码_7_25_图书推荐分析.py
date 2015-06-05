# -*- coding: utf-8 -*-
fej_dict = {}
for i in result_list:
	if i[3] not in fej_dict:
		k_value = 0
		for j in result_list:
			if j[3] == i[3]:
				k_value += 1
		fej_dict[i[3]] = k_value
for i in fej_dict:
	print(i, fej_dict[i])
