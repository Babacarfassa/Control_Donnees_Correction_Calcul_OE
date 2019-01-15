import processing, re,itertools,sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import * 
from qgis.utils import *

def Controle_des_cables_function(shape_boite,shape_cables,Fichier_CONF_PYTHON):
	#Creation dune liste de mon fichier de configuration
	list_file_con=[]
	layer_ref_conf = QgsVectorLayer(Fichier_CONF_PYTHON, 'Fichier_CONF_PYTHON', 'ogr')
	for field_ref in layer_ref_conf.getFeatures():
		list_file_con.append([field_ref[0],field_ref[1],field_ref[2],field_ref[3]])

	#Declaration des noms des colonnes
	shape_CB_name_CB_NOM='CB_NOM'
	distance_buffer_tampon='GLOB_DIST_TAMPON'
	#Function pour la recuperation de mon code_parametre en fonction de mon fichier de parametrage
	def get_field_name(name_attribut,shape_name):
		field_name=''
		#prov = processing.getObject(shape_name).dataProvider()
		field_names_shape = [field.name() for field in shape_name.pendingFields()]
		for field_ref in list_file_con:
			for field_shape in field_names_shape:
				#if field_shape == field_ref[2]: #feat[1] == nom dattribut du shape dans le fichier de conf
				if field_ref[1] == name_attribut: #feat[4] == code du nom dattribut du shape dans le fichier de conf
						field_name=field_ref[2]
		return field_name



	nom_dela_colonne_identifiant_desCables=get_field_name(shape_CB_name_CB_NOM,shape_cables)#NOM
	distance_buffer=get_field_name(distance_buffer_tampon,shape_cables)#NOM

	layerPBO = shape_boite
	layercables =  shape_cables
	layercables2 =  shape_cables


	#Creation des shapefles des erreurs
	cables_sans_boite_ou_probleme_daccrochage = QgsVectorLayer("LineString?crs=epsg:2154", "cables_sans_boite_ou_probleme_daccrochage", "memory")
	cables_sans_boite_ou_probleme_daccrochage_pr2 = cables_sans_boite_ou_probleme_daccrochage.dataProvider()
	cables_sans_boite_ou_probleme_daccrochage_attr2 = layercables.dataProvider().fields().toList()
	cables_sans_boite_ou_probleme_daccrochage_pr2.addAttributes(cables_sans_boite_ou_probleme_daccrochage_attr2)
	cables_sans_boite_ou_probleme_daccrochage.updateFields()

	cables_ayant_meme_extremite = QgsVectorLayer("LineString?crs=epsg:2154", "cables_ayant_meme_extremite", "memory")
	cables_ayant_meme_extremite_pr2 = cables_ayant_meme_extremite.dataProvider()
	cables_ayant_meme_extremite_attr2 = layercables.dataProvider().fields().toList()
	cables_ayant_meme_extremite_pr2.addAttributes(cables_ayant_meme_extremite_attr2)
	cables_ayant_meme_extremite.updateFields()

	cables_ayant_meme_geometrie = QgsVectorLayer("LineString?crs=epsg:2154", "cables_ayant_meme_geometrie", "memory")
	cables_ayant_meme_geometrie_pr2 = cables_ayant_meme_geometrie.dataProvider()
	cables_ayant_meme_geometrie_attr2 = layercables.dataProvider().fields().toList()
	cables_ayant_meme_geometrie_pr2.addAttributes(cables_ayant_meme_geometrie_attr2)
	cables_ayant_meme_geometrie.updateFields()

	cables_ayant_Invalide_geometrie = QgsVectorLayer("LineString?crs=epsg:2154", "cables_ayant_Invalide_geometrie", "memory")
	cables_ayant_Invalide_geometrie_pr2 = cables_ayant_Invalide_geometrie.dataProvider()
	cables_ayant_Invalide_geometrie_attr2 = layercables.dataProvider().fields().toList()
	cables_ayant_Invalide_geometrie_pr2.addAttributes(cables_ayant_Invalide_geometrie_attr2)
	cables_ayant_Invalide_geometrie.updateFields()

	cables_de_type_multilignes = QgsVectorLayer("LineString?crs=epsg:2154", "cables_de_type_multilignes", "memory")
	cables_de_type_multilignes_pr2 = cables_de_type_multilignes.dataProvider()
	cables_de_type_multilignes_attr2 = layercables.dataProvider().fields().toList()
	cables_de_type_multilignes_pr2.addAttributes(cables_de_type_multilignes_attr2)
	cables_de_type_multilignes.updateFields()

	list_extremite=[]
	for shape_cables in layercables.getFeatures():
		res='OK'
		if shape_cables.geometry() ==NULL:
			cables_ayant_Invalide_geometrie_pr2.addFeatures([shape_cables]) 
		
		if shape_cables.geometry() !=NULL:
			geom_cable=shape_cables.geometry()
			bboxshape_cables = geom_cable.buffer(5,5).boundingBox()
			request = QgsFeatureRequest()
			request.setFilterRect(bboxshape_cables)
			
			
			for shape_cables2 in layercables.getFeatures(request):
				geom_cable2=shape_cables2.geometry()
				if geom_cable.within((geom_cable2.buffer((float(distance_buffer)),(float(distance_buffer))))) and shape_cables[nom_dela_colonne_identifiant_desCables] !=shape_cables2[nom_dela_colonne_identifiant_desCables]:
					res='KO'
			if res=='KO':
				cables_ayant_meme_geometrie_pr2.addFeatures([shape_cables]) 
				#print shape_cables[nom_dela_colonne_identifiant_desCables]#,';',shape_cables2[nom_dela_colonne_identifiant_desCables]
					#cables_ayant_meme_geometrie_pr2.addFeatures([shape_cables]) 
					
			
			cable_sans_origine='KO'
			cable_sans_extremite='KO'

			if geom_cable.wkbType()==QGis.WKBMultiLineString:
				cables_de_type_multilignes_pr2.addFeatures([shape_cables]) 
				geom_cable_type=geom_cable.asMultiPolyline()
				cable_origine=geom_cable_type[0][0]
				cable_extremite=geom_cable_type[-1][-1]
				
			if geom_cable.wkbType()==QGis.WKBLineString:
				geom_cable_type=geom_cable.asPolyline()
				cable_origine=geom_cable_type[0]
				cable_extremite=geom_cable_type[-1]
			
			list_extremite.append([shape_cables[nom_dela_colonne_identifiant_desCables],(QgsGeometry.fromPoint(QgsPoint(cable_extremite))).exportToWkt()])

			if geom_cable.wkbType() in [QGis.WKBMultiLineString,QGis.WKBLineString]:     
				
				for geom_noeud in layerPBO.getFeatures(request):
					
					if (QgsGeometry.fromPoint(QgsPoint(cable_origine))).equals(geom_noeud.geometry()):#within (geom_noeud.geometry().buffer((float(distance_buffer)),(float(distance_buffer)))):
						cable_sans_origine='OK'
						
					if  (QgsGeometry.fromPoint(QgsPoint(cable_extremite))).equals(geom_noeud.geometry()):#.within (geom_noeud.geometry().buffer((float(distance_buffer)),(float(distance_buffer)))):
						cable_sans_extremite='OK'
				
						
			if cable_sans_origine=='KO' or cable_sans_extremite=='KO':
				cables_sans_boite_ou_probleme_daccrochage_pr2.addFeatures([shape_cables]) 

	#Function qui prend en parametre une liste et regarde les doublons
	def get_doublon(count_doublon_list):
		
		counts = {}
		result_double_list=[]
		for i in count_doublon_list:
		  counts[i[1]] = counts.get(i[1], 0) + 1
		  #print counts.get(i, 0),';',counts.get(i),';',counts[i]
		for key,value in counts.items():
			if value > 1:
				for i in count_doublon_list:
					if i[1]==key:
						result_double_list.append([i[0],key])
		return result_double_list

	for i in get_doublon(list_extremite):
		for shape_cables in layercables.getFeatures():
			if shape_cables[nom_dela_colonne_identifiant_desCables] == i[0]:
				cables_ayant_meme_extremite_pr2.addFeatures([shape_cables]) 

	#Ajout des shapes derreur dans QGIS
	QgsMapLayerRegistry.instance().addMapLayer(cables_ayant_meme_extremite)
	QgsMapLayerRegistry.instance().addMapLayer(cables_sans_boite_ou_probleme_daccrochage)
	#QgsMapLayerRegistry.instance().addMapLayer(cables_ayant_meme_geometrie)
	QgsMapLayerRegistry.instance().addMapLayer(cables_ayant_Invalide_geometrie)
	QgsMapLayerRegistry.instance().addMapLayer(cables_de_type_multilignes)


	'''
	QgsVectorFileWriter.writeAsVectorFormat(cables_ayant_meme_extremite,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\SRO5_Normandie\cables_ayant_meme_extremite.shp", "LATIN1", None, "ESRI Shapefile")
	QgsVectorFileWriter.writeAsVectorFormat(cables_sans_boite_ou_probleme_daccrochage,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\SRO5_Normandie\cables_sans_boite_ou_probleme_daccrochage.shp", "LATIN1", None, "ESRI Shapefile")
	QgsVectorFileWriter.writeAsVectorFormat(cables_ayant_meme_geometrie,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\SRO5_Normandie\cables_ayant_meme_geometrie.shp", "LATIN1", None, "ESRI Shapefile")
	QgsVectorFileWriter.writeAsVectorFormat(cables_ayant_Invalide_geometrie,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\SRO5_Normandie\cables_ayant_Invalide_geometrie.shp", "LATIN1", None, "ESRI Shapefile")
	'''
