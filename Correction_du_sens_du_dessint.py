import processing, re,itertools,sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import * 
from qgis.utils import *

def RectifSensDessin_function(shape_boite,shape_sro,shape_cable,Fichier_CONF_PYTHON):
	list_file_con=[]
	layer_ref_conf = QgsVectorLayer(Fichier_CONF_PYTHON, 'Fichier_CONF_PYTHON', 'ogr')
	for field_ref in layer_ref_conf.getFeatures():
		list_file_con.append([field_ref[0],field_ref[1],field_ref[2],field_ref[3]])

	#Declaration des noms des colonnes
	shape_BP_name_BP_NOM='BP_NOM'
	shape_CB_name_CB_NOM='CB_NOM'

	#Declaration des noms des entites

	layershape_boite = shape_boite
	layershape_sro = shape_sro
	layershape_cable = shape_cable

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

	shape_pbo_Nom_Colonne_Nom=get_field_name(shape_BP_name_BP_NOM,shape_boite)#CODE_BPE
	shape_cable_Nom_Colonne_Nom=get_field_name(shape_CB_name_CB_NOM,shape_cable)#CODE_CB

	shape_boite_Nom_Colonne_Nom=shape_pbo_Nom_Colonne_Nom
	shape_cable_Nom_Colonne_Nom=shape_cable_Nom_Colonne_Nom


	def return_Not_Null(field):
		if field == NULL:
			return 'Identifiant NULL pour cette entite'
		else :
			return field

	listshape_boite = []
	for shape_boites in layershape_boite.getFeatures():
		shape_boite = [shape_boites[shape_boite_Nom_Colonne_Nom],shape_boites.geometry().exportToWkt(),-1,-1,-1,-1]
		listshape_boite.append(shape_boite)

	listshape_sro = []
	for shape_sro  in layershape_sro.getFeatures():
		shape_sros = [shape_sro.geometry().exportToWkt()]
		#print shape_sro.geometry().exportToWkt()
		listshape_sro.append(shape_sros)
		
	point_depart_sro=str(min(listshape_sro)).replace('[','').replace(']','').replace('u','').replace("'",'')

	list_shape_cable=[]
	for shape_cable in layershape_cable.getFeatures():
		
		res_origine='KO'
		res_extremite='KO'
		

		geom_support=shape_cable.geometry()
		bboxinfra = geom_support.buffer(5, 5).boundingBox()
		request = QgsFeatureRequest()
		request.setFilterRect(bboxinfra)
		
		if geom_support.wkbType()==QGis.WKBMultiLineString:
			geom_support_type=geom_support.asMultiPolyline()
			support_origine=geom_support_type[0][0]
			support_extremite=geom_support_type[-1][-1]
			
		if geom_support.wkbType()==QGis.WKBLineString:
			geom_support_type=geom_support.asPolyline()
			support_origine=geom_support_type[0]
			support_extremite=geom_support_type[-1]
		
		shape_cables_origine=(QgsGeometry.fromPoint(QgsPoint(support_origine))).exportToWkt()
		shape_cables_extremite=(QgsGeometry.fromPoint(QgsPoint(support_extremite))).exportToWkt()
		
		geom_support_lines=geom_support.exportToWkt()
		#print shape_cable[0],';',geom_support_type,';',support_origine,';',support_extremite
		
		list_shape_cable.append([shape_cable[shape_cable_Nom_Colonne_Nom],shape_cables_origine,shape_cables_extremite,0,-1,-1,geom_support_lines])


	#Fonction nommage_support_parcours
	#depart_origine_support : point de depart courant de la recursion
	#pt_amont :  nom du dernier point technique rencontredans la reursion
	#ordre : ordre du support depuis le dernier point technique rencontre
	def nommage_support_parcours(depart_origine_support,pt_amont,ordre,niveau):
		
		pt_aval = ""

		if niveau < 100000:
			for shape_cable in list_shape_cable:         
				# On ne prend que les supports non parcourus dont lorigine est le point dorigine est depart_origine_support
				if (shape_cable[1]==depart_origine_support) and (shape_cable[3]==0):
					#le support est dans le bon sens
					shape_cable[3] = 1
					# on verifie si il y a un point technique en extremite de ce support
					#print shape_cable[1]
					ptextremite_good_sens = 0
					for shape_boite in listshape_boite:
						if shape_cable[2] == shape_boite[1]:
							#print shape_cable[1],';',shape_cable[0]
							# si il y a un point technique en extremite, on recommence la reursion a partir de ce point
							ptextremite_good_sens = 1
							nommage_support_parcours(shape_cable[2],shape_boite[0],ordre,niveau+1)
							pt_aval = return_Not_Null(shape_boite[0])
					if ptextremite_good_sens == 0:
						# si il ny a pas de point technique en extremite, on recommence la recursion apartir de lextremiteen se souvenant du dernier point technique rencontre
						pt_aval =nommage_support_parcours(shape_cable[2],pt_amont,ordre+1,niveau+1)
					
					shape_cable[4]=return_Not_Null(pt_amont)
					shape_cable[5]=return_Not_Null(pt_aval)
					
				# On ne prend que les supports non parcourus dont l'extremite est le point dorigine est depart_origine_support
				elif (shape_cable[2]==depart_origine_support) and (shape_cable[3]==0):
					#le support nest pas dans le bon sens
					shape_cable[3] = -1
					# on verifie si il y a un point technique en extremite en fait origine) de ce support
					ptextremite_bad_sens = 0
					for shape_boite in listshape_boite:
						if shape_cable[1] == shape_boite[1]:
							ptextremite_bad_sens = 1
							# si il y a un point technique en extremite (en fait origine), on recommence la recursion a partir de ce point
							nommage_support_parcours(shape_cable[1],shape_boite[0],1,niveau+1)
							
							pt_aval = return_Not_Null(shape_boite[0])
								
					if ptextremite_bad_sens == 0:
						# si il ny a pas de point technique en extremite, on recommence la recursion a partir de lextremite en se souvenant du dernier point technique rencontre
						pt_aval=nommage_support_parcours(shape_cable[1],pt_amont,ordre+1,niveau+1)
						
					shape_cable[4]=return_Not_Null(pt_amont)
					shape_cable[5]=return_Not_Null(pt_aval)

			if pt_aval == "" or pt_aval == NULL:
				pt_aval = 'Erreur pas de PT Extremite'
				for shape_boite in listshape_boite:
					if depart_origine_support == shape_boite[1]:
						pt_aval = shape_boite[0]

			return pt_aval

	nommage_support_parcours(point_depart_sro ,'PM',1,1)


	Erreur_mauvais_sens = QgsVectorLayer("LineString?crs=epsg:2154", "Erreur_mauvais_sens", "memory")
	Erreur_mauvais_sens_pr2 = Erreur_mauvais_sens.dataProvider()
	Erreur_mauvais_sens_attr2 = layershape_cable.dataProvider().fields().toList()
	Erreur_mauvais_sens_pr2.addAttributes(Erreur_mauvais_sens_attr2)
	Erreur_mauvais_sens.updateFields()
	Erreur_mauvais_sens.commitChanges()



	#Partie du script pour identifier les troncons qui sont dessines dans le mauvais sens ainsi que leur correction
	for shape_cable in list_shape_cable: 
		outFeat = QgsFeature()
		a= shape_cable[0],';',shape_cable[1],';',shape_cable[2],';',shape_cable[3],';',shape_cable[4],';',shape_cable[5]
		attribut_support=[shape_cable[0]]

		#Prendre que les supports qui sont dans le mauvais sens
		if shape_cable[3] == -1:
			geom_support=QgsGeometry.fromWkt(shape_cable[6])
			#print shape_cable[0] ,';',shape_cable[3] ,';',geom_support

			#Inverser le sens
			geom_support_Rec=None
			if geom_support and not geom_support.isEmpty():
				reversedLine = geom_support.geometry().reversed()
			geom_support_Rec=QgsGeometry(reversedLine)
			outFeat.setGeometry(geom_support_Rec)
			outFeat.setAttributes(attribut_support)
			Erreur_mauvais_sens_pr2.addFeatures([outFeat])
			
			#Mise a jour de la geometrie dans le shape support pour corriger le sens du dessin
			layershape_cable.startEditing()
			
			for shape_cable_shape in layershape_cable.getFeatures():
				if shape_cable[0] == shape_cable_shape[shape_cable_Nom_Colonne_Nom]:
					layershape_cable.dataProvider().changeGeometryValues({shape_cable_shape.id(): (geom_support_Rec)})

		#print shape_cable[0],';',shape_cable[3],';',shape_cable[4],';',shape_cable[5]

	layershape_cable.commitChanges()
	layershape_cable.commitChanges()


	QgsMapLayerRegistry.instance().addMapLayer(Erreur_mauvais_sens)

