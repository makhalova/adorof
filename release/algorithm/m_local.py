#! /usr/bin/env python
# -*- coding: UTF-8 -*-

## Common dependencies
import numpy as __np

class m_local(object) :
	"""Класс m-локальной кластеризации. Использование:
		sloc = m_local(
			data = данные,
			crit = класс критерия качества кластеризации )
		## Полный раунд s-локальной оптимизации. Разбиение изменяется или
		##  не изменяетя автоматически. Возвращает новое значение критерия
		##  кластеризации для полученного нового разбиения. Агрумент pi
		##  передаётся по ссылке и претерпевает изменения!
		sloc.m_local(
			pi = текущее разбиение,
			s = количество перебрасываемых точек,
			I0 = текущее значение критерия )
		## Полная процедура m-локальной оптимизации. Производит m полных
		##  раундов s-локальной оптимизации. Аргумент разбиения передаётся
		##  по ссылке и изменяется в процессе работы процедуры.
		sloc.m_local(
			pi = текущее разбиение,
			m = количество перебрасываемых точек )
	"""
	def __init__( self, criterion ):
		super(m_local, self).__init__( )
		self.__criterion = criterion
## A basic step of the s-local optimisation procedure
	def __xfer( self, pi, src, dst, V0, s = 1 ) :
## There is no point in shuffling the data points withing the same class
		if src == dst :
			return V0
## Keep moving batches of s elements partition until convergence
		while len( pi[ src ] ) >= s + 2 :
## Find candidates for moving
			sNN = self.__criterion.find_candidates( pi[ src ], pi[ dst ], s = s )
## Save the original classes (copies) 
			S0, D0 = list( pi[ src ] ), list( pi[ dst ] )
## Move them from S to D: this modifies the partition pi directly!
			list.extend( pi[ dst ], ( S0[ n ] for n in sNN ) )
			pi[ src ] = list( x for n, x in enumerate( S0 ) if n not in sNN )
## Compute the criterion of the modified partition
			V1 = self.__criterion.evaluate( pi )
## If the criterion has not increased, rollback
			if V1 <= V0 :
				pi[ src ], pi[ dst ] = S0, D0
				break
## Indicate that the partition has been altered and proceed
			V0 = V1
## The partition is updated (or not) automatically
		return V0
	def __cycle( self, pi, src, V0, s = 1 ) :
## a full cycle through the classes
		dst = 0
## Pick the class to modify. If we fall off the array, this means stabilization has occurred
		while dst < len( pi ) and len( pi[ src ] ) >= s + 2 :			
			V1 = self.__xfer( pi, src, dst, V0, s = s )
## Continue if the transfers did not yield significant fittness increase
			if V1 <= V0 :
				dst += 1
				continue
## Otherwise restart
			V0 = V1 ; dst = 0
		return V0
	def __s_local( self, pi, V0, s = 1 ) :
		src = 0
		while src < len( pi ) :
## If the class is of sufficient volume ( the least volume is 2 points )
			if len( pi[ src ] ) >= s + 2 :
##  begin the s-local point transfer cycle
				V1 = self.__cycle( pi, src, V0, s = s )
				print src, V0, V1
## If the partition has been modified, restart
				if V1 > V0 :
					V0 = V1 ; src = 0
					continue
## Otherwise continue
			src += 1
## The s-local optimization step is finished when no
##  modification to the partition have been made.
		return V0
## m-local optimization: go through the number of points transferred between
##  classes in succession.
	def __call__( self, pi, m = 5 ) :
		V0 = self.__criterion.evaluate( pi )
		s = 1
		while s <= m :
			V1 = self.__s_local( pi, V0, s = s )
			if V1 <= V0 :
## No improvement -- proceed to the next round of point transfers
				s += 1
				continue
## Restart from the very beginning
			V0 = V1 ; s = 1
		return V0
