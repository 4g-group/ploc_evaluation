#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''Copyright © 2020 by SGME (4G group)
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the “Software”),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express
or implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose and noninfringement. In no event shall
the authors or copyright holders X be liable for any claim, damages or
other liability, whether in an action of contract, tort or otherwise,
arising from, out of or in connection with the software or the use or
other dealings in the Software.

Except as contained in this notice, the name of the SGME (4G group)
shall not be used in advertising or otherwise to promote the sale,
use or other dealings in this Software without prior written authorization
from the SGME (4G group).
'''

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import numpy
import simplekml
import datetime
import picket
import geopy.distance
import sys
import getopt
from shapely.geometry import Point, Polygon
import xml.etree.ElementTree as ET
import xmltodict
import csv
import shutil
sys.path.append('../')
import time as TIME
from lib.Bag2csv import write2csv
reload(sys)
sys.setdefaultencoding("utf-8")

def groundtruth_retrieval(groundtruth, scenario):
    if scenario == 'ref':
        groundtruth_time = groundtruth + "/" + "TEMPS_PASSAGE_CyborgLoc_Ref.txt"
        groundtruth_base =  groundtruth + "/" + "BASE_3D_CFIS41_scenario_ref.xml"
    elif scenario == 'eval':
        groundtruth_time = groundtruth + "/" "TEMPS_PASSAGE_CyborgLoc_Eval.txt"
        groundtruth_base =  groundtruth + "/" + "BASE_3D_CFIS41_scenario_eval.xml"
    groundtruth_plan = groundtruth + "/" + "BASE_PLAN_CFIS41.xml"
    groundtruth_plan_soussol = groundtruth + "/"+ "sdis_-1.png"
    groundtruth_plan_rdc = groundtruth + "/"+ "sdis_0.png"
    groundtruth_plan_premier = groundtruth + "/"+ "sdis_1.png"
    groundtruth_plan_second = groundtruth + "/"+ "sdis_2.png"
    groundtruth_plan_troisieme = groundtruth + "/"+ "sdis_3.png"
    groundtruth_plan_quatrieme = groundtruth + "/"+ "sdis_4.png"
    groundtruth_plan_cinquieme = groundtruth + "/"+ "sdis_5.png"
    groundtruth_plan_sixieme = groundtruth + "/"+ "sdis_6.png"
    overlays = {'-1':groundtruth_plan_soussol, '0':groundtruth_plan_rdc, '1':groundtruth_plan_premier,'2':groundtruth_plan_second, '3':groundtruth_plan_troisieme, '4':groundtruth_plan_quatrieme, '5':groundtruth_plan_cinquieme, '6':groundtruth_plan_sixieme}
    # Read time from txt file given by DGA and put it in panda dataframe
    dg_time = pd.read_csv(groundtruth_time, header=None, skip_blank_lines=True, delimiter=';',
               names= ['TimeStart', 'TimeEnd', 'Numero', 'Type'], index_col=False, encoding='utf-8')
    dg_time.Numero= dg_time.Numero.astype(int)
    secs_start = []
    secs_end = []
    year = 2019
    month = 9
    if scenario == 'ref':
        date = 26
    elif scenario == 'eval':
        date = 25
    for row in dg_time[['TimeStart', 'TimeEnd']].values:
        start_utc = datetime.datetime(year, month, date, int(str(row[0])[0:2]), int(str(row[0])[2:4]), int(str(row[0])[4:6]), int(str(row[0])[7:9])*10000)
        end_utc = datetime.datetime(year, month, date, int(str(row[1])[0:2]), int(str(row[1])[2:4]), int(str(row[1])[4:6]), int(str(row[1])[7:9])*10000)
        secs_start.append(TIME.mktime(start_utc.timetuple()) + start_utc.microsecond / 1e6)
        secs_end.append(TIME.mktime(end_utc.timetuple()) + end_utc.microsecond / 1e6)
    dg_time['SecsStart'] = secs_start
    dg_time['SecsEnd'] = secs_end
    #  Read time from xml file given by DGA and put it in panda dataframe
    tree = ET.parse(groundtruth_base)
    root = tree.getroot()
    dg = pd.DataFrame(columns = ['Type', 'Numero', 'Nom', 'Latitude', 'Hemishere', 'Longitude', 'Meridien', 'Altitude', 'Orientation', 'Etage'])
    for child in root:
        if child.tag == 'stationnaire':
            if float(child.find('orientation').text) == -1.0:
                orientation = numpy.NAN
                type = 'S'
            else :
                orientation = float(child.find('orientation').text)
                type = 'S'
            if ((child.find('nom').text == 'Pt_Vol1') | (child.find('nom').text == 'Pt_Vol2') | (child.find('nom').text == 'E0b') | (child.find('nom').text == 'R0') | (child.find('nom').text == 'VT1_centre') | (child.find('nom').text == 'R0b') | (child.find('nom').text == 'VT2_centre')):
                environnement = 'O'
            else:
                environnement = 'I'
            dg = dg.append(pd.Series([type, int(child.find('numero').text), child.find('nom').text, float(child.find('lat').text), child.find('hemis').text, float(child.find('lon').text), child.find('merid').text,  float(child.find('z').text), orientation, int(child.find('etage').text), str(environnement)], index =['Type', 'Numero', 'Nom', 'Latitude', 'Hemishere', 'Longitude', 'Meridien', 'Altitude', 'Orientation', 'Etage', 'Environnement']),ignore_index=True)
        elif child.tag == 'volume':
            type = 'V'
            if scenario == 'ref':
                if (child.find('numero').text=='0'):
                    etage = 0
                if (child.find('numero').text=='1'):
                    etage = -1
                elif (child.find('numero').text=='2'):
                    etage = 0
                elif (child.find('numero').text=='3'):
                    etage = 3
                elif (child.find('numero').text=='4'):
                    etage = 6
                elif (child.find('numero').text=='5'):
                    etage = 0
            elif scenario == 'eval':
                if (child.find('numero').text=='0'):
                    etage = 0
                if (child.find('numero').text=='1'):
                    etage = 0
                elif (child.find('numero').text=='2'):
                    etage = 1
                elif (child.find('numero').text=='3'):
                    etage = 3
                elif (child.find('numero').text=='4'):
                    etage = 6
                elif (child.find('numero').text=='5'):
                    etage = 0
                elif (child.find('numero').text=='6'):
                    etage = 0
            if ((child.find('nom').text == 'VR0') | (child.find('nom').text == 'VR5') | (child.find('nom').text == 'VE0') | (child.find('nom').text == 'VE6')):
                environnement = 'O'
            else:
                environnement = 'I'
            for elem in child:
                if elem.tag=='segment':
                    dg = dg.append(pd.Series([type, int(child.find('numero').text), elem.find('nom').text,  float(elem.find('lat').text), elem.find('hemis').text, float(elem.find('lon').text), elem.find('merid').text, float(elem.find('alt').text), numpy.NAN, etage, environnement], index = ['Type', 'Numero', 'Nom', 'Latitude', 'Hemishere', 'Longitude', 'Meridien', 'Altitude','Orientation', 'Etage', 'Environnement' ]),ignore_index=True)
    tree = ET.parse(groundtruth_plan)
    root = tree.getroot()
    dplan = pd.DataFrame(columns = ['Etage', 'Lat_min', 'Lon_min', 'Lat_max', 'Lon_max'])
    for child in root:
        if child.tag == 'plan':
            if (child.find('numero').text=='2'):
                etage= -1
            elif(child.find('numero').text=='3'):
                etage=0
            elif(child.find('numero').text=='4'):
                etage=1
            elif(child.find('numero').text=='5'):
                etage=2
            elif(child.find('numero').text=='6'):
                etage=3
            elif(child.find('numero').text=='7'):
                etage=4
            elif(child.find('numero').text=='8'):
                etage=5
            elif(child.find('numero').text=='9'):
                etage=6
            else:
                etage=numpy.nan
            dplan = dplan.append(pd.Series([etage, float(child.find('lat_min').text), float(child.find('lon_min').text), float(child.find('lat_max').text), float(child.find('lon_max').text)], index =['Etage',  'Lat_max', 'Lon_min', 'Lat_min', 'Lon_max']), ignore_index=True)
    print(dplan)
    return dplan, dg, dg_time, overlays

def bag2pd(bag, topic, option):
    write2csv(bag, topic)
    folder = bag.rstrip(".bag") + "_csv"
    filename = folder + '/' + topic[0].replace('/', '_slash_') + '.csv'
    data = pd.read_csv(filename)
    if not option:
        shutil.rmtree(folder, ignore_errors=True)
    data.columns = '/decision_maker/ploc/' + data.columns
    print(data.columns)
    return data


def main(bag, groundtruth, scenario, init, figure_format, plot_show):
    plt.rcParams['figure.figsize'] = [10, 10]
    pd.set_option("display.precision", 10)
    # ground_truth
    if (groundtruth):
        dplan, dg, dg_time, overlays = groundtruth_retrieval(groundtruth, scenario)
        mergedStuff = pd.merge(dg_time, dg, on=['Numero','Type'], how='left')
        # Read stationnary point
        eval = mergedStuff[['Longitude', 'Latitude', 'Altitude', 'Nom', 'Type', 'Orientation','Numero', 'SecsStart', 'SecsEnd','Etage']].copy()
        # Read evaluation volume
        eval_volume = eval[eval['Type'].str.contains('V', regex=False)].copy()
        eval_points = eval[eval['Type'].str.match('S')].copy()
        print(eval_volume)
        print(eval_points)
    # PLOC
    topics=["/decision_maker/ploc"]
    df = bag2pd(bag, topics, False)
    print "df ready ! {}".format(df.columns.values.tolist())
    position = df[['/decision_maker/ploc/lat', '/decision_maker/ploc/lat_dir', '/decision_maker/ploc/lon', '/decision_maker/ploc/lon_dir']]
    # Convert deg min to deg decimal
    decimallat = []
    decimallon = []
    for i in position.values:
        data = str(i[0])
        decimalPointPosition = data.index('.')
        degrees = float(data[:decimalPointPosition-2])
        minutes = float(data[decimalPointPosition-2:])/60
        output = degrees + minutes
        if i[1] == 'S':
            output = -output
        decimallat.append(output)
        data = str(i[2])
        decimalPointPosition = data.index('.')
        degrees = float(data[:decimalPointPosition-2])
        minutes = float(data[decimalPointPosition-2:])/60
        output = degrees + minutes
        if i[3] == 'W':
            output = -output
        decimallon.append(output)

    df['decimal lat'] = decimallat
    df['decimal lon'] = decimallon

    # convert UTC time to secs
    secs = []
    for row in df[['/decision_maker/ploc/utc_date', '/decision_maker/ploc/utc_time']].values:
        date = row[0]
        time = row[1]
        if time < 100000.:
            utc = datetime.datetime(int("20"+str(date)[4:6]), int(str(date)[2:4]), int(str(date)[0:2]), int(str(time)[0:1]), int(str(time)[1:3]), int(str(time)[4:6]), int(str(time)[7:9])*10000)
        else:
            utc = datetime.datetime(int("20"+str(date)[4:6]), int(str(date)[2:4]), int(str(date)[0:2]), int(str(time)[0:2]), int(str(time)[2:4]), int(str(time)[4:6]), int(str(time)[7:9])*10000)
        secs.append(TIME.mktime(utc.timetuple()) + utc.microsecond / 1e6)

    df['Secs']=secs

    # Create kml with path, stationnary point and volumes
    kml = simplekml.Kml()
    sharedstyle = simplekml.Style()
    sharedstyle.iconstyle.color = simplekml.Color.orangered  # orange-Red
    sharedstyle.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
    sharedstyle.polystyle.color = simplekml.Color.changealpha("77", simplekml.Color.red)
    sharedstyle.linestyle.color = simplekml.Color.deeppink
    path = kml.newlinestring(name="Position", description="Parcours" + bag.rstrip(".bag"), coords=list(zip(df['decimal lon'], df['decimal lat'])))
    path.style = sharedstyle
    if (groundtruth):
        for row in eval_points.values:
            pnt = kml.newpoint(name=row[3], description="Stationnaires", coords=[(row[0], row[1])])
            pnt.style = sharedstyle
        my_fences = []
        for row in range(0, numpy.size(eval_volume.values, 0), 4):
            vol = kml.newpolygon(name=eval_volume.values[row][3], description="Volumes",
                                 outerboundaryis=[(eval_volume.values[row][0], eval_volume.values[row][1]), (eval_volume.values[row+1][0], eval_volume.values[row+1][1]), (eval_volume.values[row+2][0], eval_volume.values[row+2][1]), (eval_volume.values[row+3][0], eval_volume.values[row+3][1])],
                                 innerboundaryis=[])
            # Create a Polygon
            a = Polygon([(eval_volume.values[row][0], eval_volume.values[row][1]), (eval_volume.values[row+1][0], eval_volume.values[row+1][1]), (eval_volume.values[row+2][0], eval_volume.values[row+2][1]), (eval_volume.values[row+3][0], eval_volume.values[row+3][1])])
            my_fences.append(a)
            vol.style = sharedstyle

    kml.save(bag.rstrip(".bag") + '_PLOC_trace.kml')

    # Create kml with path, stationnary point and volumes and background level maps
    for level in dplan['Etage'].dropna().drop_duplicates():
        print(level)
        kml_level = simplekml.Kml()
        ground = kml_level.newgroundoverlay(name='Level' + str(level))
        print(overlays[str(int(level))])
        ground.icon.href = overlays[str(int(level))]
        coords=dplan.loc[dplan['Etage']== level]
        print([(coords.iloc[0]['Lon_min'], coords.iloc[0]['Lat_min']), (coords.iloc[0]['Lon_max'],coords.iloc[0]['Lat_min']), (coords.iloc[0]['Lon_max'], coords.iloc[0]['Lat_max']), (coords.iloc[0]['Lon_min'], coords.iloc[0]['Lat_max'])])
        ground.gxlatlonquad.coords = [(coords.iloc[0]['Lon_min'], coords.iloc[0]['Lat_min']), (coords.iloc[0]['Lon_max'],coords.iloc[0]['Lat_min']), (coords.iloc[0]['Lon_max'], coords.iloc[0]['Lat_max']), (coords.iloc[0]['Lon_min'], coords.iloc[0]['Lat_max'])]
        ground.style.iconstyle.color = simplekml.Color.changealpha("72", simplekml.Color.white)
        path = kml_level.newlinestring(name="Position", description="Parcours" + bag.rstrip(".bag"), coords=list(zip(df.loc[df['/decision_maker/ploc/level']==level,'decimal lon'], df.loc[df['/decision_maker/ploc/level']==level,'decimal lat'])))
        path.style = sharedstyle
        if (groundtruth):
            points=eval_points.loc[eval_points['Etage']==int(level)].values
            print(points)
            for row in points:
                pnt = kml_level.newpoint(name=row[3], description="Point de référence", coords=[(row[0], row[1])])
                pnt.style = sharedstyle
                for cpt, row2 in enumerate(eval_volume.loc[eval_volume['Etage']==int(level)].values):
                    if cpt % 4 == 0 :
                        vol = kml_level.newpolygon(name=row2[3], description="Volume de reference",
                            outerboundaryis=[(row2[0], row2[1]), (eval_volume.loc[eval_volume['Etage']==int(level)].values[cpt+1][0], eval_volume.loc[eval_volume['Etage']==int(level)].values[cpt+1][1]), (eval_volume.loc[eval_volume['Etage']==int(level)].values[cpt+2][0], eval_volume.loc[eval_volume['Etage']==int(level)].values[cpt+2][1]), (eval_volume.loc[eval_volume['Etage']==int(level)].values[cpt+3][0], eval_volume.loc[eval_volume['Etage']==int(level)].values[cpt+3][1])],
                            innerboundaryis=[])
                        vol.style = sharedstyle
        kml_level.save(bag.rstrip(".bag") + '_PLOC_trace_level_'+str(int(level))+'.kml')

    # plot path in 3D
    threedee = plt.figure().gca(projection='3d')
    colors = {'-3':'red','-2': 'red','-1':'tab:green', '0':'tab:blue', '1':'black', '2':'tab:orange', '3':'tab:purple', '4':'tab:pink', '5':'tab:cyan','6':'m', '7':'coral', '8':'cadetblue'}
    threedee.plot(df['decimal lon'], df['decimal lat'],df['/decision_maker/ploc/alt'], c='gray', label='WGS-trace')
    # Additional options
    threedee.scatter(df['decimal lon'], df['decimal lat'],df['/decision_maker/ploc/alt'], c=df['/decision_maker/ploc/level'].apply(lambda x: colors[str(int(x))]), s=100, lw=0)
    threedee.set_xlabel(u'latitude')
    threedee.set_ylabel(u'longitude')
    threedee.set_zlabel(u'altitude')
    plt.title(u'Tracé WGS (deg.dddd)')
    plt.legend(loc='best')
    plt.grid()
    plt.savefig(bag.rstrip(".bag") + '_PLOC_WGS.'+ figure_format, format=figure_format)
    if plot_show:
        plt.show()

    if (groundtruth):
        points_to_consider_volume = []
        cpt = 0
        for row in range(0, numpy.size(eval_volume[['SecsStart', 'SecsEnd']].values, 0), 4):
            a = df[df['Secs'] < eval_volume[['SecsEnd']].values[row][0]]
            b = a[a['Secs'] > eval_volume[['SecsStart']].values[row][0]]
            c = b[['decimal lat', 'decimal lon', '/decision_maker/ploc/alt']].values
            points_to_consider_volume.append(c)
            cpt += 1

        Topo = []
        moy = 0.0
        cpt = 0.0
        cpt_total_total = 0.0
        cpt_total_inside = 0.0
        for i, volume in enumerate(points_to_consider_volume):
            cpt_inside = 0.0
            cpt_total = 0.0
            for points in volume:
                cpt_total += 1.0
                # Create Point objects
                p1 = Point(points[1], points[0])
                if (p1.within(my_fences[i]) & (eval_volume[['Altitude']].values[4*i][0]<=points[2]+1.0<2.0+eval_volume[['Altitude']].values[4*i][0])):
                    cpt_inside += 1.0
            if cpt_total != 0.0:
                Critere_topo = float(cpt_inside) / float(cpt_total)
            else:
                Critere_topo = 0.

            cpt_total_inside += cpt_inside
            cpt_total_total += cpt_total
            moy += Critere_topo
            cpt += 1.0
            Topo.append({"Volume": eval_volume[['Nom']].values[4*i][0], "Critere_topo": Critere_topo, "cpt_total": cpt_total, "cpt_inside": cpt_inside})
        note_topo = 200. * cpt_total_inside / cpt_total_total
        moy = moy/cpt * 100.
        print(Topo)
        fig, ax = plt.subplots(2, 1, sharex=True)
        critere = []
        for volume in Topo:
            ax[0].bar(volume['Volume'], volume['cpt_total'], color='tab:blue')
            ax[0].bar(volume['Volume'], volume['cpt_inside'], color='tab:orange')
            critere.append(volume['Critere_topo'])

        ax[1].plot(numpy.arange(0, len(Topo)), critere, label='Erreur topologique')
        ax[1].set(xlabel=u'Numéro de volume', ylabel=u'Erreur topologique', title=u'Critere topologique')
        ax[1].legend()
        ax[0].grid()
        ax[0].set(xlabel=u'Numéro de volume', ylabel=u'Nombre de points', title=u'Critere topologique')
        ax[0].legend((u'Total', u'Inside'))
        ax[0].grid()
        plt.savefig(bag.rstrip(".bag") + '_PLOC_topologie.'+ figure_format, format=figure_format)
        if plot_show:
            plt.show()

        # first select Calculé point between Temps start en Temps end,
        # if stationnary type then calculate the (cep75H) 75% 2D-Error, 75% V-Error (cep75v)
        # That is take the third quartile of the error on the sample (error is euclidean distance between points)
        # Compute PEG2d = EXP(-CEP75/3), pegv = EXP(-CEP75v/3)
        # Create Vérité terrain from time_start to time_end
        # to do comupte the error
        points_to_consider_stationnary = []
        for row in eval_points.values:
            a = df[df['Secs'] < row[8]]
            b = a[a['Secs'] > row[7]]
            c = b[['decimal lat', 'decimal lon', '/decision_maker/ploc/alt']].values
            points_to_consider_stationnary.append(c)

        error_stationnary = []
        CEPH75 = []
        CEPV75 = []
        note_cep_h = 0.0
        note_cep_v = 0.0
        for i, stationnary in enumerate(points_to_consider_stationnary):
            gt = eval_points[['Longitude', 'Latitude', 'Numero']].iloc[[i]].values
            ht = eval_points[['Altitude']].iloc[[i]].values
            error_h = []
            error_v = []
            for point in stationnary:
                coords_1 = (gt[0][1], gt[0][0])
                coords_2 = (point[0], point[1])
                dist = geopy.distance.vincenty(coords_1, coords_2).m
                error_h.append(dist)
                error_v.append(numpy.float(numpy.absolute(point[2]-ht)))
            # plot the data
            q3 = int(round(3/4 * numpy.size(error_h)))
            if (len(error_h)>0):
                error_h = sorted(error_h)
                error_v = sorted(error_v)
                CEPH75.append(error_h[q3])
                CEPV75.append(error_v[q3])
                # num_bins = 50
                # fig, ax = plt.subplots()
                # # the histogram of the data
                # n, bins, patches = ax.hist(error_h, num_bins, density=1)
                # ax.set_xlabel(u"Distribution de l'erreur 2D (m)")
                # ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x}"))
                # ax.set_ylabel(u"Nombre de points pour une erreur donnée")
                # ax.set_title(u"Histogramme de l'erreur au stationnaire n°: " + str(gt[0][2]))
                # # Tweak spacing to prevent clipping of ylabel
                # fig.tight_layout()
                # plt.savefig(bag.rstrip(".bag") + '_PLOC_Erreur-2D-Stationnaire_' + str(gt[0][2]) +'.'+ figure_format, format=figure_format)
                # if plot_show:
                #     plt.show()
                error_stationnary.append({u'Numero de stationnaire': eval_points[['Numero']].values[i][0], u'Erreur 2D': error_h[q3], u'Erreur V': error_v[q3]})
                note_cep_h += numpy.exp(- error_h[q3] /3)
                note_cep_v += numpy.exp(- error_v[q3] / 3)
        note_cep_h = 130. * note_cep_h / len(points_to_consider_stationnary)
        note_cep_v = 70. * note_cep_v / len(points_to_consider_stationnary)
        fig, ax = plt.subplots()
        plt.plot(numpy.arange(0, len(CEPH75)), CEPH75, '-o', linewidth=2, label=u'CEPH75')  # Additional options
        plt.plot(numpy.arange(0, len(CEPH75)), CEPV75, '-o', linewidth=2, label=u'CEPV75')
        for x,y,z in zip(numpy.arange(0, len(CEPH75)), CEPH75, CEPV75):                                       # <--
            ax.annotate('%s' % eval_points[['Numero']].values[x][0], xy=(x, y),  xytext=(0, 3),textcoords="offset points",
                    ha='center', va='bottom')
            ax.annotate('%s' % eval_points[['Numero']].values[x][0], xy=(x, z),  xytext=(0, 3),textcoords="offset points",
                    ha='center', va='bottom')
        plt.xlabel(u'Stationnaire ')
        plt.ylabel(u'Erreur (m)')
        plt.title(u'Erreur CEP75')
        plt.legend()
        plt.grid()
        plt.savefig(bag.rstrip(".bag") + '_PLOC_CEP.'+ figure_format, format=figure_format)
        if plot_show:
            plt.show()
        mean_CEPH75 = numpy.mean(CEPH75)
        mean_CEPV75 = numpy.mean(CEPV75)


        # Erreur Orientation
        if init:
            T_max = 15.0
            T_min= 5.0
        else:
            T_max = 20.0
            T_min= 10.0
        points_to_consider_stationnary_with_h = []
        for row in eval_points.dropna().values:
            a = df[df['Secs'] < row[8]]
            b = a[a['Secs'] > row[7]]
            c = b[['decimal lat', 'decimal lon', '/decision_maker/ploc/alt', '/decision_maker/ploc/heading']].values
            points_to_consider_stationnary_with_h.append(c)

        error_heading = []
        for i, stationnary in enumerate(points_to_consider_stationnary_with_h):
            gt = eval_points[['Orientation']].dropna().iloc[[i]].values
            if (gt!= numpy.NAN):
                error_o = []
                for point in stationnary:
                    error_o.append(numpy.float(numpy.absolute(point[3]-gt)))
                error_heading.append(numpy.mean(error_o))
        mean_error_heading = numpy.mean(error_heading)
        note_heading = 20. * (T_max - min(T_max, max(T_min, mean_error_heading)))/(T_max - T_min)
        fig, ax = plt.subplots()
        plt.plot(numpy.arange(0, len(error_heading)), error_heading, 'o', linewidth=2, label=u'Erreur')  # Additional options
        plt.xlabel(u'Stationnaire avec orientation n°')
        plt.ylabel(u'Erreur (°)')
        plt.title(u"Erreur d'orientation")
        plt.legend()
        plt.grid()
        for x,y in zip(numpy.arange(0, len(error_heading)), error_heading):
            ax.annotate('%s' % eval_points[['Orientation','Numero']].dropna().values[x][1], xy=(x, y),  xytext=(0, 3),textcoords="offset points",
                    ha='center', va='bottom')
        plt.savefig(bag.rstrip(".bag") + '_PLOC_orientation_erreur.' + figure_format, format=figure_format)
        if plot_show:
            plt.show()
        obFichier = open(bag.rstrip(".bag") +'_PLOC_Erreur_Note.txt', 'w')
        obFichier.write('Erreurs CEP')
        obFichier.write("\nErreur CEP :" + str(error_stationnary))
        obFichier.write("\nErreur Horizontale à 75% :" + str(mean_CEPH75))
        obFichier.write("\nErreur Verticale à 75% :" + str(mean_CEPV75))
        obFichier.write("\nCritère Topologique :" + str(Topo))
        obFichier.write("\nErreur Orientation :" + str(mean_error_heading))
        obFichier.write("\n========================================================")
        obFichier.write("\nNote Précision Topologique :" + str(note_topo) + " sur 200")
        obFichier.write("\nNote Précision Géométrique 2D :" + str(note_cep_h)+ " sur 130" )
        obFichier.write("\nNote Précision Géométrique V :" + str(note_cep_v) + " sur 70")
        obFichier.write("\nNote Précision orientation :" + str(note_heading) + " sur 20")
        obFichier.close()
        ground_truth_environnement = []
        ground_truth_heading = []
        ground_truth_altitude = []
        ground_truth_niveau = []
        ground_truth_state = []
        time_windows = []
        for row in mergedStuff[['SecsStart', 'SecsEnd', 'Environnement', 'Orientation', 'Altitude', 'Etage', 'Type']].values:
            time_windows.extend(list(range(int(row[0]), int(row[1]))))
            ground_truth_environnement.extend([row[2] for i in range(int(row[0]), int(row[1]))])
            ground_truth_heading.extend([row[3] for i in range(int(row[0]), int(row[1]))])
            ground_truth_altitude.extend([row[4] for i in range(int(row[0]), int(row[1]))])
            ground_truth_niveau.extend([row[5] for i in range(int(row[0]), int(row[1]))])
            if row[6] in "S":
                ground_truth_state.extend([row[6] for i in range(int(row[0]), int(row[1]))])
            else:
                ground_truth_state.extend(['D' for i in range(int(row[0]), int(row[1]))])

    # Plot Environnement I/O, Computation Mode
    fig, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(df['Secs'], df['/decision_maker/ploc/pose_mode'], linewidth=2, label=u'Mode')  # Additional options
    ax[0].set(xlabel=u'Temps (s)', ylabel=u'Mode', title='Mode de positionnement')
    ax[0].grid()
    ax[1].plot(df['Secs'], df['/decision_maker/ploc/environment_state'], linewidth=2, label=u'Calculé')
    if(groundtruth):
        ax[1].plot(time_windows, ground_truth_environnement, '*', label=u'Vérité terrain')  # Additional options
    ax[1].set(xlabel=u'Temps (s)', title=u'Indoor/Outdoor')
    ax[1].grid()
    ax[1].legend()
    plt.savefig(bag.rstrip(".bag") + '_PLOC_Environnement.' + figure_format, format=figure_format)
    if plot_show:
        plt.show()

    # Plot Orientation
    plt.figure()
    plt.plot(df['Secs'], df['/decision_maker/ploc/heading'], linewidth=2, label=u'Calculé')  # Additional options
    if(groundtruth):
        plt.plot(time_windows, ground_truth_heading, '*', label=u'Vérité terrain')
    plt.xlabel(u'Temps (s)')
    plt.ylabel(u'Cap (degrés)')
    plt.title(u'Orientation')
    plt.legend()
    plt.grid()
    plt.savefig(bag.rstrip(".bag") + '_PLOC_orientation.' + figure_format, format=figure_format)
    if plot_show:
        plt.show()
    # Plot level and altitude
    fig, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(df['Secs'], df['/decision_maker/ploc/alt'], linewidth=2, label=u'Calculé')  # Additional options
    if(groundtruth):
        ax[0].plot(time_windows, ground_truth_altitude, '*', label=u'Vérité Terrain')
    ax[0].set(xlabel=u'Temps (s)', ylabel=u'Altitude (m)', title=u'Altitude')
    ax[0].legend()
    ax[0].grid()
    ax[1].plot(df['Secs'], df['/decision_maker/ploc/level'], linewidth=2, label=u'Calculé')  # Additional options
    if(groundtruth):
        ax[1].plot(time_windows, ground_truth_niveau, '*', label=u'Vérité terrain')
    ax[1].set(xlabel=u'Temps (s)', ylabel=u'Niveau', title=u'Niveau')
    ax[1].grid()
    ax[1].legend()
    plt.savefig(bag.rstrip(".bag") + '_PLOC_Altitude.' + figure_format, format=figure_format)
    if plot_show:
        plt.show()

    # Plot Speed and State
    fig, ax = plt.subplots(2, 1, sharex=True)
    ax[0].plot(df['Secs'], df['/decision_maker/ploc/speed'], linewidth=2, label=u'Calculé')  # Additional options
    ax[0].set(xlabel=u'Temps (s)', ylabel=u'Vitesse (m/s)', title=u'Vitesse')
    ax[0].grid()
    ax[1].plot(df['Secs'], df['/decision_maker/ploc/moving_state'], linewidth=2, label=u'Calculé')  # Additional options
    if(groundtruth):
        ax[1].plot(time_windows, ground_truth_state, '*', label=u'Vérité terrain')
    ax[1].set(xlabel=u'Temps (s)', ylabel=u'Déplacement', title=u'Mode de déplacement')
    ax[1].legend()
    ax[1].grid()
    plt.savefig(bag.rstrip(".bag") + '_PLOC_Deplacement.'+figure_format, format=figure_format)
    if plot_show:
        plt.show()

def usage(comment):
    print(comment)
    print('\nUsage: \n ./PLOC-plot.py -b <Bag-path> -g <Ground-truth-directory> -s <Scenario-name> -i <Initialisation-boolean> -f <Output-image-format> [-d]')

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:g:s:i:f:d:", ['help', 'bagpath=', 'gtdirectory=', 'scenario=', 'init=', 'figure_format=', 'display='])
    except getopt.GetoptError as err:
        sys.exit(2)
    bag = None
    groundtruth = None
    scenario = None
    init = False
    figure_format = 'png'
    plot_show = False
    for opt, arg in opts:
        if opt == '-h':
            sys.exit()
        elif opt in ("-b", "--bagpath"):
            bag = arg
            print('Bag file : ', bag)
        elif opt in ("-g", "--gtdirectory"):
            groundtruth = arg
            print('Ground Truth Directory : ', groundtruth)
        elif opt in ("-s", "--scenario"):
            scenario = arg
            print('Scenario : ', scenario)
        elif opt in ("-i", "--init"):
            init = arg.lower() == 'true'
            print('Initialisation : ', init)
        elif opt in("-f", "--format"):
            figure_format = arg
            print('Figure format to output', figure_format)
        elif opt in("-d", "--display"):
            plot_show = True
            print('Display figures during runtime :', plot_show)
        else:
            assert False, "Unhandled option"
    main(bag, groundtruth, scenario, init, figure_format, plot_show)
