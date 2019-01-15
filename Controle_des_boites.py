import processing, re,itertools,sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import * 
from qgis.utils import *

def Controle_des_boites_function(shape_boite,shape_point_technique,shape_cables):
	
	def boite_sans_PT(shape_boite,shape_point_technique,shape_cables):
		

		layershape_boite=shape_boite
		layershape_point_technique = shape_point_technique
		layershape_cables= shape_cables


		boite_sans_PT = QgsVectorLayer("Point?crs=epsg:2154", "boite_sans_PT", "memory")
		boite_sans_PT_pr = boite_sans_PT.dataProvider()
		boite_sans_PT_attr = layershape_boite.dataProvider().fields().toList()
		boite_sans_PT_pr.addAttributes(boite_sans_PT_attr)
		boite_sans_PT.updateFields()

		boite_sans_cables= QgsVectorLayer("Point?crs=epsg:2154", "boite_sans_cables", "memory")
		boite_sans_cables_pr = boite_sans_cables.dataProvider()
		boite_sans_cables_attr = layershape_cables.dataProvider().fields().toList()
		boite_sans_cables_pr.addAttributes(boite_sans_PT_attr)
		boite_sans_cables.updateFields()
			
		for shape_boite in layershape_boite.getFeatures():
			bboxinfra = shape_boite.geometry().buffer(5, 5).boundingBox()
			request = QgsFeatureRequest()
			request.setFilterRect(bboxinfra)
			res='KO'
			res_boite_seule='KO'
			elem= QgsFeature()
			for shape_point_technique in layershape_point_technique.getFeatures(request):
				if shape_boite.geometry().within((shape_point_technique.geometry().buffer(0.1, 0.1))):
					res='OK'
			if res == 'KO':
				boite_sans_PT_pr.addFeatures([shape_boite])  
				
			for shape_cables in layershape_cables.getFeatures(request):
				geom_cable=shape_cables.geometry()
				if (shape_boite.geometry().buffer(0.1,0.1)).intersects(geom_cable):
					res_boite_seule='OK'
			if res_boite_seule=='KO':
				boite_sans_cables_pr.addFeatures([shape_boite])    

		QgsMapLayerRegistry.instance().addMapLayer(boite_sans_PT)
		QgsMapLayerRegistry.instance().addMapLayer(boite_sans_cables)
		
		'''QgsVectorFileWriter.writeAsVectorFormat(boite_sans_PT,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\SRO5_Normandie\boite_sans_PT.shp", "LATIN1", None, "ESRI Shapefile")
		QgsVectorFileWriter.writeAsVectorFormat(boite_sans_cables,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\SRO5_Normandie\boite_sans_cables.shp", "LATIN1", None, "ESRI Shapefile")'''
		
				#Execution de la fonction de verification des boites sans PT et des boites sans Cables
	boite_sans_PT(shape_boite,shape_point_technique,shape_cables)
