import os,sys, zipfile,shutil,glob,datetime, processing,itertools,psycopg2, sys, PyQt4.QtSql, csv,os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from itertools import *
from PyQt4.QtSql import * 
from qgis.utils import *


def cable_sans_support_function(layershape_cables,layershape_infra):
	def erreur_superposition_infra_optique():
		
		#layershape_cables = processing.getObject(shape_cables)
		#layershape_infra = processing.getObject(shape_infra)

		buffLyr = QgsVectorLayer('Linestring?crs=EPSG:2154', 'Erreur_supperposition_Cable_Cheminement' , 'memory')
		pr = buffLyr.dataProvider()
		pr_attribut = layershape_cables.dataProvider().fields().toList()
		pr.addAttributes(pr_attribut)
		buffLyr.updateFields()
					
		for par_etude in layershape_cables.getFeatures():
			bboxshape_infra = par_etude.geometry().buffer(5, 5).boundingBox()
			request = QgsFeatureRequest()
			request.setFilterRect(bboxshape_infra)
			res = 'KO'
			bf_inGeom = par_etude.geometry().buffer(0.0000001,0.0000001)#buffer(0.0000001,0.0000001)
			for par_etude_chem in layershape_infra.getFeatures(request):
				if par_etude_chem.geometry().within(bf_inGeom) :
					res = 'OK'
			if res == 'KO':
				pr.addFeatures([par_etude])
		QgsMapLayerRegistry.instance().addMapLayers([buffLyr])
		#QgsVectorFileWriter.writeAsVectorFormat(buffLyr,"C:\Certification_Gracethd\Resultats_Certificateur_Gracethd\SICTIAM\Erreur_supperposition_Cable_Cheminement.shp", "LATIN1", None, "ESRI Shapefile")
				#print  'NO',par_etude_chem.attributes()[0],';',par_etude.attributes()[0]

	erreur_superposition_infra_optique()