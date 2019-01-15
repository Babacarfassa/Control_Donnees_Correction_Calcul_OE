# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Control_Avant_Detection
								 A QGIS plugin
 Control_Avant_Detection
							  -------------------
		begin				: 2018-07-26
		git sha			  : $Format:%H$
		copyright			: (C) 2018 by Circet
		email				: Babacar.FASSA@circet.fr
 ***************************************************************************/

/***************************************************************************
 *																		 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or	 *
 *   (at your option) any later version.								   *
 *																		 *
 ***************************************************************************/
"""
import processing, re,itertools,sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import * 
from qgis.utils import *

# Initialize Qt resources from file resources.py
import resources
from Controle_des_cables import Controle_des_cables_function
from Controle_des_boites import Controle_des_boites_function
from Correction_des_accrochages_ligne_point import Correction_Accrochage_function
from Correction_du_sens_du_dessint import RectifSensDessin_function
from Detection_des_origines_extremites_des_cables import Detection_des_origines_extremites_des_cables_function
from Verification_des_origines_extremites_cables import Verification_des_origines_extremites_cables_function
from Calcul_des_distances_PBO_SRO import Calcul_des_distances_PBO_SRO_function
from cable_sans_support import cable_sans_support_function
# Import the code for the dialog
from Control_Avant_Detection_dialog import Control_Avant_DetectionDialog
from BoiteSansPTCables_dialog import BoiteSansPTCablesDialog
from Correction_Accrochage_dialog import Correction_AccrochageDialog
from RectifSensDessin_dialog import RectifSensDessinDialog
from Detection_Origine_Extremite_dialog import Detection_Origine_ExtremiteDialog
from Verification_Detection_Origine_Extemitee_dialog import Verification_Detection_Origine_ExtemiteeDialog
from Calcul_Distance_PBO_NRO_dialog import Calcul_Distance_PBO_NRODialog
from Cable_sans_infra_general_dialog import Cable_sans_infra_generalDialog
import os.path


class Control_Avant_Detection:
	"""QGIS Plugin Implementation."""

	def __init__(self, iface):
		"""Constructor.

		:param iface: An interface instance that will be passed to this class
			which provides the hook by which you can manipulate the QGIS
			application at run time.
		:type iface: QgisInterface
		"""
		# Save reference to the QGIS interface
		self.iface = iface
		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
		# initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'Control_Avant_Detection_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)


		# Declare instance attributes
		self.actions = []
		#self.menu = self.tr(u'&Pre Control Topologie')
		# TODO: We are going to let the user set this up in a future iteration
		#self.toolbar = self.iface.addToolBar(u'Control_Avant_Detection')
		#self.toolbar.setObjectName(u'Control_Avant_Detection')

	# noinspection PyMethodMayBeStatic
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return message#QCoreApplication.translate('Control_Avant_Detection', message)


	'''def add_action(
		self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=False,
		status_tip=None,
		whats_this=None,
		parent=None):

		# Create the dialog (after translation) and keep reference
		#self.dlg = Control_Avant_DetectionDialog()

		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action'''
	
	#Declaration des actions pour regrouper des plugins
	def initGui(self):
		self.menu = "&[Circet] A.1. Controle des donnees,corrections et calculs origines/extremites"
		self.action = QAction(
			QIcon(':/plugins/Control_Avant_Detection/icon.png'),
			u"controle_donnees", self.iface.mainWindow())
		self.action0 = QAction( QCoreApplication.translate("controle_donnees", "A.1.3. Controle des cables" ), self.iface.mainWindow() )
		self.action1 = QAction( QCoreApplication.translate("controle_donnees", "A.1.4. Controle des boites" ), self.iface.mainWindow() )
		self.action2 = QAction( QCoreApplication.translate("controle_donnees", "A.1.1. Correction des accrochages ligne/point" ), self.iface.mainWindow() )
		self.action3 = QAction( QCoreApplication.translate("controle_donnees", "A.1.2. Correction du sens du dessin" ), self.iface.mainWindow() )
		self.action4 = QAction( QCoreApplication.translate("controle_donnees", "A.1.5. Detection des origines/extremites des cables" ), self.iface.mainWindow() )
		self.action5 = QAction( QCoreApplication.translate("controle_donnees", "A.1.6. Verification des origines et extremites des cables" ), self.iface.mainWindow() )
		self.action6 = QAction( QCoreApplication.translate("controle_donnees", "A.1.7. Calcul des distances PBO_SRO" ), self.iface.mainWindow() )
		self.action7 = QAction( QCoreApplication.translate("controle_donnees", "A.1.8. Verification des cables sans supports" ), self.iface.mainWindow() )

		
		# connect the action to the run method
		self.action.triggered.connect(self.run)
		self.action0.triggered.connect(self.run)
		self.action1.triggered.connect(self.runboitesanscable)
		self.action2.triggered.connect(self.runcorrectionaccrochage)
		self.action3.triggered.connect(self.runrectifsensdessin)
		self.action4.triggered.connect(self.rundetectionOE)
		self.action5.triggered.connect(self.runverificcationdetectionOE)
		self.action6.triggered.connect(self.runCalcul_des_distances_PBO_SRO)
		self.action7.triggered.connect(self.runcable_sans_support)
	 
		self.iface.addPluginToMenu(self.menu, self.action0)
		self.iface.addPluginToMenu(self.menu, self.action1)
		self.iface.addPluginToMenu(self.menu, self.action2)
		self.iface.addPluginToMenu(self.menu, self.action3)
		self.iface.addPluginToMenu(self.menu, self.action4)
		self.iface.addPluginToMenu(self.menu, self.action5)
		self.iface.addPluginToMenu(self.menu, self.action6)
		self.iface.addPluginToMenu(self.menu, self.action7)

		self.actions.append(self.action0)
		self.actions.append(self.action1)
		self.actions.append(self.action2)
		self.actions.append(self.action3)
		self.actions.append(self.action4)
		self.actions.append(self.action5)
		self.actions.append(self.action6)
		self.actions.append(self.action7)
	
	'''def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/Control_Avant_Detection/icon.png'
		self.add_action(
			icon_path,
			text=self.tr(u'Control Avant Detection'),
			callback=self.run,
			parent=self.iface.mainWindow())'''


	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""
		for action in self.actions:
			self.iface.removePluginMenu(self.menu,action)
			#self.iface.removePluginMenu(self.tr(u'&Control_Avant_Detection'),action)
			#self.iface.removeToolBarIcon(action)
		# remove the toolbar
		#del self.toolbar


	def run(self):
		"""Run method that performs all the real work"""
		self.dlg = Control_Avant_DetectionDialog()
		self.dlg.comboBoite.clear()
		self.dlg.comboCABLES.clear()
		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layerType = layer.type()
			if layerType == QgsMapLayer.VectorLayer:
				layer_list.append(layer.name())
		self.dlg.comboBoite.addItems(layer_list)
		self.dlg.comboCABLES.addItems(layer_list)
		 
		# show the dialog
		self.dlg.show()
		# Run the dialog event loop
		result = self.dlg.exec_()
		# See if OK was pressed
		if result:
			

			BoiteLayerIndex = self.dlg.comboBoite.currentIndex()
			BoiteLayer = layers[BoiteLayerIndex]
			shape_boite= BoiteLayer

			CABLESLayerIndex = self.dlg.comboCABLES.currentIndex()
			CABLESLayer = layers[CABLESLayerIndex]
			shape_cables= CABLESLayer

			Fichier_CONF_PYTHON=QFileDialog.getOpenFileName(None, "Fichier_CONF_PYTHON", "", "xlsx files (*.xlsx)")
			Controle_des_cables_function(shape_boite,shape_cables,Fichier_CONF_PYTHON)
			

	def runboitesanscable(self):
		
		"""Run method that performs all the real work"""
		self.dlgboitesanscable = BoiteSansPTCablesDialog()
		self.dlgboitesanscable.comboBoite.clear()
		self.dlgboitesanscable.comboCABLES.clear()
		self.dlgboitesanscable.comboPT.clear()

		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layerType = layer.type()
			if layerType == QgsMapLayer.VectorLayer:
				layer_list.append(layer.name())


		self.dlgboitesanscable.comboBoite.addItems(layer_list)
		self.dlgboitesanscable.comboCABLES.addItems(layer_list)
		self.dlgboitesanscable.comboPT.addItems(layer_list)
  
		# show the dialog
		self.dlgboitesanscable.show()
        # Run the dialog event loop
		result = self.dlgboitesanscable.exec_()
		# See if OK was pressed
		if result:
			BoiteLayerIndex = self.dlgboitesanscable.comboBoite.currentIndex()
			BoiteLayer = layers[BoiteLayerIndex]
			shape_boite= BoiteLayer
			CABLESLayerIndex = self.dlgboitesanscable.comboCABLES.currentIndex()
			CABLESLayer = layers[CABLESLayerIndex]
			shape_cables= CABLESLayer
			PTLayerIndex = self.dlgboitesanscable.comboPT.currentIndex()
			PTLayer = layers[PTLayerIndex]
			shape_point_technique= PTLayer
			#Fichier_CONF_PYTHON=QFileDialog.getOpenFileName(None, "Fichier_CONF_PYTHON", "", "xlsx files (*.xlsx)")
			Controle_des_boites_function(shape_boite,shape_point_technique,shape_cables)
		

	def runcorrectionaccrochage(self):
		"""Run method that performs all the real work"""
		self.dlgcorrectionaccrochage = Correction_AccrochageDialog()
		self.dlgcorrectionaccrochage.comboBoite.clear()
		self.dlgcorrectionaccrochage.comboCABLES.clear()
		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layerType = layer.type()
			if layerType == QgsMapLayer.VectorLayer:
				layer_list.append(layer.name())

		self.dlgcorrectionaccrochage.comboBoite.addItems(layer_list)
		self.dlgcorrectionaccrochage.comboCABLES.addItems(layer_list)

		# show the dialog
		self.dlgcorrectionaccrochage.show()
		# Run the dialog event loop
		result = self.dlgcorrectionaccrochage.exec_()
		# See if OK was pressed
		if result:
			BoiteLayerIndex = self.dlgcorrectionaccrochage.comboBoite.currentIndex()
			BoiteLayer = layers[BoiteLayerIndex]
			shape_point= BoiteLayer

			CABLESLayerIndex = self.dlgcorrectionaccrochage.comboCABLES.currentIndex()
			CABLESLayer = layers[CABLESLayerIndex]
			shape_ligne= CABLESLayer
			
			Correction_Accrochage_function(shape_point,shape_ligne)


	def runrectifsensdessin(self):
		"""Run method that performs all the real work"""
		self.dlgcorrectionsensdessin = RectifSensDessinDialog()
		self.dlgcorrectionsensdessin.comboCable.clear()
		self.dlgcorrectionsensdessin.comboBoite.clear()
		self.dlgcorrectionsensdessin.comboSRO.clear()


		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layerType = layer.type()
			if layerType == QgsMapLayer.VectorLayer:
				layer_list.append(layer.name())


		self.dlgcorrectionsensdessin.comboCable.addItems(layer_list)
		self.dlgcorrectionsensdessin.comboBoite.addItems(layer_list)
		self.dlgcorrectionsensdessin.comboSRO.addItems(layer_list)

		# show the dialog
		self.dlgcorrectionsensdessin.show()
		# Run the dialog event loop
		result = self.dlgcorrectionsensdessin.exec_()
		# See if OK was pressed
		if result:
			

			SROLayerIndex = self.dlgcorrectionsensdessin.comboSRO.currentIndex()
			SROLayer = layers[SROLayerIndex]
			shape_sro= SROLayer

			CableLayerIndex = self.dlgcorrectionsensdessin.comboCable.currentIndex()
			CableLayer = layers[CableLayerIndex]
			shape_cable= CableLayer

			BoiteLayerIndex = self.dlgcorrectionsensdessin.comboBoite.currentIndex()
			BoiteLayer = layers[BoiteLayerIndex]
			shape_boite= BoiteLayer

			#Fichier_CONF_PYTHON=string=C:\Certification_Gracethd\Fichier_CONF_PYTHON_User.xlsx
			Fichier_CONF_PYTHON=QFileDialog.getOpenFileName(None, "Fichier_CONF_PYTHON", "", "xlsx files (*.xlsx)")
			
			RectifSensDessin_function(shape_boite,shape_sro,shape_cable,Fichier_CONF_PYTHON)
			
			
	def rundetectionOE(self):
		"""Run method that performs all the real work"""
		self.dlgdetectionOE = Detection_Origine_ExtremiteDialog()
		self.dlgdetectionOE.comboPBO.clear()
		self.dlgdetectionOE.comboCABLES.clear()
		self.dlgdetectionOE.comboSRO.clear()
		self.dlgdetectionOE.comboSUF.clear()
		


		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layerType = layer.type()
			if layerType == QgsMapLayer.VectorLayer:
				layer_list.append(layer.name())


		self.dlgdetectionOE.comboPBO.addItems(layer_list)
		self.dlgdetectionOE.comboCABLES.addItems(layer_list)
		self.dlgdetectionOE.comboSRO.addItems(layer_list)
		self.dlgdetectionOE.comboSUF.addItems(layer_list)
		# show the dialog
		self.dlgdetectionOE.show()
		# Run the dialog event loop
		result = self.dlgdetectionOE.exec_()
		# See if OK was pressed
		if result:
			

			PBOLayerIndex = self.dlgdetectionOE.comboPBO.currentIndex()
			PBOLayer = layers[PBOLayerIndex]
			shape_pbo= PBOLayer

			CABLESLayerIndex = self.dlgdetectionOE.comboCABLES.currentIndex()
			CABLESLayer = layers[CABLESLayerIndex]
			shape_cables= CABLESLayer

			SROLayerIndex = self.dlgdetectionOE.comboSRO.currentIndex()
			SROLayer = layers[SROLayerIndex]
			shape_sro= SROLayer
			
			SUFLayerIndex = self.dlgdetectionOE.comboSUF.currentIndex()
			SUFLayer = layers[SUFLayerIndex]
			shape_suf= SUFLayer

			#Fichier_CONF_PYTHON=string=C:\Certification_Gracethd\Fichier_CONF_PYTHON_User.xlsx
			Fichier_CONF_PYTHON=QFileDialog.getOpenFileName(None, "Fichier_CONF_PYTHON", "", "xlsx files (*.xlsx)")
			
			Detection_des_origines_extremites_des_cables_function(shape_pbo,shape_cables,shape_sro,Fichier_CONF_PYTHON,shape_suf)
			
			
	def runverificcationdetectionOE(self):
		"""Run method that performs all the real work"""
		self.dlgverificationdetectionOE = Verification_Detection_Origine_ExtemiteeDialog()
		self.dlgverificationdetectionOE.comboPBO.clear()
		self.dlgverificationdetectionOE.comboCABLES.clear()


		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layerType = layer.type()
			if layerType == QgsMapLayer.VectorLayer:
				layer_list.append(layer.name())


		self.dlgverificationdetectionOE.comboPBO.addItems(layer_list)
		self.dlgverificationdetectionOE.comboCABLES.addItems(layer_list)

		# show the dialog
		self.dlgverificationdetectionOE.show()
		# Run the dialog event loop
		result = self.dlgverificationdetectionOE.exec_()
		# See if OK was pressed
		if result:
			

			PBOLayerIndex = self.dlgverificationdetectionOE.comboPBO.currentIndex()
			PBOLayer = layers[PBOLayerIndex]
			shape_pbo= PBOLayer

			CABLESLayerIndex = self.dlgverificationdetectionOE.comboCABLES.currentIndex()
			CABLESLayer = layers[CABLESLayerIndex]
			shape_cables= CABLESLayer

			Fichier_CONF_PYTHON=QFileDialog.getOpenFileName(None, "Fichier_CONF_PYTHON", "", "xlsx files (*.xlsx)")
			Verification_des_origines_extremites_cables_function(shape_pbo,shape_cables,Fichier_CONF_PYTHON)
			
	def runCalcul_des_distances_PBO_SRO(self):
		"""Run method that performs all the real work"""
		self.dlgcalculdistancePBOSRO = Calcul_Distance_PBO_NRODialog()
		self.dlgcalculdistancePBOSRO.comboPBO.clear()
		self.dlgcalculdistancePBOSRO.comboCABLES.clear()
		self.dlgcalculdistancePBOSRO.comboSITES.clear()



		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layerType = layer.type()
			if layerType == QgsMapLayer.VectorLayer:
				layer_list.append(layer.name())


		self.dlgcalculdistancePBOSRO.comboPBO.addItems(layer_list)
		self.dlgcalculdistancePBOSRO.comboCABLES.addItems(layer_list)
		self.dlgcalculdistancePBOSRO.comboSITES.addItems(layer_list)
		 
		# show the dialog
		self.dlgcalculdistancePBOSRO.show()
		# Run the dialog event loop
		result = self.dlgcalculdistancePBOSRO.exec_()
		# See if OK was pressed
		if result:
			

			PBOLayerIndex = self.dlgcalculdistancePBOSRO.comboPBO.currentIndex()
			PBOLayer = layers[PBOLayerIndex]
			shape_pbo= PBOLayer

			CABLESLayerIndex = self.dlgcalculdistancePBOSRO.comboCABLES.currentIndex()
			CABLESLayer = layers[CABLESLayerIndex]
			shape_cables= CABLESLayer

			SITESLayerIndex = self.dlgcalculdistancePBOSRO.comboSITES.currentIndex()
			SITESLayer = layers[SITESLayerIndex]
			shape_sites= SITESLayer


			#Fichier_CONF_PYTHON=string=C:\Certification_Gracethd\Fichier_CONF_PYTHON_User.xlsx
			Fichier_CONF_PYTHON=QFileDialog.getOpenFileName(None, "Fichier_CONF_PYTHON", "", "xlsx files (*.xlsx)")
			Calcul_des_distances_PBO_SRO_function(shape_pbo,shape_cables,shape_sites,Fichier_CONF_PYTHON)
			
			
			
	def runcable_sans_support(self):
		"""Run method that performs all the real work"""
		# show the dialog
		self.dlgcablesanssupport = Cable_sans_infra_generalDialog()
		self.dlgcablesanssupport.comboInfra.clear()
		self.dlgcablesanssupport.comboCables.clear()



		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layerType = layer.type()
			if layerType == QgsMapLayer.VectorLayer:
				layer_list.append(layer.name())


		self.dlgcablesanssupport.comboInfra.addItems(layer_list)
		self.dlgcablesanssupport.comboCables.addItems(layer_list)

		# show the dialog
		self.dlgcablesanssupport.show()
		# Run the dialog event loop
		result = self.dlgcablesanssupport.exec_()
		# See if OK was pressed
		if result:
			

			CablesLayerIndex = self.dlgcablesanssupport.comboCables.currentIndex()
			layershape_cables = layers[CablesLayerIndex]
			

			InfraLayerIndex = self.dlgcablesanssupport.comboInfra.currentIndex()
			layershape_infra = layers[InfraLayerIndex]
			
			cable_sans_support_function(layershape_cables,layershape_infra)