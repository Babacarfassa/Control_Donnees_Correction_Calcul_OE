import processing
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import * 
from qgis.utils import *

def Verification_des_origines_extremites_cables_function(shape_pbo,shape_cables,Fichier_CONF_PYTHON):
	#Creation dune liste de mon fichier de configuration
	list_file_con=[]
	layer_ref_conf = QgsVectorLayer(Fichier_CONF_PYTHON, 'Fichier_CONF_PYTHON', 'ogr')
	for field_ref in layer_ref_conf.getFeatures():
		list_file_con.append([field_ref[0],field_ref[1],field_ref[2],field_ref[3]])


	#Declaration des noms des colonnes
	shape_BP_name_BP_NOM='BP_NOM'
	shape_CB_name_CB_NOM='CB_NOM'
	shape_CB_name_CB_Origine='CB_Origine'
	shape_CB_name_CB_Extremite='CB_Extremite'

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


	shape_pbo_Nom_Colonne_Nom=get_field_name(shape_BP_name_BP_NOM,shape_pbo)#NOM
	shape_cables_Nom_Colonne_Nom=get_field_name(shape_CB_name_CB_NOM,shape_cables)#NOM
	shape_cables_Nom_Colonne_origine=get_field_name(shape_CB_name_CB_Origine,shape_cables)#'originee'
	shape_cables_Nom_Colonne_extremite=get_field_name(shape_CB_name_CB_Extremite,shape_cables)#'extremitee'


	#Fonction pour identifier les doublons dientifiant des boites
	def get_cnt(lVals):
		#creation dun dictionnary avec des occurrences initialisees a zero
		d = dict(zip(lVals, [0] * len(lVals)))
		#parcours de la list en argument
		for x in lVals:
			#compter les occurrences pour identifier les doublons
			d[x] += 1
		for key, value in d.items():
			#Condition de verification des doublons
			if value > 1:
				#print key, ';',value
				return key
		return -1


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


	def verification_detection_originee_extremitee(shape_pbo,shape_cables,shape_pbo_Nom_Colonne_Nom,shape_cables_Nom_Colonne_Nom,shape_cables_Nom_Colonne_origine,shape_cables_Nom_Colonne_extremite):

		layershape_pbo =shape_pbo
		layershape_pbo2 = shape_pbo

		layershape_cables = shape_cables
		list_cable = [shape_cables for shape_cables in layershape_cables.getFeatures()]
		
		list_pbo=[]
		
		for shape_pbo in layershape_pbo.getFeatures():
			a= [shape_pbo.geometry().exportToWkt(),shape_pbo[shape_pbo_Nom_Colonne_Nom]]
			list_pbo.append(a)
			
		list_cables_doublon=[]
		for shape_cables in layershape_cables.getFeatures():
			a= [shape_cables.geometry().exportToWkt(),shape_cables[shape_cables_Nom_Colonne_Nom]]
			list_cables_doublon.append(a)
			
		#Verification des doublons des extremites detectees.
		list_extremite_control_detection=[]
		for shape_cables in layershape_cables.getFeatures():
			list_extremite_control_detection.append([shape_cables[shape_cables_Nom_Colonne_Nom],shape_cables[shape_cables_Nom_Colonne_extremite]])

		#Creation de shapefile pour le resultat des erreurs des id en doublons des boites qui se superposent
		probleme_coherence_boite= QgsVectorLayer("Point?crs=epsg:2154", "probleme_coherence_boite", "memory")
		pr = probleme_coherence_boite.dataProvider()
		probleme_coherence_boite.startEditing()
		pr.addAttributes([QgsField(shape_pbo_Nom_Colonne_Nom, QVariant.String),QgsField('Nature', QVariant.String)])
		probleme_coherence_boite.updateFields()
		probleme_coherence_boite.commitChanges()

		#Creation de shapefile pour le resultat des erreurs des id en doublons des boites qui se superposent
		origine_shape_cables_egal_extremite= QgsVectorLayer("LineString?crs=epsg:2154", "origine_shape_cables_egal_extremite", "memory")
		pr_shape_cables = origine_shape_cables_egal_extremite.dataProvider()
		origine_shape_cables_egal_extremite.startEditing()
		pr_shape_cables.addAttributes([QgsField(shape_cables_Nom_Colonne_Nom, QVariant.String),QgsField('Erreur_Nature', QVariant.String)])
		origine_shape_cables_egal_extremite.updateFields()
		origine_shape_cables_egal_extremite.commitChanges()
		
		#Creation de shapefile pour le resultat des erreurs des id en doublons des boites
		Erreur_doublon_id_boite= QgsVectorLayer("Point?crs=epsg:2154", "Erreur_doublon_id_boite", "memory")
		Erreur_doublon_id_boite_pr = Erreur_doublon_id_boite.dataProvider()
		Erreur_doublon_id_boite.startEditing()
		Erreur_doublon_id_boite_pr.addAttributes([QgsField(shape_pbo_Nom_Colonne_Nom, QVariant.String),QgsField('Nature', QVariant.String)])
		Erreur_doublon_id_boite.updateFields()
		Erreur_doublon_id_boite.commitChanges()
		
		#Creation de shapefile pour le resultat des erreurs des id en doublons des cables
		erreur_doublon_id_cable= QgsVectorLayer("LineString?crs=epsg:2154", "erreur_doublon_id_cable", "memory")
		erreur_doublon_id_cable_pr= erreur_doublon_id_cable.dataProvider()
		erreur_doublon_id_cable.startEditing()
		erreur_doublon_id_cable_pr.addAttributes([QgsField(shape_cables_Nom_Colonne_Nom, QVariant.String),QgsField('Erreur_Nature', QVariant.String)])
		erreur_doublon_id_cable.updateFields()
		erreur_doublon_id_cable.commitChanges()
		
		#Identification des extremites en doublons des cables
		erreur_doublon_extremite_cable= QgsVectorLayer("LineString?crs=epsg:2154", "erreur_doublon_extremite_cable", "memory")
		erreur_doublon_extremite_cable_pr= erreur_doublon_extremite_cable.dataProvider()
		erreur_doublon_extremite_cable_attr2 = layershape_cables.dataProvider().fields().toList()
		erreur_doublon_extremite_cable_pr.addAttributes(erreur_doublon_extremite_cable_attr2)
		erreur_doublon_extremite_cable.updateFields()
		erreur_doublon_extremite_cable.commitChanges()

		Erreur_probleme_coherence_boite='Erreur : il existe des boites qui se supperposent ici'

		Erreur_origine_shape_cables_egal_extremite='ERREUR: ce cable a une boite qui est a la fois origine et extemite'

		Erreur_nbre_cable_rentrant_superieur_un='ERREUR: cette boite a un nombre de cable rentrant superieur a un' 

		Erreur_boite_presente_plus1fois_extremite_cable='ERREUR: cette boite nest pas presente dans extremite du cable'
		
		Erreur_doublon_ID_shape_pbo='Erreur : Cet ID est present plus dune fois dans shape_pbo'
		
		Erreur_doublon_ID_shape_cables='Erreur : Cet ID est present plus dune fois dans shape_cables'
		
		#identification des doublons didentifiant de boites
		for boite_double in get_doublon(list_pbo):
			#print boite_double[1]
			attrs=[boite_double[1],Erreur_doublon_ID_shape_pbo]
			elem= QgsFeature()
			elem.setGeometry(QgsGeometry.fromWkt(boite_double[0]))
			elem.setAttributes(attrs)
			Erreur_doublon_id_boite_pr.addFeatures([elem])   
		
		#identification des doublons didentifiant de cables
		for cable_double in get_doublon(list_cables_doublon):
			#print cable_double[1]
			attrs=[cable_double[1],Erreur_doublon_ID_shape_cables]
			elem= QgsFeature()
			elem.setGeometry(QgsGeometry.fromWkt(cable_double[0]))
			elem.setAttributes(attrs)
			erreur_doublon_id_cable_pr.addFeatures([elem])   
		
		#Identification des ID extremites detectes dans la 
		for i in get_doublon(list_extremite_control_detection):
			for j in list_cable:
				if i[0] == j[shape_cables_Nom_Colonne_Nom]:
					erreur_doublon_extremite_cable_pr.addFeatures([j])
		
		#ERREUR si boites qui se supperposent
		for shape_pbo in layershape_pbo.getFeatures():
			count_sortant = 0
			count_rentrant = 0
			count_boite_extremite=0
			boite_not_in_extremite_cable='KO'
			bboxshape_cables = shape_pbo.geometry().buffer(0.5,0.5).boundingBox()
			request = QgsFeatureRequest()
			request.setFilterRect(bboxshape_cables)    
			
			for shape_pbo2 in layershape_pbo2.getFeatures(request):
				 if (shape_pbo.geometry().intersects(shape_pbo2.geometry())) and (shape_pbo[shape_pbo_Nom_Colonne_Nom] != shape_pbo2[shape_pbo_Nom_Colonne_Nom]):
					 #print shape_pbo[shape_pbo_Nom_Colonne_Nom],';', shape_pbo2[shape_pbo_Nom_Colonne_Nom]    
					 attrs=[shape_pbo[shape_pbo_Nom_Colonne_Nom],Erreur_probleme_coherence_boite]
					 elem= QgsFeature()
					 elem.setGeometry(QgsGeometry.fromWkt(shape_pbo.geometry().exportToWkt()))
					 elem.setAttributes(attrs)
					 pr.addFeatures([elem])         

				 
			for shape_cables in layershape_cables.getFeatures(request):
				#ERREUR si boite presente plus dune fois dans extremite cable
				if shape_cables[shape_cables_Nom_Colonne_extremite] == shape_pbo[shape_pbo_Nom_Colonne_Nom]:
					count_boite_extremite += 1
				
				#ERREUR si boite nest pas presente dans extremite cable
				if shape_cables[shape_cables_Nom_Colonne_extremite] == shape_pbo[shape_pbo_Nom_Colonne_Nom]:
					boite_not_in_extremite_cable ='OK'
				
				#ERREUR si originee  egal a extremite
				if shape_cables[shape_cables_Nom_Colonne_extremite] == shape_cables[shape_cables_Nom_Colonne_origine]:
					attrs=[shape_cables[shape_cables_Nom_Colonne_Nom],Erreur_origine_shape_cables_egal_extremite]
					elem= QgsFeature()
					elem.setGeometry(QgsGeometry.fromWkt(shape_cables.geometry().exportToWkt()))
					elem.setAttributes(attrs)
					pr_shape_cables.addFeatures([elem])
					
				if shape_pbo[shape_pbo_Nom_Colonne_Nom] == shape_cables[shape_cables_Nom_Colonne_extremite]:
					count_rentrant +=1           
					
				#cable_sortant
				if shape_pbo[shape_pbo_Nom_Colonne_Nom] == shape_cables[shape_cables_Nom_Colonne_origine]:
					count_sortant +=1
				
				'''if get_cnt(list_cables_doublon) == shape_cables[shape_cables_Nom_Colonne_Nom]:
					attrs=[shape_cables[shape_cables_Nom_Colonne_Nom],Erreur_doublon_ID_shape_cables ]
					elem= QgsFeature()
					elem.setGeometry(QgsGeometry.fromWkt(shape_cables.geometry().exportToWkt()))
					elem.setAttributes(attrs)
					pr_shape_cables.addFeatures([elem])'''
				

			for shape_cables in list_cable:
					#calcul  du nombre de cable rentrant de la boite
					if shape_cables[shape_cables_Nom_Colonne_extremite] == shape_pbo[shape_pbo_Nom_Colonne_Nom]:
						#ERREUR si Nombre de shape_cables rentrant dans une boite superieur a 1
						if count_rentrant > 1:
							attrs=[shape_pbo[shape_pbo_Nom_Colonne_Nom],Erreur_nbre_cable_rentrant_superieur_un ]
							elem= QgsFeature()
							elem.setGeometry(QgsGeometry.fromWkt(shape_pbo.geometry().exportToWkt()))
							elem.setAttributes(attrs)
							pr.addFeatures([elem])
			#ERREUR si boite presente plus dune fois dans extremite cable
			if boite_not_in_extremite_cable =='KO':
				#print count_boite_extremite,';',shape_pbo[shape_pbo_Nom_Colonne_Nom]
				attrs=[shape_pbo[shape_pbo_Nom_Colonne_Nom],Erreur_boite_presente_plus1fois_extremite_cable ]
				elem= QgsFeature()
				elem.setGeometry(QgsGeometry.fromWkt(shape_pbo.geometry().exportToWkt()))
				elem.setAttributes(attrs)
				pr.addFeatures([elem])
				
			''''if get_doublon(list_pbo) == shape_pbo[shape_pbo_Nom_Colonne_Nom]:
				#print shape_pbo[shape_pbo_Nom_Colonne_Nom]
				attrs=[shape_pbo[shape_pbo_Nom_Colonne_Nom],Erreur_doublon_ID_shape_pbo ]
				elem= QgsFeature()
				elem.setGeometry(QgsGeometry.fromWkt(shape_pbo.geometry().exportToWkt()))
				elem.setAttributes(attrs)
				pr.addFeatures([elem])'''
			
		QgsMapLayerRegistry.instance().addMapLayer(probleme_coherence_boite)
		QgsMapLayerRegistry.instance().addMapLayer(origine_shape_cables_egal_extremite)
		QgsMapLayerRegistry.instance().addMapLayer(Erreur_doublon_id_boite) 
		QgsMapLayerRegistry.instance().addMapLayer(erreur_doublon_id_cable) 
		QgsMapLayerRegistry.instance().addMapLayer(erreur_doublon_extremite_cable)
		
		"""QgsVectorFileWriter.writeAsVectorFormat(probleme_coherence_boite,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\114AP0_08_03_2018\probleme_coherence_boite.shp", "LATIN1", None, "ESRI Shapefile")
		QgsVectorFileWriter.writeAsVectorFormat(origine_shape_cables_egal_extremite,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\114AP0_08_03_2018\origine_shape_cables_egal_extremite.shp", "LATIN1", None, "ESRI Shapefile")
		QgsVectorFileWriter.writeAsVectorFormat(Erreur_doublon_id_boite,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\114AP0_08_03_2018\Erreur_doublon_id_boite.shp", "LATIN1", None, "ESRI Shapefile")
		QgsVectorFileWriter.writeAsVectorFormat(erreur_doublon_id_cable,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\114AP0_08_03_2018\erreur_doublon_id_cable.shp", "LATIN1", None, "ESRI Shapefile")
		QgsVectorFileWriter.writeAsVectorFormat(erreur_doublon_extremite_cable,r"C:\Certification_Gracethd\AUDIT_NANCY_NRO\114AP0_08_03_2018\erreur_doublon_extremite_cable.shp", "LATIN1", None, "ESRI Shapefile")"""
		


	#Verification des sites qui sont ni individuel ni collectif
	def verfication_sites_indiv_col(shape_sites,shape_sites_Nom_Colonne_Nom,shape_sites_Nom_Colonne_Type,shape_sites_Individuel_Valeur,shape_sites_Collectif_Valeur):
		
		layershape_sites = processing.getObject(shape_sites)   
		
		Erreur_shape_sites_erreur_indiv_col='Erreur : Type de site qui nest pas individuel ou collectif'
		
		shape_sites_erreur_indiv_col= QgsVectorLayer("Point?crs=epsg:2154", "Type de site qui nest pas individuel ou collectif", "memory")
		pr_shape_sites_erreur_indiv_col = shape_sites_erreur_indiv_col.dataProvider()
		shape_sites_erreur_indiv_col.startEditing()
		pr_shape_sites_erreur_indiv_col.addAttributes([QgsField(shape_sites_Nom_Colonne_Nom, QVariant.String),QgsField('Nature', QVariant.String)])
		shape_sites_erreur_indiv_col.updateFields()
		shape_sites_erreur_indiv_col.commitChanges()
		
		for shape_sites in layershape_sites.getFeatures():
			if shape_sites[shape_sites_Nom_Colonne_Type] != shape_sites_Individuel_Valeur and shape_sites[shape_sites_Nom_Colonne_Type] != shape_sites_Collectif_Valeur:
				#print 'different',';',shape_sites[shape_sites_Nom_Colonne_Type],';',shape_sites[shape_sites_Nom_Colonne_Type],';',shape_sites[0]
				
				attrs=[shape_sites[shape_sites_Nom_Colonne_Nom],Erreur_shape_sites_erreur_indiv_col ]
				elem= QgsFeature()
				elem.setGeometry(QgsGeometry.fromWkt(shape_sites.geometry().exportToWkt()))
				elem.setAttributes(attrs)
				pr_shape_sites_erreur_indiv_col.addFeatures([elem])
		QgsMapLayerRegistry.instance().addMapLayer(shape_sites_erreur_indiv_col)
		

	#Execution de la fonction verification de la detectionFailed
	verification_detection_originee_extremitee(shape_pbo,shape_cables,shape_pbo_Nom_Colonne_Nom,shape_cables_Nom_Colonne_Nom,shape_cables_Nom_Colonne_origine,shape_cables_Nom_Colonne_extremite)

	#Execution de la fonction verification des sites individuels et collectifs
	#verfication_sites_indiv_col(shape_sites,shape_sites_Nom_Colonne_Nom,shape_sites_Nom_Colonne_Type,shape_sites_Individuel_Valeur,shape_sites_Collectif_Valeur)
