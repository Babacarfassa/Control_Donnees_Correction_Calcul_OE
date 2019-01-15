import processing, re,itertools,sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import * 
from qgis.utils import *


def Correction_Accrochage_function(shape_point,shape_ligne):

	distance_buffer=0.1 

	def function_accrochage_lines_to_point(shape_point,shape_ligne,distance_buffer):

		layershape_point_technique = shape_point
		layershape_support = shape_ligne

		#lineLayer = iface.addVectorLayer("LineString?crs=epsg:2154", "Line Layer", "memory")

		correction_daccrochage = QgsVectorLayer("LineString?crs=epsg:2154", "correction_daccrochage", "memory")
		correction_daccrochage_pr2 = correction_daccrochage.dataProvider()
		correction_daccrochage_attr2 = layershape_support.dataProvider().fields().toList()
		correction_daccrochage_pr2.addAttributes(correction_daccrochage_attr2)
		correction_daccrochage.updateFields()

		for shape_support in layershape_support.getFeatures():
			
			res_originee='KO'
			res_extremitee='KO'
			
			geom_support=shape_support.geometry()
			if geom_support != NULL:
				bboxinfra = geom_support.buffer(5, 5).boundingBox()
				request = QgsFeatureRequest()
				request.setFilterRect(bboxinfra)
				
				"""geom_support_type=geom_support.asPolyline()
				
				for pt in layershape_point_technique.getFeatures(request):
					if (QgsGeometry.fromPoint(QgsPoint(geom_support_type[0]))).equals(pt.geometry()):
						res_originee='OK'
					if (QgsGeometry.fromPoint(QgsPoint(geom_support_type[-1]))).equals(pt.geometry()):
						res_extremitee='OK'
				
				for pt in layershape_point_technique.getFeatures(request):
					geom_pt_type=pt.geometry().asPoint()
					if res_originee=='KO':
						if (QgsGeometry.fromPoint(QgsPoint(geom_support_type[0]))).within(pt.geometry().buffer(0.1,0.1)):
							geom_support_type.insert(0,geom_pt_type)
					if res_extremitee=='KO':
						if (QgsGeometry.fromPoint(QgsPoint(geom_support_type[-1]))).within(pt.geometry().buffer(0.1,0.1)):
							geom_support_type.append(geom_pt_type)
				#print shape_support[0],';',geom_support_type,';',geom_pt_type
				
				
				ft = QgsFeature()
				polyline = QgsGeometry.fromPolyline(geom_support_type)
				ft.setAttributes(shape_support.attributes())
				ft.setGeometry(polyline)
				correction_daccrochage_pr2.addFeatures([ft])

			QgsMapLayerRegistry.instance().addMapLayer(correction_daccrochage)
				
			"""    
				if geom_support.wkbType()==QGis.WKBMultiLineString:
					geom_support_type=geom_support.asMultiPolyline()
					support_origine=geom_support_type[0][0]
					support_extremite=geom_support_type[-1][-1]
					
				if geom_support.wkbType()==QGis.WKBLineString:
					geom_support_type=geom_support.asPolyline()
					support_origine=geom_support_type[0]
					support_extremite=geom_support_type[-1]
				
					
				for pt in layershape_point_technique.getFeatures(request):
					if (QgsGeometry.fromPoint(QgsPoint(support_origine))).equals(pt.geometry()):
						res_originee='OK'
					if (QgsGeometry.fromPoint(QgsPoint(support_extremite))).equals(pt.geometry()):
						res_extremitee='OK'
					
				if res_originee=='KO' or res_extremitee=='KO':
					#a= shape_support[0],';',pt[0],';',pt[0]
					for pt in layershape_point_technique.getFeatures(request):
						geom_pt_type=pt.geometry().asPoint()
						if (QgsGeometry.fromPoint(QgsPoint(support_origine))).within(pt.geometry().buffer((float(distance_buffer)),(float(distance_buffer)))):
							geom_support_type.insert(0,geom_pt_type)
						if (QgsGeometry.fromPoint(QgsPoint(support_extremite))).within(pt.geometry().buffer((float(distance_buffer)),(float(distance_buffer)))):
							geom_support_type.append(geom_pt_type)

				ft = QgsFeature()
				if geom_support.wkbType() in [QGis.WKBMultiLineString,QGis.WKBLineString]:
					polyline = QgsGeometry.fromPolyline(geom_support_type)
					ft.setAttributes(shape_support.attributes())
					ft.setGeometry(polyline)
					correction_daccrochage_pr2.addFeatures([ft])


		QgsMapLayerRegistry.instance().addMapLayer(correction_daccrochage)
			
				
	function_accrochage_lines_to_point(shape_point,shape_ligne,distance_buffer)
